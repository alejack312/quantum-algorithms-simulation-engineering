from __future__ import annotations

import math
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from quantum_swe_artifacts.backends.qiskit_backend import run_circuit
from quantum_swe_artifacts.logging_utils import write_csv, write_json
from quantum_swe_artifacts.plotting import plot_grad_variance


def _parse_grid(config: dict) -> tuple[list[int], list[int], int, int]:
    sweep = config.get("sweep", {})
    circuit_cfg = config.get("circuit", {})
    repeats_cfg = config.get("repeats", {})

    qubits = circuit_cfg.get("n_qubits", sweep.get("qubits", [2, 4, 6]))
    depths = circuit_cfg.get("depth", sweep.get("depth", [2]))

    if not isinstance(qubits, list):
        qubits = [int(qubits)]
    if not isinstance(depths, list):
        depths = [int(depths)]

    k = int(repeats_cfg.get("seeds", config.get("init_samples", config.get("repetitions", 20))))
    base_seed = int(repeats_cfg.get("base_seed", config.get("seed", 42)))
    return [int(x) for x in qubits], [int(x) for x in depths], k, base_seed


def _build_parametric_circuit(
    n_qubits: int,
    depth: int,
    params: np.ndarray,
    circuit_family: str,
    seed_circuit: int,
    parameter_tying: str,
    entangler_prob: float,
) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits)
    idx = 0

    if circuit_family == "iqp":
        for q in range(n_qubits):
            qc.h(q)

        rng = np.random.default_rng(seed_circuit)
        for _ in range(depth):
            if parameter_tying == "global_shared":
                theta = float(params[0])
                for q in range(n_qubits):
                    qc.rz(theta, q)
            elif parameter_tying == "layer_shared":
                theta = float(params[idx])
                idx += 1
                for q in range(n_qubits):
                    qc.rz(theta, q)
            else:
                for q in range(n_qubits):
                    qc.rz(float(params[idx]), q)
                    idx += 1
            for q in range(n_qubits - 1):
                if rng.random() < entangler_prob:
                    qc.cx(q, q + 1)
                    qc.rz(math.pi / 8.0, q + 1)
                    qc.cx(q, q + 1)

        for q in range(n_qubits):
            qc.h(q)
        return qc

    # Default family: hardware-efficient layered RX + CZ chain.
    for _ in range(depth):
        if parameter_tying == "global_shared":
            theta = float(params[0])
            for q in range(n_qubits):
                qc.rx(theta, q)
        elif parameter_tying == "layer_shared":
            theta = float(params[idx])
            idx += 1
            for q in range(n_qubits):
                qc.rx(theta, q)
        else:
            for q in range(n_qubits):
                qc.rx(float(params[idx]), q)
                idx += 1
        for q in range(n_qubits - 1):
            qc.cz(q, q + 1)

    return qc


def _expectation_z0_exact(circuit: QuantumCircuit) -> float:
    state = Statevector.from_instruction(circuit)
    probs = np.abs(state.data) ** 2
    n_qubits = circuit.num_qubits
    exp_z0 = 0.0
    for idx, p in enumerate(probs):
        bit = format(idx, f"0{n_qubits}b")[-1]
        exp_z0 += (1.0 if bit == "0" else -1.0) * p
    return float(exp_z0)


def _expectation_z0(circuit: QuantumCircuit, shots: int | None, seed_shots: int) -> tuple[float, str]:
    if shots is None:
        return _expectation_z0_exact(circuit), "statevector_exact"

    res = run_circuit(circuit, shots=int(shots), seed=seed_shots, noise_model=None)
    return float(res["expect_z0"]), str(res["backend"])


