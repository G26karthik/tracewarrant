# Historical design reconstruction

Both supplied handoffs were read completely on 2026-09-28. The DOCX has 24 tables, no drawing objects or tracked revisions, plus a header/footer. Its expanded comparison/reversal tables, resource profiles, failure examples and interview evidence reinforce the Markdown architecture. No conflicting current architecture was found between them. The bundled renderer failed because `soffice.exe` is unavailable; page-layout fidelity was not visually verified. No DOCX modifications were made.

Original thesis: ContextForge compiled evidence, tools, skills and memory into a typed ContextPackage under token/latency/cost/risk budgets, then ran ResearchOps through durable Temporal execution. Chronos supplied bounded scheduling policies, Sentinel supplied failure/recovery experiments. PostgreSQL owned metadata, candidate Qdrant owned a rebuildable index (pgvector was the baseline), and Langfuse/OTel supplied observations. The low-level proposal was a MaxSim reranker, with profiling as the acceptance gate. None of these proposals was implemented in the supplied workspace.

| Historical idea | V2 disposition and trigger |
| --- | --- |
| ContextPackage/compiler | Optional future workload transformation; no core context engine |
| Context/token budgets | Per-node workload features and task-quality constraints |
| ResearchOps roles | One later non-coding validation application, not separate services by default |
| Retrieval/reranking; Qdrant vs pgvector | Calibration workload alternatives if measured bottlenecks justify them |
| Tool/skill selection | Procedure metadata and optional what-if transformations |
| MCP/A2A | Tool metadata/import adapter; no new gateway; A2A still deferred |
| Chronos policies | Simulation scheduler policies with FIFO baseline |
| Sentinel | Fault/retry/cancellation scenarios plus real validation |
| Temporal | Source/runtime adapter; no workflow durability ownership in the analyzer |
| Langfuse/Phoenix | Optional data integration, not mandatory storage/UI |
| C++ hot path | Proposed DES core after reference semantics and throughput evidence |
| CUDA MaxSim kernel | Historical experiment retained; current CUDA direction is measured service-curve calibration |
| Azure and IaC | Short validation experiments with teardown; no inherited AKS requirement |
| ADRs, ablations, negative results | Retained as governing engineering practice |

The original root documents remain historical records, byte-for-byte. Their recommendations and dated external feature claims are not automatically current dependencies. See `historical-sha256.json` for preservation evidence.
