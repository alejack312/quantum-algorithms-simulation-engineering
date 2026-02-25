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
Run executed:

```bash
python -m quantum_swe_artifacts.cli run --config configs/noise_shot_scaling_full_001.yaml
```

Observed from `results/noise_shot_scaling_full_001/summary.json`:
- `mean_abs_error` at 10 shots vs 5000 shots:
  - `iqp (8,6)`: `0.238289 -> 0.007865`
  - `iqp (12,8)`: `0.207621 -> 0.009322`
  - `random (8,6)`: `0.243756 -> 0.007735`
  - `random (12,8)`: `0.366276 -> 0.010880`
- Runtime at 10 shots vs 5000 shots:
  - `iqp (8,6)`: `0.255665s -> 0.276210s`
  - `iqp (12,8)`: `0.264974s -> 0.296403s`
  - `random (8,6)`: `0.252319s -> 0.269828s`
  - `random (12,8)`: `0.255957s -> 0.284540s`

Threshold summary (`mean_abs_error < 1e-2`):

| circuit_family | n_qubits | depth | shots to cross | mean_abs_error at crossing | mean_runtime_s at crossing |
|---|---:|---:|---:|---:|---:|
| iqp | 8 | 6 | 5000 | 0.007865 | 0.276210 |
| iqp | 12 | 8 | 5000 | 0.009322 | 0.296403 |
| random | 8 | 6 | 5000 | 0.007735 | 0.269828 |
| random | 12 | 8 | not reached | - | - |

Interpretation constrained to this run:
- Error decreases strongly with more shots across all tested curves.
- A strict `1e-2` target is near the tested upper bound; one curve remains slightly above it at 5000 shots.
- Within this implementation, runtime grows with shots but much less sharply than error shrinks over 10 to 5000 shots.

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
