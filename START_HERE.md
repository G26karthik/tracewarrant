# Project refresher

TraceWarrant is this Python project's selected public name; Workload Lab was its internal codename. It checks whether application traces contain enough information to support performance claims, then compares frozen model predictions with real measurements. It can explicitly report UNKNOWN or that a simple heuristic provides the same decision as a simulator.

The original ambition was an agent capacity planner. Experiments did not justify that broader product, so V3 narrowed the project to instrumentation conformance and model validation. The original research and negative results are preserved. This is an experimental local toolkit, with no running hosted service or recurring paid work.

## What you can use now

From the repository directory, with Python 3.11+ and uv:

```sh
uv sync --locked
uv run tracewarrant --help
uv run tracewarrant inspect examples/traces/pydantic-ai-2.51.0.otlp.json
uv run python -m benchmarks.v3_audit --output audit-new.json
```

The inspection reports unsupported queue/service claims for the unextended framework trace. The audit verifies historical preservation, rechecks three trace sources and reproduces the frozen external evaluation. It needs no model, GPU, service, credentials or network after dependencies are installed. Use a fresh output filename; existing files are never overwritten.

For your own application: export content-free OTLP JSON, run `inspect`, add missing instrumentation according to the contract, and emit neutral prediction/measurement artifacts from any model. Freeze predictions before collecting the intervention measurements. Run `evaluate` to compare models and cheap baselines. [Interface guide](docs/v3/artifacts-and-validation.md), [observation contract](docs/v3/observation-contract.md).

## What happened in the research

The external FRAMES study ran 16 calibration and 48 held-out sessions. The model's median mean-latency error was 1.50%, but a utilization heuristic chose the same intervention. All 48 held-out strict answer checks failed. Those results support the validation workflow; they do not establish a useful agent or a quality-preserving capacity recommendation. [Full V3 report](V3_PROJECT_REPORT.md).

## Current completion work

The 0.3.1 patch fixes comparison and output-integrity edge cases and adds reproducible installed-package qualification. It preserves the frozen study unchanged. [Current status](PROJECT_STATUS.md), [qualification procedure](docs/v3/release-qualification.md), [decision record](docs/adr/ADR-0018-controlled-comparisons-and-release-qualification.md).

TraceWarrant is licensed Apache-2.0 and has a public repository at [G26karthik/tracewarrant](https://github.com/G26karthik/tracewarrant). Private vulnerability reporting is enabled. The maintainer authorized publication of the code, documentation and experimental GitHub release. [Release procedure](PUBLIC_RELEASE.md). No additional research success, native rewrite, CUDA, optimizer or cloud deployment is required to honestly complete this scoped toolkit.

A separate clean checkout reproduces the tests, builds, installed-package qualification, frozen-study audit and analytical checks. Follow [hosted verification](https://github.com/G26karthik/tracewarrant/actions/workflows/ci.yml) and [GitHub releases](https://github.com/G26karthik/tracewarrant/releases) for the published results and artifacts.
