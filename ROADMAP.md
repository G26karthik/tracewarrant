# Gated roadmap

Continuation authorization permits autonomous progress through evidence gates. Status is updated by validation records, not aspirations.

Current delivery: M0/M1 and [M1.5 trace compatibility](docs/validation/milestone-1.5.md) pass locally. M2 is the next gate. See [current status](PROJECT_STATUS.md).

| Milestone | Deliverable | Exit gate |
| --- | --- | --- |
| M0 | Research, adversarial review, V2, 12 ADRs, repo conventions, CI, benchmark methodology | Sources linked, old files preserved, unsupported claims removed, reproducible environment |
| M1 | Local OTLP -> typed IR -> explicit DAG -> critical path/contribution report | Hand-solvable serial/fork/join/nesting cases; malformed/cyclic/partial/privacy tests; deterministic JSON; bounded parser |
| M1.5 | Actual controlled and PydanticAI traces, observed lifecycle contract | PASS: explicit joins, real queueing, unknown missing components, privacy and semantic tests |
| M2 | Python DES with pools, queues, distributions, retry/failure/branch semantics | Event/conservation invariants, D/D/1 and M/M/1 validation, SimPy cross-check, deterministic seeds |
| M3 | Conditional C++20 engine/bindings | Python semantic parity, measured speed/memory benefit on a declared event workload; reconsider using upstream engine first |
| M4 | Calibration and held-out replay | Envelope, missingness/censoring, uncertainty, calibration cost and validation errors published; narrow thesis reassessed |
| M5 | Exact tiny replica planning then heuristics | Exhaustive oracle agreement, constraints/abstention, independent finalist validation, Pareto candidates |
| M6 | One non-coding real agent workload adapter | Model/retrieval/browser/API steps, branch/retry examples, framework-neutral export, quality floor |
| M7 | Conditional CUDA hardware characterization | Service-model need demonstrated, real-serving anchors, profile provenance, CPU/vendor baselines |
| M8 | Small Azure experiment | Preregistered prediction, held-out concurrency/resource intervention, measured effect, costs and teardown evidence |
| M9 | Capacity regression CI | Validated performance model, uncertainty-aware diffs, version/mix control and controlled false-positive rate |

M1 tasks: define execution semantics before schema; import safe fields; validate graph; implement deterministic algorithms; add representative fixtures and CLI; test edge cases; run CPU harness and publish raw measurements with limitations. No simulate/plan command stubs implying working features.

Success requires the full measurement -> model -> simulated intervention -> real intervention -> verified improvement loop. M1 is a useful analytical foundation, not proof of that thesis. A local controlled service experiment may precede formal M6 if required to invalidate assumptions early; no multi-framework expansion is authorized by this roadmap.
