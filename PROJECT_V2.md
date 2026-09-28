Status: CANONICAL V2  
Supersedes: ContextForge handoff as implementation specification  
Preserves: ContextForge handoff as historical architecture context

# Workload Lab — internal codename

Specification date: 2026-09-28; evidence update 2026-09-29. Status: Experimental / Research Prototype. Public name undecided. The continuation brief authorizes gated autonomous work beyond M1. M1.5 passed the bounded trace compatibility gate; future milestones require their own evidence.

Current state takes precedence over the historical proposals below: [PROJECT_STATUS.md](PROJECT_STATUS.md). [M1.5](docs/validation/milestone-1.5.md) adds observed lifecycle fields in schema 0.2, actual concurrent traces and one optional PydanticAI integration. Ordinary framework traces remain incomplete with UNKNOWN queue/service. [ADR-0013](docs/adr/ADR-0013-observed-resource-lifecycle.md) extends ADR-0002/0003/0009 without replacing their containment/privacy principles. [Minimum instrumentation contract](docs/design/instrumentation-contract.md).

## 1. Executive summary

Investigate whether content-free observations of a heterogeneous agent workflow can support calibrated resource-contention models and trustworthy infrastructure decisions. The proposed product turns supported traces into an execution graph, separates observed facts from modeling assumptions, and eventually evaluates resource changes against held-out real runs. The central experiment is whether browser/retrieval/database limits alter capacity decisions that inference-only or fixed-tool-gap models would make.

The broad digital-twin thesis does not by itself differentiate this project. AgentServeSim, AISimulate and PerfSim are serious precedents/competitors. The narrower thesis survives **conditionally**, pending intervention accuracy and user value. Today the executable scope is local trace-to-graph analysis; it cannot simulate, optimize or recommend purchases.

## 2. Historical ContextForge design

The original was a budget-aware durable agent runtime and context compiler. ContextPackage combined evidence, budgets, permissions, tools, skills and cacheable prefixes. ResearchOps was the non-coding workload; Temporal supplied durable execution; Chronos and Sentinel supplied scheduling and reliability experiments. C++/CUDA was proposed for reranking. Qdrant was a candidate, pgvector a baseline. See [historical reconstruction](docs/design/historical-mapping.md) and the two unchanged root handoffs. The DOCX's expanded tables were inspected structurally; its page layout could not be rendered in this environment.

## 3. Reason for pivot

Operating a complete agent runtime would divide effort across mature infrastructure and obscure the research contribution. V2 shifts ownership from executing agents to representing and validating their performance. Historical ideas remain optional workload/policy experiments. No database, framework or cloud dependency carries over merely because it appeared in the old diagram.

## 4. Problem statement

End-to-end latency and sustainable arrivals depend on multiple resource pools, external waits and synchronization. Observed duration alone does not identify service demand or predict scaling. We need an inspectable chain from telemetry to assumptions to predictions to intervention results, and a clear refusal when the data cannot support the requested inference.

## 5. Target users

First: maintainers of one non-coding agent application with access to instrumentation and at least one controllable tool-worker pool. Later: small infrastructure teams, researchers, students, self-hosters and labs comparing deployment configurations. Avoid initial enterprise inventory discovery, billing integration or universal framework support.

## 6. Non-goals

No agent framework, workflow engine, inference engine, vector store, MCP gateway, model router, general observability UI or Kubernetes scheduler. No autonomous deployment. No inference of task quality from timing. No promise that an arbitrary uninstrumented application can become an accurate twin. No cloud or GPU requirement for M0–M2.

## 7. Competitive landscape summary

[The dated landscape](docs/research/competitive-landscape.md) records capability boundaries, licenses, activity and evidence. AgentServeSim already uses agent programs and causal successor release; AISimulate already offers inference planning and experimental agentic replay; PerfSim already models heterogeneous service chains. SimPy/SimGrid/WRENCH are credible engine alternatives. OTel, Langfuse and Phoenix already cover observation. k6/direct load tests are necessary validation baselines, not competitors to dismiss.

## 8. Exact differentiation to test

Proposed contribution: a small representation and calibration workflow for **independently contended non-LLM pools coupled to inference**, with explicit uncertainty and measured intervention checks. Test browser-worker increases against inference-worker increases under the same task mix. Compare an independently calibrated pool model against fixed tool delays, naive scaling and direct load sweeps. “Whole agent” and “digital twin” are aspirations until this experiment succeeds. Prefer upstream adapters if existing engines already solve the problem.

## 9. Product principles

Evidence before recommendation; content-free by default; local execution; explicit scope/envelope; unknown is not zero; frameworks remain adapters; smallest reversible architecture; publish prediction error and negative results. Do not claim GPU saturation, service demand, queueing or branch probabilities from wall-clock span duration alone. Public name and final brand require fresh clearance.

