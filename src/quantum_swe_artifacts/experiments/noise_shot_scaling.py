from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from qiskit import QuantumCircuit

from quantum_swe_artifacts.backends.qiskit_backend import run_circuit, run_statevector
from quantum_swe_artifacts.circuits.random_circuits import make_random_circuit
from quantum_swe_artifacts.logging_utils import write_csv, write_json


@dataclass(frozen=True)
class Regime:
    n_qubits: int
    depth: int


def _z0_expectation_from_statevector(statevector: np.ndarray, n_qubits: int) -> float:
    probs = np.abs(statevector) ** 2
    total = 0.0
    for idx, prob in enumerate(probs):
        bitstring = format(int(idx), f"0{n_qubits}b")
        z0 = 1.0 if bitstring[-1] == "0" else -1.0
        total += z0 * float(prob)
    return float(total)


def _z0_expectation_from_counts(counts: dict[str, int], shots: int) -> float:
    if shots <= 0:
        return 0.0
    total = 0.0
    for bitstring, count in counts.items():
        z0 = 1.0 if bitstring[-1] == "0" else -1.0
        total += z0 * count
    return float(total) / float(shots)


def _make_iqp_depth_circuit(n_qubits: int, depth: int, seed_circuit: int, seed_params: int) -> QuantumCircuit:
    rng_structure = np.random.default_rng(seed_circuit)
    rng_params = np.random.default_rng(seed_params)
    qc = QuantumCircuit(n_qubits)

    for q in range(n_qubits):
        qc.h(q)

    for _ in range(depth):
        for q in range(n_qubits):
            qc.rz(float(rng_params.uniform(-np.pi, np.pi)), q)
        for q in range(n_qubits - 1):
            if rng_structure.random() < 0.6:
                qc.cx(q, q + 1)
                qc.rz(float(rng_params.uniform(-np.pi / 3.0, np.pi / 3.0)), q + 1)
                qc.cx(q, q + 1)

    for q in range(n_qubits):
        qc.h(q)

    return qc


def _build_circuit(
    circuit_family: str,
    n_qubits: int,
    depth: int,
    seed_circuit: int,
    seed_params: int,
) -> QuantumCircuit:
    if circuit_family == "iqp":
        return _make_iqp_depth_circuit(
            n_qubits=n_qubits,
            depth=depth,
            seed_circuit=seed_circuit,
            seed_params=seed_params,
        )
    if circuit_family == "random":
        merged_seed = int(seed_circuit + 10_000 * seed_params)
        return make_random_circuit(n_qubits=n_qubits, depth=depth, seed=merged_seed)
    raise ValueError(f"Unsupported circuit family '{circuit_family}'")


def _parse_regimes(config: dict) -> list[Regime]:
    raw_regimes = config.get("sweep", {}).get("regimes", [])
    if not raw_regimes:
        raw_regimes = [
            {"n_qubits": 8, "depth": 6},
            {"n_qubits": 12, "depth": 8},
        ]
    regimes: list[Regime] = []
    for item in raw_regimes:
        regimes.append(Regime(n_qubits=int(item["n_qubits"]), depth=int(item["depth"])))
    return regimes


