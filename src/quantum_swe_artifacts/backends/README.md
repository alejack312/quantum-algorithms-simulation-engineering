# Backends

## Custom Backend Adapter Contract

`custom_backend_adapter.py` exposes a stable adapter surface for benchmark experiments.

- Class: `CustomBackendAdapter`
- Default implementation name: `custom_adapter_pass_through`
- Entry point: `execute(circ, mode, observable="Z0", shots=None, seed=0)`

Supported modes:
- `statevector_exact`: ignores `shots`, computes expectation from the exact statevector.
- `qasm_shots`: requires `shots`, computes expectation from sampled counts.

Expected response keys:
- `backend_name`: stable adapter identity.
- `backend_impl`: concrete runtime backend used internally.
- `mode`: execution mode.
- `shots`: integer for shot-based mode, otherwise `null`.
- `runtime_s`: wall-clock runtime in seconds.
- `expectation_value`: computed observable expectation for this trial.

This implementation currently passes through Qiskit execution APIs while preserving an adapter abstraction so a true custom simulator can be swapped in without changing experiment code.