## 10. Agent Workload IR v0 proposal

There are two different objects: **observed execution instances** and, later, **generative workload templates**. Implement only instances now. An instance contains a version, trace identity, source digest/origin, normalized spans, explicit dependency edges, and diagnostics. A node retains stable `(trace_id, span_id)`, parent ID, node kind, resource/service label, role, integer nanosecond timestamps, status, optional token/model metadata, and evidence for reported timing. Known kinds: workflow, llm, embedding, retrieval, reranker, tool, compute, database, queue, external_api, human_gate, unknown.

Parentage expresses containment; a separate edge expresses finish-to-start dependency. Never convert a parent link or generic OTel link directly to a dependency. Work nodes are atomic leaves; nested instrumentation defaults to containers, avoiding inclusive double counting. Explicit atomic work containing child spans is rejected in v0. Retries remain distinct observed nodes. Cycles, duplicate IDs, invalid timestamps and dangling declared dependencies are errors. Missing parents/sampling/topology produce incomplete diagnostics. A graph-complete flag is an instrumentation assertion, not independently verified truth.

Explicit queue/service nanoseconds may be imported; otherwise UNKNOWN. Their sum may not exceed the span. Resource demand, capacities, retry policies, cancellation semantics, arrivals and distributions are unimplemented extensions, not silently invented fields. A null queue is not a zero queue. [IR contract](docs/concepts/workload-ir.md) is synchronized with code and fixtures.

## 11. Measurement and provenance model

Use MEASURED, CALIBRATED, INTERPOLATED, EXTRAPOLATED, SIMULATED, ESTIMATED and UNKNOWN as evidence categories, not an ordered confidence scale. Separately retain origin (observed/synthetic), method, source IDs/digest, assumptions, sample count and optional bounds with their statistical meaning. A simulated result can depend on measured and extrapolated inputs. A synthetic fixture's timestamps are ESTIMATED, never empirical measurements. Derived graph statistics describe the supplied graph and retain input lineage. A null interval means no bound established; it does not mean certainty.

Future recommendations carry weakest relevant inputs, supported operating envelope, held-out error and sensitivity. Sampling error, model discrepancy and scenario uncertainty must remain distinct. [Provenance contract](docs/concepts/provenance.md).

## 12. Architecture

```text
Local OTLP JSON / JSONL
  -> strict importer and content allowlist
  -> execution IR validation
  -> explicit work DAG
  -> deterministic analysis
  -> text / JSON report

Later: execution cohorts -> calibration -> workload template + deployment
       -> simulator -> constrained search -> candidate + evidence
       -> held-out intervention validation -> calibration revision
```

Python library functions own domain behavior. CLI handles paths/formatting/errors. JSON is the initial artifact boundary. No long-running service is required. [Architecture](ARCHITECTURE.md) documents implemented modules and future interfaces.

## 13. Algorithms

M1: iterative DAG validation and topological longest path, deterministic tie breaking, interval-union accounting and contribution along one tied critical path. Longest path weights are observed leaf-span elapsed times; it is a fixed-weight zero-gap model, not an identified service-demand model. Container duration is excluded. Report total work separately from wall-clock coverage; concurrent contributions must not be portrayed as an end-to-end percentage decomposition. Alternative tied paths may yield different attribution.

Later: stochastic DAG replay; queueing approximations only with diagnosed stationarity/arrival/service assumptions; FIFO first, then SPT/EDF/critical-path/fairness policies; tiny exact replica enumeration before heuristics; Pareto cost/latency/reliability comparisons. M/M/k is a validation case, not a default model of every provider. Cache/placement algorithms require a measured decision problem before implementation.

## 14. C++ strategy

PROPOSED: C++20 DES behind batch-oriented pybind11 bindings. First establish Python reference semantics and compare against SimPy. Benchmark event throughput, memory/event and parity on fixed seeds. Native work is justified by experiment runtime or memory bottlenecks; retain Python if absent. Start with binary heap and stable event sequence numbers. Calendar queues, timing wheels, object pools, SoA and PDES require separate benchmarks. No native code in M1.

## 15. CUDA strategy

PROPOSED: hardware characterization after a service model needs it. Measure bandwidth/GEMM/launch/concurrency curves and representative serving anchors, recording GPU SKU, VRAM, clocks, power, driver, CUDA, kernel source and input shape. Synthetic kernels cannot alone predict model serving. Never label RTX 4060 measurements as another GPU's profile. The old MaxSim idea remains a historical optional experiment.

## 16. OTel ingestion strategy

