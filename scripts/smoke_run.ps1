param(
    [switch]$Quick = $true
)

$ErrorActionPreference = "Stop"

$config = "configs/example_bench_qiskit_vs_custom.yaml"
$quickArg = if ($Quick) { "--quick" } else { "" }

python -m quantum_swe_artifacts run --config $config $quickArg
