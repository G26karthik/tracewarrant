# Validation plan

Status: proposed. No real agent capacity results exist yet.

Reference workflow: non-coding technical research with LLM planning/synthesis, retrieval, bounded browser/tool workers, a database/API, one branch and bounded retries. First use controlled service stubs for semantic checks; later substitute real services and keep task success fixed.

1. Record trace completeness and enqueue/start/end alongside configured pool sizes. Measure timestamp precision, clock offsets, sampling/drop behavior and instrumentation overhead.
2. Calibrate at low and near-saturation load; retain sessions and correlated service episodes. Declare workload version/mix and arrival mode (open arrival rate versus closed concurrency).
3. Freeze model, seed schedule and predictions before testing. Hold out intermediate/higher loads and at least one browser-worker change and one inference-resource change.
4. Run actual interventions; measure p50/p95/p99 latency, completions per second, rejections, failures, queue wait, pool occupancy and quality. Report incomplete/censored runs.
5. Compare naive linear scaling, fixed tool-gap replay, generic SimPy pools and calibrated pools. Ablate queue measurements, correlation and uncertain providers. Report calibration plus experiment cost.
6. Assess provisional gates: p50 error <=10%, p95 <=20%, saturation load <=15%, and correct intervention direction. These are design targets. Publish absolute errors, confidence intervals, sample counts and every cell; mark p99 underpowered when needed.
7. Optimize only after acceptable validation. Re-deploy the candidate and verify its predicted benefit and quality floor. If prediction ranking is unstable under uncertainty, abstain and select the next informative measurement.

| Cell | Load mode/value | Pools | Model version | Observed | Predicted | Error | Interval | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Not measured | Not simulated | Unknown | Unknown | None |

Azure experiment manifest later includes region/SKU, images, IaC version, budget ceiling, TTL, load driver isolation, timestamps, artifact path, spend and teardown verification. No account, resource or billable action is needed now.
