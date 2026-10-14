# Evidence-gated roadmap

## Active V5 application qualification

The maintainer requested the next real-application stage on 2026-10-14.
[V5](PROJECT_V5.md) preregisters one public HotpotQA local QA application, with
official answer scoring and fixed disjoint samples. Performance-model and cheap
baseline comparison is conditional on useful task quality. A failed quality
gate closes the study honestly; the toolkit and 0.4.0 release remain complete.

## Completed V4 workflow increment

Autonomous continuation authorized and delivered 2026-10-14. [PROJECT_V4.md](PROJECT_V4.md) defines five completed gates: A strict manifest/contained inputs; B explicit quality/performance policy; C reports/CI/portable verified bundles; D retained real-evidence replay and installed-package checks; E documentation, hosted CI and verified 0.4.0 experimental release. [Closeout](docs/v4/public-release-0.4.0.md). No required engineering gate is queued; production/adoption or a harder scientific study would need a new evidence-based scope.

## Completed V3 experimental scope

Active direction: [PROJECT_V3.md](PROJECT_V3.md). The standalone planner roadmap is superseded. Its full historical state remains in V2 and tag `research-pilot-1`; this roadmap does not resume M3/M5/M7/M8/M9.

| Stage | Deliverable | Evidence / status |
| --- | --- | --- |
| V3-A | Preserve pilot; refresh primary-source overlap; observation contract and ADRs | 64-file preservation manifest; V3 research; ADR-0016/0017 |
| V3-B | Runnable content-free conformance and explicit refusals | Controlled, PydanticAI and external FRAMES sources; real binding defect detected |
| V3-C | Model-neutral schema, freeze, evaluation, first-class baselines | Independent SimPy, fixed-delay and ordinal utilization producers; integrity/unit/provenance tests |
| V3-D | Preregistered external workload/intervention study | Executed: 16 calibration + 48 held-out sessions. Heuristic matches model; exact-answer gate fails. Hard-decision workload remains unestablished. |
| V3-E | Reproduction, package and evidence audit | Complete: offline byte-exact evaluation, preservation/trace audit, 150 tests per hosted matrix job, installed qualification and verified public prerelease; see release closeout |

Potential future work, requiring a separate scope, is an independently motivated application with a defensible quality measure and a nontrivial intervention choice, or upstream integration of the already useful conformance/validation interfaces. Do not select by whether simulation wins. Preserve failed studies and include a cheap baseline. External adoption is not established by running our executor on external tasks. This is not unfinished work for the completed experimental release.

The completion patch uses the delegated public name **TraceWarrant**, corrects four validation/output edge cases, and adds local Linux/Windows and installed-distribution qualification. [Completion report](docs/v3/completion-0.3.1.md), [ADR-0018](docs/adr/ADR-0018-controlled-comparisons-and-release-qualification.md).

C++, CUDA, optimization and cloud deployment require a measured V3 product need. None is queued. The public repository and experimental `v0.3.1` prerelease are published and verified; private security reporting is enabled. [Release closeout](docs/v3/public-release-0.3.1.md). Local use needs no credentials or paid resources.

[External results](docs/v3/results.md), [reproduction](docs/v3/reproduce.md), [current status](PROJECT_STATUS.md), [frozen V2 conclusion](FINAL_PROJECT_REPORT.md).
