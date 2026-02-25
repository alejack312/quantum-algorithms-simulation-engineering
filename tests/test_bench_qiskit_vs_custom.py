from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import yaml

from quantum_swe_artifacts.cli import main


def _fresh_dir(name: str) -> Path:
    out = Path("results") / name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def test_bench_micro_config_and_schema() -> None:
    out_dir = _fresh_dir("test_bench_qiskit_vs_custom_micro")
    cfg = yaml.safe_load(Path("configs/bench_qiskit_vs_custom_micro.yaml").read_text(encoding="utf-8"))
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
    required = {
        "n_qubits",
        "depth",
        "circuit_family",
        "observable",
        "backend_name",
        "mode",
        "shots",
        "seed",
        "runtime_s",
        "expectation_value",
        "abs_error_vs_reference",
    }
    assert required.issubset(set(df.columns))

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload.get("experiment") == "bench_qiskit_vs_custom"
    assert payload.get("aggregates")
    agg = payload["aggregates"][0]
    for key in ["runtime_mean_s", "runtime_std_s", "runtime_stderr_s", "abs_error_mean"]:
        assert key in agg
