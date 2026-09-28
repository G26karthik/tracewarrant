# Adversarial review

Date: 2026-09-28. Verdict: **conditional go for a narrower research prototype**. The broad pitch does not establish differentiation. Evidence: [landscape](competitive-landscape.md). No market demand or prediction accuracy has yet been demonstrated.

| Attack | Assessment and consequence |
| --- | --- |
| Why not OTel + Grafana? | They already explain observed latency. M1 overlaps deliberately as infrastructure for the experiment. Further work earns value only through accurate interventions outside the captured run. Do not sell M1 as a digital twin. |
| Why not an LLM capacity planner? | AISimulate/Vidur should supply inference models if useful. The hypothesis concerns shared browser/retrieval/database limits that constrain application throughput independently of GPUs. If the reference workload is inference dominated, the thesis loses its test case. |
| Why not AgentServeSim? | It is a direct intellectual competitor. Independently contended non-LLM pools and observed queue/service separation must add predictive value over its tool-gap abstraction. Do not claim “first agent simulator.” |
| Why not a general DES? | SimPy/SimGrid already supply events and resources. Our value must be a defensible mapping from incomplete telemetry into qualified models and validation. If model authoring remains mostly manual, ship a library on an existing simulator. |
| Why not cloud capacity planning? | Commercial planners already optimize resources. A local transparent workflow model can investigate application tool limits and unavailable deployments, but that distinction needs user evidence. Cloud inventory discovery is out of scope. |
| Why not load testing? | A modest load sweep is often better and cheaper. Simulation is useful only when several unavailable/expensive alternatives can be screened after limited calibration. Compare total calibration plus modeling time against direct sweeps. |
| Why not Langfuse/Phoenix? | Tracing/evaluation UI is already solved. No dashboard project. Accept exports later; make model assumptions and intervention errors the deliverable. |
| Why can't users benchmark their app? | They can and should. Establish an experimental break-even curve: number of candidate configurations versus total engineering/compute cost. If one benchmark answers the question, recommend that. |
| Is accurate whole-agent simulation possible? | Only in a stated operating envelope. Logical work changes with model outputs, timeouts and policies. Separate fixed-work replay from generative branch models, and never extrapolate quality from timing. |
| Are external APIs too stochastic? | Sometimes. Use time-of-day/provider cohorts, correlated episodes, empirical tails and slowdown scenarios. Censoring and rate-limit feedback invalidate IID fits. Unknown providers get sensitivity bounds and no confident recommendation. |
| How much calibration is required? | Queue/service timestamps, resource pool size and at least low/near-saturation observations are needed for capacity claims. A single loaded latency trace cannot identify service demand. Measure calibration effort explicitly; gather more data only if decision sensitivity justifies it. |
| Can the optimizer be dangerously confident? | Yes: it exploits model error. Require held-out validation, calibration envelope checks, uncertainty scenarios and an abstain state. No automatic deployments; infeasible and unknown differ. |
| Is UX too complicated? | Possibly. Start with one local file and a report that explains missing instrumentation. Avoid 20 required YAML files. Configuration should describe resources the user actually controls. |
| Is there repeat OSS usage? | Unproven. Candidate repeated jobs are pre-release capacity checks and revised deployment planning. Validate with maintainers before building hosted infrastructure. |
| Can value precede 20 frameworks? | Yes if one OTLP export and one custom non-coding workload share the same library core. A framework-specific profiler is insufficient. |
| Is standardizing workload IR impossible? | Universal standardization is not the goal. Version a small experimental execution representation, preserve source identity, and defer probabilistic workflow templates. Reject unsupported semantics instead of promising universal import. |
| What is the smallest proof? | A non-coding research workflow with inference, retrieval and a bounded browser pool; calibrate at two loads, predict held-out loads and a worker-count change, execute the changes, then compare against fixed-gap and naive scaling baselines. M1 alone proves only graph/accounting correctness. |

## Hard failure modes

1. Parent spans enclose child spans; summing both double counts. Parentage also does not encode joins. Use explicit finish-to-start edges and separate containment.
2. Span wall time mixes queueing, service, network and retries. Never use it as uncontended demand without evidence.
3. A dependency can release a successor before its parent span ends; the basic DAG cannot represent streaming. Reject such declared finish-to-start edges until richer semantics exist.
4. Observed branches are outcomes, not branch probabilities. Missing failed/slow traces bias tail estimates.
5. Unknown GPU utilization cannot be inferred from time spent in model spans. Metrics must be time-aligned and calibrated separately.
6. Equal marginal distributions do not imply equal fan-in tail latency; correlated branches matter.
7. An optimizer must not trade task success for speed silently. Quality and side-effect constraints remain independent.

## Falsifiable gates (targets, not results)

The first validation experiment targets p50 relative error <=10%, p95 <=20%, and saturation-load error <=15% over predeclared held-out cells, with bootstrap intervals and absolute errors reported. These are provisional engineering tolerances, not confidence guarantees. A p99 claim needs sufficient tail observations; otherwise report it as underpowered. A recommendation must predict the sign of the measured intervention and preserve the task-quality floor.

Compare naive linear scaling, fixed recorded tool delays, a generic SimPy implementation and the calibrated pool model. Ablate queue measurements and correlation preservation. If the pool model does not improve useful decisions after two bounded calibration iterations, stop optimizer/native development and reassess as an adapter/validation toolkit. If an upstream simulator already covers the same loop, prefer contributing upstream. Revisit at M4 and before M3 investment; the roadmap is gated, not a technology checklist.
