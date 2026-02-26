# Config Schema

All experiment configs are YAML files with this structure:

```yaml
experiment: bench_qiskit_vs_custom   # one of: bench_qiskit_vs_custom, noise_shot_scaling, grad_variance, transpile_study
output_dir: results/20260101_120000_bench_qiskit_vs_custom
seed: 42
repetitions: 5
sweep:
  qubits: [2, 4, 6]
  depth: [10, 20]
backend:
  type: qiskit_aer
  shots: 1024
  optimization_level: 1
plot:
  enabled: true
  formats: [png]
```

Notes:
- `output_dir` is optional. If omitted, the CLI auto-generates `results/<timestamp>_<experiment>`.
- `repetitions` should be >= 5 for stable measurements, but smoke runs can use 2.
- `sweep` keys depend on experiment.
- `plot.formats` currently supports PNG output.

### grad_variance extended fields

```yaml
circuit:
  family: iqp | hwe
  parameter_tying: per_qubit | layer_shared | global_shared
  entangler_prob: 0.2
estimation:
  observable: Z0
  grad_method: param_shift
  shots: null
repeats:
  seeds: 30
  base_seed: 0
runtime:
  parallelism: 1
```

Trial-level `results.csv` includes `seed_circuit`, `seed_params`, `seed_shots`, `G_scalar`, `mean_abs_grad`, and `runtime_s`.

### bench_qiskit_vs_custom extended fields

```yaml
sweep:
  circuit_families: [iqp, random]
  observable: [Z0, sumZ]
  n_qubits: [4, 6, 8, 10, 12]
  depth: [2, 4, 6, 8]
  K: 5
modes:
  - name: statevector_exact
    shots: null
  - name: qasm_shots
    shots: 1000
```

Trial-level `results.csv` required columns for this experiment:
- `n_qubits`, `depth`, `circuit_family`, `observable`, `backend_name`, `mode`, `shots`, `seed`
- `runtime_s`, `expectation_value`, `abs_error_vs_reference`

### noise_shot_scaling extended fields

```yaml
observable: Z0
sweep:
  circuit_families: [iqp, random]
  regimes:
    - n_qubits: 8
      depth: 6
    - n_qubits: 12
      depth: 8
  shots: [10, 25, 50, 100, 200, 500, 1000, 2000, 5000]
  K: 30
```

Trial-level `results.csv` required columns for this experiment:
- `circuit_family`, `observable`, `n_qubits`, `depth`, `shots`, `seed`, `seed_circuit`, `seed_params`, `seed_shots`
- `backend_name`, `mode`, `expectation_est`, `expectation_ref`, `abs_error`, `runtime_s`
