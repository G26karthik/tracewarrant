# Final autonomous project report

Date: 2026-09-29 (maintainer local date). Classification: **PIVOT RECOMMENDED**.

The repository now demonstrates observation → explicit graph → calibration → simulation → frozen prediction → measured intervention → reported error for a controlled workload. It predicted latency accurately, but a utilization heuristic selected the same useful intervention. A real-model application exposed shared inference behavior and little non-LLM demand. The evidence supports narrowing to an instrumentation/validation toolkit before expanding a standalone planner.

## Built, changed and verified

ContextForge proposed a durable agent runtime/context compiler. Its two original handoffs remain byte-for-byte unchanged. Initial Workload Lab V2 pivoted to trace analysis and proposed capacity modeling. This continuation implemented and tested that modeling loop within a narrow controlled scope, then revised the next product step on evidence.

| Milestone | Evidence and disposition |
| --- | --- |
| Baseline | Clean `9e15d8c`, 63 tests, source/history/docs inspected before edits |
| M1.5 | [Passed](docs/validation/milestone-1.5.md): actual concurrent and PydanticAI traces, direct lifecycle contract, missingness/privacy tests |
| M2 | [Passed](docs/validation/milestone-2.md): reference DES, queues/retries/cancellation/censoring, explicit scenario CLI, analytical and independent SimPy checks |
| M3 | [Assessed](docs/validation/milestone-3.md): native code deferred after fresh-process scale/memory measurements |
| M4 | [Controlled pass, general calibration partial](docs/validation/milestone-4.md): empirical cohorts and frozen held-out evaluation |
| M6 | [Applicability probe](docs/validation/milestone-6.md): real local-model non-coding application; no real-model predictive gate claimed |
| M5/M7/M8/M9 | Optimizer, custom CUDA, cloud topology and predictive regression CI remain gated |

The final suite has **102 tests passing on Windows CPython 3.12.12 and 3.13**. Lint, formatting, sdist/wheel build and an isolated wheel-only simulation pass. Hosted Linux/Windows CI is configured but has not run. The core wheel has zero third-party runtime dependencies; framework and SimPy dependencies are optional groups. No model download, paid provider call, cloud resource, GitHub publication or package upload occurred.

## Algorithms and architecture

Implemented iterative DAG validation/topological longest path, interval-union accounting, lifecycle identification, binary-heap DES with integer time and total microstep/phase/sequence ordering, FIFO finite pools/queues, bounded failures/retries/backoff, timeout/cancellation lag, horizon censoring, named SplitMix64 streams, empirical distributions and paired-session sensitivity. The event contract was committed before the kernel. Calibration records counts, provenance, tails and correlations and refuses incomplete/failing/mixed-topology cohorts. It does not fit missing service demand by guessing.

Observed instances and generative scenarios are separate. Parentage is containment, never inferred causality. Acquisition/release measures owned occupancy, not CPU/GPU demand. Core import/simulation never executes tools. Byte/span/nesting/string/numeric/state/event bounds constrain untrusted input. Example applications execute explicitly requested local measurement workloads.

Five generated M/M/1 cases (100,000 sessions) have 1.62% aggregate analytical mean-latency error; utilization and common-window Little's Law checks pass. Twenty independent SimPy FIFO cases match acquisition/release times exactly. These establish reference semantics, not actual-agent predictive validity.

## Predictions and measured interventions

The controlled workflow uses stub planning/synthesis, actual finite worker queues, local retrieval/tools, SQLite, fan-out/join and external waits. Training comprised 160 sessions in separate 2/s and 9/s cohorts. All eight 6/s and 8/s BASELINE / TOOL+ / MODEL+ / RETRIEVAL+ forecasts were committed at `377180c` (`pilot-1-freeze`) **before** 960 held-out sessions. [Immutable artifacts and reproduction commands](docs/experiments/README.md) preserve traces, models, lineage, seeds, predictions, replications and scores.

Median p95 relative error was **1.70%** across eight cells, against a preregistered 15% target. At 8/s, measured p95 fell from about **1,721 ms to 229 ms** with extra tool capacity. Both material intervention pairs were correctly ordered, with a small denominator of two. The single clear tool bottleneck agreed; the low-load case was marked ambiguous. Saturation was not identified from finite draining batches; p99 is underpowered. Per-cell signed/absolute/relative error, observed bootstrap intervals, paired sensitivity and fixed-tool-delay comparisons are published.

