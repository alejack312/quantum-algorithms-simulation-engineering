from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from qiskit import QuantumCircuit

from quantum_swe_artifacts.backends.custom_backend_adapter import get_default_adapter
from quantum_swe_artifacts.backends.qiskit_backend import run_circuit, run_statevector
from quantum_swe_artifacts.circuits.random_circuits import make_random_circuit
from quantum_swe_artifacts.logging_utils import write_csv, write_json


@dataclass(frozen=True)
class ModeSpec:
    name: str
    shots: int | None


def _z_value_from_bit(bit: str) -> float:
    return 1.0 if bit == "0" else -1.0


def _expectation_from_statevector(statevector: np.ndarray, n_qubits: int, observable: str) -> float:
    probs = np.abs(statevector) ** 2
    total = 0.0
    for idx, prob in enumerate(probs):
        bitstring = format(int(idx), f"0{n_qubits}b")
        if observable == "sumZ":
            value = sum(_z_value_from_bit(bit) for bit in bitstring)
        else:
            value = _z_value_from_bit(bitstring[-1])
        total += value * float(prob)
    return float(total)


def _expectation_from_counts(counts: dict[str, int], shots: int, observable: str) -> float:
    if shots <= 0:
        return 0.0
    total = 0.0
    for bitstring, count in counts.items():
        if observable == "sumZ":
            value = sum(_z_value_from_bit(bit) for bit in bitstring)
        else:
            value = _z_value_from_bit(bitstring[-1])
        total += value * count
    return float(total) / float(shots)


def _parse_list(value, default: list, cast_type=int) -> list:
    if value is None:
        return list(default)
    if isinstance(value, list):
        return [cast_type(v) for v in value]
    return [cast_type(value)]


def _parse_modes(config: dict) -> list[ModeSpec]:
    raw_modes = config.get("modes") or [
        {"name": "statevector_exact", "shots": None},
        {"name": "qasm_shots", "shots": int(config.get("backend", {}).get("shots", 1024))},
    ]

    modes: list[ModeSpec] = []
    for item in raw_modes:
        if isinstance(item, str):
            if item == "statevector_exact":
                modes.append(ModeSpec(name="statevector_exact", shots=None))
            elif item == "qasm_shots":
                shots_default = int(config.get("backend", {}).get("shots", 1024))
                modes.append(ModeSpec(name="qasm_shots", shots=shots_default))
            else:
                raise ValueError(f"Unsupported mode '{item}'")
            continue

        name = str(item.get("name", "")).strip()
        if name not in {"statevector_exact", "qasm_shots"}:
            raise ValueError(f"Unsupported mode '{name}'")
        shots = item.get("shots")
        if name == "statevector_exact":
            shots = None
        elif shots is None:
            shots = int(config.get("backend", {}).get("shots", 1024))
        modes.append(ModeSpec(name=name, shots=None if shots is None else int(shots)))

    return modes


def _make_iqp_depth_circuit(n_qubits: int, depth: int, seed: int, entangler_prob: float = 0.35) -> QuantumCircuit:
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_qubits)

    for q in range(n_qubits):
        qc.h(q)

    for _ in range(depth):
        for q in range(n_qubits):
            qc.rz(float(rng.uniform(-np.pi, np.pi)), q)
        for q in range(n_qubits - 1):
            if rng.random() < entangler_prob:
                qc.cx(q, q + 1)
                qc.rz(float(rng.uniform(-np.pi / 3.0, np.pi / 3.0)), q + 1)
                qc.cx(q, q + 1)

    for q in range(n_qubits):
        qc.h(q)

    return qc


