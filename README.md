# Workload Lab (internal codename)

Status: Experimental / Research Prototype

This prototype converts supported local OTLP execution traces into a framework-neutral workload graph and reports deterministic path and timing contributions. It exposes missing dependencies and keeps observed and synthetic data separate. There is no simulator, optimizer or capacity recommendation yet.

The research question is whether calibrated non-LLM resource contention can improve agent capacity decisions. The broad idea has close competitors; see the [research](docs/research/competitive-landscape.md), [adversarial review](docs/research/adversarial-review.md) and [canonical V2](PROJECT_V2.md).

## Run the working slice

Python 3.11+; no database, GPU, model, agent framework or server needed. From this directory:

```sh
uv sync --locked
uv run workload-lab analyze examples/research-workflow.otlp.json --origin synthetic
uv run workload-lab analyze examples/research-workflow.otlp.json --format json
uv run workload-lab ingest examples/research-workflow.otlp.json --output workload-ir.json
uv run pytest
```

`--output` creates a new file and refuses overwrite. `analyze` consumes original OTLP JSON/JSONL, not compiled IR JSON in v0. Runtime-only installation also works with `python -m pip install .`; the distribution name is internal and must not be published.

```python
from workload_lab import analyze, compile_workload, ingest

dataset = ingest("examples/research-workflow.otlp.json", origin="synthetic")
for workflow in compile_workload(dataset):
    report = analyze(workflow)
    print(report.critical_path_elapsed.value)  # nanoseconds, with evidence beside it
```

The synthetic example has a hand-derived 11 s declared path, 14 s total work and 1 s unattributed wall time. These are fixture arithmetic, not benchmark claims. [Example explanation](examples/README.md).

## What the report means

OTel nesting expresses containment, not dependency. Declare finish-to-start prerequisites with `workload_lab.depends_on`; otherwise the graph remains incomplete. Work spans are atomic leaves; container spans are excluded from additive work. Longest path uses fixed observed elapsed weights and zero gaps. It cannot predict another load, infer service time or prove a capacity bottleneck. Contributions along one tied path may not be unique.

Missing queue/service values are UNKNOWN. Uncovered time is unattributed. GPU utilization and capacity recommendations remain unavailable. Every timing quantity carries origin, provenance, source and derivation method. Synthetic resources downgrade evidence automatically; no confidence interval is invented from one trace.

## Input and privacy

Accepts OTLP JSON `resourceSpans/scopeSpans/spans` envelopes, or one envelope per JSONL line. Not arbitrary framework exports or SDK console output. Default limits: 16 MiB and 50,000 spans. [Exact mapping](docs/design/otel-mapping.md), [IR semantics](docs/concepts/workload-ir.md).

No upload or telemetry. The allowlist removes payload-bearing names, prompts, arguments, messages and events. Selected service/model/tool labels and IDs remain potentially sensitive. [Security](SECURITY.md).

## Development and direction

[Architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [ADRs](docs/adr/README.md), [contributing](CONTRIBUTING.md), [benchmark methodology](docs/benchmarks/methodology.md), [validation plan](docs/validation/plan.md), [license inventory](docs/dependency-licenses.md).

The two ContextForge handoffs remain unchanged historical context. ContextForge and agentplan already have naming conflicts. No final public name or trademark clearance is claimed. New project code is Apache-2.0; reviewed competitor code has not been imported.
