from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from quantum_swe_artifacts.logging_utils import write_csv, write_json
from quantum_swe_artifacts.plotting import plot_runtime_scaling


def _fresh_dir(name: str) -> Path:
    out = Path("results") / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def test_logging_and_plotting() -> None:
    out_dir = _fresh_dir("test_logging_plotting")
    rows = [
        {"n_qubits": 2, "depth": 5, "qiskit_time_s": 0.01},
        {"n_qubits": 4, "depth": 5, "qiskit_time_s": 0.02},
    ]

    write_csv(rows, out_dir / "results.csv")
    write_json({"ok": True}, out_dir / "summary.json")

    df = pd.DataFrame(rows)
    plot_runtime_scaling(df, out_dir / "figures" / "runtime.png")

    assert (out_dir / "results.csv").exists()
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "figures" / "runtime.png").exists()