def _build_circuit(circuit_family: str, n_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    if circuit_family == "iqp":
        return _make_iqp_depth_circuit(n_qubits=n_qubits, depth=depth, seed=seed)
    if circuit_family == "random":
        return make_random_circuit(n_qubits=n_qubits, depth=depth, seed=seed)
    raise ValueError(f"Unsupported circuit family '{circuit_family}'")


def _run_qiskit_backend(circ: QuantumCircuit, mode: ModeSpec, observable: str, seed: int) -> dict:
    if mode.name == "statevector_exact":
        result = run_statevector(circ, seed=seed)
        expectation = _expectation_from_statevector(
            statevector=np.asarray(result["statevector"], dtype=complex),
            n_qubits=circ.num_qubits,
            observable=observable,
        )
        return {
            "backend_name": "qiskit_backend",
            "backend_impl": str(result.get("backend", "qiskit_statevector")),
            "mode": mode.name,
            "shots": None,
            "runtime_s": float(result["wall_time_s"]),
            "expectation_value": float(expectation),
        }

    if mode.shots is None:
        raise ValueError("qasm_shots mode requires shots")

    result = run_circuit(circ, shots=int(mode.shots), seed=seed, noise_model=None)
    expectation = _expectation_from_counts(
        counts=dict(result.get("counts", {})),
        shots=int(mode.shots),
        observable=observable,
    )
    return {
        "backend_name": "qiskit_backend",
        "backend_impl": str(result.get("backend", "qiskit_qasm")),
        "mode": mode.name,
        "shots": int(mode.shots),
        "runtime_s": float(result["wall_time_s"]),
        "expectation_value": float(expectation),
    }


def _aggregate_summary(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = [
        "n_qubits",
        "depth",
        "circuit_family",
        "observable",
        "backend_name",
        "mode",
        "shots",
    ]
    summary = (
        df.groupby(group_cols, as_index=False, dropna=False)
        .agg(
            trials=("runtime_s", "count"),
            runtime_mean_s=("runtime_s", "mean"),
            runtime_std_s=("runtime_s", "std"),
            expectation_mean=("expectation_value", "mean"),
            expectation_std=("expectation_value", "std"),
            abs_error_mean=("abs_error_vs_reference", "mean"),
            abs_error_std=("abs_error_vs_reference", "std"),
        )
    )
    for col in ["runtime_std_s", "expectation_std", "abs_error_std"]:
        summary[col] = summary[col].fillna(0.0)
    summary["runtime_stderr_s"] = summary["runtime_std_s"] / np.sqrt(summary["trials"].clip(lower=1))
    summary["abs_error_stderr"] = summary["abs_error_std"] / np.sqrt(summary["trials"].clip(lower=1))
    return summary


def _plot_runtime_vs_n(summary: pd.DataFrame, outpath: Path, representative_depth: int) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    subset = summary[summary["depth"] == representative_depth].copy()
    if subset.empty:
        return

    grouped = (
        subset.groupby(["n_qubits", "backend_name", "mode"], as_index=False)
        .agg(runtime_mean_s=("runtime_mean_s", "mean"))
        .sort_values(["backend_name", "mode", "n_qubits"])
    )

    plt.figure(figsize=(8, 5))
    for (backend_name, mode), sub in grouped.groupby(["backend_name", "mode"]):
        plt.plot(sub["n_qubits"], sub["runtime_mean_s"], marker="o", label=f"{backend_name} | {mode}")
    plt.xlabel("n_qubits")
    plt.ylabel("runtime (s)")
    plt.title(f"Runtime vs n_qubits (depth={representative_depth})")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def _plot_runtime_vs_depth(summary: pd.DataFrame, outpath: Path, representative_n: int) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    subset = summary[summary["n_qubits"] == representative_n].copy()
    if subset.empty:
        return

    grouped = (
        subset.groupby(["depth", "backend_name", "mode"], as_index=False)
        .agg(runtime_mean_s=("runtime_mean_s", "mean"))
        .sort_values(["backend_name", "mode", "depth"])
    )

    plt.figure(figsize=(8, 5))
    for (backend_name, mode), sub in grouped.groupby(["backend_name", "mode"]):
        plt.plot(sub["depth"], sub["runtime_mean_s"], marker="o", label=f"{backend_name} | {mode}")
    plt.xlabel("depth")
    plt.ylabel("runtime (s)")
    plt.title(f"Runtime vs depth (n_qubits={representative_n})")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def _plot_abs_error_vs_n(summary: pd.DataFrame, outpath: Path, representative_depth: int) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    subset = summary[(summary["depth"] == representative_depth) & (summary["mode"] == "qasm_shots")].copy()

    plt.figure(figsize=(8, 5))
    if subset.empty:
        plt.text(0.5, 0.5, "No shot-based rows available", ha="center", va="center")
        plt.axis("off")
    else:
        grouped = (
            subset.groupby(["n_qubits", "backend_name"], as_index=False)
            .agg(abs_error_mean=("abs_error_mean", "mean"))
            .sort_values(["backend_name", "n_qubits"])
        )
        for backend_name, sub in grouped.groupby("backend_name"):
            plt.plot(sub["n_qubits"], sub["abs_error_mean"], marker="o", label=str(backend_name))
        plt.xlabel("n_qubits")
        plt.ylabel("mean abs error vs reference")
        plt.title(f"Abs error vs n_qubits (mode=qasm_shots, depth={representative_depth})")
        plt.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def run(config: dict, output_dir: Path) -> dict:
    sweep = config.get("sweep", {})
    n_qubits_values = _parse_list(sweep.get("n_qubits", sweep.get("qubits", [4, 6])), default=[4, 6], cast_type=int)
    depth_values = _parse_list(sweep.get("depth", [2, 4]), default=[2, 4], cast_type=int)
    circuit_families = _parse_list(sweep.get("circuit_families", ["iqp", "random"]), default=["iqp", "random"], cast_type=str)
    observables = _parse_list(sweep.get("observable", ["Z0"]), default=["Z0"], cast_type=str)
    k = int(sweep.get("K", config.get("repetitions", 5)))
    base_seed = int(config.get("seed", 42))
    modes = _parse_modes(config)

    adapter = get_default_adapter()
    rows: list[dict] = []

    for circuit_family in circuit_families:
        for observable in observables:
            for n_qubits in n_qubits_values:
                for depth in depth_values:
                    for rep in range(k):
                        trial_seed = int(base_seed + rep)
                        circuit_seed = int(base_seed + 10_000 * n_qubits + 100 * depth + rep)
                        circ = _build_circuit(
                            circuit_family=circuit_family,
                            n_qubits=int(n_qubits),
                            depth=int(depth),
                            seed=circuit_seed,
                        )

                        reference_state = run_statevector(circ, seed=circuit_seed)
                        reference_expectation = _expectation_from_statevector(
                            statevector=np.asarray(reference_state["statevector"], dtype=complex),
                            n_qubits=int(n_qubits),
                            observable=observable,
                        )

                        for mode in modes:
                            trial_key = {
                                "n_qubits": int(n_qubits),
                                "depth": int(depth),
                                "circuit_family": circuit_family,
                                "observable": observable,
                                "mode": mode.name,
                                "shots": mode.shots,
                                "seed": trial_seed,
                            }

                            qiskit_row = _run_qiskit_backend(circ=circ, mode=mode, observable=observable, seed=trial_seed)
                            qiskit_row.update(trial_key)
                            qiskit_row["reference_expectation"] = float(reference_expectation)
                            qiskit_row["abs_error_vs_reference"] = abs(
                                float(qiskit_row["expectation_value"]) - float(reference_expectation)
                            )
                            rows.append(qiskit_row)

                            custom_row = adapter.execute(
                                circ=circ,
                                mode=mode.name,
                                observable=observable,
                                shots=mode.shots,
                                seed=trial_seed,
                            )
                            custom_row.update(trial_key)
                            custom_row["reference_expectation"] = float(reference_expectation)
                            custom_row["abs_error_vs_reference"] = abs(
                                float(custom_row["expectation_value"]) - float(reference_expectation)
                            )
                            rows.append(custom_row)

    write_csv(rows, output_dir / "results.csv")

    results_df = pd.DataFrame(rows)
    summary_df = _aggregate_summary(results_df)
    summary_df["shots"] = summary_df["shots"].astype(object)
    summary_df.loc[summary_df["mode"] == "statevector_exact", "shots"] = None
    summary_df.loc[summary_df["mode"] != "statevector_exact", "shots"] = summary_df.loc[
        summary_df["mode"] != "statevector_exact", "shots"
    ].apply(lambda x: int(float(x)))
    summary = {
        "experiment": "bench_qiskit_vs_custom",
        "config": {
            "n_qubits": n_qubits_values,
            "depth": depth_values,
            "circuit_families": circuit_families,
            "observable": observables,
            "modes": [{"name": m.name, "shots": m.shots} for m in modes],
            "K": k,
            "seed": base_seed,
        },
        "required_columns": [
            "n_qubits",
            "depth",
            "circuit_family",
            "observable",
            "backend_name",
            "mode",
            "shots",
            "seed",
            "runtime_s",
            "expectation_value",
            "abs_error_vs_reference",
        ],
        "aggregates": summary_df.to_dict(orient="records"),
    }
    write_json(summary, output_dir / "summary.json")

    artifact_fig_dir = Path("artifacts/01_bench_qiskit_vs_custom/figures")
    representative_depth = sorted(depth_values)[len(depth_values) // 2]
    representative_n = sorted(n_qubits_values)[len(n_qubits_values) // 2]
    _plot_runtime_vs_n(
        summary=summary_df,
        outpath=artifact_fig_dir / "runtime_vs_n_300dpi.png",
        representative_depth=int(representative_depth),
    )
    _plot_runtime_vs_depth(
        summary=summary_df,
        outpath=artifact_fig_dir / "runtime_vs_depth_300dpi.png",
        representative_n=int(representative_n),
    )
    _plot_abs_error_vs_n(
        summary=summary_df,
        outpath=artifact_fig_dir / "abs_error_vs_n_300dpi.png",
        representative_depth=int(representative_depth),
    )

    return {
        "rows": len(rows),
        "output_dir": str(output_dir),
        "artifact_figures": str(artifact_fig_dir),
    }
