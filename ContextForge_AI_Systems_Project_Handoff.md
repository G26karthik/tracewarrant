# ContextForge — AI Systems Flagship Project / Handoff

**Snapshot:** 28 September 2026  
**Purpose:** State transfer for a temporary chat. A future AI should be able to continue without asking the user to repeat objectives, constraints, hardware, or the prior project discussion.

## 1. User objective

Build **one serious, defensible, end-to-end production-grade project** that can represent the user as an **AI Engineer / ML Systems / AI Infrastructure Engineer**. It must show:

- algorithmic ability;
- system design;
- production thinking;
- Python + C++ + CUDA;
- distributed-systems reasoning;
- agentic/multi-agent systems, context engineering, harness/loop engineering;
- tool calls and Agent Skills where justified;
- current open-source tooling where it is genuinely useful;
- rigorous “why this, not competitor X?” reasoning for every important dependency.

It is **not a coding-agent project**.

Every major choice must have an **ADR** with: context, candidates, evaluation criteria, benchmark/evidence, decision, consequences, what is sacrificed, and a **reversal trigger**.

## 2. Resource envelope

- CPU: AMD Ryzen 9 (exact SKU unspecified).
- GPU: NVIDIA GeForce RTX 4060. Treat VRAM conservatively; assume 8 GB until verified.
- RAM: 16 GB.
- Kaggle: free compute allowance as available; use for offline experiments/reproducibility, not production.
- Lightning AI: about $30 credit/free allowance reported by user; reserve for short GPU-heavy experiments.
- Azure: about $200 credit + education/free-service benefits reported by user. Do not make architecture dependent on the credit.
- AWS: suspended; exclude from baseline.

The 16 GB RAM limit means services must run in **profiles**, not all permanently at once.

## 3. Decision: one flagship, with parts of the previous three ideas

### Core: ContextForge
A **budget-aware, durable multi-agent runtime and context compiler**.

### Narrow Chronos component
Workflow-aware scheduling: critical path, deadlines, predicted service time, tenant fairness, cancellation, optional cache/prefix affinity.

### Narrow Sentinel component
Reliability/chaos/evaluation: failure injection, trace-based diagnosis, recovery verification, SLO tests.

Do **not** build three disconnected products. ContextForge is the coherent flagship.

## 4. Portfolio thesis

Do not present ContextForge as “a multi-agent application.” Present it as an **AI systems runtime**. A non-coding multi-agent workload is used to stress/evaluate the runtime.

The agents are the workload. The runtime is the project.

## 5. Reference workload: ResearchOps (non-coding)

A technical research / due-diligence task requiring multi-source retrieval, document analysis, calculations, contradiction handling, tool calls, verification, and sourced synthesis.

Logical roles:

1. Planner — typed workflow DAG + evidence requirements.
2. Retriever — evidence candidates + provenance.
3. Evidence analyst — claims, freshness, conflicts.
4. Verifier — attempts falsification and requests more evidence.
5. Synthesizer — final output from accepted evidence.

A “role” does not imply a separate process. Split into independent services only when isolation/scaling/ownership/model specialization justifies it.

## 6. Central abstraction: Context IR

```text
ContextPackage
├── task_spec
├── workflow_state
├── evidence[]
│   ├── source_id / provenance
│   ├── retrieval scores
│   ├── freshness
│   ├── permissions
│   ├── contradiction links
│   └── token_cost
├── selected_skills[]
├── exposed_tools[]
├── memory_items[]
├── policy_constraints
├── budget
│   ├── tokens
│   ├── latency
│   ├── monetary_cost
│   └── risk
├── cacheable_prefix
└── compilation_trace
```

Compiler passes:

```text
retrieve candidates
→ normalize/provenance
→ permission filter
→ deduplicate/cluster
→ freshness + contradiction analysis
→ utility estimation
→ budgeted context selection
→ skill selection
→ tool-surface selection
→ ordering/prompt packing
→ ContextPackage
→ model/agent execution
```

This IR is a major contribution because context construction becomes replayable, measurable, and replaceable.

## 7. Algorithmic work

### 7.1 Budgeted context selection

Treat context as constrained optimization:

```text
maximize    Σ utility(i)·x_i
          + λ1·coverage(S)
          - λ2·redundancy(S)
          - λ3·staleness(S)
          - λ4·risk(S)

subject to  Σ tokens(i)·x_i ≤ B_tokens
            predicted_latency(S) ≤ B_latency
            predicted_cost(S) ≤ B_cost
            permissions(i) = allowed
            required evidence categories covered
```

