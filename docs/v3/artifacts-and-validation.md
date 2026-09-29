# Simulator-neutral artifacts and evaluation 1.0

[JSON Schema](../../schemas/validation-artifact-v1.schema.json) is emitted by `workload-lab schema`. JSON Schema 2020-12 consumers can validate structure without installing this package. Python adds cross-field constraints documented here: identity uniqueness, outcome conservation, UNKNOWN/null consistency, ordered intervals, complete ranking groups and valid UTC dates. Tests cross-check the fixed vocabulary against `jsonschema`; the runtime uses no external dependencies. Schema is defined in `artifact_schema.py`, exported as JSON, and tested for consistency.

The core validator imports neither simulation nor calibration. Models are data producers; no plugin code or arbitrary schema references execute. Framework adapters map into the observation IR. IDs are bounded opaque tokens, never prompts or documents. Counts and values must be finite, nonnegative and bounded. Unknown fields, duplicate JSON keys, nesting over 64 and files over 16 MiB are rejected. Evaluation additionally bounds total input bytes and comparison count. Output files are created exclusively.

## Artifacts

- **Prediction:** workload ID; model ID/version/role/method; SHA-256 input lineage; numeric/categorical calibration envelope; assumption and unsupported-dimension IDs; scenario/configuration/comparison-group identities; predicted metrics and provenance; intervals with confidence/prediction/range meaning; bottlenecks; optional tied ordinal rankings; declared extrapolation dimensions.
- **Protocol:** scenario universe, primary metric, minimize/maximize direction, material relative difference, minimum sample count and baseline requirement. Commit it before calibration/intervention according to the study design. The toolkit cannot decide the right threshold or enforce an external quality metric unless it is represented.
- **Freeze receipt:** creation timestamp plus exact-byte hashes of protocol and every prediction. Publish/commit this before intervention collection. Byte changes, including whitespace, invalidate it. It is tamper evidence, not authentication, a timestamp authority or proof that a producer did not peek at outcomes.
- **Measurement:** matching workload/configuration/scenarios; collection start/end; exact freeze hash; raw lineage; metrics/provenance/intervals; offered/completed/failed/censored counts; limitations. The caller computes statistics over a declared population and must preserve raw observations. Core evaluation never relabels ESTIMATED or SIMULATED data as MEASURED.

Metric identity includes ID, unit, statistic and population. Supported generic statistics cover mean/p50/p95/p99, throughput rates, utilization fractions, queue time and counts. No implicit conversion between milliseconds/seconds or completed/all-offered populations occurs. UNKNOWN has a null value. Missing or insufficient observations produce a reason, not a zero error. Relative error against zero is null even when absolute error is zero. Signed error is predicted minus measured.

An interval's coverage is containment of the independently observed point statistic. The report preserves interval kind/level/method and measured uncertainty. This is not automatically predictive coverage of individual requests or a significance test. Tail adequacy is experiment-specific; preregister sufficient counts or make tails UNKNOWN.

Rankings compare only the primary metric inside the same declared comparison group. A pair is material when `abs(a-b)/max(abs(a),abs(b))` meets the preregistered threshold in **every** measurement replication and directions agree. Predicted ties do not count as correct for a material pair. No qualifying pairs yields null accuracy. Ordinal-only heuristics use UNKNOWN numeric forecasts plus explicit rankings; this prevents invented baseline latency estimates.

Package 0.3.1 tightens controlled-comparison semantics: every prediction producer must declare the same `environment` for all scenarios in one comparison group. Deliberately changed variables belong in `configuration`; different environmental strata require separate groups. Measurement drift is reported and disqualifies decisions. This checks declared controls, not undisclosed confounders. Single-scenario groups can support errors but cannot establish decision value. Equal observations, including two zeros, are nonmaterial; no positive denominator floor changes relative effects at small scales.

An explicit ranking is a separate forecast and takes precedence over the numeric point ordering. If a producer intentionally ranks by an uncertainty-aware or other rule, declare it in model method/assumptions; the evaluator does not silently reconcile these forecasts. Ranking correctness and numeric errors remain separate outputs.

Baseline comparisons report identical decisions, material model/baseline wins, no material difference or insufficient evidence. Equal decisions do not imply equal numeric accuracy or prove universal equivalence. Cost, quality and economic break-even are outside this first schema unless separately modeled; keep them in the study report. A no-added-decision-value result is successful toolkit behavior.

Envelope checks compare both configuration and environment against each producer's declared bounds, retaining explicit violations and undeclared extrapolations. Absent dimensions remain UNKNOWN. No supplied envelope also remains UNKNOWN; a producer cannot become calibrated merely by omitting boundaries. Errors outside an envelope are still reported, but do not certify in-envelope or portable accuracy.

## Public path

```sh
uv run workload-lab inspect examples/traces/controlled-v1.otlp.json
uv run workload-lab check model.json
uv run workload-lab freeze --protocol protocol.json --prediction model.json --prediction baseline.json --output freeze.json
# Commit/publish protocol, predictions and receipt here, then collect independently.
uv run workload-lab evaluate --protocol protocol.json --freeze freeze.json --prediction model.json --prediction baseline.json --measurement measured-r0.json --measurement measured-r1.json --output validation.json
```

Python producers can use `validate_artifact`, `write_new`, `freeze_predictions` and `evaluate` from `workload_lab.artifacts` / `workload_lab.validation`, without adopting the DES. Each experiment must define arrival policy, cohort and clock scope, missing/censored observations, intervention costs and quality controls. This format is an experimental local convention, not an adopted industry standard.
