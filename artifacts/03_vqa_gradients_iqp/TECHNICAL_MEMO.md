# Technical Memo: Gradient Variance Scaling Study

## 1) Objective

This memo documents a controlled gradient-variance sweep for the `grad_variance` experiment and evaluates whether gradient variance decays approximately exponentially with qubit count and/or depth under a fixed circuit/estimator setup.

Primary question:

- Does `E[G]` decrease with increasing `n_qubits` and/or `depth` in this regime?

Scalar definition used in all claims:

- Per trial `t`, gradient vector `g^(t) in R^P`
- `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Report `E[G]` and `Var(G)` across trial seeds

## 2) Setup

Frozen baseline contract (no feature changes during analysis):

- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend mode: `statevector_exact`
- Shots: `null`
- Randomness axes:
  - `seed_circuit`
  - `seed_params`
  - `seed_shots` (logged but not used when `shots=null`)
- Parameter tying: `global_shared`
- Entangler probability: `0.2`
- Sweep grid:
  - `n_qubits in [4,6,8,10,12]`
  - `depth in [2,4,6,8,10]`
  - `K=20` seeds per cell
- Total trials: `5 * 5 * 20 = 500`

Outputs used:

- `results/grad_variance_full_sweep_001/results.csv`
- `results/grad_variance_full_sweep_001/summary.json`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`

## 3) Assumptions

- Statevector simulation is an ideal unitary reference (no hardware noise).
- Parameter-shift implementation and observable evaluation are deterministic under fixed seeds.
- Seed-wise variance over `(seed_circuit, seed_params)` approximates ensemble behavior for this circuit family and parameterization.
- `global_shared` tying is treated as a constrained parameterization regime; conclusions do not automatically transfer to untied parameterizations.

## 4) Results

### 4.1 Key figures

- `log(mean_G)` vs `n_qubits` with one curve per depth:
  - `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `log(mean_G)` vs `depth` with one curve per `n_qubits`:
  - `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`

### 4.2 Fit table: `log(mean_G)` vs `n_qubits` (per depth)

| Depth | slope (vs n) | r2 | Notes |
|---:|---:|---:|---|
| 2 | 0.2592 | 0.9397 | high log-linear quality, positive slope |
| 4 | 0.2592 | 0.9776 | high log-linear quality, positive slope |
| 6 | 0.2806 | 0.9762 | high log-linear quality, positive slope |
| 8 | 0.3344 | 0.9834 | high log-linear quality, positive slope |
| 10 | 0.3126 | 0.9619 | high log-linear quality, positive slope |

Interpretation of sign:

- Positive slope in `log(mean_G)` vs `n_qubits` means `mean_G` increases with `n_qubits` over this tested range.
- Therefore, this dataset does not support exponential decay in `mean_G` under the frozen contract.

### 4.3 Fit table: `log(mean_G)` vs `depth` (per n_qubits)

- r2 ranges are mixed (`~0.50` to `~0.78`), indicating weaker log-linear behavior vs depth than vs qubits in this setup.

## 5) Interpretation

Defensible claims:

- Under `iqp + global_shared + parameter-shift + statevector_exact + Z0`, `mean_G` is nonzero and tends to increase with tested `n_qubits` and depth ranges.
- The qubit-axis fits are strongly log-linear in this finite regime (high `r2`) but with positive slope, so they do not indicate barren-plateau-style decay for `mean_G` here.

Non-claims (explicitly avoided):

- No claim of asymptotic behavior beyond tested ranges.
- No claim that untied parameterizations behave similarly.

## 6) Deviations and Confounds

### Confound A: Parameter tying (`global_shared`)

- This materially changes parameter dimension and gradient statistics.
- Results should be interpreted as trainability behavior under shared-parameter constraints, not as a generic barren-plateau statement.

### Confound B: K=20 instead of K=30

- Addressed by targeted robustness reruns with `K=40` on representative cells:
  - `(4,2)`, `(8,6)`, `(12,10)`
- Mean values remained close and within reported uncertainty scales.
- Detailed comparison is in `artifacts/03_vqa_gradients_iqp/AUTO_REPORT.md`.

### Confound C: Shot noise

- Not applicable in this baseline (`shots=null`).
- No shot-noise floor is expected in this exact statevector mode.

## 7) Limitations and Next Steps

- Run a smaller untied comparison sweep (`parameter_tying=per_qubit`) on reduced grid to isolate tying effects.
- Test additional observables (`sumZ` or problem-aligned Hamiltonian) for sensitivity analysis.
- Extend depth and qubit ranges if runtime budget allows.
- Add finite-shot variants to quantify transition from estimator behavior to shot-noise floor.

## 8) Interview Ownership Talking Points

- `G^(t)` avoids ambiguity between parameter-axis variance and trial-axis variance.
- Randomness was controlled on separate axes (`seed_circuit`, `seed_params`, `seed_shots`).
- Strong log-linear qubit-axis behavior exists in this regime, but slope sign indicates growth, not decay.
- `global_shared` tying is a deliberate constrained regime and a primary confound.
- Robustness was validated by raising `K` from 20 to 40 on representative cells.

## 9) Minimal Comparative Study: Tying vs Untied

A matched-grid contrast was run to isolate parameter tying:

- Untied run: `results/grad_variance_untied_sweep_001/`
- Grid: `n=[4,6,8,10]`, `d=[2,4,6,8]`, `K=20`
- All other settings held fixed.

Outcome summary:

- Tied (`global_shared`) slopes vs `n`: positive at all depths.
- Untied (`none`) slopes vs `n`: negative at all depths.

Detailed numeric table is in:

- `artifacts/03_vqa_gradients_iqp/COMPARISON_TYING_VS_UNTIED.md`

This supports a controlled, conditional interpretation: parameter tying is a major factor in the observed scaling direction in this regime.