Implement/compare:
- top-k;
- greedy utility/token;
- MMR;
- submodular/coverage-aware greedy;
- dynamic programming / ILP exact oracle on small instances;
- optional learned utility model later.

### 7.2 Retrieval
- dense + sparse/BM25 hybrid candidate generation;
- RRF and weighted fusion;
- cross-encoder or late-interaction rerank;
- MMR / clustering for diversity;
- provenance, version, freshness retained end to end.

### 7.3 Tool/Skill surface minimization
Do not expose all tools/procedures on every call.

Baselines:
- rules/metadata;
- embedding selection;
- budgeted set cover minimizing schema-token cost;
- optional contextual bandit later.

### 7.4 Scheduler (Chronos-lite)
DAG scheduling for LLM/retrieval/tool steps:
- FIFO baseline;
- EDF;
- shortest predicted service time;
- critical-path-aware + fairness + cancellation;
- optional prefix/cache affinity.

Use a **stub model server** for high-volume scheduler experiments.

### 7.5 Cache algorithm (optional)
Compare LRU/LFU/TinyLFU-like policies with an eviction score based on **expected recomputation cost**, using trace replay.

### 7.6 C++ / CUDA
Recommended project-owned low-level component:
**batched late-interaction MaxSim reranker** for top-N candidates as a PyTorch C++/CUDA extension.

Compare:
- PyTorch reference;
- optional Triton;
- custom C++/CUDA;
- CPU C++ vectorized baseline.

Profile with Nsight. Measure crossover points, bandwidth, occupancy, batch/candidate/token dimensions. A negative result is acceptable if explained.

Optional research branch: TurboQuant-style compressed scoring. Do not force it into production.

## 8. Protocol boundaries

### MCP
Use at **capability boundaries**: search, document retrieval, SQL/analytics, calculator, experiment service, external tools.

ContextForge decides which MCP tools are visible to a step. Carry trace context, deadlines, auth context, and idempotency where applicable.

Do not use MCP to replace ordinary internal function calls.

### Agent Skills
Use Skills for **procedural knowledge**, not executable API duplication.

Examples:
- source-triangulation;
- claim-verification;
- document-table-extraction;
- statistical-sanity-check;
- report-synthesis.

Treat Skills as versioned/tested artifacts and measure activation precision/recall and context savings.

### A2A
**Deferred.** Add only when at least two agents become independently deployed systems with separate lifecycle/ownership/scaling. Logical multi-agent roles do not justify A2A.

## 9. System architecture

```text
HTTP API / UI
      |
      v
Temporal durable workflow
      |
  +---+-----------------------------+
  |                                 |
  v                                 v
Context Compiler               Execution Scheduler
Python                         Python → C++ if profiling justifies
  |                                 |
  +---- PostgreSQL                  +---- local/remote LLM backend
  +---- Qdrant (candidate)          +---- MCP tool calls
  +---- Skill/policy registry       +---- cancellation/backpressure
  |
ContextPackage
  |
  +---- C++/CUDA reranker

All components → OpenTelemetry
              → Langfuse (AI traces/evals)
              → Prometheus/Grafana (systems metrics)
```

### State ownership
- Workflow correctness: **Temporal**
- App metadata/config/audit: **PostgreSQL**
- Retrieval index: **Qdrant candidate**, rebuildable
- Raw objects: filesystem locally, Azure Blob in cloud
- Cache: process-local first; Redis only if distributed measurements justify it
- AI traces/evals: Langfuse + raw benchmark artifacts; never workflow truth

## 10. Technology decisions

### Vector database
**Default candidate: Qdrant. Primary baseline: PostgreSQL + pgvector.**

Why Qdrant is attractive for this project:
- hybrid/multi-stage Query API;
- multivectors / late interaction;
- self-hosted distributed mode;
- quantization options including current TurboQuant support;
- advanced retrieval experiments without a Milvus-scale deployment.

Competitors:
- pgvector: operational simplicity and transactional co-location; wins if advanced features do not justify another service.
- Weaviate: strong hybrid + cluster features; more platform surface than initial needs.
- Milvus: excellent very-large-scale/cloud-native architecture, but oversized for local 16 GB and the corpus scale.
- Chroma: excellent fast prototype, but less aligned with the project’s retrieval/index experimentation goal.
- Pinecone: strong managed platform, but managed-only core would hide infrastructure and create cloud dependence.

**Decision gate:** benchmark Qdrant vs pgvector on the real corpus. If Qdrant’s advanced path does not materially improve the target metric, choose pgvector.

### Durable orchestration
**Temporal default.**
Reason: real durable replay/recovery; do not spend the project recreating a workflow engine.

