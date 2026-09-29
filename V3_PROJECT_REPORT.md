# V3 post-pilot report

This is the preserved initial 0.3.0 phase assessment. The later 0.3.1 engineering completion and selected TraceWarrant name are recorded in the [completion report](docs/v3/completion-0.3.1.md); the study conclusions below are unchanged.

2026-09-29. **Delivered: a local instrumentation/conformance and simulator-neutral validation prototype. Stronger scientific success remains unestablished.** Internal package 0.3.0, no public release.

The V2 decision **PIVOT RECOMMENDED** remains accepted. `PROJECT_V2.md`, `FINAL_PROJECT_REPORT.md`, commit `c0fad29`, tag `research-pilot-1`, both ContextForge handoffs and all protected historical evidence are unchanged. V3 supersedes only the active product direction.

## What is usable

- `inspect`: explicit support/missingness/contradiction reports over local OTLP, with content-free output and UNKNOWN inference demand.
- `schema` / `check`: a versioned open JSON Schema for predictions, protocols, measurements and freeze receipts, plus semantic checks independent of the DES.
- `freeze`: exact-byte hashes binding all producers and criteria before measurement. It does not authenticate clocks or collector honesty.
- `evaluate`: signed/absolute/relative errors; p50/p95/p99 when evidence permits; throughput/queue/utilization; typed interval containment; bottleneck agreement; material rankings; calibration-envelope violations; first-class baseline comparison.
- Public Python APIs and examples, a narrow explicit trace adapter, an offline reproduction audit, and retained raw/calibrated/simulated artifacts.

The core has zero third-party runtime dependencies and does not load a simulator for validation. The preserved DES remains a reference/backend. SimPy, fixed-delay and utilization producers use the same interchange without DES types. Ordinal heuristics keep numeric predictions UNKNOWN. No aggregate confidence score disguises missing evidence.

## External evidence

The externally authored FRAMES tasks were selected before measurements using a deterministic row/source-count rule. The local executor performs real fetch/parse, retrieval, SQLite and cached Llama inference. Sixteen calibration sessions preceded a committed prediction freeze at `af36005` / `v3-frames-freeze`; 48 held-out sessions followed. No tasks or unfavorable batches were removed.

SimPy's median mean-latency relative error was **1.50% over six cells**; FETCH2 errors were 6.68% and 11.78%, so the median is not a complete accuracy summary. Both SimPy and the utilization heuristic selected FETCH2 and ordered the two material pairs correctly. There was **no added intervention-choice value over utilization**. Seed-range containment was 4/6 and is not a statistical confidence guarantee. All offered sessions completed, but the strict exact-answer gate passed **0/48** in holdout. Equivalent wording is not accepted by that proxy, and semantic quality is unvalidated. Speedups cannot be presented as useful-agent capacity recommendations.

The workload is tool-heavy, but fetch utilization already made the intervention apparent. The requested stronger case, with adequate task quality and a decision that current utilization cannot resolve, has not been established. This is a negative result from one bounded study, not proof such workloads do not exist.

Conformance independently caught an actual collector defect: the wrong root-completeness key. The original traces are preserved and refused. A narrow adapter renames only the existing boolean root assertion; all 72 feasibility/calibration/holdout graphs then pass structural validation. No dependency is invented, and GPU demand stays UNKNOWN. [Detailed results](docs/v3/results.md).

## Success criteria assessed separately

| Requested criterion | Evidence and limit |
| --- | --- |
| Multiple trace sources against a clear contract | Controlled concurrency, PydanticAI and external FRAMES captures inspected |
| Correct refusal of unsupported claims | Missing queues/topology, wrong binding, GPU demand, insufficient samples/provenance and mismatched metric semantics refused |
| Multiple independent model sources | SimPy, fixed-delay and ordinal utilization artifacts; validator imports none of those engines |
| Frozen artifacts independently evaluated | Git freeze precedes collection; hashes checked; offline evaluation reproduces byte for byte |
| First-class simple baselines | Numeric fixed-delay plus ordinal utilization, with no invented heuristic latencies |
| Reveal added value or its absence | Real study reports no added choice value; tests cover baseline wins and insufficient evidence |
| Reproducible and content-free defaults | Raw lifecycle observations/digests/options retained; prompts/documents/answers/reasoning omitted |
| External/non-author workload | Eight Google FRAMES task definitions; executor authored here, no external adoption claimed |
| Explicit limitations | Quality failure, trivial fetch bottleneck, unidentifiable inference, small correlated batches, extrapolation and unauthenticated chronology |
| Useful without capacity-planner thesis | Standalone conformance, open artifacts, integrity and independent comparisons all work without the DES |

## Verification and release boundaries

**139 tests pass on Windows Python 3.11, 3.12.12 and 3.13.** Ruff lint/format, wheel/sdist build, exported-schema interoperability, historical preservation and isolated wheel-only evaluation pass. The wheel reproduces the published validation byte for byte with one installed package and no runtime dependencies. Hosted CI is configured but unexecuted. [Verification](docs/v3/verification.md), [reproduction](docs/v3/reproduce.md).

Research was refreshed before the V3 contract was finalized. AISimulate/AgentServeSim, SimPy/SimGrid/WRENCH, OTel, Langfuse/Phoenix, agent evaluators, telemetry-validation and load-testing systems overlap substantially. No uniqueness or unperformed competitor reproduction is claimed. Integration/upstream use is preferable to building another platform. [Landscape](docs/v3/research.md), [ADR-0016](docs/adr/ADR-0016-validation-toolkit.md), [ADR-0017](docs/adr/ADR-0017-neutral-artifact-integrity.md).

C++, CUDA, optimizer and Azure expansion were not justified. No paid inference, cloud resources, external messages, public naming, package upload or GitHub publication occurred. Public release and independent adoption remain unqualified. Future work should improve independent workload/quality evidence or integrate the already useful validation interfaces; it should not manufacture a reason to resume the old roadmap.
