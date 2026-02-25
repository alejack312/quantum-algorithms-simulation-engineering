from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from quantum_swe_artifacts.backends.qiskit_backend import run_circuit as qiskit_run_circuit
from quantum_swe_artifacts.backends.qiskit_backend import run_statevector as qiskit_run_statevector


def _z_value_from_bit(bit: str) -> float:
    return 1.0 if bit == "0" else -1.0


def _expectation_from_counts(counts: dict[str, int], shots: int, observable: str) -> float:
    if shots <= 0:
        return 0.0
    total = 0.0
    for bitstring, count in counts.items():
        if observable == "sumZ":
            z = sum(_z_value_from_bit(bit) for bit in bitstring)
        else:
            z = _z_value_from_bit(bitstring[-1])
        total += z * count
    return float(total) / float(shots)


def _expectation_from_statevector(statevector: np.ndarray, n_qubits: int, observable: str) -> float:
    probs = np.abs(statevector) ** 2
    total = 0.0
    for idx, prob in enumerate(probs):
        bitstring = format(int(idx), f"0{n_qubits}b")
        if observable == "sumZ":
            z = sum(_z_value_from_bit(bit) for bit in bitstring)
        else:
            z = _z_value_from_bit(bitstring[-1])
        total += z * float(prob)
    return float(total)


@dataclass(frozen=True)
class CustomBackendAdapter:
    """Stable custom backend interface with a pass-through implementation."""

    name: str = "custom_adapter_pass_through"

    def execute(
        self,
        circ,
        mode: str,
        observable: str = "Z0",
        shots: int | None = None,
        seed: int = 0,
    ) -> dict[str, Any]:
        if mode == "statevector_exact":
            return self.run_statevector(circ=circ, observable=observable, seed=seed)
        if mode == "qasm_shots":
            if shots is None:
                raise ValueError("shots must be provided for qasm_shots mode")
            return self.run_shots(circ=circ, observable=observable, shots=int(shots), seed=seed)
        raise ValueError(f"Unsupported mode '{mode}'. Expected statevector_exact or qasm_shots.")

    def run_statevector(self, circ, observable: str = "Z0", seed: int = 0) -> dict[str, Any]:
        t0 = time.perf_counter()
        result = qiskit_run_statevector(circ, seed=seed)
        runtime_s = time.perf_counter() - t0
        statevector = np.asarray(result["statevector"], dtype=complex)
        expectation = _expectation_from_statevector(
            statevector=statevector,
            n_qubits=int(circ.num_qubits),
            observable=observable,
        )
        return {
            "backend_name": self.name,
            "backend_impl": str(result.get("backend", "qiskit_statevector")),
            "mode": "statevector_exact",
            "shots": None,
            "runtime_s": float(runtime_s),
            "expectation_value": float(expectation),
        }

    def run_shots(self, circ, shots: int, observable: str = "Z0", seed: int = 0) -> dict[str, Any]:
        t0 = time.perf_counter()
        result = qiskit_run_circuit(circ, shots=shots, seed=seed, noise_model=None)
        runtime_s = time.perf_counter() - t0
        counts = dict(result.get("counts", {}))
        expectation = _expectation_from_counts(counts=counts, shots=int(shots), observable=observable)
        return {
            "backend_name": self.name,
            "backend_impl": str(result.get("backend", "qiskit_qasm")),
            "mode": "qasm_shots",
            "shots": int(shots),
            "runtime_s": float(runtime_s),
            "expectation_value": float(expectation),
        }


_DEFAULT_ADAPTER = CustomBackendAdapter()


def get_default_adapter() -> CustomBackendAdapter:
    return _DEFAULT_ADAPTER


def execute(circ, mode: str, observable: str = "Z0", shots: int | None = None, seed: int = 0) -> dict[str, Any]:
    return _DEFAULT_ADAPTER.execute(circ=circ, mode=mode, observable=observable, shots=shots, seed=seed)


def run_statevector(circ, observable: str = "Z0", seed: int = 0) -> dict[str, Any]:
    return _DEFAULT_ADAPTER.run_statevector(circ=circ, observable=observable, seed=seed)
