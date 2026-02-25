from __future__ import annotations

import platform
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version

import numpy as np


@dataclass
class EnvInfo:
    python: str
    qiskit: str
    numpy: str
    os: str
    cpu: str


def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def collect_env_info() -> dict[str, str]:
    info = EnvInfo(
        python=platform.python_version(),
        qiskit=_pkg_version("qiskit"),
        numpy=np.__version__,
        os=f"{platform.system()} {platform.release()}",
        cpu=platform.processor() or "unknown",
    )
    return asdict(info)
