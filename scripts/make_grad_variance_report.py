from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg", force=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fit_table_markdown(fits: list[dict], fit_type: str, key: str) -> str:
    rows = [f for f in fits if f.get("fit_type") == fit_type]
    rows = sorted(rows, key=lambda x: x[key])
    lines = [f"| {key} | slope | intercept | r2 |", "|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(
            f"| {r[key]} | {r['slope']:.6f} | {r['intercept']:.6f} | {r['r2']:.4f} |"
        )
    return "\n".join(lines)


def make_plots(agg_df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    floor = 1e-300

    plt.figure(figsize=(8, 5))
    for depth, sub in agg_df.groupby("depth"):
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        plt.plot(sub["n_qubits"], y, marker="o", label=f"depth={depth}")
    plt.xlabel("n_qubits")
    plt.ylabel("log(mean_G)")
    plt.title("log(mean_G) vs n_qubits")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "log_meanG_vs_n_300dpi.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    for n, sub in agg_df.groupby("n_qubits"):
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        plt.plot(sub["depth"], y, marker="o", label=f"n={n}")
    plt.xlabel("depth")
    plt.ylabel("log(mean_G)")
    plt.title("log(mean_G) vs depth")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "log_meanG_vs_depth_300dpi.png", dpi=300)
    plt.close()


def sanity_checks(agg_df: pd.DataFrame, full_results_df: pd.DataFrame) -> dict:
    checks: dict[str, str] = {}

    checks["mean_abs_grad_nonzero_small_regime"] = (
        "pass" if (agg_df.query("n_qubits == 4 and depth == 2")["mean_abs_grad"].iloc[0] > 0) else "fail"
    )
    checks["mean_G_nonnegative"] = "pass" if (agg_df["mean_G"] >= 0).all() else "fail"
    checks["var_G_nonnegative"] = "pass" if (agg_df["var_G"] >= 0).all() else "fail"

    trials = full_results_df.groupby(["n_qubits", "depth"]).size().unique().tolist()
    checks["constant_trial_count_per_cell"] = "pass" if len(trials) == 1 else "warn"
    checks["trials_per_cell"] = str(trials[0] if trials else "unknown")

    return checks


def load_k40_compare(base_summary: dict, root: Path) -> list[dict]:
    selected = [(4, 2, "results/grad_variance_k40_n4d2/summary.json"), (8, 6, "results/grad_variance_k40_n8d6/summary.json"), (12, 10, "results/grad_variance_k40_n12d10/summary.json")]
    base_df = pd.DataFrame(base_summary["aggregates"])
    comparisons: list[dict] = []
    for n, d, rel in selected:
        p = root / rel
        if not p.exists():
            continue
        k40 = load_json(p)
        k40_df = pd.DataFrame(k40["aggregates"])
        base_row = base_df.query("n_qubits == @n and depth == @d").iloc[0]
        k40_row = k40_df.query("n_qubits == @n and depth == @d").iloc[0]
        comparisons.append(
            {
                "n_qubits": n,
                "depth": d,
                "mean_G_k20": float(base_row["mean_G"]),
                "stderr_k20": float(base_row["stderr_G"]),
                "mean_G_k40": float(k40_row["mean_G"]),
                "stderr_k40": float(k40_row["stderr_G"]),
                "abs_diff": abs(float(base_row["mean_G"]) - float(k40_row["mean_G"])),
            }
        )
    return comparisons


def k40_table_md(rows: list[dict]) -> str:
    if not rows:
        return "No K=40 comparison files found."
    lines = [
        "| n_qubits | depth | mean_G (K=20) | stderr (K=20) | mean_G (K=40) | stderr (K=40) | abs diff |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['n_qubits']} | {r['depth']} | {r['mean_G_k20']:.3e} | {r['stderr_k20']:.3e} | {r['mean_G_k40']:.3e} | {r['stderr_k40']:.3e} | {r['abs_diff']:.3e} |"
        )
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    summary_path = root / "results/grad_variance_full_sweep_001/summary.json"
    results_path = root / "results/grad_variance_full_sweep_001/results.csv"
    out_dir = root / "artifacts/03_vqa_gradients_iqp/figures"
    report_path = root / "artifacts/03_vqa_gradients_iqp/AUTO_REPORT.md"

    summary = load_json(summary_path)
    agg_df = pd.DataFrame(summary["aggregates"])
    full_results_df = pd.read_csv(results_path)

    make_plots(agg_df, out_dir)

    checks = sanity_checks(agg_df, full_results_df)
    fit_n_md = fit_table_markdown(summary["fits"], "log(mean_G) vs n_qubits", "depth")
    fit_d_md = fit_table_markdown(summary["fits"], "log(mean_G) vs depth", "n_qubits")
    k40_rows = load_k40_compare(summary, root)
    k40_md = k40_table_md(k40_rows)

    cfg = summary["config"]
    contract = f"""
- Circuit family: `{cfg['circuit_family']}`
- Observable: `{cfg['observable']}`
- Gradient estimator: `{cfg['grad_method']}`
- Backend mode: `statevector_exact` (`shots: {cfg['shots']}`)
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Sweep grid: `n_qubits={cfg['qubits']}`, `depth={cfg['depths']}`, `K={cfg['repeats']}`
- Parameter tying: `{cfg['parameter_tying']}`
""".strip()

    report = f"""# Auto Report: grad_variance_full_sweep_001

## Frozen Experimental Contract
{contract}

## Fit Table: log(mean_G) vs n_qubits (per depth)
{fit_n_md}

## Fit Table: log(mean_G) vs depth (per n_qubits)
{fit_d_md}

## Sanity Checks
- mean_abs_grad nonzero in small regime: `{checks['mean_abs_grad_nonzero_small_regime']}`
- mean_G nonnegative: `{checks['mean_G_nonnegative']}`
- var_G nonnegative: `{checks['var_G_nonnegative']}`
- constant trials per cell: `{checks['constant_trial_count_per_cell']}` (trials/cell=`{checks['trials_per_cell']}`)
- shot noise floor check: `not applicable (shots=null)`

## K=20 vs K=40 Robustness (Representative Cells)
{k40_md}

## Generated Figures
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`
"""

    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
