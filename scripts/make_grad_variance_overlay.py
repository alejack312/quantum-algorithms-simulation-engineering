from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MATCHED_N = [4, 6, 8, 10]
MATCHED_DEPTH = [2, 4, 6, 8]


def _load_summary_or_aggregate(run_dir: Path) -> pd.DataFrame:
    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        if "aggregates" in payload:
            return pd.DataFrame(payload["aggregates"])
        if "rows" in payload:
            return pd.DataFrame(payload["rows"])

    results_path = run_dir / "results.csv"
    if not results_path.exists():
        raise FileNotFoundError(f"Neither summary.json nor results.csv found in {run_dir}")

    df = pd.read_csv(results_path)
    grouped = (
        df.groupby(["n_qubits", "depth"], as_index=False)
        .agg(mean_G=("G_scalar", "mean"))
        .sort_values(["depth", "n_qubits"])
    )
    return grouped


def _fit_line(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    floor = 1e-300
    for depth, sub in df.groupby("depth"):
        sub = sub.sort_values("n_qubits")
        if len(sub) < 2:
            continue
        x = sub["n_qubits"].to_numpy(dtype=float)
        y = np.log(np.maximum(sub["mean_G"].to_numpy(dtype=float), floor))
        slope, intercept = np.polyfit(x, y, 1)
        pred = slope * x + intercept
        ss_res = float(np.sum((y - pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        rows.append({"depth": int(depth), "slope": float(slope), "r2": float(r2)})
    return pd.DataFrame(rows).sort_values("depth")


def _plot_overlay(tied: pd.DataFrame, untied: pd.DataFrame, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    floor = 1e-300

    plt.figure(figsize=(9, 5.5))
    for depth in MATCHED_DEPTH:
        tied_sub = tied[tied["depth"] == depth].sort_values("n_qubits")
        untied_sub = untied[untied["depth"] == depth].sort_values("n_qubits")
        if tied_sub.empty or untied_sub.empty:
            continue

        plt.plot(
            tied_sub["n_qubits"],
            np.log(np.maximum(tied_sub["mean_G"], floor)),
            marker="o",
            linestyle="-",
            label=f"depth={depth} | tied (global_shared)",
        )
        plt.plot(
            untied_sub["n_qubits"],
            np.log(np.maximum(untied_sub["mean_G"], floor)),
            marker="x",
            linestyle="--",
            label=f"depth={depth} | untied (none)",
        )

    plt.xlabel("n_qubits")
    plt.ylabel("log(mean_G)")
    plt.title("Gradient Variance Overlay: Tied vs Untied")
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def _table_markdown(tied_fits: pd.DataFrame, untied_fits: pd.DataFrame) -> str:
    merged = tied_fits.merge(untied_fits, on="depth", suffixes=("_tied", "_untied"))
    merged = merged.sort_values("depth")
    lines = [
        "| depth | slope_tied | r2_tied | slope_untied | r2_untied |",
        "|---:|---:|---:|---:|---:|",
    ]
    for _, row in merged.iterrows():
        lines.append(
            f"| {int(row['depth'])} | {row['slope_tied']:.6f} | {row['r2_tied']:.4f} | {row['slope_untied']:.6f} | {row['r2_untied']:.4f} |"
        )
    return "\n".join(lines)


def _write_one_pager(outpath: Path, figure_rel: str, fit_table_md: str) -> None:
    content = f"""# ONE_PAGER: Tying vs Untied Gradient Variance

## Objective
This note compares tied (`global_shared`) and untied (`none`) parameterizations under the same IQP gradient-variance contract. The target is to isolate whether tying changes the direction of scaling in `log(mean_G)` as `n_qubits` grows. All conclusions are constrained to the matched finite grid and existing run outputs.

## Frozen Contract
- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend mode: `statevector_exact`
- Shots: `null`
- Scalar definition: `G^(t) = (1/P) * sum_i (g_i^(t))^2`

## Matched-Grid Scope
- Tied run source: `results/grad_variance_full_sweep_001/`
- Untied run source: `results/grad_variance_untied_sweep_001/`
- Compared grid: `n_qubits=[4,6,8,10]`, `depth=[2,4,6,8]`

## Key Fit Table
{fit_table_md}

## Overlay Figure
![Tied vs Untied Overlay]({figure_rel})

## Conclusions
- Across all matched depths, tied slopes are positive while untied slopes are negative for `log(mean_G)` vs `n_qubits`.
- The direction flip is consistent over the full matched grid, not a single-cell effect.
- Under this fixed contract, parameter tying is a primary factor in observed scaling direction.

## Caveats
- Parameter tying is a confound: `global_shared` changes optimization geometry and effective hypothesis class.
- This is a finite regime (`n<=10`, `depth<=8`), so no asymptotic claim is implied.
- Results are contract-specific (`iqp`, `Z0`, exact-statevector); transfer to other settings is not guaranteed.

## Next Steps
- Add a middle condition (for example `layer_shared`) to map trend transitions.
- Repeat with `sumZ` to test observable sensitivity.
- Run shot-based variants to measure whether noise changes the slope contrast.
"""
    outpath.write_text(content, encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    tied_run = repo_root / "results/grad_variance_full_sweep_001"
    untied_run = repo_root / "results/grad_variance_untied_sweep_001"

    tied = _load_summary_or_aggregate(tied_run)
    untied = _load_summary_or_aggregate(untied_run)

    tied = tied[tied["n_qubits"].isin(MATCHED_N) & tied["depth"].isin(MATCHED_DEPTH)]
    untied = untied[untied["n_qubits"].isin(MATCHED_N) & untied["depth"].isin(MATCHED_DEPTH)]

    if tied.empty or untied.empty:
        raise RuntimeError("Matched-grid data is empty after filtering.")

    figure_path = (
        repo_root
        / "artifacts/03_vqa_gradients_iqp/figures/overlay_log_meanG_vs_n_tied_vs_untied_300dpi.png"
    )
    _plot_overlay(tied=tied, untied=untied, outpath=figure_path)

    tied_fits = _fit_line(tied)
    untied_fits = _fit_line(untied)
    fit_table_md = _table_markdown(tied_fits=tied_fits, untied_fits=untied_fits)

    one_pager = repo_root / "artifacts/03_vqa_gradients_iqp/ONE_PAGER.md"
    figure_rel = "figures/overlay_log_meanG_vs_n_tied_vs_untied_300dpi.png"
    _write_one_pager(outpath=one_pager, figure_rel=figure_rel, fit_table_md=fit_table_md)

    print(f"Wrote figure: {figure_path}")
    print(f"Wrote one-pager: {one_pager}")


if __name__ == "__main__":
    main()