**The utilization heuristic also chose TOOL+.** Inference-only and naive-slot baselines chose other options, but added choice value over the stronger heuristic was not demonstrated. Forecasting 720 scenarios took 6.26 s, versus 150.8 s held-out collection plus 51.9 s calibration collection. Engineering effort is unmeasured; this is not an economic break-even claim.

The real application uses PydanticAI, deterministic tool planning, parallel retrieval/SQLite and actual Llama 3.1 8B synthesis over fictional facility facts. All 48 sessions passed three exact fact checks; reasoning quality remains unvalidated. Doubling client slots increased average occupied time per call **1.73x**. Client slots are not independent GPU replicas. Tool work was small and adding tool slots produced modest observed changes. No forecasts were frozen for this exploratory application, so no real-agent prediction-accuracy claim is made.

## Failures, negative results and revised assumptions

- Ordinary framework telemetry did not identify joins, pool capacity or queue/service separation; missing components stayed UNKNOWN.
- Short asyncio sleeps were unsuitable anchors on this Windows/Python clock (15.625 ms monotonic resolution). Original captures were preserved; longer v2 intervals were chosen before calibration.
- The first local Qwen structured-output warmup returned empty answer content and exhausted framework retries. Its failure artifact remains. Reasoning text was neither persisted nor promoted into an answer. An already-cached non-thinking model supported the amended exploratory probe.
- Inference-client occupancy changed under concurrency. It cannot be used as invariant GPU service demand without identifying hidden backend behavior.
- Successful controlled decisions were matched by a simpler heuristic. This is an explicit pivot signal, not a concealed finding.

Measurements used a shared workstation. Ancillary model/account discovery occurred during part of the latter controlled block; it remains a confound, and no unfavorable batch was discarded. Small sample sizes and two real replications limit tails, uncertainty and causal interpretation.

## C++, CUDA, cloud and deliberate omissions

No project-owned C++ was justified: the million-event reference case had median 3.361 s and roughly 280 MB whole-process peak; actual pilot simulation cost was small. No native speedup was measured or implied. The 10-million-event case was not run in the single-task harness because its session count exceeds the declared bound and current experiments do not need it.

No custom CUDA was justified. Existing Ollama inference used the verified RTX 4060 Laptop GPU (8,188 MiB, driver 616.56); backend-reported Llama residency is recorded. That is not a CUDA throughput profile or evidence for another GPU. The immediate gap is service identification, not an established kernel bottleneck.

An enabled Azure CLI account was observed, but no spend was authorized or incurred. IaC and a cost estimate were not invented before a useful cloud experiment exists. [Future authorization](HUMAN_ACTION_REQUIRED.md) is separate from the scientific gate. Cloud access is not why local work stops: the evidence does not justify the larger planner scope. Optimization and predictive capacity-regression CI remain unimplemented for the same reason.

## Competitors, remaining distinction and public readiness

AgentServeSim, AISimulate, Vidur and PerfSim overlap substantially; SimPy/SimGrid/WRENCH already supply simulation mechanisms. OTel, observability systems and direct load tests cover adjacent needs. [Dated research](docs/research/competitive-landscape.md) and [adversarial reassessment](docs/research/adversarial-review.md) contain the boundaries. No novelty claim or unperformed competitor reproduction is implied.

The useful remaining contribution is a content-free observation contract, explicit unknown/refusal behavior and reproducible validation with negative results. [ADR-0015](docs/adr/ADR-0015-narrow-to-validation.md) recommends developing that as a toolkit or upstream adapter. This is a conditional product-direction judgment, not proof simulation cannot help other workloads.

Unsupported: arbitrary framework operation alignment, missing entire traces, unseen tails, shared outages/nonstationarity, censor-aware fitting, real inference internals, sustainable capacity, quality-preserving optimization and external adoption. Current fitting assumes stable per-template operation identities. The controlled fit must not be transferred to the real-model application.

This is a reproducible research prototype, **not ready for a production/public package release**. Public naming, a private reporting contact, independent reproduction and release qualification remain unfinished. Reopen broader development for an independently motivated tool-heavy non-coding workload, identifiable inference behavior and frozen held-out decisions that justify modeling effort beyond a utilization heuristic. Prefer existing engines where they fit.
