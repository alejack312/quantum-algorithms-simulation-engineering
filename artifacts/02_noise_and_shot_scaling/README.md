# Artifact 02: Noise and Shot Scaling

This legacy path is retained for compatibility.
Current interview-facing artifact docs and figures are maintained at:
- `artifacts/02_noise_shot_scaling/README.md`

## What It Measures

This artifact estimates how observable variance changes with shot count under increasing noise-strength proxies.

## How to Run

```bash
python -m quantum_swe_artifacts run --config configs/example_noise_shot_scaling.yaml
```

## Expected Outputs

- `results.csv` containing estimates across `(shots, noise_strength, repetition)`
- `summary.json` with aggregated variance/time summaries
- `env.json` and copied `config.yaml`
- `figures/variance_vs_shots.png`
