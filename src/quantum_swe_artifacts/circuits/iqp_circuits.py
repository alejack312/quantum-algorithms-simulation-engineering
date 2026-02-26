from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit


def make_iqp_circuit(n_qubits: int, density: float, seed: int) -> QuantumCircuit:
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n_qubits)

    for q in range(n_qubits):
        qc.h(q)

    for q in range(n_qubits):
        if rng.random() < density:
            qc.rz(float(rng.uniform(-np.pi, np.pi)), q)

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            if rng.random() < density:
                theta = float(rng.uniform(-np.pi, np.pi))
                qc.cx(i, j)
                qc.rz(theta, j)
                qc.cx(i, j)

    for q in range(n_qubits):
        qc.h(q)

    return qc