OTLP/JSON ExportTraceServiceRequest envelopes are the initial interchange, optionally one envelope per JSONL line. No collector endpoint, protobuf, arbitrary SDK console output or vendor export is claimed. Support case-insensitive hexadecimal IDs, integer nanosecond strings, resourceSpans/scopeSpans and typed attribute values. Preserve schema URLs as provenance; unknown content-bearing attributes/events are discarded. Input limits and strict errors prevent uncontrolled ingestion.

GenAI conventions moved to their own repository and remain development-status in reviewed agent documentation. Pin the researched mapping snapshot rather than claiming all “OTel” versions work. Standard attributes cover operations, model/provider, token counts, retrieval metadata and tool identity; resource pool capacity, queue/service decomposition, dependency completeness and retry/cancel scheduling need narrowly documented `workload_lab.*` extensions. [Exact mapping and omissions](docs/design/otel-mapping.md).

## 17. Framework integration strategy

Core imports normalized OTLP, not framework objects. Later support one real non-coding application, preferably custom instrumentation first or one framework exporting the necessary information. Temporal, MCP, LangGraph, CrewAI, PydanticAI and backend-native exports remain adapter candidates. Langfuse and Phoenix are optional data boundaries. Every adapter needs versioned contract fixtures, loss diagnostics and no core dependency on its runtime.

## 18. Storage requirements

M1: local bounded JSON/JSONL input and deterministic JSON output. No raw input copies by default. Source SHA-256 supports lineage without retaining content. Trace IDs and service labels can still be sensitive. Later Parquet for columnar cohorts, DuckDB for offline analysis, SQLite for an artifact index only when query requirements justify them. No vector DB. Immutable model/experiment manifests remain portable files.

## 19. Simulator architecture

PROPOSED M2: single-threaded integer-time DES with total event ordering `(time, phase, insertion_sequence)`, explicit finite pools and bounded queues, deterministic named PRNG streams, and releases driven by predecessor completion. Define same-time completion/cancellation/admission order before coding. Separate external waits from occupied worker time. Preserve queue/service split, failures, retries, backoff, fan-out/join, cancellation and terminated-session accounting. No recorded-timestamp replay for changed-resource predictions. [Simulator design](docs/concepts/simulator.md).

## 20. Optimizer architecture

PROPOSED M5: finite-domain exact enumeration for tiny replica spaces, explicit budget horizon/currency and provider limits. Evaluate service-level success probability jointly with latency; distinguish completed-only latency from timeout/failure probability. Reject uncalibrated candidates as “insufficient evidence,” not “feasible.” Search on training scenarios; verify finalists on fresh seeds/holdout runs to reduce optimizer overfitting. Return Pareto candidates and assumptions. [Optimization design](docs/concepts/optimization.md).

## 21. Calibration design

PROPOSED M4: fit per-resource service/arrival/branch/retry distributions within version/hardware/load cohorts. Require enqueue/start/end where capacity is inferred; wall time alone is not identifiable. Preserve within-session and shared-outage correlation; compare empirical bootstrap against parametric fits. Split by session/time/configuration to prevent leakage. Track sample counts, censoring, missing traces and instrumentation overhead. [Calibration](docs/concepts/calibration.md).

## 22. Reliability and failure model

M1 stores normalized observed error status, without executing retries. M2 will model bounded attempts, retry storms, rate limits, outages, timeouts, worker loss, cancellation lag and side effects. Cancellation does not always release resources immediately. Human gates are external waits; do not assume a worker is reserved. No simulator may invoke actual tools or reproduce side effects. Report failed and censored sessions in denominators.

## 23. Production architecture

Initial product remains an offline library/CLI. Later batch workers may process immutable experiments with bounded memory and versioned artifacts. Only add an API when multi-user requirements demand authentication, quotas and isolation. Imported data is untrusted; parsing must not load plugins or execute code. Operational reliability belongs to the analyzer; workflow recovery belongs to the source application. No claim of production readiness before security, scale and recovery validation.

## 24. Testing strategy

Unit/contract tests cover typed IR, exact timestamps, malformed IDs/data, duplicates, cycles, orphan parents, explicit dependencies, nesting and sensitive-content exclusion. Property tests cover serial sums, parallel maxima, deterministic ordering and graph-weight monotonicity. CLI integration tests use files and clean stdout/stderr. M2 adds queue conservation, analytic cases and termination/failure invariants; M3 adds differential parity; M4 adds held-out replay. Test unsupported cases explicitly rather than silently accepting them.

## 25. Benchmark and evaluation strategy

