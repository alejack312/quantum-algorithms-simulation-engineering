# Auto Report: grad_variance_full_sweep_001

## Frozen Experimental Contract
- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend mode: `statevector_exact` (`shots: None`)
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Sweep grid: `n_qubits=[4, 6, 8, 10, 12]`, `depth=[2, 4, 6, 8, 10]`, `K=20`
- Parameter tying: `global_shared`

## Fit Table: log(mean_G) vs n_qubits (per depth)
| depth | slope | intercept | r2 |
|---:|---:|---:|---:|
| 2 | 0.259218 | -72.525476 | 0.9397 |
| 4 | 0.259179 | -71.449914 | 0.9776 |
| 6 | 0.280629 | -70.806329 | 0.9762 |
| 8 | 0.334382 | -71.202068 | 0.9834 |
| 10 | 0.312585 | -71.272802 | 0.9619 |

## Fit Table: log(mean_G) vs depth (per n_qubits)
| n_qubits | slope | intercept | r2 |
|---:|---:|---:|---:|
| 4 | 0.193538 | -71.602031 | 0.6157 |
| 6 | 0.146674 | -70.502113 | 0.4993 |
| 8 | 0.238587 | -70.422030 | 0.7754 |
| 10 | 0.231057 | -69.937184 | 0.6584 |
| 12 | 0.242315 | -69.538320 | 0.7381 |

## Sanity Checks
- mean_abs_grad nonzero in small regime: `pass`
- mean_G nonnegative: `pass`
- var_G nonnegative: `pass`
- constant trials per cell: `pass` (trials/cell=`20`)
- shot noise floor check: `not applicable (shots=null)`

## K=20 vs K=40 Robustness (Representative Cells)
| n_qubits | depth | mean_G (K=20) | stderr (K=20) | mean_G (K=40) | stderr (K=40) | abs diff |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 2 | 6.907e-32 | 2.558e-32 | 6.989e-32 | 1.959e-32 | 8.218e-34 |
| 8 | 6 | 1.915e-30 | 7.831e-31 | 1.970e-30 | 5.840e-31 | 5.508e-32 |
| 12 | 10 | 4.331e-30 | 1.780e-30 | 4.122e-30 | 1.293e-30 | 2.086e-31 |

## Generated Figures
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_n_300dpi.png`
- `artifacts/03_vqa_gradients_iqp/figures/log_meanG_vs_depth_300dpi.png`