def _aggregate(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["circuit_family", "observable", "n_qubits", "depth", "shots"]
    summary = (
        df.groupby(group_cols, as_index=False)
        .agg(
            trials=("abs_error", "count"),
            mean_abs_error=("abs_error", "mean"),
            std_abs_error=("abs_error", "std"),
            mean_runtime_s=("runtime_s", "mean"),
            std_runtime_s=("runtime_s", "std"),
        )
        .fillna(0.0)
    )
    summary["stderr_abs_error"] = summary["std_abs_error"] / np.sqrt(summary["trials"].clip(lower=1))
    summary["stderr_runtime_s"] = summary["std_runtime_s"] / np.sqrt(summary["trials"].clip(lower=1))
    return summary


def _curve_label(family: str, n_qubits: int, depth: int) -> str:
    return f"{family} | n={n_qubits}, d={depth}"


def _plot_metric(
    summary_df: pd.DataFrame,
    y_col: str,
    y_label: str,
    title: str,
    outpath: Path,
) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8.5, 5.2))

    keys = ["circuit_family", "n_qubits", "depth"]
    for (family, n_qubits, depth), sub in summary_df.groupby(keys):
        sub = sub.sort_values("shots")
        plt.plot(
            sub["shots"],
            sub[y_col],
            marker="o",
            label=_curve_label(family=family, n_qubits=int(n_qubits), depth=int(depth)),
        )

    plt.xscale("log")
    plt.xlabel("shots")
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def run(config: dict, output_dir: Path) -> dict:
    sweep = config.get("sweep", {})
    circuit_families = sweep.get("circuit_families", ["iqp", "random"])
    observable = str(config.get("observable", "Z0"))
    if observable != "Z0":
        raise ValueError("noise_shot_scaling currently supports observable='Z0' only.")

    shots_values = [int(v) for v in sweep.get("shots", [10, 25, 50, 100, 200, 500, 1000, 2000, 5000])]
    repeats = int(sweep.get("K", config.get("repetitions", 30)))
    base_seed = int(config.get("seed", 42))
    regimes = _parse_regimes(config)

    rows: list[dict] = []

    for family in circuit_families:
        for regime in regimes:
            for shots in shots_values:
                for rep in range(repeats):
                    seed = int(base_seed + rep)
                    seed_circuit = int(base_seed + 10_000 * regime.n_qubits + 100 * regime.depth + rep)
                    seed_params = int(base_seed + 20_000 * regime.n_qubits + 200 * regime.depth + rep)
                    seed_shots = int(base_seed + 30_000 * regime.n_qubits + 300 * regime.depth + shots + rep)

                    circuit = _build_circuit(
                        circuit_family=str(family),
                        n_qubits=int(regime.n_qubits),
                        depth=int(regime.depth),
                        seed_circuit=seed_circuit,
                        seed_params=seed_params,
                    )

                    ref_result = run_statevector(circuit, seed=seed)
                    expectation_ref = _z0_expectation_from_statevector(
                        statevector=np.asarray(ref_result["statevector"], dtype=complex),
                        n_qubits=int(regime.n_qubits),
                    )

                    est_result = run_circuit(circuit, shots=int(shots), seed=seed_shots, noise_model=None)
                    expectation_est = _z0_expectation_from_counts(
                        counts=dict(est_result.get("counts", {})),
                        shots=int(shots),
                    )

                    rows.append(
                        {
                            "circuit_family": str(family),
                            "observable": observable,
                            "n_qubits": int(regime.n_qubits),
                            "depth": int(regime.depth),
                            "shots": int(shots),
                            "seed": seed,
                            "seed_circuit": seed_circuit,
                            "seed_params": seed_params,
                            "seed_shots": seed_shots,
                            "backend_name": str(est_result.get("backend", "qiskit_aer")),
                            "mode": "qasm_shots",
                            "expectation_est": float(expectation_est),
                            "expectation_ref": float(expectation_ref),
                            "abs_error": abs(float(expectation_est) - float(expectation_ref)),
                            "runtime_s": float(est_result["wall_time_s"]),
                        }
                    )

    write_csv(rows, output_dir / "results.csv")
    df = pd.DataFrame(rows)
    summary_df = _aggregate(df)

    summary = {
        "experiment": "noise_shot_scaling",
        "config": {
            "circuit_families": list(circuit_families),
            "observable": observable,
            "regimes": [{"n_qubits": r.n_qubits, "depth": r.depth} for r in regimes],
            "shots": shots_values,
            "K": repeats,
            "seed": base_seed,
            "reference_mode": "statevector_exact",
            "estimate_mode": "qasm_shots",
        },
        "aggregates": summary_df.to_dict(orient="records"),
    }
    write_json(summary, output_dir / "summary.json")

    artifact_dir = Path("artifacts/02_noise_shot_scaling/figures")
    _plot_metric(
        summary_df=summary_df,
        y_col="mean_abs_error",
        y_label="mean abs error",
        title="Abs Error vs Shots (qasm_shots vs statevector reference)",
        outpath=artifact_dir / "abs_error_vs_shots_300dpi.png",
    )
    _plot_metric(
        summary_df=summary_df,
        y_col="stderr_abs_error",
        y_label="stderr(abs error)",
        title="StdErr Abs Error vs Shots",
        outpath=artifact_dir / "stderr_abs_error_vs_shots_300dpi.png",
    )
    _plot_metric(
        summary_df=summary_df,
        y_col="mean_runtime_s",
        y_label="mean runtime (s)",
        title="Runtime vs Shots (qasm_shots)",
        outpath=artifact_dir / "runtime_vs_shots_300dpi.png",
    )

    return {
        "rows": len(rows),
        "output_dir": str(output_dir),
        "artifact_figures": str(artifact_dir),
    }
