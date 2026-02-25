from __future__ import annotations

from qiskit import transpile


def run_transpile(circuit, optimization_level: int, seed: int = 0):
    return transpile(circuit, optimization_level=optimization_level, seed_transpiler=seed)
