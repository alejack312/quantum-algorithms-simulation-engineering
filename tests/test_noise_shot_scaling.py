from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import yaml

from quantum_swe_artifacts.cli import main


REQUIRED_COLUMNS = {
    "circuit_family",
    "observable",
    "n_qubits",
    "depth",
    "shots",
    "seed",
    "seed_circuit",
    "seed_params",
    "seed_shots",
    "backend_name",
    "mode",
    "expectation_est",
    "expectation_ref",
    "abs_error",
    "runtime_s",
}


def _fresh_dir(name: str) -> Path:
    out = Path("results") / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def test_noise_shot_scaling_micro_schema_and_figures() -> None:
    out_dir = _fresh_dir("test_noise_shot_scaling_micro")
    cfg = yaml.safe_load(Path("configs/noise_shot_scaling_micro.yaml").read_text(encoding="utf-8"))
    cfg["output_dir"] = str(out_dir)

    cfg_path = out_dir / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

    rc = main(["run", "--config", str(cfg_path)])
    assert rc == 0

    results_path = out_dir / "results.csv"
    summary_path = out_dir / "summary.json"
    assert results_path.exists()
    assert summary_path.exists()

    df = pd.read_csv(results_path)
    assert REQUIRED_COLUMNS.issubset(set(df.columns))

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary.get("experiment") == "noise_shot_scaling"
    assert summary.get("aggregates")

    fig_dir = Path("artifacts/02_noise_shot_scaling/figures")
    assert (fig_dir / "abs_error_vs_shots_300dpi.png").exists()
    assert (fig_dir / "stderr_abs_error_vs_shots_300dpi.png").exists()
    assert (fig_dir / "runtime_vs_shots_300dpi.png").exists()