def _gradient_vector(
    n_qubits: int,
    depth: int,
    params: np.ndarray,
    circuit_family: str,
    seed_circuit: int,
    shots: int | None,
    seed_shots: int,
    parameter_tying: str,
    entangler_prob: float,
) -> tuple[np.ndarray, str]:
    shift = np.pi / 2.0
    grads = np.zeros_like(params, dtype=float)
    backend_name = "statevector_exact"

    for i in range(len(params)):
        plus = params.copy()
        minus = params.copy()
        plus[i] += shift
        minus[i] -= shift

        c_plus = _build_parametric_circuit(
            n_qubits, depth, plus, circuit_family, seed_circuit, parameter_tying, entangler_prob
        )
        c_minus = _build_parametric_circuit(
            n_qubits, depth, minus, circuit_family, seed_circuit, parameter_tying, entangler_prob
        )

        e_plus, backend_name = _expectation_z0(c_plus, shots=shots, seed_shots=seed_shots + i)
        e_minus, _ = _expectation_z0(c_minus, shots=shots, seed_shots=seed_shots + 1000 + i)
        grads[i] = 0.5 * (e_plus - e_minus)

    return grads, backend_name


def _fit_log_linear(df_summary: pd.DataFrame, x_col: str, group_col: str) -> list[dict]:
    fits: list[dict] = []
    floor = 1e-300

    for group_val, sub in df_summary.groupby(group_col):
        if sub.shape[0] < 2:
            continue
        x = sub[x_col].to_numpy(dtype=float)
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        coeffs = np.polyfit(x, y, deg=1)
        pred = coeffs[0] * x + coeffs[1]
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        fits.append(
            {
                "fit_type": f"log(mean_G) vs {x_col}",
                group_col: int(group_val),
                "slope": float(coeffs[0]),
                "intercept": float(coeffs[1]),
                "r2": r2,
            }
        )

    return fits


def _plot_log_fits(summary_df: pd.DataFrame, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    floor = 1e-300

    plt.figure(figsize=(7, 4))
    for depth, sub in summary_df.groupby("depth"):
        x = sub["n_qubits"].to_numpy(dtype=float)
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        plt.plot(x, y, marker="o", label=f"depth={depth}")
    plt.xlabel("n_qubits")
    plt.ylabel("log(mean_G)")
    plt.title("log(mean_G) vs n_qubits")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "log_meanG_vs_n.png")
    plt.close()

    plt.figure(figsize=(7, 4))
    for n, sub in summary_df.groupby("n_qubits"):
        x = sub["depth"].to_numpy(dtype=float)
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        plt.plot(x, y, marker="o", label=f"n={n}")
    plt.xlabel("depth")
    plt.ylabel("log(mean_G)")
    plt.title("log(mean_G) vs depth")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "log_meanG_vs_depth.png")
    plt.close()


