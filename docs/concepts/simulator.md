# Simulator — implemented bounded reference

M2 inputs are explicit workload template, deployment, arrivals, scenario and seed. Observed executions supply calibration evidence, not fixed successor timestamps under changed resources. No live tools run. [Exact committed semantics](../design/simulation-semantics.md) and [analytical validation](../validation/milestone-2.md) supersede the original proposal. Optional aligned empirical vectors now permit paired whole-session sampling; no shared-outage process is inferred.

Use integer nanoseconds and total order `(time, microstep, phase, sequence)`: completion/release, cancellation/deadline, arrival/readiness, admission. Scheduling an earlier phase at the same time advances the microstep. Existing completion at a deadline is accepted; a newly ready zero-time successor remains subject to the deadline. Acquisitions release once or remain explicitly outstanding at a censoring horizon. External wait follows release and owns no undeclared pool.

FIFO finite pools are baseline. Queue limits, rejected work, bounded retry attempts, backoff, outage episodes, fan-out/join and conditional outcomes need named contracts. A join waits for its configured required predecessors; losing speculative work may continue until cancellation acknowledgment. Fixed seeds use independent streams per arrival/service/failure/branch source; a scheduler may not see future random samples.

Validate D/D/1 exactly; validate stable M/M/1 against W=1/(mu-lambda) after warmup, over repeated seeds and confidence intervals. Test overloaded queues with a finite horizon and censored work, never report completed-only throughput as sustainable capacity. Compare generic pools against an independent SimPy model. Python/C++ parity later requires identical PRNG and event-order contracts; Python's default PRNG is not assumed cross-language portable.

Binary heap first. Profile before batching, pools, SoA, calendar queues or timing wheels. PDES is deferred. Inference service models can call or import calibrated results from established inference simulators; do not clone their internals.
