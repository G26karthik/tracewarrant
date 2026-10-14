# Final requirement acceptance map

This map uses the maintainer's V3 pivot requirements as the product boundary;
the superseded planner roadmap is not an outstanding backlog. V3 implementation
and scientific records remain preserved. The V4–V8 workflow additions are also
closed. Final V9 integrity/package/public-release qualification passed. The
agreed experimental scope is complete, with **zero required remaining stages**.
[Verified public closeout](public-release-0.7.1.md), [acceptance record](acceptance.json).

| Original V3 requirement | Delivered evidence |
| --- | --- |
| Multiple trace sources and a clear observation contract | [Contract](../v3/observation-contract.md); controlled, PydanticAI and FRAMES fixtures; `tests/test_v3_conformance.py`; installed source checks |
| Correctly refuse unsupported performance claims | `src/workload_lab/conformance.py`, `validation.py`; tests for missing/contradictory telemetry and unknown dimensions; original misspelled graph assertion stays refused |
| At least two independent model sources share the format | SimPy, fixed-delay and ordinal utilization producers; [model-neutral artifact contract](../v3/artifacts-and-validation.md); `tests/test_v3_validation.py` |
| Freeze predictions and independently evaluate real measurements | Preserved `docs/v3/frames-frozen/` and `frames-evaluation/`; `freeze`/`evaluate`; raw-byte hashes and exact offline replay |
| First-class simpler baselines | Fixed-delay/utilization competitors; explicit eligibility and baseline decisions in evaluation; absent baseline prevents added-value claims |
| Reveal when complex modeling adds value and when it does not | Held-out FRAMES result `no_added_decision_value`; [results](../v3/results.md); comparison tests cover model/baseline wins and ties |
| Reproducible, content-free by default | Strict bounded formats, diagnostics and escaped local reports; privacy/refusal tests; public scalar-only studies; fresh installed qualification and 64-file preservation audit |
| At least one external/non-author workload tested | 72 FRAMES sessions, including 16 calibration and 48 held-out; later eight-task HotpotQA feasibility completed with failed quality floors |
| Explicit limitations and identifiability boundaries | Contract/evaluation provenance, UNKNOWN/support/refusal and limitation fields; honest [FRAMES](../v3/results.md) and [HotpotQA](../v5/results.md) negative results |
| Useful toolkit after planner thesis is abandoned | Dependency-free conformance/freeze/evaluation plus quality/CI/portable evidence interfaces, multiple independent producers; simulator remains optional |

All ten engineering criteria have supporting implementation/evidence. This does
not convert poor answer quality or an easy intervention choice into a scientific
success. The stronger model-superiority outcome was explicitly not required for
honest completion. Caller-declared evidence is not independently authenticated.

| Subsequent bounded scope | Delivered state |
| --- | --- |
| V4 reusable validation jobs | Strict contained snapshot, explicit gates, CLI exits, standalone reports, portable evidence; verified 0.4.0 release |
| V5 real application prerequisite | Fixed HotpotQA sample/scorer; eight completed, 4/8 exact and mean F1 0.541667; study closed negative under stopping rule, performance study not unlocked |
| V6 standalone quality checks | Strict scalar sample/policy, offered-population multiple gates and HTML/JSON; verified 0.5.0 |
| V7 policy/population binding | Exact plan/receipt bytes, identities and roster membership; verified 0.6.0; retrospective example chronology remains unauthenticated |
| V8 portable quality evidence | Bound/unbound snapshots, checksum and JSON/HTML replay, refusals and installed/public-download qualification; verified 0.7.0 |
| V9 final acceptance | Reproduced performance-HTML defect fixed; 292 tests per hosted matrix job, fresh installed/hosted and all ten public 0.7.1 downloads/replays/refusals passed |

Final checks: full tests/lint/format, isolated installed wheel/source bytes and
both commands, conformance sources, frozen evaluation, strict/performance/quality
workflow, bound/unbound bundles and rehashed false reports, protected files/tags,
exact-source/tag CI, all public asset hashes and fresh downloaded installed replay.
The release closeout binds these passed checks to clean immutable source
`ecc0ebe1c224a9345b355d38ef44a0a0c6f1ac61`. No required check or feature stage remains.

Remaining claims outside completion: production readiness, independent adoption,
authenticated measurements/chronology, and model superiority over cheap baselines.
No extra feature stage is implied by any of them. Historical planner ADRs still
marked PROPOSED are superseded research, not queued implementation. [Final decision](../adr/ADR-0024-final-acceptance-and-rendered-evidence.md),
[completion checkpoint](../../PROJECT_COMPLETION.md).
