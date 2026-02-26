from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable

import yaml


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(rows: list[dict], outpath: Path) -> None:
    if not rows:
        return
    ensure_dir(outpath.parent)
    with outpath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(data: dict, outpath: Path) -> None:
    ensure_dir(outpath.parent)
    outpath.write_text(json.dumps(data, indent=2), encoding="utf-8")


def copy_config(config: dict, outdir: Path) -> None:
    ensure_dir(outdir)
    with (outdir / "config.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)


def summarize(rows: Iterable[dict], group_keys: list[str], value_keys: list[str]) -> dict:
    buckets: dict[tuple, list[dict]] = {}
    for row in rows:
        key = tuple(row[k] for k in group_keys)
        buckets.setdefault(key, []).append(row)

    summary_rows = []
    for key, items in buckets.items():
        entry = {k: v for k, v in zip(group_keys, key)}
        for value_key in value_keys:
            values = [float(i[value_key]) for i in items if i.get(value_key) is not None]
            if not values:
                entry[f"{value_key}_mean"] = None
                entry[f"{value_key}_std"] = None
            else:
                entry[f"{value_key}_mean"] = mean(values)
                entry[f"{value_key}_std"] = pstdev(values) if len(values) > 1 else 0.0
        summary_rows.append(entry)

    return {
        "groups": group_keys,
        "metrics": value_keys,
        "rows": summary_rows,
    }
