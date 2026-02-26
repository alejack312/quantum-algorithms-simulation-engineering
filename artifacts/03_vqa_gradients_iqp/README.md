# Artifact 03: VQA Gradients (IQP-Friendly Scaffold)

## What It Measures

This artifact computes parameter-shift gradients and studies gradient-variance scaling over qubit count and depth.

Per trial `t`, with gradient vector `g^(t) in R^P`, we define:

`G^(t) = (1/P) * sum_i (g_i^(t))^2`

We then report `E[G]` and `Var(G)` across seeds for each `(n_qubits, depth)` cell.

## Frozen Experimental Contract (Baseline)

- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend: `statevector_exact` (`shots: null`)
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Sweep grid: `n_qubits=[4,6,8,10,12]`, `depth=[2,4,6,8,10]`, `K=20`
- Parameter tying: `global_shared`

## How to Run

Micro sanity sweep (2x2x5 = 20 trials):

```bash
python -m quantum_swe_artifacts run --config configs/grad_variance_micro_sweep.yaml
```

Full sweep (5x5x20 = 500 trials):

```bash
python -m quantum_swe_artifacts run --config configs/grad_variance_full_sweep_001.yaml
```

Generate report artifacts (fit tables + 300-DPI figures):

```bash
python scripts/make_grad_variance_report.py
python scripts/make_grad_variance_overlay.py
```

## Expected Outputs

- `results.csv` with one row per trial and required columns:
  - `n_qubits`, `depth`, `seed`, `seed_circuit`, `seed_params`, `seed_shots`
  - `circuit_family`, `n_params`, `grad_estimator`, `shots`, `backend`
  - `G_scalar`, `mean_abs_grad`, `runtime_s`
- `summary.json` with per-cell aggregates and log-linear fit coefficients
- `env.json` and copied `config.yaml`
- `figures/grad_variance.png`
- `figures/log_meanG_vs_n.png`
- `figures/log_meanG_vs_depth.png`
- `artifacts/03_vqa_gradients_iqp/AUTO_REPORT.md`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/ONE_PAGER.md`
- `artifacts/03_vqa_gradients_iqp/figures/overlay_log_meanG_vs_n_tied_vs_untied_300dpi.png`

## Robustness Check for K (20 -> 40)

Representative cells rerun with `K=40`:

- `(n=4, d=2)`
- `(n=8, d=6)`
- `(n=12, d=10)`

Comparison table is generated in `artifacts/03_vqa_gradients_iqp/AUTO_REPORT.md`.

## Interview Package

- One-page summary: `artifacts/03_vqa_gradients_iqp/ONE_PAGER.md`
- Comparative note: `artifacts/03_vqa_gradients_iqp/COMPARISON_TYING_VS_UNTIED.md`
- Technical memo: `artifacts/03_vqa_gradients_iqp/TECHNICAL_MEMO.md`
- Overlay figure: `artifacts/03_vqa_gradients_iqp/figures/tied_vs_untied_overlay_log_meanG_vs_n_300dpi.png`

Latest tied-vs-untied packet:
- ONE_PAGER: `artifacts/03_vqa_gradients_iqp/ONE_PAGER.md`
- Overlay figure: `artifacts/03_vqa_gradients_iqp/figures/overlay_log_meanG_vs_n_tied_vs_untied_300dpi.png`
