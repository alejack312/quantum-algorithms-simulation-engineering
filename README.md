# quantum-swe-artifacts

This repository is a production-oriented benchmark suite for quantum software engineering artifacts. It focuses on reproducible experiments across simulator benchmarking, noise/shot scaling, gradient variance behavior, and transpilation effects. The codebase is intentionally lightweight, built around Python 3.11+ and Qiskit, with simple configs and deterministic defaults. The target is to support a growing set of 34 artifacts while keeping every run auditable and easy to reproduce.

Latest Result: [Gradient tying vs untied one-pager](artifacts/03_vqa_gradients_iqp/ONE_PAGER.md)

## Highlights (Interview-Ready)
- [Gradient scaling: tying vs untied](artifacts/03_vqa_gradients_iqp/ONE_PAGER.md)
- [Backend benchmark: runtime + error tradeoffs](artifacts/01_bench_qiskit_vs_custom/README.md) (figures: `artifacts/01_bench_qiskit_vs_custom/figures/`)

## Reproducibility + CI Scope
- Overlay report (uses existing tied/untied outputs):
  - `python scripts/make_grad_variance_overlay.py`
- Micro benchmark (quick path):
  - `python -m quantum_swe_artifacts.cli run --config configs/bench_qiskit_vs_custom_micro.yaml`
- Outputs land in `results/<run_name>/` and artifact figures land in `artifacts/01_bench_qiskit_vs_custom/figures/` and `artifacts/03_vqa_gradients_iqp/figures/`.
- CI intentionally does not run `bench_qiskit_vs_custom_full_001.yaml`; only micro/smoke benchmark paths are expected in CI.

## Methodology
I structured the architecture in pseudocode first. I explicitly separated 
circuit generation from metric evaluation. I validated variance computation
under randomness sources.

## Quickstart

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## CLI

```bash
python -m quantum_swe_artifacts --help
python -m quantum_swe_artifacts list
python -m quantum_swe_artifacts env
python -m quantum_swe_artifacts run --config configs/example_bench_qiskit_vs_custom.yaml
```

## Run Each Artifact

```bash
python -m quantum_swe_artifacts run --config configs/example_bench_qiskit_vs_custom.yaml
python -m quantum_swe_artifacts run --config configs/example_noise_shot_scaling.yaml
python -m quantum_swe_artifacts run --config configs/example_grad_var.yaml
python -m quantum_swe_artifacts run --config configs/example_transpile.yaml
```

## Frozen Contract: grad_variance_full_sweep_001

This contract is frozen for current interpretation and comparison.

- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend mode: `statevector_exact`
- Shots: `null`
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Sweep grid: `n_qubits=[4,6,8,10,12]`, `depth=[2,4,6,8,10]`, `K=20`
- Parameter tying: `global_shared`

## grad_variance Fit Table (log(mean_G) vs n_qubits)

| Depth | slope | r2 |
|---:|---:|---:|
| 2 | 0.259218 | 0.9397 |
| 4 | 0.259179 | 0.9776 |
| 6 | 0.280629 | 0.9762 |
| 8 | 0.334382 | 0.9834 |
| 10 | 0.312585 | 0.9619 |

Interpretation boundary:
- The tested regime is log-linear with respect to `n_qubits` for each depth (high `r2`), but slope signs are positive. Under this frozen contract, this does not support gradient-variance decay with increasing qubits.


## grad_variance Comparative Follow-up (Tying vs Untied)

Matched-grid contrast (`n=[4,6,8,10]`, `d=[2,4,6,8]`, `K=20`) shows:
- `global_shared` tying: positive slope of `log(mean_G)` vs `n`
- `none` (untied): negative slope of `log(mean_G)` vs `n`

Reference:
- `artifacts/03_vqa_gradients_iqp/COMPARISON_TYING_VS_UNTIED.md`
## Results and Plots

Each run writes into `results/<timestamp>_<experiment>/` (or `output_dir` if provided), including:
- `results.csv`
- `summary.json`
- `env.json`
- `config.yaml`
- `figures/*.png`

Additional report artifacts for grad variance:
- `artifacts/03_vqa_gradients_iqp/AUTO_REPORT.md`
- `artifacts/03_vqa_gradients_iqp/TECHNICAL_MEMO.md`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`

Regenerate plots by rerunning the same config; plotting happens automatically when `plot.enabled: true`.

## Smoke Run (<60s)

```bash
python -m quantum_swe_artifacts run --config configs/example_bench_qiskit_vs_custom.yaml --quick
# or
powershell -ExecutionPolicy Bypass -File scripts/smoke_run.ps1
```

## Results Table

| Artifact | Config | Key metric | Latest value |
|---|---|---|---|
| Qiskit vs custom benchmark | `example_bench_qiskit_vs_custom.yaml` | mean runtime (s) | run-specific |
| Noise + shot scaling | `example_noise_shot_scaling.yaml` | estimator variance @ shots | run-specific |
| Gradient variance scaling | `grad_variance_full_sweep_001.yaml` | slope(log(mean_G) vs n) | positive (0.259 to 0.334 by depth) |
| Transpile study | `example_transpile.yaml` | transpiled depth | run-specific |

## Dev Commands

```bash
make install
make lint
make test
make smoke
python scripts/make_grad_variance_report.py
```
