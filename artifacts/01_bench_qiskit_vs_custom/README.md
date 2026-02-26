# Artifact 01: bench_qiskit_vs_custom

## Objective
Benchmark runtime and expectation accuracy for two backend paths on the same circuit trials:
- `qiskit_backend`
- `custom_adapter_pass_through` (adapter baseline)

## Experimental Contract
- Circuit families: `iqp`, `random`
- Observables: `Z0`, `sumZ`
- Modes:
  - `statevector_exact` (`shots: null`)
  - `qasm_shots` (`shots: 1000` in full run)
- Grid: `n_qubits=[4,6,8,10,12]`, `depth=[2,4,6,8]`
- Repeats: `K=5` seeds per cell
- Reference definition: exact statevector expectation on the same circuit seed/trial

## How To Run

```bash
python -m quantum_swe_artifacts.cli run --config configs/bench_qiskit_vs_custom_micro.yaml
python -m quantum_swe_artifacts.cli run --config configs/bench_qiskit_vs_custom_full_001.yaml
```

## Outputs
- Trial rows: `results/<run_dir>/results.csv`
- Cell aggregates: `results/<run_dir>/summary.json`
- Benchmark figures (300 DPI):
  - `artifacts/01_bench_qiskit_vs_custom/figures/runtime_vs_n_300dpi.png`
  - `artifacts/01_bench_qiskit_vs_custom/figures/runtime_vs_depth_300dpi.png`
  - `artifacts/01_bench_qiskit_vs_custom/figures/abs_error_vs_n_300dpi.png`

## Key Findings
Source run: `results/bench_qiskit_vs_custom_full_001/summary.json` (full grid, non-quick).

- Runtime: `qiskit_backend` is fastest in 156/160 regime cells; `custom_adapter_pass_through` wins 4 cells in `qasm_shots`.
- Accuracy vs reference: identical aggregate error for both backends (`mean abs_error = 0.035183` in `qasm_shots`, `0.0` in `statevector_exact`).
- No backend-specific accuracy gap is observed in this baseline because the custom adapter is pass-through.

Tiny fastest-backend table (average runtime over each `mode x circuit_family` slice):

| mode | circuit_family | fastest_backend | mean_runtime_s |
|---|---|---|---:|
| qasm_shots | iqp | qiskit_backend | 0.2667 |
| qasm_shots | random | qiskit_backend | 0.3128 |
| statevector_exact | iqp | qiskit_backend | 0.0112 |
| statevector_exact | random | qiskit_backend | 0.0091 |

## Repro + CI Scope
- Reproduce full benchmark: `python -m quantum_swe_artifacts.cli run --config configs/bench_qiskit_vs_custom_full_001.yaml`
- Reproduce micro benchmark (CI-safe): `python -m quantum_swe_artifacts.cli run --config configs/bench_qiskit_vs_custom_micro.yaml`
- CI intentionally runs micro/smoke only; full benchmark is excluded from CI due to runtime.
