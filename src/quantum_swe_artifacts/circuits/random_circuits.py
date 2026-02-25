from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def make_random_circuit(n_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_qubits)

    for _ in range(depth):
        for q in range(n_qubits):
            gate = rng.integers(0, 3)
            if gate == 0:
                qc.h(q)
            elif gate == 1:
                qc.rz(float(rng.uniform(-np.pi, np.pi)), q)
            else:
                qc.rx(float(rng.uniform(-np.pi, np.pi)), q)

        if n_qubits > 1:
            for q in range(n_qubits - 1):
                if rng.random() < 0.6:
                    qc.cx(q, q + 1)

    return qc
