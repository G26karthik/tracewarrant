# Observation Contract 1.0

This is a claim-support contract, independent of any simulator. The current OTLP binding is the preserved IR 0.2 `workload_lab.*` allowlist; integrations can construct a `Dataset` directly. UNKNOWN never means zero. `inspect_observations` reports coverage over all atomic spans unless a narrower denominator is stated. Non-resource work can lower coverage: absence of a pool does not establish that no resource was used.

| Claim | Required evidence | Interpretation / limit |
| --- | --- | --- |
| Causality | explicit `depends_on`, atomic/container `role`, one root `graph_complete` assertion | Identifiable with instrumentation; parentage and elapsed overlap imply no dependency. Finish-to-start only. |
| Fan-out/fan-in | explicit branches and every join predecessor; complete topology assertion | Counts of declared edges; missing topology remains incomplete. |
| Acquisition/release | `acquired_ns`, `released_ns`, stable globally scoped `pool` | Observed owned occupancy. Half-open intervals; zero durations consume no interval area. |
| Queue wait | `enqueued_ns`, `acquired_ns` on one clock and attempt | Acquisition minus enqueue; absence is UNKNOWN. |
| Service interval | `service_start_ns`, `service_end_ns` | Observed interval, not CPU/GPU demand; internal waits and sharing need additional instruments. |
| Finite capacity | pool identity plus `capacity` and configuration epoch | Reported configuration, checked against overlapping observations; changing capacity without epoch is unsupported. Current binding has no epoch, so split cohorts. |
| Retry | `attempt_group`, consecutive positive `attempt`, terminal `outcome`, explicit dependencies/backoff spans | Attempts partly observable; no hidden retry inference. Missing sequence/duplicate attempts flagged. Sampling completeness needed to prove retry absence. |
| Cancellation | `cancel_requested_ns`, outcome, owned release, remote acknowledgement if claimed | Local cancellation and local release do not prove backend work stopped. |
| Timeout | deadline, terminal outcome, release/cancel semantics | Current IR records outcome but not deadline or remote acknowledgement; full semantics unsupported. |
| External wait | explicit `external_wait_ns` plus application placement/overlap semantics | Direct reported duration only; never inferred from unexplained wall time. |
| Inference client occupancy | client acquisition/release | Identifiable; includes hidden backend queue/scheduling. Intrinsic inference service demand is NOT IDENTIFIABLE here. |
| Calibration | complete representative offered population, outcomes/censoring, stable hardware/configuration/task cohort, demand identification | Calibratable under explicit assumptions; a single conforming trace does not suffice. |
| Prediction/capacity | frozen model, envelope and independent controlled intervention | Unsupported by trace conformance alone. |

Timestamps must share an explicit comparable clock domain; the existing binding assumes this and rejects contradictory order/nesting/edges. Cross-host skew correction and async child spans outside parent intervals require a future importer, not silent repair. Record capture/sampling policy, start/end boundary and offered population outside traces; missing entire traces cannot be detected from a file. Root completeness is a trusted collector assertion with structural checks, not a proof that every operation was instrumented.

`workload-lab inspect input.json` emits JSON with per-claim observed/eligible coverage, absent field counts, required extensions, contradictions and refusal reasons. A strict importer error fails the file; valid-looking subsets are not certified from a structurally invalid dataset. Synthetic-origin inputs remain labeled synthetic and never gain measured predictive support.

Content-free defaults: no prompts, responses, reasoning, documents, SQL, URLs, user names, raw service/tool names or exception payloads in inspection reports. Source SHA-256 and numeric counts provide lineage. Input allowlisting cannot sanitize a secret deliberately placed in an allowed label; collectors must use opaque IDs. Pool identities must distinguish independent instances across hosts and restarts. Never merge equal display names as proof of shared capacity.

Support categories and provenance are orthogonal. Directly observable means the collector supplied an observation, not that the collector is trustworthy. Identifiable means the required boundary instruments permit a stated derivation. Calibratable means assumptions and representative cohorts are still required. Not identifiable and unsupported remain explicit refusals; no confidence score combines them.
