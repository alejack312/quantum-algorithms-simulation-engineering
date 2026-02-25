# Technical Memo: Noise Shot Scaling (Artifact 02)

## 1) Purpose
This memo documents the engineering interpretation of shot-count scaling for estimator error and runtime under a fixed reference contract.

The experiment compares a shot-based estimator (`qasm_shots`) against a deterministic reference (`statevector_exact`) on matched circuits and seeds.

## 2) Contract (Frozen for this Artifact)
- Circuit families: `iqp`, `random`
- Observable: `Z0`
- Regimes: `(8,6)` and `(12,8)` in `(n_qubits, depth)`
- Shot sweep: `10` to `5000`
- Repeats: `K=30`
- Trial reference: exact expectation from statevector on the same circuit instance

## 3) Logged Quantities
Per trial row captures:
- `expectation_est` (shot-based)
- `expectation_ref` (exact)
- `abs_error = |expectation_est - expectation_ref|`
- `runtime_s`
- full seed lineage (`seed`, `seed_circuit`, `seed_params`, `seed_shots`)

Aggregates per `(circuit_family, n_qubits, depth, shots)` include:
- `mean_abs_error`, `std_abs_error`, `stderr_abs_error`
- `mean_runtime_s`, `stderr_runtime_s`

## 4) Theory Frame (Why this artifact matters)
For Monte Carlo measurement estimates of bounded observables, sampling error typically decays as `O(1/sqrt(shots))`.

Practical results can deviate from ideal scaling due to:
- circuit-dependent output distributions,
- regime-specific concentration effects,
- backend overhead that is not purely per-shot linear,
- finite trial budget (`K`) at each shot level.

This artifact is designed to show where empirical curves follow expected behavior and where they flatten into a practical shot-noise floor for the tested regimes.

## 5) How To Read the Figures
- `abs_error_vs_shots_300dpi.png`: central trend of estimator error vs shots.
- `stderr_abs_error_vs_shots_300dpi.png`: stability/confidence of the error estimate across seeds.
- `runtime_vs_shots_300dpi.png`: runtime cost growth vs shots.

Each curve is labeled by `circuit_family | n=<n_qubits>, d=<depth>`.

## 6) Fill After Full Run (No invented claims)
After running:

```bash
python -m quantum_swe_artifacts.cli run --config configs/noise_shot_scaling_full_001.yaml
```

Record here:
- Observed scaling slope region for each curve family/regime.
- Any apparent shot-noise floor in mean error.
- Runtime growth pattern and notable nonlinear regions.
- Tradeoff recommendation (e.g., shot range where marginal error reduction becomes small relative to runtime increase).

## 7) Reproducibility
- Configs:
  - `configs/noise_shot_scaling_micro.yaml`
  - `configs/noise_shot_scaling_full_001.yaml`
- Runner:
  - `python -m quantum_swe_artifacts.cli run --config <config>`
- Outputs:
  - `results/noise_shot_scaling_*`
  - `artifacts/02_noise_shot_scaling/figures/*`

## 8) CI Scope
CI should execute only the micro config path through tests. The full config is intentionally excluded from CI runtime.
