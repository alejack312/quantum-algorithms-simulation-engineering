from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantum_swe_artifacts.backends.qiskit_backend import run_circuit
from quantum_swe_artifacts.circuits.iqp_circuits import make_iqp_circuit
from quantum_swe_artifacts.logging_utils import summarize, write_csv, write_json
from quantum_swe_artifacts.plotting import plot_variance_vs_shots


def _build_noise_model(noise_type: str, noise_strength: float):
    if noise_strength <= 0:
        return None
    try:
        from qiskit_aer.noise import NoiseModel, amplitude_damping_error, depolarizing_error
    except Exception:
        return None

    model = NoiseModel()
    p = max(0.0, min(1.0, float(noise_strength)))

    if noise_type == "amplitude_damping":
        one_qubit_error = amplitude_damping_error(p)
        two_qubit_error = amplitude_damping_error(p).tensor(amplitude_damping_error(p))
    else:
        one_qubit_error = depolarizing_error(p, 1)
        two_qubit_error = depolarizing_error(min(1.0, 2.0 * p), 2)

    model.add_all_qubit_quantum_error(one_qubit_error, ["h", "rx", "rz"])
    model.add_all_qubit_quantum_error(two_qubit_error, ["cx"])
    return model


def run(config: dict, output_dir: Path) -> dict:
    sweep = config.get("sweep", {})
    shots_values = sweep.get("shots", [128, 256, 512, 1024, 2048])
    noise_values = sweep.get("noise_strength", [0.0, 0.01])
    n_qubits = int(config.get("n_qubits", 4))
    density = float(config.get("density", 0.4))
    noise_type = str(config.get("noise_type", "depolarizing"))
    repetitions = int(config.get("repetitions", 5))
    seed = int(config.get("seed", 42))

    rows: list[dict] = []
    for shots in shots_values:
        for noise_strength in noise_values:
            noise_model = _build_noise_model(noise_type=noise_type, noise_strength=float(noise_strength))
            warmup = make_iqp_circuit(n_qubits=n_qubits, density=density, seed=seed)
            run_circuit(warmup, shots=shots, seed=seed, noise_model=noise_model)
            for rep in range(repetitions):
                rep_seed = seed + rep + int(noise_strength * 1000) + shots
                circ = make_iqp_circuit(n_qubits=n_qubits, density=density, seed=rep_seed)
                noiseless = run_circuit(circ, shots=shots, seed=rep_seed, noise_model=None)
                noisy = run_circuit(circ, shots=shots, seed=rep_seed, noise_model=noise_model)
                estimate = float(noisy["expect_z0"])
                baseline = float(noiseless["expect_z0"])
                rows.append(
                    {
                        "experiment": "noise_shot_scaling",
                        "noise_type": noise_type,
                        "shots": shots,
                        "noise_strength": noise_strength,
                        "rep": rep,
                        "estimate": estimate,
                        "noiseless_estimate": baseline,
                        "abs_error_vs_noiseless": abs(estimate - baseline),
                        "noise_model_active": noise_model is not None,
                        "wall_time_s": float(noisy["wall_time_s"]),
                    }
                )

    write_csv(rows, output_dir / "results.csv")
    summary = summarize(
        rows,
        group_keys=["shots", "noise_strength", "noise_type"],
        value_keys=["estimate", "abs_error_vs_noiseless", "wall_time_s"],
    )
    write_json(summary, output_dir / "summary.json")

    if config.get("plot", {}).get("enabled", True):
        df = pd.DataFrame(rows)
        plot_variance_vs_shots(df, output_dir / "figures" / "variance_vs_shots.png")

    return {"rows": len(rows), "output_dir": str(output_dir)}
