# V3 result: useful validation prototype, no added model decision value established

The standalone planner remains abandoned. V3 implements a useful local conformance and model-validation path; it does not certify general infrastructure predictions. [Specification](../../PROJECT_V3.md), [schema contract](artifacts-and-validation.md), [preregistration](frames-preregistration.md).

## External study and freeze

Eight independently authored Google FRAMES tasks were selected by original row order and three-to-five-source eligibility, before timing results. Dataset revision `58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef`; exact IDs and digest are in [selection](frames-selection.json). The executor is ours; this is external task coverage, not outside adoption or an independently operated application. Oracle source URLs and limited lexical paragraph retrieval differ from a full FRAMES agent.

Actual resources: public HTML fetch/parse worker pool, retrieval worker, SQLite, and local Ollama Llama 3.1 8B client pool. No delay inflation or downloaded model. Feasibility: 8 sessions. Calibration: 16 sessions in two baseline bursts. Holdout: 48 sessions in six eight-task bursts. All completed at runtime. Prompts, answers, reasoning, documents and source URLs are absent from published telemetry; digests, counts and exact-match booleans remain.

Calibration source `85fe81c`; producer source `ca4966e`; immutable [prediction bundle](frames-frozen/freeze.json) committed at **`af36005` / `v3-frames-freeze` before held-out interventions**. Held-out source was clean at that commit. Collection start/end UTC are in [raw holdout](frames-holdout.json). Prediction hashes and protocol are checked during independent evaluation. Later validation guard improvements reject mixed units/environments; they do not change this experiment's criteria, predictions or scores.

## Measurements versus frozen forecasts

Primary mean completed-session latency, seconds; two separate replications. Eight observations per cell are insufficient for tail claims, so p95/p99 are UNKNOWN.

| Configuration | SimPy prediction | Measured repetition 0 | Measured repetition 1 |
| --- | ---: | ---: | ---: |
| BASE: fetch 1 / client 1 | 10.129 | 10.266 | 10.083 |
| FETCH2: fetch 2 / client 1 | 5.494 | 5.887 | 6.227 |
| CLIENT2: fetch 1 / client 2 | 10.129 | 10.300 | 10.150 |

SimPy's median mean-latency relative error was **1.50% over six cells**. FETCH2 errors were larger, **6.68% and 11.78%**; the median alone obscures these intervention errors. Both material pairs were correctly ordered (2/2, small denominator). The empirical 90% seed ranges contained 4/6 observed means; these are simulation ranges, not qualified confidence/prediction intervals.

The utilization heuristic also selected **FETCH2** and ordered both material pairs correctly. **No added intervention-choice value beyond that heuristic was demonstrated.** The fixed-delay model tied all choices and missed both material pair orderings. Its overall median relative error was 1.84%, illustrating that a small median error can conceal poor intervention discrimination. A tied choice set does not yield a unique decision-value comparison.

[Full neutral evaluation](frames-evaluation/validation.json) includes signed/absolute/relative errors for mean/p50 latency, finite-drain throughput, queue time and occupied fraction; interval containment; ranking denominators; UNKNOWN bottlenecks; and envelope violations. Added worker/client capacity is explicitly EXTRAPOLATED from baseline capacity-one calibration. The heuristic has ordinal predictions and null numeric forecasts, never fabricated latency. The producers share the interchange schema, not a simulator engine.

## Failed quality gate and workload qualification

The preregistered strict normalized-answer proxy passed **1/8 feasibility, 0/16 calibration and 0/48 holdout**. Every holdout cell failed the 6/8 threshold. Exact text match is not a semantic quality evaluation and may reject equivalent wording; it nevertheless failed the declared gate. No grading rule, sample or prompt was changed to rescue the result. The study establishes runtime measurements and conditional model comparisons, **not a useful research agent or quality-preserving capacity recommendation**.

Feasibility non-LLM occupancy was 69.89%, with real fetch/retrieval queues. Fetch remained the obvious constrained resource; adding client slots had little effect. This is tool-heavy but did **not** establish the requested harder case in which current utilization cannot resolve the decision. Stronger scientific success remains unmet. That fact is retained, rather than searching outcomes for a favorable model win or expanding the planner.

## Conformance found an actual instrumentation defect

The frozen executor emitted `workload_lab.graph_complete`, while the importer contract requires `workload_lab.graph.complete`. Initial inspection of the [original held-out trace](../../examples/v3/frames-heldout-base.otlp.json) refused graph completeness for all eight sessions despite explicit edges and valid resource boundaries. The first V3 contract prose also used the wrong binding name; it is corrected with this erratum.

The [explicit adapter](../../examples/adapt_frames_trace.py) renames only an existing boolean root assertion, rejects ambiguous/duplicate/current bindings and never invents one. Future collector code uses the correct key. All original telemetry and forecasts are unchanged. The [offline audit](offline-audit.json) checks all 72 sessions: original graph-completeness claims refused; 72 structurally complete graphs after the documented binding adaptation. Both views still refuse intrinsic GPU service demand and validated prediction suitability. SimPy's topology came from the declared executor structure and stage records, not an auto-calibration claim based on the malformed OTLP key.

This is direct value from conformance: valid-looking span trees did not silently become certified dependency graphs.

## Limits and disposition

Two replications, one shared workstation, variable public network/content/cache state, deterministic ordering reversed once, and a weak local answer pipeline limit generalization. Normal local source/document editing continued during collection, but no competing benchmark/model experiment was launched. Hardware/software/model identity and source hashes are in raw records. Collectors and local timestamps are not authenticated. Quality reasoning, service invariance, stable GPU capacity, monetary cost, cross-machine transfer and sustainable load remain unsupported.

Do not use this as evidence for optimizer, C++, CUDA or cloud investment. No paid API, Azure resource, publication or external message occurred. The product is a small independently usable validator; external adoption and a qualified harder workload remain open research requirements. Prefer integrations with OTel, existing evaluators and simulators, as the [refreshed landscape](research.md) recommends.
