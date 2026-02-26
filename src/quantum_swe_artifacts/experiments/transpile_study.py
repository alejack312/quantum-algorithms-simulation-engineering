from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantum_swe_artifacts.circuits.random_circuits import make_random_circuit
from quantum_swe_artifacts.logging_utils import summarize, write_csv, write_json
from quantum_swe_artifacts.plotting import plot_transpile_depth
from quantum_swe_artifacts.transpile.passes import run_transpile


def _count_ops(circuit) -> dict[str, int]:
    counts = circuit.count_ops()
    return {str(k): int(v) for k, v in counts.items()}


def run(config: dict, output_dir: Path) -> dict:
    sweep = config.get("sweep", {})
    n_qubits_values = sweep.get("qubits", [4])
    depths = sweep.get("depth", [12])
    optimization_levels = sweep.get("optimization_level", [0, 1, 2, 3])
    seed = int(config.get("seed", 42))

    rows: list[dict] = []

    for n_qubits in n_qubits_values:
        for depth in depths:
            base = make_random_circuit(n_qubits=n_qubits, depth=depth, seed=seed + n_qubits + depth)
            for level in optimization_levels:
                transpiled = run_transpile(base, optimization_level=int(level), seed=seed)
                rows.append(
                    {
                        "experiment": "transpile_study",
                        "n_qubits": n_qubits,
                        "depth": depth,
                        "optimization_level": int(level),
                        "original_depth": int(base.depth()),
                        "transpiled_depth": int(transpiled.depth()),
                        "original_ops": _count_ops(base),
                        "transpiled_ops": _count_ops(transpiled),
                    }
                )

    write_csv(rows, output_dir / "results.csv")
    summary = summarize(rows, group_keys=["n_qubits", "depth", "optimization_level"], value_keys=["transpiled_depth"])
    write_json(summary, output_dir / "summary.json")

    if config.get("plot", {}).get("enabled", True):
        df = pd.DataFrame(rows)
        plot_transpile_depth(df, output_dir / "figures" / "transpile_depth.png")

    return {"rows": len(rows), "output_dir": str(output_dir)}