LangGraph is a comparison/optional agent-layer tool, but avoid two competing persistence models.

### Inference
- vLLM default local backend when model fits GPU;
- SGLang comparison for prefix-heavy workloads;
- TensorRT-LLM optimization path, not milestone 1;
- NVIDIA Dynamo = reference/optional distributed routing experiment, not core on one 4060;
- Ray Serve LLM = optional cloud distributed-serving comparison.

### Observability
- OpenTelemetry = source instrumentation standard;
- Langfuse = AI-specific traces/evals;
- Prometheus/Grafana = systems;
- Phoenix = open-source alternative if Langfuse becomes too heavy.

### Messaging/cache
- Kafka: no initial requirement.
- NATS JetStream: optional only if a separate replayable event plane appears; Temporal task queues already dispatch workflow work.
- Redis: defer until multiple replicas demonstrate need for a shared cache/rate-limit state.
- Azure Service Bus: cloud comparison only.

### Deployment
- Local: Docker Compose + native GPU process.
- Local Kubernetes: kind/k3d only for a deployment milestone.
- Azure CPU/control plane: Container Apps Consumption where useful.
- AKS: short-lived final proof, not always-on.
- IaC: OpenTofu/Terraform-style destroy/recreate.

## 11. Hardware-aware run profiles

- DEV-LITE: API + Temporal dev + Postgres + Qdrant + small model.
- RETRIEVAL: vector DB + embedding/rerank + benchmark harness.
- GPU-KERNEL: CUDA benchmark only.
- OBSERVE: core + Langfuse/OTel OR systems dashboard stack as needed.
- CHAOS: stub model + core services + failure injector.

Do not make the system depend on a large local model. Verify actual 4060 VRAM. Keep model-provider interface OpenAI-compatible and swappable.

Cloud:
- Azure: CPU services, multi-replica tests, short AKS proof.
- Lightning: only experiments needing a larger GPU.
- Kaggle: offline preprocessing/evaluation.
- AWS: excluded.

## 12. Production requirements

Must demonstrate:
- timeouts, bounded retries/jitter;
- cancellation and deadlines;
- idempotency;
- backpressure/admission control;
- tenant concurrency/fairness;
- schema migrations;
- versioned embeddings and re-index path;
- AuthN/AuthZ;
- least-privilege tool exposure;
- secrets handling;
- prompt-injection-aware tool policy;
- distributed trace propagation;
- metrics/logs/traces;
- health/readiness + graceful shutdown;
- rollout/rollback;
- cost budgets/rate limits;
- unit/property/integration/contract/load/chaos/regression tests;
- dependency pinning and supply-chain scan.

Failure demos:
- kill worker mid-tool-call;
- tool timeout;
- DB/vector-store restart;
- duplicate response/event;
- slow model endpoint;
- stale/bad evidence;
- concurrent tenants.

## 13. Evaluation

Metrics:

- retrieval: Recall@k, nDCG/MRR, hybrid/rerank gain, latency, memory;
- compiler: task success, context precision/recall, token count, redundancy, evidence coverage, compile p95, cost/success;
- tool/skills: selection precision/recall, schema tokens, unnecessary/unsafe exposure;
- workflow: grounded claim rate, loop count, tool calls, retries, latency, cost;
- scheduler: p50/p95/p99, deadlines, fairness, throughput, utilization, canceled work;
- native: speedup, latency/QPS, bandwidth/occupancy, correctness, CPU/GPU crossover;
- reliability: recovery success/time, duplicate effects, SLO violations.

Required ablations:
- dense vs sparse vs hybrid vs reranked vs late interaction;
- top-k vs MMR vs budgeted/coverage-aware selection;
- FIFO vs EDF vs SPT vs ContextForge scheduler;
- PyTorch vs optional Triton vs custom CUDA;
- monolithic prompt vs normal RAG vs all-tools agent vs compiled ContextForge.

Store raw benchmark outputs in machine-readable files and record hardware/software/model/dataset/git versions.

## 14. Phased roadmap

0. Spec + benchmark harness + ADR template + tracing skeleton.
1. Context compiler v1.
2. Temporal durability.
3. MCP tools + Skills.
4. Qdrant/pgvector retrieval ADR with benchmarks.
5. C++/CUDA reranker.
6. Scheduler.
7. Production hardening/load/chaos.
8. Azure cloud proof.
9. Architecture/benchmark report + demo + postmortems.

**Scope rule:** add technology only in response to a measured requirement.

## 15. Required ADRs

