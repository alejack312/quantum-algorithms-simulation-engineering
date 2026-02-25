# Artifact 02: Noise Shot Scaling

## Objective
Quantify how shot count affects shot-based estimator quality and runtime, using a statevector-exact expectation as the reference for each identical circuit trial.

## Experimental Contract
- Circuit families: `iqp`, `random`
- Observable: `Z0`
- Regimes:
  - `(n_qubits=8, depth=6)`
  - `(n_qubits=12, depth=8)`
- Shot sweep: `[10, 25, 50, 100, 200, 500, 1000, 2000, 5000]`
- Repeats per cell: `K=30`
- Reference mode: `statevector_exact` (`shots=null`)
- Estimate mode: `qasm_shots`

## How To Run

```bash
python -m quantum_swe_artifacts.cli run --config configs/noise_shot_scaling_micro.yaml
python -m quantum_swe_artifacts.cli run --config configs/noise_shot_scaling_full_001.yaml
pytest -q
```

## Outputs
- Trial-level results:
  - `results/noise_shot_scaling_micro/results.csv`
  - `results/noise_shot_scaling_full_001/results.csv`
- Aggregates:
  - `results/noise_shot_scaling_micro/summary.json`
  - `results/noise_shot_scaling_full_001/summary.json`
- Interview figures (300 DPI):
  - `artifacts/02_noise_shot_scaling/figures/abs_error_vs_shots_300dpi.png`
  - `artifacts/02_noise_shot_scaling/figures/stderr_abs_error_vs_shots_300dpi.png`
  - `artifacts/02_noise_shot_scaling/figures/runtime_vs_shots_300dpi.png`

## Notes
- CI is expected to run only the micro config; full run is manual due to runtime.
- Full run findings should be recorded in `TECHNICAL_MEMO.md` after execution.

## Key Findings (from `results/noise_shot_scaling_full_001/summary.json`)
- Mean absolute error decreases substantially as shots increase in all tested curves.
- Runtime increases with shots over the tested range, but in this setup the increase is moderate relative to the error reduction.
- At threshold `mean_abs_error < 1e-2`, three of four family/regime curves reach target by 5000 shots.

Threshold table (`mean_abs_error < 1e-2`):

| circuit_family | n_qubits | depth | shots to cross threshold | mean_abs_error at crossing | mean_runtime_s at crossing |
|---|---:|---:|---:|---:|---:|
| iqp | 8 | 6 | 5000 | 0.007865 | 0.276210 |
| iqp | 12 | 8 | 5000 | 0.009322 | 0.296403 |
| random | 8 | 6 | 5000 | 0.007735 | 0.269828 |
| random | 12 | 8 | not reached | - | - |
