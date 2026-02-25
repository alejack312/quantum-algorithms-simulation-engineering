from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from quantum_swe_artifacts.cli import main


def _fresh_dir(name: str) -> Path:
    out = Path("results") / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def test_cli_smoke() -> None:
    out_dir = _fresh_dir("test_cli_smoke")
    cfg = {
        "experiment": "bench_qiskit_vs_custom",
        "output_dir": str(out_dir),
        "seed": 1,
        "repetitions": 2,
        "sweep": {"qubits": [2], "depth": [3]},
        "backend": {"type": "qiskit_aer", "shots": 128, "optimization_level": 0},
        "plot": {"enabled": True, "formats": ["png"]},
    }
    cfg_path = out_dir / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    rc = main(["run", "--config", str(cfg_path), "--quick"])
    assert rc == 0
    assert (out_dir / "results.csv").exists()
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "env.json").exists()


def test_cli_smoke_grad_variance() -> None:
    out_dir = _fresh_dir("test_cli_smoke_grad")
    cfg = {
        "experiment": "grad_variance",
        "output_dir": str(out_dir),
        "seed": 7,
        "repetitions": 2,
        "init_samples": 4,
        "sweep": {"qubits": [2]},
        "backend": {"type": "qiskit_aer", "shots": 128, "optimization_level": 0},
        "plot": {"enabled": True, "formats": ["png"]},
    }
    cfg_path = out_dir / "cfg_grad.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    rc = main(["run", "--config", str(cfg_path), "--quick"])
    assert rc == 0
    assert (out_dir / "results.csv").exists()
    assert (out_dir / "summary.json").exists()
    assert (out_dir / "env.json").exists()
