# Quantum SWE Implementation Schedule (8 Weeks)

Timeline anchor from your plan:
- Start: February 23, 2026
- Target completion: April 20, 2026

## Assumptions
- Python 3.11+
- Qiskit-first stack (Aer if available, graceful fallback otherwise)
- YAML-driven experiment configs
- Reproducibility via fixed seeds and config/environment snapshots

## Week-by-Week File Programming Plan

Status legend:
- `[x]` done
- `[ ]` pending

### Week 1 (Feb 23 - Mar 1): Foundation, CLI, Config, Logging Skeleton
Program these files:
- [x] `pyproject.toml`
- [x] `requirements.txt`
- [x] `Makefile`
- [x] `.github/workflows/ci.yml`
- [x] `src/quantum_swe_artifacts/__init__.py`
- [x] `src/quantum_swe_artifacts/__main__.py`
- [x] `src/quantum_swe_artifacts/cli.py`
- [x] `src/quantum_swe_artifacts/registry.py`
- [x] `src/quantum_swe_artifacts/env.py`
- [x] `src/quantum_swe_artifacts/logging_utils.py`
- [x] `configs/schema.md`
- [x] `configs/example_bench_qiskit_vs_custom.yaml`
- [x] `scripts/smoke_run.ps1`

### Week 2 (Mar 2 - Mar 8): Benchmark Artifact End-to-End
Program these files:
- [x] `src/quantum_swe_artifacts/circuits/random_circuits.py`
- [x] `src/quantum_swe_artifacts/backends/qiskit_backend.py`
- [x] `src/quantum_swe_artifacts/backends/custom_backend_adapter.py`
- [x] `src/quantum_swe_artifacts/experiments/bench_qiskit_vs_custom.py`
- [x] `src/quantum_swe_artifacts/plotting.py` (runtime plot function)
- [x] `artifacts/01_benchmarks_qiskit_vs_custom/README.md`
- [x] `tests/test_cli_smoke.py`
- [x] `tests/test_circuit_generators.py`

### Week 3 (Mar 9 - Mar 15): Noise + Shot Scaling Core
Program these files:
- [x] `src/quantum_swe_artifacts/circuits/iqp_circuits.py`
- [x] `src/quantum_swe_artifacts/experiments/noise_shot_scaling.py`
- [x] `configs/example_noise_shot_scaling.yaml`
- [x] `src/quantum_swe_artifacts/plotting.py` (variance vs shots function)
- [x] `artifacts/02_noise_and_shot_scaling/README.md`

### Week 4 (Mar 16 - Mar 22): Noise Study Validation + Reporting
Program/refine these files:
- [x] `src/quantum_swe_artifacts/experiments/noise_shot_scaling.py` (fidelity/proxy + convergence details)
- [x] `src/quantum_swe_artifacts/logging_utils.py` (summary metrics)
- [x] `tests/test_logging_and_plots.py`
- [x] `README.md` (results table updates)
- [x] `artifacts/02_noise_and_shot_scaling/README.md`

### Week 5 (Mar 23 - Mar 29): Variational Scaffold + Gradients
Program these files:
- [x] `src/quantum_swe_artifacts/experiments/grad_variance.py`
- [x] `configs/example_grad_var.yaml`
- [x] `src/quantum_swe_artifacts/plotting.py` (gradient variance function)
- [x] `artifacts/03_vqa_gradients_iqp/README.md`

### Week 6 (Mar 30 - Apr 5): Gradient Scaling Completion
Program/refine these files:
- [x] `src/quantum_swe_artifacts/experiments/grad_variance.py` (sampling, init strategies, stats)
- [x] `src/quantum_swe_artifacts/logging_utils.py` (aggregation for grad study)
- [x] `tests/test_cli_smoke.py` (tiny grad config path optional)
- [x] `README.md` (add gradient results placeholders)

### Week 7 (Apr 6 - Apr 12): Transpilation Experiment Core
Program these files:
- [x] `src/quantum_swe_artifacts/transpile/passes.py`
- [x] `src/quantum_swe_artifacts/experiments/transpile_study.py`
- [x] `configs/example_transpile.yaml`
- [x] `src/quantum_swe_artifacts/plotting.py` (transpile depth function)
- [x] `artifacts/04_transpilation_passes/README.md`

### Week 8 (Apr 13 - Apr 20): Final Integration, CI Hardening, Documentation
Program/refine these files:
- [x] `.github/workflows/ci.yml`
- [x] `README.md`
- [x] `tests/test_cli_smoke.py`
- [x] `tests/test_logging_and_plots.py`
- [x] `scripts/smoke_run.ps1`
- [x] `configs/*.yaml` (final default sanity)

## Bookmarked Pseudocode (Week X, Step Y)

### Week 1 Pseudocode
- Week 1, Step 1: Initialize package metadata and dependency files.
  - Input: project requirements and Python version constraints.
  - Output: installable project scaffold.
  - Complexity: O(1) setup per file.
