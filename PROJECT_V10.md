# V10 — usable observation collection and framework integration

New scope authorized by the maintainer on 2026-10-14: inspect the codebase,
research a concrete next requirement and plan it in line with the product intent.
V3–V9 and the verified 0.7.1 release remain complete; their results/tags are not
reopened. This document scopes a new increment, not an unfinished old milestone.

## Concrete requirement

A developer using a standard traced Python agent should be able to collect
explicit, content-free dependency and owned-resource evidence through a small
supported interface, then run TraceWarrant inspection without copying one of our
application-specific collectors. Unsupported parts must remain visible.

The current product validates supplied evidence well, but observation production
lives in examples. Fresh Pydantic AI 2.51.0 TestModel telemetry contains five spans
(one workflow, two model calls, two tools), with explicit dependency coverage 0/1
and queue/occupancy coverage 0/4. Its native limiter emits one wait span with four
attributes that the current allowlist does not retain. Waiting alone does not
identify release or full occupancy. [Research](docs/v10/research.md),
[recorded probe](docs/v10/integration-research.json).

## Recommended deliverable

A small framework-neutral observation recorder for explicitly owned operations,
an optional OpenTelemetry bridge, and a pinned Pydantic AI integration example.
Start with caller-owned Python/asyncio resources; preserve execution semantics.
Record actual enqueue/acquire/release, known outcomes, opaque pool identities and
caller-declared dependency edges. Treat native framework telemetry as a companion
source, not proof of hidden synchronization or backend service demand.

Do not auto-assert graph completeness from a span tree. Completeness must be
explicitly enabled for a closed, fully instrumented scope; missing/dropped work
disables it. Caller-owned work and nested framework containers need explicit
roles to avoid double counting. Uninstrumented operations remain in coverage
denominators. Existing wire names and 0.7.1 interfaces remain compatible.

The default recorder must capture no prompts, outputs, tool arguments, SQL, URLs,
raw exception messages or arbitrary labels. Enforce bounded events/buffers and
opaque identity rules at collection, not only at report rendering. Optional OTel
imports belong outside the dependency-free core import path. No exporter/provider
or network connection should be installed globally as a side effect.

## Finite gates

| Gate | Acceptance |
| --- | --- |
| A: requirement and compatibility research | Source/test/example inventory; pinned primary-source review; fresh locked-framework probe; alternatives and resource budget recorded |
| B: neutral collection primitive | One supported boundary/lease interface works in a plain asyncio application; explicit roles/edges; monotonic comparable clocks; fixed globally scoped pool identity; bounded output and no payload capture |
| C: framework integration | Pydantic AI example delegates to the same primitive; actual acquisition/release and optional known edges appear in inspection; uninstrumented spans stay partial/unsupported; TestModel prevents service calls |
| D: qualification and distribution | Failure/cancellation/timeout/retry and capacity-conflict cases; no token leaks or swallowed exceptions; raw-to-inspect integration; measured overhead/memory with an uninstrumented baseline; isolated installed compatibility and hosted checks; release only after gates pass |

Before B, pin the first supported integration version to the tested 2.51.0.
Its limiter uses task-owned CapacityLimiter tokens, whereas reviewed upstream
uses a semaphore and permits different-task release. Support each deliberately;
do not monkeypatch or replace either limiter's scheduling behavior. Additional
versions are separate compatibility cases, not assumed from matching names.

Cancellation before acquisition must not fabricate a release. Cancellation after
acquisition must preserve the actual owner's cleanup and original exception.
Local release is not remote backend cancellation. A capacity change requires a
new explicitly separated configuration cohort; do not rename pools to conceal a
contradiction. Cross-host clocks and remote acknowledgements remain out of scope.

## Resources and limits

Design for a 16 GiB system-memory machine. The current session actually reports
33,536,831,488 physical bytes (about 31.2 GiB), 16 logical CPUs and an RTX 4060
Laptop with 8,188 MiB VRAM. Initial integration probes need no model/GPU service.
Use a provisional 2 GiB process working-set ceiling and bounded batches; reduce
parallelism when free memory is low. Measure actual peak memory/overhead in D;
these are design targets, not demonstrated performance claims. System RAM does
not change the GPU's reported VRAM.

## Status and stopping rule

Status: **A complete.** The reproducible probe passed on clean committed source
`40cff5b545b66a64f083c051733afd8c75dd0fd5` with locked dependencies.
[Clean-source probe](docs/v10/framework-probe.json). B/C/D are planned, not
implemented or released. Package remains 0.7.1.
No new public version is chosen merely to label a plan.

If the useful evidence can be supplied entirely through an existing framework
hook with a documented recipe, ship that smaller integration instead of a broad
SDK. If lifecycle evidence cannot be obtained honestly, retain the refusal and
narrow scope. Measure the benefit as reduced collector duplication and correct
supported/refused observations, not as a model victory or external adoption.

A later independent application/intervention study needs its own question,
quality-qualified cohort, frozen predictions and cheap baseline. It is not
unlocked by more RAM or by a successful TestModel integration. Preserve FRAMES
and HotpotQA failures. No dashboard/backend, new simulator, optimizer, CUDA,
paid/cloud service, outreach or automatic rerun of failed studies is required.
