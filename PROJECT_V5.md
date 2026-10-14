# V5 — real-application quality qualification

Authorized by the maintainer's continuation request on 2026-10-14. This is a
bounded application study, not a new planner or a mandatory package release.
V4 and its immutable public 0.4.0 release remain complete.

Question: can an ordinary local multi-document question-answering application
meet a declared task-quality floor before we interpret performance decisions?
HotpotQA distractor is selected for its externally authored questions and
published answer scoring. No candidate was timed or scored before selection.

## Gates

1. Pin dataset/scorer, fixed disjoint samples, code and predeclared criteria.
2. Run eight feasibility questions through actual SQLite evidence storage,
   context assembly and local Llama 3.1 8B inference. No artificial delays.
3. Only if feasibility qualifies, calibrate and freeze whole-workflow and cheap
   baseline predictions before collecting any held-out interventions.
4. Preserve all results, run offline verification and publish a scoped conclusion.

Failure of gate 2 closes this study as a negative application qualification.
It must not trigger prompt tuning, task replacement, an easier quality threshold,
invented measurements or a performance-model success claim. A qualified workload
and external adoption are separate; operating our own executor is not adoption.

**Status: completed with a negative application-qualification result.** All
eight requests completed; 4/8 exact matches and mean answer F1 0.541667 failed
the predeclared 6/8 and 0.75 thresholds. Official scorer parity checked all
eight answers locally. All eight retained dependency/resource traces replay.
Calibration and held-out performance work were not unlocked. This is a scoped
study closeout, not a qualified application or production-ready product.

| Gate | Evidence / disposition |
| --- | --- |
| Design and selection | Preregistration, fixed disjoint source rows, pinned dataset/scorer and committed collector before any scored request |
| Feasibility | Executed eight real questions; completion passed, both quality thresholds failed |
| Conditional performance study | Not unlocked under the predeclared stopping rule; no forecasts, calibration, model victory or held-out intervention result invented |
| Verification and conclusion | Official scorer parity, content-free public trace/score evidence, offline population/source/lease/clock replay and all-result report |

Canonical [design](docs/v5/preregistration.md), [results](docs/v5/results.md),
[reproduction](docs/v5/reproduce.md), [verification](docs/v5/verification.json).
