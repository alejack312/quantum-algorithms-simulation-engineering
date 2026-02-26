from __future__ import annotations

import time

import numpy as np
from qiskit import transpile
from qiskit.quantum_info import Statevector


def _z_expectation_from_counts(counts: dict[str, int], shots: int) -> float:
    total = 0.0
    for bitstring, c in counts.items():
        z = 1.0 if bitstring[-1] == "0" else -1.0
        total += z * c
    return total / shots if shots else 0.0


def run_circuit(circ, shots: int, seed: int, noise_model=None) -> dict:
    backend_name = "statevector_fallback"
    counts = {}
    expect_z0 = None

    try:
        from qiskit_aer import Aer

        backend = Aer.get_backend("aer_simulator")
        backend_name = "qiskit_aer"
        measured = circ.copy()
        if measured.num_clbits == 0:
            measured.measure_all()
        t0 = time.perf_counter()
        compiled = transpile(measured, backend=backend, optimization_level=0, seed_transpiler=seed)
        run_kwargs = {"shots": shots}
        try:
            run_kwargs["seed_simulator"] = seed
        except Exception:
            pass
        if noise_model is not None:
            run_kwargs["noise_model"] = noise_model
        result = backend.run(compiled, **run_kwargs).result()
        wall_time = time.perf_counter() - t0
        counts = result.get_counts()
        expect_z0 = _z_expectation_from_counts(counts, shots)
        return {
            "backend": backend_name,
            "wall_time_s": wall_time,
            "counts": counts,
            "expect_z0": expect_z0,
        }
    except Exception:
        t0 = time.perf_counter()
        state = Statevector.from_instruction(circ)
        probs = np.abs(state.data) ** 2
        rng = np.random.default_rng(seed)
        samples = rng.choice(len(probs), size=shots, p=probs)
        n_qubits = circ.num_qubits
        for idx in samples:
            bitstring = format(int(idx), f"0{n_qubits}b")
            counts[bitstring] = counts.get(bitstring, 0) + 1
        wall_time = time.perf_counter() - t0
        expect_z0 = _z_expectation_from_counts(counts, shots)
        return {
            "backend": backend_name,
            "wall_time_s": wall_time,
            "counts": counts,
            "expect_z0": expect_z0,
        }


def run_statevector(circ, seed: int) -> dict:
    try:
        from qiskit_aer import Aer

        backend = Aer.get_backend("aer_simulator_statevector")
        t0 = time.perf_counter()
        compiled = transpile(circ, backend=backend, optimization_level=0, seed_transpiler=seed)
        result = backend.run(compiled, seed_simulator=seed).result()
        wall_time = time.perf_counter() - t0
        state = np.asarray(result.get_statevector())
        return {"backend": "qiskit_aer_statevector", "wall_time_s": wall_time, "statevector": state}
    except Exception:
        t0 = time.perf_counter()
        state = Statevector.from_instruction(circ)
        wall_time = time.perf_counter() - t0
        return {"backend": "statevector_fallback", "wall_time_s": wall_time, "statevector": state.data}
