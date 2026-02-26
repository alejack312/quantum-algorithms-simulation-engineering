# Interview Pitch

## 30-Second Pitch
I built a reproducible quantum benchmarking suite with three interview-ready artifacts: gradient scaling (tying vs untied), backend benchmarking (Qiskit vs custom adapter), and shot-noise scaling (error vs runtime tradeoffs). Everything is config-driven, trial-level logged, and produces publication-style plots. Each artifact has a frozen experiment contract, deterministic seeds, and reproducible outputs in `results/` plus reviewer-facing docs in `artifacts/`.

## 2-Minute Deep Dive (Outline)
1. Artifact 1: Gradient scaling (tying vs untied)
- Measured `log(mean_G)` vs `n_qubits` under a matched grid and fixed contract (`iqp`, `Z0`, `param_shift`, `statevector_exact`).
- The key variable was parameter tying (`global_shared` vs `none`).
- The fit table shows a stable sign flip in slope: tied positive, untied negative, with high `r2` in the tested finite regime.

2. Artifact 2: Backend benchmark (Qiskit vs custom adapter)
- Benchmarked runtime and expectation accuracy across circuit families, observables, and exact/shot-based modes.
- Implemented a real adapter interface (`custom_adapter_pass_through`) so the benchmark API is stable even before a true custom simulator drop-in.
- Reported fastest-backend slices and reference-aligned error behavior from trial-level aggregates.

3. Artifact 3: Noise/shot scaling (error vs runtime)
- Used statevector exact expectation as reference and qasm-shot estimate across two regimes and two circuit families.
- Logged seeded trials per shot level and summarized `mean_abs_error`, `stderr_abs_error`, and runtime.
- Added threshold guidance table (shots needed to reach `mean_abs_error < 1e-2`, with runtime at crossing) to make tradeoffs actionable.

## 5 Technical Ownership Bullets
- Randomness axes separation: explicit `seed_circuit`, `seed_params`, and `seed_shots` to isolate structure, parameterization, and sampling effects.
- Metric definitions: used explicit trial-level definitions, including `G^(t) = (1/P) * sum_i (g_i^(t))^2`, and aggregated with mean/std/stderr.
- Guardrails: fit-quality checks (`r2`) plus sanity-oriented schema and output checks in tests.
- Reference vs estimator setup: exact statevector reference paired with shot-based estimators on the same trial identity.
- CI strategy: micro configs and schema tests in CI; full sweeps intentionally manual for runtime control.
