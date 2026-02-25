from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml

from quantum_swe_artifacts.env import collect_env_info
from quantum_swe_artifacts.logging_utils import copy_config, write_json
from quantum_swe_artifacts.registry import EXPERIMENT_REGISTRY, get_experiment_runner


def _resolve_output_dir(config: dict) -> Path:
    raw = config.get("output_dir")
    if raw:
        return Path(raw)
    exp = config["experiment"]
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return Path("results") / f"{stamp}_{exp}"


def _validate_config(config: dict) -> None:
    required = ["experiment"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing config field: {key}")
    if config["experiment"] not in EXPERIMENT_REGISTRY:
        raise ValueError(f"Unknown experiment '{config['experiment']}'. Use `list` to view valid experiments.")
    config.setdefault("seed", 42)
    config.setdefault("repetitions", 5)
    config.setdefault("sweep", {})
    config.setdefault("backend", {"type": "qiskit_aer", "shots": 1024, "optimization_level": 1})
    config.setdefault("plot", {"enabled": True, "formats": ["png"]})


def cmd_list(_: argparse.Namespace) -> int:
    for name in sorted(EXPERIMENT_REGISTRY.keys()):
        print(name)
    return 0


def cmd_env(_: argparse.Namespace) -> int:
    print(json.dumps(collect_env_info(), indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    config = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    _validate_config(config)

    if args.quick:
        config["repetitions"] = min(2, int(config.get("repetitions", 2)))
        for key, values in config.get("sweep", {}).items():
            if isinstance(values, list) and values:
                config["sweep"][key] = values[:1]

    output_dir = _resolve_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    env_info = collect_env_info()
    write_json(env_info, output_dir / "env.json")
    copy_config(config, output_dir)

    fn = get_experiment_runner(config["experiment"])
    run_info = fn(config=config, output_dir=output_dir)

    print(f"Completed {config['experiment']}")
    print(f"Output: {output_dir}")
    print(json.dumps(run_info, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quantum-swe-artifacts", description="Quantum SWE artifacts runner")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run experiment from YAML config")
    run_p.add_argument("--config", required=True, help="Path to YAML config")
    run_p.add_argument("--quick", action="store_true", help="Run tiny subset for smoke checks")
    run_p.set_defaults(func=cmd_run)

    list_p = sub.add_parser("list", help="List experiments")
    list_p.set_defaults(func=cmd_list)

    env_p = sub.add_parser("env", help="Print environment info")
    env_p.set_defaults(func=cmd_env)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
