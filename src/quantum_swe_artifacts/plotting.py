from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt


def _prepare_path(outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)


def plot_runtime_scaling(df: pd.DataFrame, outpath: Path) -> None:
    _prepare_path(outpath)
    plt.figure(figsize=(6, 4))
    for depth, sub in df.groupby("depth"):
        grouped = sub.groupby("n_qubits", as_index=False)["qiskit_time_s"].mean()
        plt.plot(grouped["n_qubits"], grouped["qiskit_time_s"], marker="o", label=f"depth={depth}")
    plt.xlabel("Qubits")
    plt.ylabel("Runtime (s)")
    plt.title("Qiskit Runtime Scaling")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_variance_vs_shots(df: pd.DataFrame, outpath: Path) -> None:
    _prepare_path(outpath)
    plt.figure(figsize=(6, 4))
    for noise, sub in df.groupby("noise_strength"):
        grouped = sub.groupby("shots", as_index=False)["estimate"].var().fillna(0.0)
        plt.plot(grouped["shots"], grouped["estimate"], marker="o", label=f"noise={noise}")
    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("Shots")
    plt.ylabel("Variance")
    plt.title("Estimator Variance vs Shots")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_grad_variance(df: pd.DataFrame, outpath: Path) -> None:
    _prepare_path(outpath)
    plt.figure(figsize=(6, 4))

    if "depth" in df.columns and "G_scalar" in df.columns:
        grouped = (
            df.groupby(["n_qubits", "depth"], as_index=False)["G_scalar"]
            .mean()
            .rename(columns={"G_scalar": "mean_G"})
        )
        for depth, sub in grouped.groupby("depth"):
            plt.plot(sub["n_qubits"], sub["mean_G"], marker="o", label=f"depth={depth}")
        plt.yscale("log")
        plt.ylabel("mean(G)")
        plt.legend()
    else:
        grouped = df.groupby("n_qubits", as_index=False)["grad"].var().fillna(0.0)
        plt.plot(grouped["n_qubits"], grouped["grad"], marker="o")
        plt.ylabel("Gradient Variance")

    plt.xlabel("Qubits")
    plt.title("Gradient Variance Scaling")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_transpile_depth(df: pd.DataFrame, outpath: Path) -> None:
    _prepare_path(outpath)
    plt.figure(figsize=(6, 4))
    grouped = df.groupby("optimization_level", as_index=False)["transpiled_depth"].mean()
    plt.plot(grouped["optimization_level"], grouped["transpiled_depth"], marker="o")
    plt.xlabel("Optimization Level")
    plt.ylabel("Transpiled Depth")
    plt.title("Transpilation Depth vs Optimization")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
