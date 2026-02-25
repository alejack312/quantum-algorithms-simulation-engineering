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
