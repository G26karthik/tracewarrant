# Competitive landscape

## 2026-09-29 refresh before M1.5 / reference DES commitment

Reopened primary AgentServeSim v3, AISimulate AgentX guide, Vidur, PerfSim, SimGrid introduction, WRENCH, SimPy scheduling and the OTel GenAI repository. The reviewed boundaries below still apply; this was a capability refresh, not independent reproduction. Prefer established inference engines for any future inference service model. SimPy remains the independent queue baseline; a small explicit reference kernel is justified only to test our termination/event contracts, not as engine novelty. No evidence here establishes a unique product.

[PydanticAI current instrumentation](https://pydantic.dev/docs/ai/integrations/logfire/) supports OTel without a hosted backend and content suppression; [TestModel](https://pydantic.dev/docs/ai/guides/testing/) enables local tool execution with provider requests disabled. Chosen integration: pinned pydantic-ai-slim 2.51.0 plus OTel SDK 1.45.0, optional dependency group. The installed API uses an Instrumentation capability; an older `Agent(instrument=...)` invocation failed and was corrected against installed source. The actual trace has no pool/acquisition/join data, consistent with the minimum-contract gap. No framework internals were patched. See [M1.5 evidence](../validation/milestone-1.5.md).

Research date: 2026-09-28. Scope: primary repositories, papers, maintainer documentation, CNCF/OTel, Hugging Face dataset cards, and commercial product documentation. This is a bounded desk review, not a reproduction of competitors' experiments. Absence below means **not established in reviewed material**, not proof of absence. Repository activity is a snapshot; a recent push is not proof of support. Raw API metadata is in [repository-evidence.json](repository-evidence.json).

## Finding and change to the thesis

The broad thesis already has serious competition. AgentServeSim, AISimulate, and PerfSim overlap with execution modeling, what-if analysis, or planning. Merely adding tool durations to an inference simulator is insufficient. We will investigate **calibrated contention across independently constrained tools, retrieval, databases, and inference**, with trace evidence and held-out intervention validation. Whether this warrants a standalone product remains an experimental question. Reassess upstream integration before M3.

No complete, directly interchangeable open-source implementation of that narrower loop was established in this review. This is not a novelty claim. In particular, AISimulate's fast-moving agentic support warrants continued comparison before any public differentiation claim.

## Review records

Each record gives activity/license; abstraction, inputs and outputs; modeled and unestablished scope; simulation/planning/optimization; trace/OTel, agent/inference/distributed support; overlap and classification.

### AgentServeSim — DIRECT COMPETITOR to the broad thesis

[Paper v3, 2026-09-05](https://arxiv.org/html/2606.09613v3). Active research revision; an attributable implementation repository and its code license were not established by the searches. Paper license is not a code license. Abstraction: agent program and cross-turn state. Inputs: ordered model calls, token shapes, tool gaps, arrivals, policies. Outputs: completion/serving metrics and policy comparisons. Models causal successor release, dispatch and KV retention; reviewed design represents tools as time gaps, rather than independently calibrated browser/database resource pools. Simulation and policy search: yes; infrastructure planning: partial. Trace input: yes; OTel importer: unestablished. Agent and inference support: yes; distributed inference resources: yes. Closest overlap is program-level counterfactual execution. Our proposed difference is non-LLM queue contention and intervention validation; neither program identity nor causal release is our invention. Reported paper accuracy has not been independently reproduced here.

### AISimulate — DIRECT COMPETITOR to broad planning; NEAR COMPETITOR to narrowed scope

[Repository](https://github.com/ai-dynamo/aisimulate), [AgentX guide](https://github.com/ai-dynamo/aisimulate/blob/main/docs/agentx-quickstart.md), [license](https://github.com/ai-dynamo/aisimulate/blob/main/LICENSE). Active; Apache-2.0 with separately attributed third-party material. Abstraction: serving engine/deployment and traffic. Inputs: hardware/backend configuration, performance data and agentic traces; outputs: predictions and deployment recommendations. Models inference workers, KV/cache and inter-worker transfer. Independently fitted tool-worker queues and arbitrary OTel application graphs were not established. Simulation/planning/optimization: yes. Trace: yes, including Weka; canonical OTel importer: unestablished. Agent support: experimental AgentX; inference/distributed serving: yes. The AgentX guide explicitly limits qualification to functional behavior, not hardware accuracy. Integrate a future inference ServiceModel instead of duplicating this engine. Differentiation must be demonstrated against this baseline, not assumed.

### AIConfigurator — INTEGRATION TARGET / RESEARCH PRECEDENT

[Repository](https://github.com/ai-dynamo/aiconfigurator). Apache-2.0; maintenance-only transition to AISimulate is documented, despite recent activity. Abstraction: inference configuration/performance database. Inputs: model, GPU, backend, workload shapes; outputs: serving estimates and configuration search. Models inference primitives and backend behavior, not established whole-application resource queues. Simulation: performance modeling; capacity planning/optimization: yes. Trace support: workload dependent; arbitrary OTel: unestablished. Agent application support: not its reviewed boundary; LLM and distributed inference: yes. Overlap is hardware calibration and deployment search. Preserve as precedent, prefer the successor for future integration research.

### Vidur — NEAR COMPETITOR / INTEGRATION TARGET

[Repository](https://github.com/microsoft/vidur), [paper](https://arxiv.org/abs/2405.05465). MIT; non-archived, last API push 2026-08-24. Abstraction: LLM request/batch/replica. Inputs: profiles, request traces and configuration; outputs: serving latency, throughput and deployment search. Models inference scheduling and parallelism; independently contended heterogeneous tool services are not established. DES/capacity/optimization: yes. Trace input: yes; arbitrary OTel: unestablished. Agent-specific execution: not its core reviewed abstraction; LLM/distributed inference: yes. Overlap is simulation plus cost/capacity search. Candidate inference oracle, not a reason to build a second inference engine.

### PerfSim — NEAR COMPETITOR

[Repository](https://github.com/michelgokan/perfsim), [paper](https://arxiv.org/abs/2103.08983). GPL-2.0; non-archived but last API push 2025-06-10, so current maintenance is uncertain. Abstraction: microservice chain and hosts. Inputs: user-supplied service models/topologies and scenarios; outputs: service-chain performance. Models CPU/network/resource allocation; the repository explicitly excludes the performance-model construction component. DES: yes; capacity what-if: yes; turnkey SLO/cost optimization: unestablished. Trace-related modeling workflow: yes; canonical OTel ingestion: unestablished. Agent/LLM-specific semantics: unestablished; distributed systems: yes. This is a strong whole-system precedent. Our potential contribution is extracting and qualifying agent models, not inventing heterogeneous simulation. No source code is copied into this permissively licensed project.

### SimGrid — RESEARCH PRECEDENT / possible engine alternative

[Repository](https://github.com/simgrid/simgrid), [license documentation](https://simgrid.org/doc/latest/community.html). Active mirror; LGPL family, inspect per-component terms before integration. Abstraction: distributed computation, communication and platform. Inputs: application/platform models and traces; outputs: simulated execution and performance. Broad distributed resource simulation; no reviewed turnkey agent trace calibration or SLO planner. DES: yes; planning/optimization can be built on it. Trace/replay: yes; OTel: unestablished. Agent and LLM support requires modeling; distributed support: core. Our engine must justify its narrower semantics and portability against using this mature substrate.

### WRENCH — RESEARCH PRECEDENT

[Repository](https://github.com/wrench-project/wrench). Active, LGPL-3.0. Abstraction: workflow/application and cyberinfrastructure services on SimGrid. Inputs: platform, workflow and controller code; outputs: simulated workflow execution. Models heterogeneous compute/storage/batch/cloud services; automatic agent calibration not established. DES: yes; capacity/policy exploration: programmable; turnkey optimizer: unestablished. Workflow input: yes; OTel: unestablished. Agent/LLM semantics: custom; distributed support: yes. Overlap: workflow/resource co-modeling. Prefer an adapter or upstream contribution if custom engine value does not survive benchmarks.

### WfCommons — RESEARCH PRECEDENT

[Repository](https://github.com/wfcommons/WfCommons). Active, LGPL-3.0. Abstraction: scientific workflow instance/recipe. Inputs: workflow execution data; outputs: standardized instances, analysis, synthetic workflows and benchmark artifacts. Models workflow structure and workload characteristics, rather than an agent-specific serving engine. Simulation: integration with simulators; capacity/optimization: downstream. Trace ingestion: supported workflow formats; OTel: unestablished. Agent/LLM-specific support: unestablished; distributed workflow support: yes. Strong precedent for separating observed executions from generative workload recipes; v0 must not claim to standardize all workflows.

### SimPy — RESEARCH PRECEDENT / M2 baseline

[Maintainer documentation](https://simpy.readthedocs.io/en/latest/). Maintained documentation, MIT. Abstraction: event/process/resource. Inputs: Python model; outputs: events and model-defined metrics. Models generic queues/contention but supplies no domain calibration. DES: yes; capacity/planning/optimization: user code. Trace/OTel: custom. Agent/LLM/distributed abstractions: custom. Closest overlap is the simulation mechanism; domain contracts and validation must supply our value. Use it as a correctness baseline before committing to a custom native engine.

### Langfuse — ADJACENT / INTEGRATION TARGET

[Repository](https://github.com/langfuse/langfuse). Active; MIT core, enterprise directories separately licensed. Abstraction: observed LLM/agent execution and evaluation. Inputs: instrumented traces, evaluations and prompts; outputs: traces, metrics, comparisons. Observes heterogeneous agent calls but offline resource-contention simulation and infrastructure synthesis were not established. Simulation/capacity optimizer: not established. Trace/OTel: yes; agent/LLM: yes; distributed visibility: yes. Overlap is ingest/analyze and regression UX. A static latency report alone provides insufficient differentiation; import/export should avoid mandatory self-hosted infrastructure.

### Phoenix — ADJACENT / INTEGRATION TARGET

[Repository](https://github.com/Arize-ai/phoenix), [license](https://github.com/Arize-ai/phoenix/blob/main/LICENSE). Active; Elastic License 2.0, not a permissive dependency. Abstraction: traces and evaluations; inputs: instrumented agent/LLM executions; outputs: inspection, datasets/evaluations. Observability, not a demonstrated resource synthesis loop. Simulation/capacity optimizer: unestablished. Trace/OTel/OpenInference: yes; agents/LLM/distributed trace visibility: yes. Overlap is diagnostics. Keep integration at exported data boundaries; do not inherit an old handoff's generic “open-source alternative” label as a license decision.

### OpenTelemetry and Grafana — ADJACENT / INTEGRATION TARGET

[OTel GenAI](https://github.com/open-telemetry/semantic-conventions-genai), [Grafana](https://github.com/grafana/grafana). Active ecosystems; OTel Apache-2.0; Grafana OSS AGPL-3.0 with separately licensed offerings/components. Abstraction: telemetry and dashboards. Inputs: spans/metrics/logs; outputs: observed queries, alerts and visualizations. Models no executable counterfactual workload by itself. Simulation/SLO-constrained infrastructure optimizer: not established in these boundaries. Trace/OTel: yes; agent/LLM conventions available; distributed observability: core. Overlap is almost all M1 user-visible analysis. Adopt OTel and earn the later modeling contribution.

### k6 — ADJACENT / VALIDATION TARGET

[Repository](https://github.com/grafana/k6). Active, AGPL-3.0. Abstraction: executable load test. Inputs: scripts, arrivals/concurrency and deployed endpoints; outputs: observed latency/throughput/threshold outcomes. Exercises real systems, including agents when scripted. Offline simulator/planner/optimizer: not its reviewed boundary. Trace/OTel ecosystem integration: available, not arbitrary graph compilation. Agent/LLM-specific semantics: custom; distributed load: supported ecosystem. Overlap: direct capacity evidence. A small real sweep is the baseline we must beat on calibration-plus-exploration cost, not something to replace.

### OpenCost — ADJACENT / INTEGRATION TARGET

[Repository](https://github.com/opencost/opencost). Active CNCF project, Apache-2.0. Abstraction: infrastructure cost allocation. Inputs: Kubernetes/cloud resource and pricing data; outputs: cost allocation/metrics. Models infrastructure costs rather than causal agent execution. DES: no reviewed facility; capacity optimization: downstream. Trace/OTel workload graph ingestion: not established. Agent/LLM: not specific; distributed cluster costs: yes. Useful future CostModel data source; unnecessary in local M1.

### IBM Turbonomic — NEAR COMPETITOR in commercial planning

[Plan scenarios](https://www.ibm.com/docs/en/turbonomic-for-gov?topic=future-setting-up-plan-scenarios). Current commercial documentation; proprietary terms. Abstraction: application/resource supply and demand. Inputs: monitored environments and what-if changes; outputs: plans and resource actions. Infrastructure planning and optimization: yes; internal simulation implementation: not established. Monitoring integration: yes; arbitrary OTel agent graph importer: unestablished. Agent/LLM-specific semantics: unestablished; distributed infrastructure: yes. Strong substitute for infrastructure teams; our proposed advantage is a local inspectable model of application resource boundaries and public validation artifacts, not generic rightsizing.

### DSPy — ADJACENT

[Repository](https://github.com/stanfordnlp/dspy). Active, MIT. Abstraction: LM program/modules and quality optimizers. Inputs: program, examples and metric; outputs: optimized program parameters. Models/evaluates program quality and costs through execution, not demonstrated heterogeneous infrastructure queues. DES/capacity planning: unestablished; program optimization: yes. Traces: framework-specific/integrations; OTel boundary: not established here. Agents/LLMs: yes; distributed capacity model: unestablished. Context and tool policies may later be workload transformations, with task-quality constraints.

### IBM ContextForge — ADJACENT / naming conflict

[Repository](https://github.com/IBM/mcp-context-forge). Active, Apache-2.0. Abstraction: gateway/registry/proxy for tools and agent protocols. Inputs: service registrations/requests; outputs: mediated requests and telemetry/management. Models operational gateway controls, not offline calibrated infrastructure synthesis. Simulation/capacity optimizer: unestablished. Trace/OTel integration: documented ecosystem; agent/tool support: yes; LLM serving simulation: no reviewed facility; distributed services: gateway boundary. Closest overlap: MCP telemetry, not the proposed core. Do not reuse ContextForge as the public name.

### llm-d inference simulator — ADJACENT / VALIDATION TARGET

[Repository](https://github.com/llm-d/llm-d-inference-sim). Active, Apache-2.0. Abstraction: configurable model endpoint. Inputs: request traffic and latency/cache configuration; outputs: synthetic responses and timing. Simulates inference-facing behavior in real time; not a complete agent digital twin. Simulation: yes, endpoint emulation; planning/optimization: external harness. Trace inputs: datasets/configuration; OTel compiler: unestablished. LLM: yes; agent and distributed infrastructure: test integration. Useful validation stub baseline, but synthetic endpoint agreement cannot prove real inference fidelity.

## Search log and coverage limits

Queries included “AgentServeSim agent serving simulator”, “agent workflow trace calibrated simulator capacity planning”, “trace driven microservice simulator”, “LLM inference capacity planner”, “agent capacity planning simulator github”, “OpenTelemetry GenAI agent spans”, and naming queries on GitHub, PyPI and npm. Followed primary links from arXiv and Hugging Face. Inspected repository README/license/activity and the latest AgentServeSim revision rather than relying on older search snippets. Additional discoveries: [Frontier](https://github.com/NetX-lab/Frontier), [Simthesizer](https://arxiv.org/abs/2608.24650), and [distributed search simulation](https://github.com/amazon-science/Distributed-Search-Engine-Simulator). These require deeper reproduction if they become implementation baselines; no capability claims are based solely on search snippets.

[AgentTrace](https://huggingface.co/datasets/pagarsky/agent-trace) offers execution/resource telemetry, but its coding/command workloads are unsuitable as the project's primary non-coding demonstration. Dataset card license is Apache-2.0 subject to upstream task terms. [Multi-benchmark OTel traces](https://huggingface.co/datasets/DiscoPosse/agent-llm-traces) is a candidate for format inspection, not a validated workload or redistribution authorization. No dataset was downloaded or incorporated. Transcript datasets often lack resource capacities, enqueue times and causal synchronization, so they cannot alone calibrate a twin.

## Naming disposition

ContextForge collides with IBM and [other GitHub projects](https://github.com/simonecamerano/contextforge), [PyPI](https://pypi.org/project/contextforge-repo/) and [npm](https://www.npmjs.com/package/@contextforge/cli) usage. Agentplan is already a [GitHub project](https://github.com/fraction12/agentplan) and [PyPI package](https://pypi.org/project/agentplan/); an [agentplan CLI](https://github.com/niklas-schmidt-dev/agentplan) also exists. Reject both for this product. Use **Workload Lab** / `workload_lab` strictly as an internal codename; no package reservation or publication. Trademark clearance remains unperformed because no public name is being selected. Before naming, check relevant jurisdictions, registries and common usage using the [USPTO search guidance](https://www.uspto.gov/trademarks/search/comprehensive-clearance-search-similar-trademarks) and applicable national registries. Registry availability alone is not clearance.
