# Architecture

Canonical scope: [PROJECT_V2.md](PROJECT_V2.md). Implemented boundary: offline deterministic analysis only.

```text
src/workload_lab/
  ir.py          immutable instance types and domain validation
  ingest.py      bounded OTLP JSON/JSONL importer and allowlist
  graph.py       DAG ordering and longest path
  analysis.py    interval coverage, contributions and evidence
  cli.py         file IO, text/JSON formatting and exit codes
tests/           unit, property and CLI contracts
examples/        synthetic OTLP inputs with hand-verifiable answers
benchmarks/      reproducible CPU analysis harness
docs/            research, ADRs, contracts and future designs
```

The source trace remains local and is not copied. The importer creates a normalized execution dataset; the compiler validates one work DAG per trace; analysis outputs evidence-carrying metrics. CLI and library use the same functions. Public artifacts are versioned JSON, while Python API compatibility remains experimental.

TraceImporter and WorkloadCompiler are small Python Protocol boundaries. Concrete simulation interfaces (ServiceModel, ResourceModel, Scheduler, SimulationEngine, CostModel, Optimizer, HardwareProfile, ValidationBackend) remain documented proposals until their first implementation. Avoid empty vendor classes and abstract factories with no consumer.

Containment is not causality. Container nodes establish observed envelopes; only atomic work nodes receive DAG weight. Explicit edges describe completed prerequisites, not parent nesting. Missing synchronization disables complete-graph claims. No unknown wait becomes a measured queue. Source IDs, method and origin accompany analysis.

Later the simulator receives a workload template, deployment and arrivals, not a raw trace tree. Calibration owns inference of those model parameters and its validation envelope. Optimization consumes a validated simulator and never owns truth about measurements. External runtimes execute applications; this project does not.
