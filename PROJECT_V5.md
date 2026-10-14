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

Status: scope and harness being prepared. Canonical design:
[preregistration](docs/v5/preregistration.md).
