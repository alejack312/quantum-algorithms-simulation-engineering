from __future__ import annotations

from importlib import import_module
from typing import Callable

EXPERIMENT_REGISTRY = {
    "bench_qiskit_vs_custom": "quantum_swe_artifacts.experiments.bench_qiskit_vs_custom",
    "noise_shot_scaling": "quantum_swe_artifacts.experiments.noise_shot_scaling",
    "grad_variance": "quantum_swe_artifacts.experiments.grad_variance",
    "transpile_study": "quantum_swe_artifacts.experiments.transpile_study",
}


def get_experiment_runner(name: str) -> Callable:
    module_path = EXPERIMENT_REGISTRY[name]
    module = import_module(module_path)
    return module.run
