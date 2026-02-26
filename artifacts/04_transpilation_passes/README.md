# Artifact 04: Transpilation Passes Study

## What It Measures

This artifact records circuit depth changes across Qiskit transpilation optimization levels.

## How to Run

```bash
python -m quantum_swe_artifacts run --config configs/example_transpile.yaml
```

## Expected Outputs

- `results.csv` with depth and op-count metadata per optimization level
- `summary.json` with grouped transpiled depth statistics
- `env.json` and copied `config.yaml`
- `figures/transpile_depth.png`
