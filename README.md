# TraceWarrant

**Check the evidence behind performance claims.**

Status: Experimental / Research Prototype

TraceWarrant checks whether observations support a performance model and whether frozen predictions survive real interventions. Use its trace conformance checker and simulator-neutral validator without adopting our simulator. UNKNOWN, unsupported claims and a simple baseline beating a complex model are useful results. Returning to the project? Start with [the short refresher](START_HERE.md), then [PROJECT_V3.md](PROJECT_V3.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md).

Former internal name: Workload Lab. The selected public name and local distribution are `tracewarrant`; this candidate has not been published. The `workload-lab` command, `workload_lab` Python imports and versioned artifact/telemetry bindings remain compatible. Apache-2.0 licensed. [Naming decision](docs/v3/naming-2026-09-29.md), [release qualification](docs/v3/release-qualification.md).

V3 accepts the pilot's **PIVOT RECOMMENDED** conclusion. [V2](PROJECT_V2.md), [its final report](FINAL_PROJECT_REPORT.md), `research-pilot-1` and all frozen evidence remain unchanged. This is a local research prototype, not a capacity planner or production release. [Refreshed research](docs/v3/research.md) establishes substantial overlap; no uniqueness is claimed.

## Inspect and validate without a simulator

Python 3.11+; core runtime has no third-party dependencies, service or GPU requirement.

```sh
uv sync --locked
uv run tracewarrant inspect examples/traces/pydantic-ai-2.51.0.otlp.json
uv run tracewarrant inspect examples/v3/frames-heldout-base.otlp.json
uv run tracewarrant schema
uv run tracewarrant check docs/v3/frames-frozen/simpy.json
```

The framework capture cannot identify queue/service boundaries. The external FRAMES capture exposes a misspelled completeness binding; inspection refuses it. [An explicit adapter and the retained failure](docs/v3/results.md) show how to fix an existing assertion without guessing topology.

Re-evaluate the frozen external experiment entirely offline:

```sh
uv run workload-lab evaluate --protocol docs/v3/frames-frozen/protocol.json --freeze docs/v3/frames-frozen/freeze.json --prediction docs/v3/frames-frozen/simpy.json --prediction docs/v3/frames-frozen/fixed.json --prediction docs/v3/frames-frozen/utilization.json --measurement docs/v3/frames-evaluation/measured-r0.json --measurement docs/v3/frames-evaluation/measured-r1.json
```

In that study, SimPy and the utilization heuristic selected the same intervention. Exact-answer quality failed, so measured speedups do not establish a useful agent. [Results and limits](docs/v3/results.md), [reproduction](docs/v3/reproduce.md), [observation contract](docs/v3/observation-contract.md), [artifact schema/evaluation](docs/v3/artifacts-and-validation.md).

```python
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import ingest

report = inspect_observations(ingest("traces.json"))
print(report["claims"]["inference_service_demand"])  # UNKNOWN, with required instruments
```

## Preserved reference backend

Python 3.11+; no database, GPU, model, agent framework or server needed. From this directory:

```sh
uv sync --locked
uv run workload-lab analyze examples/research-workflow.otlp.json --origin synthetic
uv run workload-lab analyze examples/research-workflow.otlp.json --format json
uv run workload-lab ingest examples/research-workflow.otlp.json --output workload-ir.json
uv run workload-lab simulate examples/scenario.json --output simulation.json
uv run pytest
```

`--output` creates a new file and refuses overwrite. `analyze` consumes original OTLP JSON/JSONL, not compiled IR. `simulate` accepts a separate explicit scenario and never executes traced tools. Runtime-only installation works with `python -m pip install .`; the local candidate retains the upload-prevention classifier pending publication.

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

Core tests use the committed content-free framework trace and need no framework. Optional groups isolate PydanticAI/OTel and the independent SimPy baseline. The [real-model probe](docs/experiments/real-model-probe-design.md) uses already-cached local `llama3.1:8b` after preserving a failed Qwen warmup. It never downloads weights or contacts a paid provider.

[Architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [ADRs](docs/adr/README.md), [contributing](CONTRIBUTING.md), [benchmark methodology](docs/benchmarks/methodology.md), [validation plan](docs/validation/plan.md), [license inventory](docs/dependency-licenses.md).

The two ContextForge handoffs remain unchanged historical context. TraceWarrant replaces the internal Workload Lab name; historical names remain in frozen evidence. New project code is Apache-2.0; reviewed competitor code has not been imported.