def run(config: dict, output_dir: Path) -> dict:
    qubits, depths, repeats, base_seed = _parse_grid(config)
    circuit_family = str(config.get("circuit", {}).get("family", "iqp"))
    parameter_tying = str(config.get("circuit", {}).get("parameter_tying", "per_qubit"))
    entangler_prob = float(config.get("circuit", {}).get("entangler_prob", 0.2))
    grad_method = str(config.get("estimation", {}).get("grad_method", "param_shift"))
    observable = str(config.get("estimation", {}).get("observable", "Z0"))
    shots = config.get("estimation", {}).get("shots")
    shots = None if shots is None else int(shots)
    parallelism = int(config.get("runtime", {}).get("parallelism", 1))

    if grad_method != "param_shift":
        raise ValueError("Only param_shift is currently implemented for grad_variance.")

    tasks: list[dict] = []

    for n_qubits in qubits:
        for depth in depths:
            if parameter_tying == "global_shared":
                n_params = 1
            elif parameter_tying == "layer_shared":
                n_params = depth
            else:
                n_params = n_qubits * depth
            for trial_seed in range(base_seed, base_seed + repeats):
                seed_circuit = int(trial_seed)
                seed_params = int(trial_seed + 10_000)
                seed_shots = int(trial_seed + 20_000)
                tasks.append(
                    {
                        "n_qubits": n_qubits,
                        "depth": depth,
                        "trial_seed": int(trial_seed),
                        "seed_circuit": seed_circuit,
                        "seed_params": seed_params,
                        "seed_shots": seed_shots,
                        "circuit_family": circuit_family,
                        "n_params": n_params,
                        "parameter_tying": parameter_tying,
                        "observable": observable,
                        "grad_method": grad_method,
                        "shots": shots,
                        "entangler_prob": entangler_prob,
                    }
                )

    if parallelism > 1 and len(tasks) > 1:
        with ThreadPoolExecutor(max_workers=parallelism) as ex:
            rows = list(ex.map(_run_single_trial, tasks))
    else:
        rows = [_run_single_trial(t) for t in tasks]

    df = pd.DataFrame(rows)
    write_csv(rows, output_dir / "results.csv")

    grouped = (
        df.groupby(["n_qubits", "depth"], as_index=False)
        .agg(
            mean_G=("G_scalar", "mean"),
            var_G=("G_scalar", "var"),
            std_G=("G_scalar", "std"),
            mean_abs_grad=("mean_abs_grad", "mean"),
            runtime_mean_s=("runtime_s", "mean"),
            trials=("G_scalar", "count"),
        )
        .fillna(0.0)
    )
    grouped["stderr_G"] = grouped["std_G"] / np.sqrt(grouped["trials"].clip(lower=1))

    fits = []
    fits.extend(_fit_log_linear(grouped, x_col="n_qubits", group_col="depth"))
    fits.extend(_fit_log_linear(grouped, x_col="depth", group_col="n_qubits"))

    summary = {
        "experiment": "grad_variance",
        "definition": "Per trial t, G^(t) = (1/P) * sum_i g_i^2. Report E[G] and Var(G) across trials.",
        "config": {
            "qubits": qubits,
            "depths": depths,
            "repeats": repeats,
            "base_seed": base_seed,
            "circuit_family": circuit_family,
            "parameter_tying": parameter_tying,
            "entangler_prob": entangler_prob,
            "observable": observable,
            "grad_method": grad_method,
            "shots": shots,
        },
        "aggregates": grouped.to_dict(orient="records"),
        "fits": fits,
    }
    write_json(summary, output_dir / "summary.json")

    if config.get("plot", {}).get("enabled", True):
        plot_grad_variance(df, output_dir / "figures" / "grad_variance.png")
        _plot_log_fits(grouped, output_dir / "figures")

    return {
        "rows": len(rows),
        "cells": len(qubits) * len(depths),
        "repeats": repeats,
        "parallelism": parallelism,
        "output_dir": str(output_dir),
    }


def _run_single_trial(task: dict) -> dict:
    rng = np.random.default_rng(task["seed_params"])
    params = rng.uniform(-np.pi, np.pi, size=task["n_params"])

    t0 = time.perf_counter()
    grad_vec, backend = _gradient_vector(
        n_qubits=task["n_qubits"],
        depth=task["depth"],
        params=params,
        circuit_family=task["circuit_family"],
        seed_circuit=task["seed_circuit"],
        shots=task["shots"],
        seed_shots=task["seed_shots"],
        parameter_tying=task["parameter_tying"],
        entangler_prob=task["entangler_prob"],
    )
    runtime_s = time.perf_counter() - t0

    g_scalar = float(np.mean(grad_vec**2))
    mean_abs_grad = float(np.mean(np.abs(grad_vec)))

    return {
        "exp_name": "grad_variance",
        "n_qubits": task["n_qubits"],
        "depth": task["depth"],
        "seed": task["trial_seed"],
        "seed_circuit": task["seed_circuit"],
        "seed_params": task["seed_params"],
        "seed_shots": task["seed_shots"] if task["shots"] is not None else None,
        "circuit_family": task["circuit_family"],
        "n_params": task["n_params"],
        "parameter_tying": task["parameter_tying"],
        "observable": task["observable"],
        "grad_estimator": task["grad_method"],
        "shots": task["shots"],
        "G_scalar": g_scalar,
        "mean_abs_grad": mean_abs_grad,
        "runtime_s": float(runtime_s),
        "backend": backend,
    }
