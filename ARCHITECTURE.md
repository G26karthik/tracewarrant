# Architecture

Active scope: [PROJECT_V3.md](PROJECT_V3.md); evidence: [PROJECT_STATUS.md](PROJECT_STATUS.md). The product boundary is offline observation conformance and model-neutral prediction evaluation. The V2 simulator remains an optional reference backend. Example applications execute explicitly requested measurement workloads; core inspection/validation executes none.

```text
src/workload_lab/
  ir.py          immutable instance types and domain validation
  ingest.py      bounded OTLP JSON/JSONL importer and allowlist
  graph.py       DAG ordering and longest path
  analysis.py    interval coverage, contributions and evidence
  conformance.py claim support, missing instrumentation and contradiction reports
  artifact_schema.py open prediction/measurement/protocol/freeze JSON Schema
  artifacts.py   bounded validation, semantic checks and exact-byte integrity receipts
  validation.py  independent error, interval, ranking, baseline and envelope comparisons
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

V3 artifact schemas contain no DES types. Library imports load the simulator lazily only when its V2 API is used. Independent SimPy, fixed-delay and ordinal utilization producers pass through identical validation. `inspect` emits no application labels; legacy `ingest`/`analyze` retain their documented safe-field metadata contract.

The reference simulator receives a workload template, deployment and arrivals, not a raw trace tree. Calibration owns identified parameters; frozen artifacts own the operating envelope and held-out score. Optimizers, C++, CUDA and cloud deployment require a measured V3 requirement. External runtimes execute applications; the core library does not. See [ADR-0016](docs/adr/ADR-0016-validation-toolkit.md) and [ADR-0017](docs/adr/ADR-0017-neutral-artifact-integrity.md).
