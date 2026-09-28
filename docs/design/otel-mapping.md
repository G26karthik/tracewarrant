# OTLP import contract

Reviewed 2026-09-28. GenAI source snapshot: [e57c543b4889619eb2a05702471937db5119165d](https://github.com/open-telemetry/semantic-conventions-genai/tree/e57c543b4889619eb2a05702471937db5119165d). Agent conventions are development status. The [old OTel GenAI pages](https://opentelemetry.io/docs/specs/semconv/gen-ai/) redirect readers to the separate repository.

Reviewed file SHA-256: agent spans `8363cc776fa9acc09345411bb1e09c162b7df785925f35e072ab6093bd18ba97`; GenAI spans `fee65ca0862b3fcd4254bc57957314e72eaf4399390797e603f7b82be7e5d987`. These pin the research evidence; input schemaUrl is retained, not claimed to be fully supported by version.

## Wire shape

M1 accepts a JSON object with `resourceSpans`, each containing resource attributes and `scopeSpans[].spans[]`. JSONL accepts one such object per nonblank line. It does not accept arbitrary vendor exports, Python SDK console JSON, protobuf, gzip or a network receiver. IDs are nonzero hexadecimal (32 characters trace, 16 span), normalized lowercase. Parent may be absent/empty/all-zero. Nanoseconds are nonnegative integer strings or JSON integers; floats and booleans are rejected. Upper limit is uint64. Enums are OTLP integer codes. Unknown fields are discarded.

See [OTLP encoding](https://opentelemetry.io/docs/specs/otlp/#json-protobuf-encoding). A 16 MiB file and 50,000 spans are default hard limits, adjustable through library/CLI limits. Both JSON and JSONL are bounded; this is not an unbounded streaming implementation.

## Normalization table

| Source | Normalized feature | Treatment |
| --- | --- | --- |
| traceId/spanId/parentSpanId | Stable trace/node/containment IDs | Direct structural facts, not dependency |
| startTimeUnixNano/endTimeUnixNano | Exact elapsed interval | Source-reported observation; synthetic origin stays ESTIMATED |
| resource `service.name` | Service label | Allowlisted string, never a capacity |
| gen_ai.operation.name = chat/generate_content/text_completion | llm | Direct classification |
| embeddings / retrieval / execute_tool | embedding / retrieval / tool | Direct classification |
| invoke_agent / invoke_workflow / create_agent / plan | workflow | Container default, even if children missing |
| gen_ai.request.model, gen_ai.provider.name | Model/provider | Optional strings |
| gen_ai.usage.input_tokens / output_tokens | Counts | Optional nonnegative integers |
| gen_ai.usage.cache_read.input_tokens | Cached input count | Subset of input count when both supplied; do not add to total |
| gen_ai.retrieval.top_k | Candidate request size | Optional count, not actual result count |
| gen_ai.tool.name | Tool identity | Optional label |
| db.system.name, http.request.method | database / external_api fallback classification | Do not retain query, URL or headers |
| status.code | UNSET / OK / ERROR | Omit description and exception text |
| scope/resource schemaUrl | Mapping provenance | Retain string; diagnostic if supplied |
| links | None in M1 | Record ignored-link diagnostic, never assume completion dependency |
| events, input/output messages, retrieval text/documents, tool args/results | None | Discard; content is not needed for timing |

The supported fields are a deliberate subset of the [GenAI span](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md) and [agent span](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md) conventions. Metrics such as time to first token and token distributions cannot be reconstructed from a single span duration; metric/log ingestion is deferred. No heuristic classification based on human span names.

## Experimental extensions

These are project-local contracts, not OTel standard attributes. Only the selected span's attributes apply; resource attributes do not override dependency semantics.

| Attribute | Type | Meaning |
| --- | --- | --- |
| workload_lab.node.kind | string enum | Explicit normalized kind; overrides operation classification |
| workload_lab.node.role | work/container | Atomic work selection; work with children is rejected |
| workload_lab.depends_on | array of span-ID strings | Same-trace finish-to-start prerequisites between work nodes |
| workload_lab.graph.complete | boolean | Only on the unique root: assertion that selected work/dependencies describe the intended instance |
| workload_lab.queue_ns | integer | Explicitly recorded queue component within this span |
| workload_lab.service_ns | integer | Explicitly recorded service component within this span |
| resource workload_lab.data.origin | string `synthetic` | Downgrades the whole input to synthetic evidence; cannot upgrade it |

No default assumptions for capacities, rate limits, retries, side effects, branch probability, tenant/session semantics or CPU/GPU demand. Those need explicit future contracts. Retries can be represented as separate work nodes with explicit edges; no retry policy is inferred.

Completeness is revoked by missing parents, multiple roots, ignored links or dropped spans/attributes. Any complete assertion on a non-root is rejected. Workflow/container gaps remain unattributed; they are not automatically queue time. Conflicting clocks on declared dependencies are rejected, with no silent skew correction. Disconnected roots are allowed only as incomplete observations.
