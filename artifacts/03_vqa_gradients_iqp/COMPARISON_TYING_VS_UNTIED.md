# Comparison Note: Tying vs Untied (grad_variance)

## Purpose

Isolate the effect of parameter tying on gradient-variance scaling.

## Matched Comparison Contract

- Circuit family: `iqp`
- Observable: `Z0`
- Gradient estimator: `param_shift`
- Backend mode: `statevector_exact`
- Shots: `null`
- Randomness axes: `seed_circuit`, `seed_params`, `seed_shots`
- Scalar: `G^(t) = (1/P) * sum_i (g_i^(t))^2`
- Matched grid:
  - `n_qubits = [4, 6, 8, 10]`
  - `depth = [2, 4, 6, 8]`
  - `K = 20`

Runs compared:
- Tied: `results/grad_variance_full_sweep_001/` (filtered to matched grid)
- Untied: `results/grad_variance_untied_sweep_001/`

## Fit Comparison (log(mean_G) vs n_qubits, fixed depth)

| depth | slope_tied | r2_tied | slope_untied | r2_untied |
|---:|---:|---:|---:|---:|
| 2 | 0.289342 | 0.9248 | -0.203099 | 0.9896 |
| 4 | 0.257941 | 0.9558 | -0.121355 | 0.8571 |
| 6 | 0.322061 | 0.9961 | -0.104491 | 0.9165 |
| 8 | 0.370939 | 0.9920 | -0.145062 | 0.9904 |

## Direct Readout

- Tied (`global_shared`): positive slopes at all depths (no decay over tested range).
- Untied (`none`): negative slopes at all depths (decay over tested range).

## Conservative Claim

Under this experimental contract and tested finite regime, parameter tying changes the observed gradient-variance scaling direction. The data supports a contrast: untied shows decay-like behavior with qubit growth, while tied does not.

## Notes

- This is a finite-range result, not an asymptotic theorem.
- Further checks can extend this with `depth > 8`, alternative observables, and shot-based regimes.
