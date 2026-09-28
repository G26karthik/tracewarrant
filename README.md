# Workload Lab (internal codename)

Status: Experimental / Research Prototype

This prototype imports local OTLP traces, builds explicit workload graphs, simulates finite resources and tests narrow empirical models against held-out interventions. It preserves unknown semantics and separates measured, calibrated and simulated evidence. There is no validated general infrastructure recommendation or production release. Start with [PROJECT_STATUS.md](PROJECT_STATUS.md).

The research question is whether calibrated non-LLM resource contention can improve agent capacity decisions. The broad idea has close competitors; see the [research](docs/research/competitive-landscape.md), [adversarial review](docs/research/adversarial-review.md) and [canonical V2](PROJECT_V2.md).

## Run the working slice

Python 3.11+; no database, GPU, model, agent framework or server needed. From this directory:

```sh
uv sync --locked
uv run workload-lab analyze examples/research-workflow.otlp.json --origin synthetic
uv run workload-lab analyze examples/research-workflow.otlp.json --format json
uv run workload-lab ingest examples/research-workflow.otlp.json --output workload-ir.json
uv run workload-lab simulate examples/scenario.json --output simulation.json
uv run pytest
```

`--output` creates a new file and refuses overwrite. `analyze` consumes original OTLP JSON/JSONL, not compiled IR. `simulate` accepts a separate explicit scenario and never executes traced tools. Runtime-only installation works with `python -m pip install .`; the internal distribution must not be published.

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

The [controlled experiment](docs/experiments/README.md) achieved 1.70% median p95 error across eight frozen held-out cells. A utilization heuristic selected the same useful intervention; the workload uses stub inference. This does not establish real-agent differentiation. See [instrumentation](docs/design/instrumentation-contract.md) and [simulation semantics](docs/design/simulation-semantics.md) before interpreting results.

For fresh artifacts, create `artifacts/` and use new output names:

```sh
uv run python -m examples.capture_controlled --output artifacts/actual.json
uv run --group integration python -m examples.capture_pydantic_ai --output artifacts/framework.json
uv run --group validation python -m benchmarks.validate_simulation --output artifacts/analytic.json
uv run python -m benchmarks.simulation_benchmark --output artifacts/scale.json
```

Core tests use the committed content-free framework trace and need no framework. Optional groups isolate PydanticAI/OTel and the independent SimPy baseline. The optional [real-model probe](docs/experiments/real-model-probe-design.md) uses an already-cached local `qwen3-vl:4b`, never a model download or paid provider.

[Architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [ADRs](docs/adr/README.md), [contributing](CONTRIBUTING.md), [benchmark methodology](docs/benchmarks/methodology.md), [validation plan](docs/validation/plan.md), [license inventory](docs/dependency-licenses.md).

The two ContextForge handoffs remain unchanged historical context. ContextForge and agentplan already have naming conflicts. No final public name or trademark clearance is claimed. New project code is Apache-2.0; reviewed competitor code has not been imported.