[Methodology](docs/benchmarks/methodology.md) separates analysis microbenchmarks, simulation throughput, application runs and deployment validation. Every result records date, commit/dirty state, hardware, OS, Python/compiler/CUDA where relevant, lock hash, workload hash/version, seed, run count and raw samples. Unknown/not-applicable fields stay explicit. Performance thresholds are not enforced on noisy shared CI. Validation records p50/p95/p99, throughput, queue wait and resource saturation over multiple loads, with intervals and missingness. Targets in the adversarial review are prospective acceptance criteria, not results.

## 26. Local hardware plan

User-reported envelope: Ryzen 9, RTX 4060, 16 GB RAM. Exact SKU/VRAM must be measured before hardware claims. M1 uses CPU, files and a single Python process; bound input bytes/spans. Native compiler/GPU services are absent. Later profiles: analysis-only, simulator-only, one calibration service, GPU-calibration-only. Avoid running observability and application stacks together unless memory permits.

## 27. Cloud validation plan

Azure is a later controlled intervention environment: provision small CPU topology, freeze prediction before load test, measure held-out changes, export raw results and destroy resources. Credits (~$200 Azure, ~$30 Lightning) are user-reported and may expire; do not depend on them. Kaggle only for permitted short offline experiments. AWS excluded. Paid actions/credentials require human involvement. IaC must include budget ceiling, TTL, region/SKU availability checks and verified teardown; Container Apps scaling behavior itself must be modeled if selected. No cloud resources are created now.

## 28. Open-source and community strategy

Choose Apache-2.0 for new project code/docs, with an explicit patent grant and permissive distribution terms; MIT was the simpler alternative. Preserve historical inputs with their original attribution. No competitor implementation is imported. [Dependency inventory](docs/dependency-licenses.md) separates installed runtime/dev dependencies from reviewed integrations. Contributions should first add privacy-reviewed traces, validation cells and reproducible profiles. A hardware profile needs provenance and calibration envelope, not just a GPU name. The concrete utility is better capacity reasoning with modest compute, not a sweeping social-impact claim.

## 29. Security and privacy

Default allowlist excludes prompts, messages, retrieved documents, URLs, SQL text, tool arguments/results, span names, status messages and events. Retain structural IDs and selected performance metadata only. This reduces content exposure but is not a complete anonymizer: model/service identifiers may contain user data. No remote upload, telemetry, trace execution or external tool call occurs during analysis. Reject nonfinite numbers and bounded input violations; do not echo raw payloads in errors. Share only reviewed synthetic or consented artifacts.

## 30. Roadmap

M0 research/spec/ADRs/tooling; M1 trace -> execution IR -> DAG analysis; mandatory M1.5 real trace compatibility; M2 Python DES; M3 conditional C++ port; M4 calibration; M5 constrained optimization; M6 one real agent adapter; M7 conditional CUDA calibration; M8 Azure validation; M9 capacity regression CI. [ROADMAP.md](ROADMAP.md) gives acceptance gates. Measurements and preregistration must precede predictive claims.

## 31. Risks

Unidentified service demand, missing synchronization, clock skew, biased sampling, distribution drift, heavy tails, correlated branches, optimizer error exploitation, scope creep and a rapidly converging competitor landscape. Mitigations are explicit unknowns, bounded models, held-out interventions, abstention and upstream-integration reversal gates. A fast simulator with no measured predictive validity is not a successful project.

## 32. Unresolved questions

Which non-coding workload has controllable non-LLM bottlenecks and repeat users? What is the minimal sufficient calibration budget? Can trace metadata describe synchronization without invasive instrumentation? Does a generic engine outperform a custom core on effort and fidelity? What intervals actually cover intervention error? Which public name is appropriate? These are open; none blocks the deterministic foundation.

## 33. ADR index

See [docs/adr](docs/adr/README.md): 0001 thesis; 0002 IR; 0003 OTel; 0004 language boundary; 0005 DES; 0006 optimizer; 0007 provenance; 0008 storage; 0009 adapters; 0010 hardware; 0011 cloud; 0012 CLI/public API. ACCEPTED applies to the bounded M1 decision, not all future mechanisms. Unjustified future choices remain PROPOSED.

## 34. References

Primary research URLs and dates are collected in [competitive landscape](docs/research/competitive-landscape.md); schema sources and snapshot hashes in [OTel mapping](docs/design/otel-mapping.md). Main precedents: [AgentServeSim v3](https://arxiv.org/html/2606.09613v3), [AISimulate](https://github.com/ai-dynamo/aisimulate), [Vidur](https://arxiv.org/abs/2405.05465), [PerfSim](https://arxiv.org/abs/2103.08983), [WfCommons](https://github.com/wfcommons/WfCommons), [SimPy](https://simpy.readthedocs.io/en/latest/), [OTLP](https://opentelemetry.io/docs/specs/otlp/), [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). Historical documents are sources of prior decisions, not fresh verification of vendor claims.
