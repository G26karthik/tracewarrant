# Next-phase research — 2026-10-14

## Recommendation

Make TraceWarrant practical to instrument in an existing application. The next
requirement is a supported, bounded path from actual caller-owned execution
boundaries to observation evidence. Existing validators and portable artifacts
can consume it. This is a new scope after completed V3–V9, not a correction of
their scientific conclusions. [Implementation gates](../../PROJECT_V10.md).

## Codebase findings

Reviewed the core module inventory, test/benchmark/example call paths, original
V3 contract, completed acceptance map and later release scopes. All 17 core
Python modules were indexed by purpose, definitions and raw-byte digest.
`ingest.py`, `ir.py`, `graph.py` and `conformance.py` establish the exact evidence
requirements; `validation.py`, `jobs.py` and `qualification.py` operate on supplied
artifacts rather than collecting an application's runtime lifecycle.

The application-specific collection path is duplicated across
`examples/capture_controlled.py`, `frames_workload.py` and `hotpot_workload.py`:
each writes lifecycle attributes and dependency identities itself. The packaged
API has no reusable recorder or framework bridge. The Pydantic capture example
filters content and exports standard spans, but supplies no pool leases or
declared finish-to-start graph. `tests/test_observation.py` explicitly asserts
that the framework fixture has no edges and UNKNOWN queue/service components.

Fresh local execution of the locked Pydantic AI 2.51.0/OTel SDK 1.45.0 combination
confirmed five spans, dependency coverage 0/1, queue/occupancy/capacity coverage
0/4 and inference client occupancy 0/2. A separate capacity-one native limiter
produced one wait span; none of its four attributes survive today's importer
allowlist. That is an integration gap, not a framework defect or proof that the
current importer should infer missing release/causality information.

The controlled fixture separately has dependency coverage 8/8 and client
occupancy 16/16. Queue coverage is only 44/61; capacity support is refused under
its recorded contradictions. Do not hide those denominators or overwrite that
fixture. The comparison shows that explicit instrumentation can supply evidence
and that the validator appropriately retains partial/refused results.

## Refreshed primary sources

Exact reviewed revisions and SHA256 digests are in
[integration-research.json](integration-research.json). Source text was inspected
locally in ignored research snapshots; no upstream implementation was copied into
the core. These are documentation/source comparisons, not competitor benchmarks.

| Source | Finding and decision |
| --- | --- |
| [Pydantic AI instrumentation](https://github.com/pydantic/pydantic-ai/blob/17423c0592f3a9beb648c7989a59b7652c45bae4/docs/capabilities/instrumentation.md) | Existing OTel agent/model/tool spans and content controls make it a practical first integration target. Reuse its tracing and providers. |
| [Pydantic AI locked limiter](https://github.com/pydantic/pydantic-ai/blob/39328d5b0d4cce94d513b6afcd2b3191bd5708d5/pydantic_ai_slim/pydantic_ai/concurrency.py), [reviewed upstream limiter](https://github.com/pydantic/pydantic-ai/blob/17423c0592f3a9beb648c7989a59b7652c45bae4/pydantic_ai_slim/pydantic_ai/concurrency.py) | Both expose waiting observability. The installed 2.51.0 is task-owned; upstream uses a semaphore and explicitly allows cross-task release. Pin compatibility and observe caller-owned boundaries; do not replace scheduling or infer release from a wait span. |
| [OTel GenAI agent conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/07794021bfe46e1c241408b6f55cb4354bd28318/docs/gen-ai/gen-ai-agent-spans.md) | Agent/tool vocabulary and opt-in payload fields overlap our importer. Continue standard transport and explicit content exclusion; project-specific pool/lease/graph attributes are not claimed as OTel standards. |
| [Microsoft Agent Framework observability](https://github.com/microsoft/agent-framework/blob/95feea605dbbe879f678602585c76fdb5a963b63/python/samples/02-agents/observability/README.md) | Another existing OTel integration surface. Keep the observation primitive independent of Pydantic; a second vendor integration is deferred until the first interface works. |
| [agentevals](https://github.com/agentevals-dev/agentevals/blob/618c9422ea6b3e08fccb9b94711061775f39cab3/README.md) | Already evaluates recorded OTel behavior against expected outcomes. Generic agent evaluations are crowded; keep our focus on observation support and frozen performance/intervention validation. |
| [AgentTelemetry](https://github.com/Krishnachaitanyakc/AgentTelemetry/blob/246838d474114b41e5d3d68bb327e5c462a65d92/README.md) | Has agent-specific kinds, framework adapters and privacy levels. Do not claim that content-free agent tracing is unique. The proposed helper's value must be demonstrated through the specific lease/dependency contract. |
| [AISimulate](https://github.com/ai-dynamo/aisimulate/blob/532a0235d43fbf67ab18d44963c096bb8772340d/README.md), [AgentServeSim paper](https://arxiv.org/abs/2606.09613) | Existing serving simulation/configuration work reinforces preserving model neutrality. Another serving engine is not the next requirement. An external prediction adapter can be considered after a real integration need is established. |
| [OTel tracing concepts](https://opentelemetry.io/docs/concepts/signals/traces/), [k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/) | Existing transport/context and load-test pass/fail semantics remain useful companions. Span relationships are not automatically finish-to-start resource dependencies; thresholds do not validate a forecast. |

No source review establishes that competitors lack equivalent mechanisms, and
no uniqueness or independently deployed adoption claim is made.

## Alternatives considered

| Candidate next work | Decision |
| --- | --- |
| Supported collection primitive plus first framework integration | Selected: directly evidenced collector duplication and unsupported native telemetry; useful without a model win, GPU or external account |
| Another larger-model quality/intervention study | Deferred: the preserved quality failures cannot be repaired by a hardware claim; a fresh task/model/protocol needs an independently motivated quality-qualified study |
| AISimulate/other model-specific prediction adapter | Deferred: the neutral format already has independent producers; investigate an adapter when an actual consumer needs it |
| Dashboard, trace backend or another generic evaluator | Not selected: current primary sources already provide these broad surfaces; no demonstrated product requirement |
| CUDA, optimizer or distributed capacity planner | Not selected: superseded thesis and no measured requirement; more RAM does not establish a need |

## What would count as progress

The first deliverable should let a plain asyncio application and a pinned
Pydantic application use the same small boundary interface. A reviewer can see
which actual operations gained queue/lease evidence, with correct coverage and
unchanged unsupported claims elsewhere. Explicitly controlled graph scopes can
declare real predecessor edges; ordinary auto-traced agents cannot silently gain
complete topology. Cancellation and capacity contradictions must still be refused
where evidence is insufficient. Reduce duplicated collection code and document
the actual minimal changes needed in an application.

Reproduce the local interface probe with the locked optional dependencies:

```sh
uv run --group integration python -m benchmarks.probe_framework_integration --output artifacts/framework-probe-new.json
```

The parent output directory must exist; the output must be new. This runs
TestModel, controlled local tools and one synchronized limiter check. It disables
remote model requests, records no answer text and uses no model/GPU service.
It is a source-checkout research probe, not an installed SDK test, a meaningful
task-quality evaluation or a throughput benchmark. The final clean-source probe
will be recorded separately from the initial exploratory snapshot.

Resource plan: target 16 GiB system RAM and a provisional 2 GiB process ceiling;
measure peak working set and overhead before making claims. The actual current
host reports about 31.2 GiB physical RAM, 16 logical CPUs and 8,188 MiB GPU memory.
Start with bounded local integration probes; increased system RAM is useful
headroom, not proof that a larger model fits GPU memory or improves quality.
