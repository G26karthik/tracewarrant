Status: CANONICAL V2  
Supersedes: ContextForge handoff as implementation specification  
Preserves: ContextForge handoff as historical architecture context

# Workload Lab — internal codename

Specification date: 2026-09-28; evidence update 2026-09-29. Status: Experimental / Research Prototype. Public name undecided. M1.5 and M2 pass locally; M3 assessment defers C++; M4 passes a controlled prediction pilot but general calibration remains partial; M6 supplies a real-model applicability probe. Final assessment: **PIVOT RECOMMENDED** toward instrumentation and validation (ADR-0015). Optimization/CUDA/cloud/regression gates remain unmet.

Current state takes precedence over the historical proposals below: [PROJECT_STATUS.md](PROJECT_STATUS.md). [M1.5](docs/validation/milestone-1.5.md) adds observed lifecycle fields in schema 0.2, actual concurrent traces and one optional PydanticAI integration. Ordinary framework traces remain incomplete with UNKNOWN queue/service. [ADR-0013](docs/adr/ADR-0013-observed-resource-lifecycle.md) extends ADR-0002/0003/0009 without replacing their containment/privacy principles. [Minimum instrumentation contract](docs/design/instrumentation-contract.md).

## 1. Executive summary

Investigate whether content-free observations of a heterogeneous agent workflow can support calibrated resource-contention models and trustworthy infrastructure decisions. The proposed product turns supported traces into an execution graph, separates observed facts from modeling assumptions, and eventually evaluates resource changes against held-out real runs. The central experiment is whether browser/retrieval/database limits alter capacity decisions that inference-only or fixed-tool-gap models would make.

The broad digital-twin thesis does not differentiate this project. AgentServeSim, AISimulate and PerfSim are serious precedents/competitors. Executable scope now includes analysis, reference simulation and narrow empirical calibration. A frozen controlled experiment achieved 1.70% median p95 error and 2/2 material rankings, but a utilization heuristic made the same useful choice. A real-model application exposed changing client occupancy and negligible tool demand. These results favor an instrumentation/validation toolkit; no purchase or deployment recommendation is justified. See [final report](FINAL_PROJECT_REPORT.md).

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

There are two distinct implemented objects: **observed execution instances** (schema 0.2) and explicit **generative scenarios** (schema 1). An instance contains source identity/digest/origin, normalized spans, explicit dependencies and diagnostics. A scenario contains a fixed DAG, supplied distributions, finite pools, arrival schedule, seed and input provenance; it is never automatically inferred from an arbitrary trace. Kinds remain workflow, llm, embedding, retrieval, reranker, tool, compute, database, queue, external_api, human_gate and unknown.

Parentage expresses containment; a separate edge expresses finish-to-start dependency. Never convert a parent link or generic OTel link directly to a dependency. Work nodes are atomic leaves; nested instrumentation defaults to containers, avoiding inclusive double counting. Explicit atomic work containing child spans is rejected in v0. Retries remain distinct observed nodes. Cycles, duplicate IDs, invalid timestamps and dangling declared dependencies are errors. Missing parents/sampling/topology produce incomplete diagnostics. A graph-complete flag is an instrumentation assertion, not independently verified truth.

Explicit lifecycle timestamps identify enqueue-to-acquisition queue and acquisition-to-release occupancy; absent components remain UNKNOWN. Capacity/outcome/attempt/cancellation metadata is optional and bounded. Occupancy is not CPU/GPU service demand. Generative retry/arrival policies must be supplied separately, never inferred from one observed attempt. A null queue is not zero. [IR contract](docs/concepts/workload-ir.md) and [minimum instrumentation](docs/design/instrumentation-contract.md) define the supported boundary.

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

Controlled pilot: execution cohorts -> empirical model + explicit deployment
       -> simulator -> frozen intervention forecasts -> measured interventions
       -> error report and model qualification