- Week 1, Step 2: Implement config loader and schema validation.
  - Input: YAML config path.
  - Output: normalized config object with defaults.
  - Complexity: O(|yaml| + g).
- Week 1, Step 3: Implement CLI commands (`list`, `env`, `run`) and registry lookup.
  - Input: CLI args.
  - Output: command dispatch and status code.
  - Complexity: O(E) for list, O(1) env, O(g) orchestration overhead for run.
- Week 1, Step 4: Implement logging skeleton and run directory bootstrap.
  - Input: config + env metadata.
  - Output: `env.json`, copied `config.yaml`, output directories.
  - Complexity: O(file_size).

### Week 2 Pseudocode
- Week 2, Step 1: Build deterministic random circuit generator.
  - Input: `n_qubits`, `depth`, `seed`.
  - Output: random circuit instance.
  - Complexity: O(n * d).
- Week 2, Step 2: Build backend runner and statevector timing path.
  - Input: circuit, shots/seed.
  - Output: runtime and optional measurements.
  - Complexity: dominated by simulation, approx O(2^n * poly(gates)).
- Week 2, Step 3: Implement benchmark experiment loop with warmup.
  - Input: sweep grid and repetitions.
  - Output: row records per (setting, repetition).
  - Complexity: O(g * r * trial_cost).
- Week 2, Step 4: Aggregate and plot runtime scaling.
  - Input: result rows.
  - Output: `results.csv`, `summary.json`, runtime PNG.
  - Complexity: O(N) for aggregation + O(P) for plotting.

### Week 3 Pseudocode
- Week 3, Step 1: Build IQP-style circuit generator.
  - Input: `n_qubits`, `density`, `seed`.
  - Output: IQP-like circuit.
  - Complexity: O(n^2) worst-case interactions.
- Week 3, Step 2: Implement shot/noise sweep experiment kernel.
  - Input: shots list, noise list, repetitions.
  - Output: estimator samples and timing rows.
  - Complexity: O(g * r * s) plus backend simulation cost.
- Week 3, Step 3: Plot variance vs shots.
  - Input: experiment rows.
  - Output: variance plot.
  - Complexity: O(N).

### Week 4 Pseudocode
- Week 4, Step 1: Add convergence/fidelity proxy metrics.
  - Input: sampled estimates and reference/noiseless estimate.
  - Output: extra columns/summary metrics.
  - Complexity: O(N).
- Week 4, Step 2: Harden tests for logging and plotting outputs.
  - Input: synthetic rows and temp output path.
  - Output: passing regression tests.
  - Complexity: O(test_data_size).

### Week 5 Pseudocode
- Week 5, Step 1: Define variational ansatz and loss function.
  - Input: `n_qubits`, params.
  - Output: scalar loss estimate.
  - Complexity: O(eval_cost), often exponential in n for statevector.
- Week 5, Step 2: Implement parameter-shift gradient routine.
  - Input: params and shift constant.
  - Output: gradient vector or scalar component.
  - Complexity: O(2 * p * eval_cost).
- Week 5, Step 3: Implement parameter initialization strategies.
  - Input: strategy name, parameter count, seed.
  - Output: initial parameter vector.
  - Complexity: O(p).

### Week 6 Pseudocode
- Week 6, Step 1: Sweep qubit counts and random initializations.
  - Input: qubit grid and sample count `k`.
  - Output: gradient samples by qubit count.
  - Complexity: O(|N_grid| * k * p * eval_cost).
- Week 6, Step 2: Measure and log gradient variance scaling.
  - Input: gradient samples.
  - Output: variance summary and plot.
  - Complexity: O(total_samples).

### Week 7 Pseudocode
- Week 7, Step 1: Implement transpile study across optimization levels.
  - Input: circuit and levels [0,1,2,3].
  - Output: before/after depth and gate counts.
  - Complexity: transpiler-dependent, generally superlinear in gate count.
- Week 7, Step 2: Plot depth vs optimization level.
  - Input: transpile result rows.
  - Output: transpilation depth plot.
  - Complexity: O(N).

### Week 8 Pseudocode
- Week 8, Step 1: Run CI-quality test/lint/smoke checks and fix drift.
  - Input: full repository.
  - Output: stable CI pass profile.
  - Complexity: O(total_tests + lint_scope).
- Week 8, Step 2: Finalize documentation and reproducibility checklist.
  - Input: latest outputs and run commands.
  - Output: complete README + artifact docs + result placeholders.
  - Complexity: O(total_docs).

## Final Weekly Acceptance Checklist
- All targeted files for that week are updated.
- At least one runnable config path remains green.
- Output artifacts are generated (`CSV`, `JSON`, `PNG`).
- README/docs for that week are updated.
- Reproducibility controls (seed/config/env snapshot) remain intact.

## Execution Protocol: Final Research Pass (Grad Variance Focus)

