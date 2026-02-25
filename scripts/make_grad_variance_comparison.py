from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg", force=True)


def _load_summary(path: Path) -> pd.DataFrame:
    d = json.loads(path.read_text(encoding="utf-8"))
    return pd.DataFrame(d["aggregates"])


def _fit_by_depth(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for depth, sub in df.groupby("depth"):
        x = sub["n_qubits"].to_numpy(dtype=float)
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), 1e-300))
        m, b = np.polyfit(x, y, 1)
        pred = m * x + b
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        rows.append({"depth": int(depth), "slope": float(m), "r2": float(r2)})
    return pd.DataFrame(rows).sort_values("depth")


def _overlay_plot(tied: pd.DataFrame, untied: pd.DataFrame, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))

    for depth in sorted(set(tied["depth"]).intersection(set(untied["depth"]))):
        tsub = tied[tied["depth"] == depth].sort_values("n_qubits")
        usub = untied[untied["depth"] == depth].sort_values("n_qubits")

        tx = tsub["n_qubits"].to_numpy(dtype=float)
        ty = np.log(np.maximum(tsub["mean_G"].to_numpy(dtype=float), 1e-300))
        ux = usub["n_qubits"].to_numpy(dtype=float)
        uy = np.log(np.maximum(usub["mean_G"].to_numpy(dtype=float), 1e-300))

        plt.plot(tx, ty, marker="o", linestyle="-", label=f"tied d={depth}")
        plt.plot(ux, uy, marker="x", linestyle="--", label=f"untied d={depth}")

    plt.xlabel("n_qubits")
    plt.ylabel("log(mean_G)")
    plt.title("Tied vs Untied: log(mean_G) vs n_qubits")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def _parameter_count_check(root: Path) -> dict:
    tied_rows = pd.read_csv(root / "results/grad_variance_full_sweep_001/results.csv")
    untied_rows = pd.read_csv(root / "results/grad_variance_untied_sweep_001/results.csv")

    tied_rows = tied_rows[tied_rows["n_qubits"].isin([4, 6, 8, 10]) & tied_rows["depth"].isin([2, 4, 6, 8])]

    tied_p = tied_rows.groupby(["n_qubits", "depth"], as_index=False)["n_params"].mean()
    untied_p = untied_rows.groupby(["n_qubits", "depth"], as_index=False)["n_params"].mean()

    merged = tied_p.merge(untied_p, on=["n_qubits", "depth"], suffixes=("_tied", "_untied"))
    merged["param_ratio_untied_over_tied"] = merged["n_params_untied"] / merged["n_params_tied"]

    return {
        "matched_cells": int(merged.shape[0]),
        "mean_params_tied": float(merged["n_params_tied"].mean()),
        "mean_params_untied": float(merged["n_params_untied"].mean()),
        "mean_param_ratio_untied_over_tied": float(merged["param_ratio_untied_over_tied"].mean()),
    }


def _table_md(tied_fit: pd.DataFrame, untied_fit: pd.DataFrame) -> str:
    merged = tied_fit.merge(untied_fit, on="depth", suffixes=("_tied", "_untied")).sort_values("depth")
    lines = [
        "| depth | slope_tied | r2_tied | slope_untied | r2_untied |",
        "|---:|---:|---:|---:|---:|",
    ]
    for _, r in merged.iterrows():
        lines.append(
            f"| {int(r['depth'])} | {r['slope_tied']:.6f} | {r['r2_tied']:.4f} | {r['slope_untied']:.6f} | {r['r2_untied']:.4f} |"
        )
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    tied = _load_summary(root / "results/grad_variance_full_sweep_001/summary.json")
    tied = tied[tied["n_qubits"].isin([4, 6, 8, 10]) & tied["depth"].isin([2, 4, 6, 8])]
    untied = _load_summary(root / "results/grad_variance_untied_sweep_001/summary.json")

    tied_fit = _fit_by_depth(tied)
    untied_fit = _fit_by_depth(untied)

    fig = root / "artifacts/03_vqa_gradients_iqp/figures/tied_vs_untied_overlay_log_meanG_vs_n_300dpi.png"
    _overlay_plot(tied, untied, fig)

    check = _parameter_count_check(root)

    claim = (
        "In this finite regime (n=4..10, depth=2..8) under IQP/Z0/param-shift/statevector, "
        "parameter tying strongly changes gradient scaling with qubits: global_shared yields "
        "increasing log(mean_G) with n, while untied yields decreasing log(mean_G) with n."
    )

    one_pager = f"""# ONE PAGER: Gradient Variance (Tied vs Untied)

## Hypothesis
Parameter tying changes the observed gradient-variance scaling trend across qubits under an otherwise fixed experiment contract.

## Contract
- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend: `statevector_exact` (`shots=null`)
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Matched comparison grid: `n=[4,6,8,10]`, `depth=[2,4,6,8]`, `K=20`
- Conditions compared: `parameter_tying=global_shared` vs `parameter_tying=none`

## Key Table (log(mean_G) vs n_qubits)
{_table_md(tied_fit, untied_fit)}

## Figure
- `artifacts/03_vqa_gradients_iqp/figures/tied_vs_untied_overlay_log_meanG_vs_n_300dpi.png`

## Precise Claim
{claim}

## Conclusions
- Tied and untied runs show opposite slope sign on `log(mean_G)` vs `n_qubits` across all tested depths.
- Fit quality is high for most depth slices, so the directional contrast is stable in this tested window.
- Under this contract, tying is a dominant explanatory variable for scaling direction.

## Caveats / Limitations
- Finite regime only; no asymptotic guarantee.
- `global_shared` is a constrained parameterization and changes training geometry beyond parameter count.
- Results are for one circuit family (`iqp`) and one local observable (`Z0`).

## Robustness: Parameter-Count Confound
- `G_scalar` is normalized by `P` (`1/P * sum g_i^2`), reducing direct parameter-count scaling bias.
- Matched-grid average `n_params`: tied={check['mean_params_tied']:.2f}, untied={check['mean_params_untied']:.2f}.
- Mean parameter ratio (untied/tied) across matched cells: {check['mean_param_ratio_untied_over_tied']:.2f}.
- Interpretation: normalization reduces but does not eliminate parameterization confounds.

## Next Steps
- Run a tied-but-not-global scheme (`layer_shared`) for an intermediate comparison.
- Repeat comparison with `sumZ` observable.
- Add shot-based repeat (`shots=256/1024`) to inspect noise-floor effects.
"""

    out = root / "artifacts/03_vqa_gradients_iqp/ONE_PAGER.md"
    out.write_text(one_pager, encoding="utf-8")
    print(f"Wrote {fig}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