Gated: constrained search -> candidate + evidence -> real-workload validation
```

Python library functions own domain behavior. CLI handles paths/formatting/errors. JSON is the initial artifact boundary. No long-running service is required. [Architecture](ARCHITECTURE.md) documents implemented modules and future interfaces.

## 13. Algorithms

M1: iterative DAG validation and topological longest path, deterministic tie breaking, interval-union accounting and contribution along one tied critical path. Longest path weights are observed leaf-span elapsed times; it is a fixed-weight zero-gap model, not an identified service-demand model. Container duration is excluded. Report total work separately from wall-clock coverage; concurrent contributions must not be portrayed as an end-to-end percentage decomposition. Alternative tied paths may yield different attribution.

Implemented M2: stochastic fixed-DAG simulation, FIFO slots, queues, bounded retries, external waits, cancellation lag and empirical sampling. M/M/1 is an explicitly generated analytical validation case, never a provider default. M4 adds whole-session empirical vectors and paired sampling sensitivity. SPT/EDF/fairness, conditional topology, cache/placement, exact replica enumeration and Pareto planning remain unimplemented and gated.

## 14. C++ strategy

DEFERRED after M3 measurement: the million-event Python case takes a median 3.361 s with about 280 MB process peak; all 720 pilot forecast scenarios took 6.26 s. No current experiment bottleneck justifies C++20/pybind11 maintenance. SimPy matches tested FIFO timings exactly. Reopen native work only for a measured need, with differential parity and material benefit; start with a stable binary heap. No project-owned C++ code or native speedup claim.

## 15. CUDA strategy

PROPOSED: hardware characterization after a service model needs it. Measure bandwidth/GEMM/launch/concurrency curves and representative serving anchors, recording GPU SKU, VRAM, clocks, power, driver, CUDA, kernel source and input shape. Synthetic kernels cannot alone predict model serving. Never label RTX 4060 measurements as another GPU's profile. The old MaxSim idea remains a historical optional experiment.

## 16. OTel ingestion strategy

OTLP/JSON ExportTraceServiceRequest envelopes are the initial interchange, optionally one envelope per JSONL line. No collector endpoint, protobuf, arbitrary SDK console output or vendor export is claimed. Support case-insensitive hexadecimal IDs, integer nanosecond strings, resourceSpans/scopeSpans and typed attribute values. Preserve schema URLs as provenance; unknown content-bearing attributes/events are discarded. Input limits and strict errors prevent uncontrolled ingestion.

GenAI conventions moved to their own repository and remain development-status in reviewed agent documentation. Pin the researched mapping snapshot rather than claiming all “OTel” versions work. Standard attributes cover operations, model/provider, token counts, retrieval metadata and tool identity; resource pool capacity, queue/service decomposition, dependency completeness and retry/cancel scheduling need narrowly documented `workload_lab.*` extensions. [Exact mapping and omissions](docs/design/otel-mapping.md).

## 17. Framework integration strategy

Core imports normalized OTLP, not framework objects. One optional PydanticAI 2.51.0 path is exercised with OTel SDK 1.45.0/TestModel; its ordinary trace remains incomplete with UNKNOWN queue/service. A real local-model PydanticAI FunctionModel bridge executes a non-coding facility report workload with owned-boundary instrumentation. The bridge is experimental, not an official general Ollama adapter. No additional framework, collector or hosted observability service is required.

## 18. Storage requirements

M1: local bounded JSON/JSONL input and deterministic JSON output. No raw input copies by default. Source SHA-256 supports lineage without retaining content. Trace IDs and service labels can still be sensitive. Later Parquet for columnar cohorts, DuckDB for offline analysis, SQLite for an artifact index only when query requirements justify them. No vector DB. Immutable model/experiment manifests remain portable files.

## 19. Simulator architecture

IMPLEMENTED M2: single-thread integer-time DES with total `(time, microstep, phase, insertion_sequence)` ordering, finite FIFO pools/queues, named SplitMix64 streams and causal successor readiness. The contract was committed before implementation. Existing completion wins over its deadline; newly ready zero-time successors remain subject to that deadline. Cancellation may retain a slot until acknowledgment. Right-censored, failed, rejected and timed-out sessions remain in denominators. No tools execute. [Exact semantics](docs/design/simulation-semantics.md), [validation](docs/validation/milestone-2.md).

## 20. Optimizer architecture

PROPOSED M5: finite-domain exact enumeration for tiny replica spaces, explicit budget horizon/currency and provider limits. Evaluate service-level success probability jointly with latency; distinguish completed-only latency from timeout/failure probability. Reject uncalibrated candidates as “insufficient evidence,” not “feasible.” Search on training scenarios; verify finalists on fresh seeds/holdout runs to reduce optimizer overfitting. Return Pareto candidates and assumptions. [Optimization design](docs/concepts/optimization.md).

## 21. Calibration design

PARTIAL M4: fit complete observed fixed-DAG cohorts with stable operation alignment, direct occupied/external measurements, source IDs/counts and empirical tails. Keep load cohorts separate; preserve paired-session vectors as a sensitivity model. Reject missing/failing/censored cohorts instead of selecting successful spans. The controlled holdout is frozen and scored separately. Generic operation alignment, branch/retry fitting, shared outages, nonstationarity, censor-aware survival models and steady-state saturation remain unsupported. [Calibration](docs/concepts/calibration.md), [pilot results](docs/validation/milestone-4.md).

## 22. Reliability and failure model

Observed status/outcome is distinct from generated policy. M2 models bounded IID attempt failure, retries/backoff, timeout, cancellation lag, queue rejection and horizon censoring. Retry storms, shared outages, rate limits, worker-loss policies and external side effects are not modeled. Cancellation does not imply instant release. External waits own no undeclared pool. No simulator invokes real tools; all termination classes remain in denominators.

## 23. Production architecture

Initial product remains an offline library/CLI. Later batch workers may process immutable experiments with bounded memory and versioned artifacts. Only add an API when multi-user requirements demand authentication, quotas and isolation. Imported data is untrusted; parsing must not load plugins or execute code. Operational reliability belongs to the analyzer; workflow recovery belongs to the source application. No claim of production readiness before security, scale and recovery validation.

## 24. Testing strategy

Unit/contract tests cover typed IR, exact timestamps, malformed IDs/data, duplicates, cycles, orphan parents, explicit dependencies, nesting and sensitive-content exclusion. Property tests cover serial sums, parallel maxima, deterministic ordering and graph-weight monotonicity. CLI integration tests use files and clean stdout/stderr. M2 adds queue conservation, analytic cases and termination/failure invariants; M3 adds differential parity; M4 adds held-out replay. Test unsupported cases explicitly rather than silently accepting them.

## 25. Benchmark and evaluation strategy

[Methodology](docs/benchmarks/methodology.md) separates analysis microbenchmarks, simulation throughput, application runs and deployment validation. Every result records date, commit/dirty state, hardware, OS, Python/compiler/CUDA where relevant, lock hash, workload hash/version, seed, run count and raw samples. Unknown/not-applicable fields stay explicit. Performance thresholds are not enforced on noisy shared CI. Validation records p50/p95/p99, throughput, queue wait and resource saturation over multiple loads, with intervals and missingness. Targets in the adversarial review are prospective acceptance criteria, not results.

## 26. Local hardware plan

Verified host: Ryzen 9 8945HS, eight cores/16 logical processors; RTX 4060 Laptop GPU, 8,188 MiB reported VRAM, driver 616.56. Exact physical RAM/OS/Python are in raw benchmark metadata. Analysis and simulation use CPU only. The separate real-model probe uses an existing local Ollama service and cached Llama 3.1 8B Q4_K_M; no weights downloaded, no custom CUDA kernels. No transfer to another GPU's performance is claimed.

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

See [docs/adr](docs/adr/README.md): original 0001–0012 are preserved; 0013 accepts observed lifecycle extensions, 0014 accepts the bounded reference simulator, and 0015 records the evidence-driven narrowing. Earlier proposed scope does not imply completed features. Unjustified native/GPU/optimizer/cloud choices remain gated.

## 34. References

Primary research URLs and dates are collected in [competitive landscape](docs/research/competitive-landscape.md); schema sources and snapshot hashes in [OTel mapping](docs/design/otel-mapping.md). Main precedents: [AgentServeSim v3](https://arxiv.org/html/2606.09613v3), [AISimulate](https://github.com/ai-dynamo/aisimulate), [Vidur](https://arxiv.org/abs/2405.05465), [PerfSim](https://arxiv.org/abs/2103.08983), [WfCommons](https://github.com/wfcommons/WfCommons), [SimPy](https://simpy.readthedocs.io/en/latest/), [OTLP](https://opentelemetry.io/docs/specs/otlp/), [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0). Historical documents are sources of prior decisions, not fresh verification of vendor claims.
