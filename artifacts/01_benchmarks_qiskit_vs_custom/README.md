# Artifact 01: Qiskit vs Custom Benchmark

## What It Measures

This artifact measures wall-clock simulation runtime for randomly generated circuits as qubit count and depth scale. It compares Qiskit statevector simulation against a custom simulator adapter when available.

## How to Run

```bash
python -m quantum_swe_artifacts run --config configs/example_bench_qiskit_vs_custom.yaml
```

## Expected Outputs

- `results.csv` with one row per `(n_qubits, depth, repetition)`
- `summary.json` with grouped mean/std runtime
- `env.json` and copied `config.yaml`
- `figures/runtime_scaling.png`
