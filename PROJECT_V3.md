# Workload Lab V3 — observation and model validation

V3 supersedes V2 as the active product direction. `PROJECT_V2.md`, `FINAL_PROJECT_REPORT.md`, commit `c0fad29` and tag `research-pilot-1` remain the frozen V2 research record. The pilot conclusion **PIVOT RECOMMENDED** is accepted, not reinterpreted.

Status: post-pilot implementation in progress, 2026-09-29. Internal name only; no public naming or release decision.

## Product question

Given telemetry and a proposed agent-system performance model, which claims are supported, which quantities remain unidentifiable, and do predictions survive controlled interventions? UNKNOWN is preferable to fabricated certainty. A baseline matching or beating an expensive model is a successful validation result.

## Smallest useful product

1. A content-free observation contract, independent of a simulator, and a conformance report over existing trace importers. Explicit dependency edges are distinct from containment. Owned resource occupancy is distinct from intrinsic service demand.
2. Versioned, bounded JSON artifacts for predictions, measurements, preregistered evaluation criteria and freeze receipts. No custom DES types, plugin loading or code execution in these formats.
3. Independent evaluation of matched scenarios/metrics, preserving provenance, unsupported dimensions, calibration-envelope violations, uncertainty and missing comparisons. No aggregate confidence score.
4. First-class cheap baselines and material intervention comparisons. Absence of an eligible baseline prevents an added-value claim.
5. A reproducible external-workload study, selected for an independently motivated non-coding task before observing intervention outcomes. Search, selection, feasibility failures and negative results are retained.

## Architecture and boundaries

Application → existing OTLP/JSONL importer → observation inspection. Any model → prediction JSON → content-addressed freeze receipt. Independent real measurements → measurement JSON. An offline validator joins explicit workload/scenario/configuration identities and reports errors, interval coverage, bottleneck agreement, ranking and envelope checks. The caller supplies the experiment design and metric semantics; a timestamp or hash alone cannot prove an honest experiment.

The Python DES remains an optional reference backend. Simple analytical/fixed-delay models must use the same validation path without importing it. Framework-specific collection belongs in examples/adapters. Existing observability, simulator and load-generation systems are preferred where they already solve the subsystem.

Content capture is opt-in outside the core. Reports omit arbitrary span names, service labels, application payloads and exception strings. Identifiers and caller-declared artifact metadata must also be sanitized at collection; allowlisting is not a universal PII detector.

## Evidence classifications

Claim support and value provenance are separate. Support: directly observable; identifiable with required instrumentation; calibratable under declared assumptions; not identifiable; unsupported. Coverage: supported, partial or unsupported, with explicit eligible and observed denominators. Provenance remains MEASURED, CALIBRATED, INTERPOLATED, EXTRAPOLATED, SIMULATED, ESTIMATED or UNKNOWN. An unsupported result retains null values and reasons.

## Acceptance stages

| Stage | Required evidence | Current status |
| --- | --- | --- |
| V3-A | frozen-record preservation, refreshed primary-source research, contract/ADRs | passed; 64 preserved files |
| V3-B | multi-source conformance, missingness/contradiction/privacy checks | passed on controlled/PydanticAI captures |
| V3-C | simulator-neutral schemas; independent model sources; freeze/evaluate CLI; baseline comparisons | interfaces tested; real producer exercise next |
| V3-D | external workload feasibility, preregistration, frozen models, real intervention measurements and all-result report | FRAMES selection and protocol committed before collection |
| V3-E | reproducible examples, tests/build, limitations, final status and coherent commits | pending |

No stage requires a complex model to win. Scientific success requires honest held-out evidence, not planner expansion. Stronger evidence would be a material decision improvement over the cheapest reasonable baseline. Do not claim uniqueness from an incomplete literature search.

Current interfaces and evidence: [observation contract](docs/v3/observation-contract.md), [artifact/evaluation contract](docs/v3/artifacts-and-validation.md), [primary-source landscape](docs/v3/research.md), [FRAMES preregistration](docs/v3/frames-preregistration.md). The first implementation passes 131 tests, including schema interoperability and a baseline beating a model. Core runtime remains dependency-free; SimPy and framework collectors are optional.

## Explicit gates

C++, CUDA, optimizers and cloud deployment require a measured V3 need. They are not scheduled. Public release requires independently reproduced behavior, a public identity/contact and packaging review. External requirements belong in `HUMAN_ACTION_REQUIRED.md`; ordinary local engineering continues autonomously.

## Preservation and traceability

New research and validation live under `docs/v3/`; previous experiment artifacts and reports are immutable. New ADRs describe current decisions without rewriting old reasoning. `PROJECT_STATUS.md` records the active phase; the final V3 report will assess each success criterion separately and identify unmet external or scientific requirements.
