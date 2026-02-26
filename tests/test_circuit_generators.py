from quantum_swe_artifacts.circuits.iqp_circuits import make_iqp_circuit
from quantum_swe_artifacts.circuits.random_circuits import make_random_circuit


def test_random_circuit_qubits() -> None:
    qc = make_random_circuit(n_qubits=4, depth=6, seed=123)
    assert qc.num_qubits == 4
    assert qc.depth() > 0


def test_iqp_circuit_qubits() -> None:
    qc = make_iqp_circuit(n_qubits=5, density=0.5, seed=123)
    assert qc.num_qubits == 5
    assert qc.depth() > 0
