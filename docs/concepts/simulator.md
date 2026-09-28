# Simulator design — proposed, not implemented

M2 inputs will be workload template, deployment, arrivals, scenario and seed. Observed executions supply calibration evidence, not fixed successor timestamps under changed resources. No live tools run.

Use integer nanoseconds and total event order: completion/resource release, cancellation/deadline, readiness/admission, dispatch; insertion sequence resolves remaining ties. Decide and test whether completion at deadline is accepted (proposal: yes). All work transitions through ready -> queued -> running -> completed/failed/cancelled; every resource acquisition must have exactly one release. External API/human waits reserve only explicitly declared resources.

FIFO finite pools are baseline. Queue limits, rejected work, bounded retry attempts, backoff, outage episodes, fan-out/join and conditional outcomes need named contracts. A join waits for its configured required predecessors; losing speculative work may continue until cancellation acknowledgment. Fixed seeds use independent streams per arrival/service/failure/branch source; a scheduler may not see future random samples.

Validate D/D/1 exactly; validate stable M/M/1 against W=1/(mu-lambda) after warmup, over repeated seeds and confidence intervals. Test overloaded queues with a finite horizon and censored work, never report completed-only throughput as sustainable capacity. Compare generic pools against an independent SimPy model. Python/C++ parity later requires identical PRNG and event-order contracts; Python's default PRNG is not assumed cross-language portable.

Binary heap first. Profile before batching, pools, SoA, calendar queues or timing wheels. PDES is deferred. Inference service models can call or import calibrated results from established inference simulators; do not clone their internals.