1. Why runtime, not another agent app.
2. Vector store comparison.
3. Temporal vs LangGraph vs custom.
4. vLLM vs SGLang vs TensorRT-LLM.
5. Context IR design.
6. Retrieval fusion/reranking.
7. Context optimization solver.
8. MCP boundary.
9. Skills policy.
10. Why A2A is deferred.
11. OTel + Langfuse boundary.
12. Why Kafka/Redis/NATS are initially absent.
13. HTTP vs gRPC boundaries.
14. Compose vs Container Apps vs AKS.
15. CUDA kernel acceptance criteria.

## 16. Key interview questions the repo must answer

- Why Qdrant rather than pgvector?
- Why Temporal rather than LangGraph?
- Why multi-agent?
- Why MCP?
- Why Skills?
- Why no A2A yet?
- What exact hot path does CUDA accelerate?
- What happens if a worker dies after an external side effect?
- How does tool authorization resist prompt injection?
- How do you know context engineering improved quality/cost?
- How would it scale beyond one GPU?
- What did you intentionally *not* build, and why?

## 17. Immediate next decision

The next session should **not** start by selecting another framework.

It should define:
1. the exact evaluation workload/corpus;
2. the first version of the `ContextPackage` schema;
3. the benchmark acceptance criteria for the vector-store ADR.

Those choices make every later architecture decision measurable.

## 18. State-transfer paragraph

> We are designing a flagship portfolio project called ContextForge for an AI Engineer / AI Infrastructure trajectory. It is a non-coding agent runtime and context compiler, not a chatbot. Core contributions: typed Context IR; budgeted context/tool/skill selection; hybrid retrieval + reranking; durable Temporal workflow; workflow-aware scheduler; MCP tool boundaries; Agent Skills; optional/deferred A2A; C++/CUDA late-interaction reranker; OTel + Langfuse observability; production/chaos/load evaluation. Hardware: Ryzen 9, RTX 4060, 16 GB RAM; Kaggle free allowance; about $30 Lightning AI; about $200 Azure education/free credit; AWS currently unavailable. Build one project, not three: absorb narrow Chronos scheduling and Sentinel reliability ideas into ContextForge. Every major tool choice must have an ADR, competitors, benchmark evidence, consequences, and a reversal trigger. Qdrant is only the default candidate; pgvector is the primary baseline. Cloud is for burst/distributed proof, not a dependency.

## 19. Current-source references checked 2026-09-28

- [R1] Qdrant Hybrid/Multi-Stage Queries — https://qdrant.tech/documentation/search/hybrid-queries/
- [R2] Qdrant Distributed Deployment — https://qdrant.tech/documentation/scaling/distributed_deployment/
- [R3] Qdrant Quantization / TurboQuant — https://qdrant.tech/documentation/manage-data/quantization/
- [R4] Qdrant Multivectors / late interaction — https://qdrant.tech/course/essentials/day-5/colbert-multivectors/
- [R5] pgvector README — https://github.com/pgvector/pgvector/blob/master/README.md
- [R6] Weaviate Hybrid Search — https://docs.weaviate.io/weaviate/search/hybrid
- [R7] Milvus Architecture — https://milvus.io/docs/architecture_overview.md
- [R8] Chroma Introduction — https://docs.trychroma.com/docs/overview/introduction
- [R9] Pinecone Index/Search Overview — https://docs.pinecone.io/guides/index-data/indexing-overview
- [R10] Temporal Durable AI — https://docs.temporal.io/ai
- [R11] LangGraph Persistence — https://docs.langchain.com/oss/python/langgraph/persistence
- [R12] MCP 2026-07-28 release — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- [R13] Agent Skills overview — https://agentskills.io/home
- [R14] A2A current spec — https://a2a-protocol.org/latest/specification
- [R15] vLLM Prefix Caching — https://docs.vllm.ai/en/latest/design/prefix_caching/
- [R16] NVIDIA Dynamo KV-aware routing — https://docs.nvidia.com/dynamo/dev/knowledge-base/modular-components/router/routing-concepts
- [R17] Ray Serve LLM — https://docs.ray.io/en/master/serve/llm/index.html
- [R18] Langfuse OTel — https://langfuse.com/integrations/native/opentelemetry
- [R19] Arize Phoenix — https://arize.com/phoenix/
- [R20] Azure Container Apps plans — https://learn.microsoft.com/en-us/azure/container-apps/plans
- [R21] Azure Monitor OTel — https://learn.microsoft.com/en-us/azure/azure-monitor/containers/opentelemetry-options
- [R22] NATS JetStream — https://docs.nats.io/learn/jetstream/
- [R23] Google Research TurboQuant — https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/

External projects evolve. Pin benchmarked versions and update ADRs when dependencies materially change.
