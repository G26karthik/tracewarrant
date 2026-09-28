# Minimum instrumentation contract (execution schema 0.2)

The 2026-09-29 real capture gate found that ordinary PydanticAI spans are useful for observed envelopes but insufficient to identify resource contention. No dependency is inferred from span ordering, parentage, links or operation names. A content-free custom wrapper around owned pool boundaries supplied the missing facts in the controlled workload. Adoption cost in a third-party production application is unmeasured.

All attributes below are **project extensions**, not OTel conventions. Retain them on atomic work/attempt spans. Optional means UNKNOWN when absent, not a default. IDs are deployment-local labels (1–128 characters); never put user content in them. All timestamps use integer Unix nanoseconds in one clock domain. Across machines, establish synchronization error separately; the current compiler rejects conflicting intervals instead of correcting clocks.

| `workload_lab.` suffix | Type / semantics |
| --- | --- |
| pool / queue | string / independent occupied resource and its admission queue |
| capacity | integer 1–1,000,000 / configured slots, not inferred utilization |
| enqueued_ns | timestamp / request offered to admission queue |
| acquired_ns | timestamp / slot ownership begins |
| service_start_ns / service_end_ns | timestamps / active operation boundaries within occupancy |
| released_ns | timestamp / slot becomes reusable, including cancellation cleanup |
| cancel_requested_ns | timestamp / observed cancellation request, not proof of immediate release |
| external_wait_ns | duration / directly measured wait without a declared occupied pool |
| attempt_group / attempt | string / positive integer; same logical operation and distinct attempt index |
| outcome | completed / failed / timeout / cancelled / unknown |

Within-span lifecycle boundaries must be ordered: enqueue <= acquire <= service start <= service end <= release. Partial observations are retained, but only enqueue+acquire identify queue time, and acquire+release identify occupied time (`service_ns` legacy field). The latter is **not CPU time or intrinsic service demand**. Partial failure/cancellation records must not be treated as completed service samples. Conflicting legacy explicit components are rejected. External wait is not added to pool occupancy. Each span represents at most one contiguous acquisition of one pool; multi-pool, suspension/reacquisition and processor sharing need split nodes or a future version.

Use `depends_on` between atomic spans for completion prerequisites. Fan-out shares a predecessor; join declares every required completed predecessor. Retries are distinct attempts with explicit backoff nodes. A failed attempt can finish before a retry begins: finish-to-start means terminal completion, not successful outcome. A root `graph.complete=true` asserts all selected work and edges were captured; it cannot prove that the application instrumented everything. Nested spans remain containers. Cross-trace dependencies, streaming overlap and asynchronous children outliving containers remain unsupported.

To fit contention later, also supply an experiment manifest: application/workload version, hardware/deployment, pool configuration, arrival schedule, capture window, all offered session outcomes and sampling policy. Pool IDs are scoped to this deployment, not globally unique. Trace spans alone cannot prove complete occupancy across other processes. Unknown queue/service, clock skew, sampled-out slow work, unobserved provider queues and shared outages remain unidentifiable without further measurement.

Privacy: importer and local framework exporter allowlist structural/performance fields, excluding names, prompts, messages, URLs, SQL, arguments/results, status descriptions and events. Labels/trace IDs can still identify users and are not anonymized. Maximum JSON nesting is 64, file default 16 MiB, spans 50,000; numeric limits and bounded labels apply before graph construction. No imported trace invokes code/tools or uploads data.