### 1) Freeze Feature Additions
- Goal: stop architecture churn and lock a stable baseline before long sweeps.
- How:
  - Declare a freeze date/time in `README.md` and this schedule.
  - Limit changes to: bug fixes, config-only sweep edits, and documentation updates.
  - Do not add new experiment types, new dependencies, or new CLI flags during freeze.
  - Keep one canonical run command for `grad_variance`.
- Files to touch:
  - `README.md`
  - `IMPLEMENTATION_SCHEDULE.md`
  - `configs/example_grad_var.yaml`

### 2) Pick `grad_variance` as the Priority Artifact
- Goal: run one deep study end-to-end with research-grade rigor.
- How:
  - Use `experiment: grad_variance` as the primary artifact.
  - Keep other experiments in maintenance mode only (smoke + no regressions).
  - Define one primary metric: `Var[g]` for gradient estimator.
  - Define one secondary metric: gradient norm distribution summary.
- Files to touch:
  - `configs/example_grad_var.yaml`
  - `artifacts/03_vqa_gradients_iqp/README.md`
  - `README.md` results table

### 3) Manually Design a Full Experimental Sweep
- Goal: cover statistically meaningful ranges for seed, qubits, and depth.
- Sweep design template:
  - Seeds: 20-50 distinct seeds (example: `0..49`)
  - Qubits: `[2, 4, 6, 8, 10]` (expand if runtime permits)
  - Depth: `[2, 4, 8, 12, 16]` or architecture-equivalent layer counts
  - Inits per setting: `k >= 20`
  - Repetitions: `r >= 5` for shot-based variants
- Manual process:
  - Create a sweep matrix table in the artifact README before running.
  - Estimate runtime per cell using `--quick`, then scale.
  - Prune cells that exceed budget while preserving monotonic n/depth coverage.
- Files to touch:
  - `configs/example_grad_var.yaml` (or add dedicated full-sweep YAML)
  - `artifacts/03_vqa_gradients_iqp/README.md`

### 4) Instrument Variance Across Seeds, Qubits, and Depth
- Goal: produce row-level data that supports robust aggregation and curve fitting.
- Required row fields in `results.csv`:
  - `seed`
  - `n_qubits`
  - `depth` (or layer count)
  - `sample_id`
  - `grad`
  - optional: `grad_norm`, `loss`
- Aggregation keys:
  - Primary: `(n_qubits, depth)`
  - Secondary: `(n_qubits)` and `(depth)`
- Pseudocode:
  - Week 8, Step 3: For each `seed` in `Seeds`, for each `n` in `Qubits`, for each `d` in `Depths`, sample `k` inits, compute gradients, write all rows.
  - Week 8, Step 4: Aggregate per `(n,d)` and compute mean/variance/std/stderr.
- Complexity:
  - O(|Seeds| * |Qubits| * |Depths| * k * p * eval_cost)
  - with statevector eval, `eval_cost` is typically exponential in `n`.

### 5) Fit Curve
- Goal: characterize scaling trend and compare to expected barren-plateau behavior.
- Candidate fits:
  - Exponential: `Var[g](n) = a * exp(-b n)`
  - Power law: `Var[g](n) = c * n^{-alpha}`
  - Linear-on-log transforms for diagnostics
- Procedure:
  - Fit on aggregated variance by fixed depth slices.
  - Report fit parameters and goodness metrics (R2 / residual trend).
  - Add residual plots or at minimum residual summary in memo.
- Pseudocode:
  - Week 8, Step 5: For each depth slice, fit exponential and power-law models; store parameters and fit scores in `summary.json`.
- Complexity:
  - O(M) to O(M * Iters) depending on fitter, where M is number of aggregated points.

### 6) Write 23-Page Technical Memo
- Goal: archive a complete, reviewable research record.
- Suggested structure:
  - Setup:
    - environment, hardware, software versions, simulator backend, runtime constraints
    - exact configs and freeze policy
  - Assumptions:
    - ansatz structure, parameter initialization distribution, estimator definitions
    - reproducibility controls and known limitations
  - Observations:
    - main plots, variance tables, fitted curves, practical breakpoints
    - stability across seeds and depth regimes
  - Deviations from literature:
    - where results align/diverge from expected barren-plateau trends
    - possible causes (finite-size effects, ansatz choice, depth regime, simulator effects)
  - Appendix:
    - raw command list, config files, output directory manifest
- Files to produce/update:
  - `artifacts/03_vqa_gradients_iqp/README.md` (short summary + link to memo)
  - `README.md` (top-level result snapshot)
  - new memo file in repo root or `artifacts/03_vqa_gradients_iqp/`


## Run Log (Current Session)
- Completed micro grad sweep with `2 x 2 x 5 = 20` trial-level rows.
- Completed full grad sweep with `5 x 5 x 20 = 500` trial-level rows (reduced from 30 repeats due runtime constraints, per plan fallback).
- Output directory: `results/grad_variance_full_sweep_001/`.
