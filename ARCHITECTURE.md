# Architecture

Canonical scope: [PROJECT_V2.md](PROJECT_V2.md); evidence: [PROJECT_STATUS.md](PROJECT_STATUS.md). Core boundary: offline analysis, explicit simulation and narrow cohort calibration. Example applications execute local workloads for measurement; the simulator never executes them.

```text
src/workload_lab/
  ir.py          immutable instance types and domain validation
  ingest.py      bounded OTLP JSON/JSONL importer and allowlist
  graph.py       DAG ordering and longest path
  analysis.py    interval coverage, contributions and evidence
  simulation.py  explicit templates, FIFO pools, stable events and termination accounting
  calibration.py complete fixed-DAG empirical cohorts; refuses missing/failing inputs
  cli.py         file IO, text/JSON formatting and exit codes
tests/           unit, property and CLI contracts
examples/        synthetic OTLP inputs with hand-verifiable answers
benchmarks/      reproducible CPU analysis harness
docs/            research, ADRs, contracts and future designs
```

The source trace remains local and is not copied. The importer creates a normalized execution dataset; the compiler validates one work DAG per trace; analysis outputs evidence-carrying metrics. CLI and library use the same functions. Public artifacts are versioned JSON, while Python API compatibility remains experimental.

TraceImporter and WorkloadCompiler are small Python Protocol boundaries. Scenario/Task/PoolSpec/Arrival dataclasses define the simulation boundary; Observation records direct lifecycle facts. Empirical cohort artifacts reference original trace digests and record sample counts and limitations. No empty vendor classes, optimizer, CostModel or GPU profile is implied. Optional PydanticAI and SimPy imports stay in example/validation runners.

Containment is not causality. Container nodes establish observed envelopes; only atomic work nodes receive DAG weight. Explicit edges describe completed prerequisites, not parent nesting. Missing synchronization disables complete-graph claims. No unknown wait becomes a measured queue. Source IDs, method and origin accompany analysis.

The simulator receives a workload template, deployment and arrivals, not a raw trace tree. Calibration owns identified parameters; frozen experiment manifests own the operating envelope and held-out score. Optimization is gated on useful real-workload validity and decision value. External runtimes execute applications; the core library does not.
