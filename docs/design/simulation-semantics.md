# Reference DES contract, preregistered before implementation

Date: 2026-09-29. Requires the passed M1.5 gate. This is a small reference semantics engine, not a contribution in general simulation engines. SimPy supplies an independent FIFO baseline; SimGrid/WRENCH remain mature alternatives. Native code is conditional on measured experiment needs.

## Inputs and separation

An explicit workload template is distinct from an observed execution. Each node has finish-to-successful-completion prerequisites, one optional pool, a discrete empirical service distribution, optional external-wait distribution, bounded attempts, failure probability, retry backoff and cancellation-release lag. External waits occur **after** releasing the pool. Parallel branches and joins follow the DAG. Failure after the final attempt terminates the session and cancels sibling work. This does not infer any policy from a span.

An arrival has a stable session ID, integer arrival time, optional absolute timeout and independent cancellation time. A deployment declares finite slot counts and optional maximum waiting queue lengths. Time is integer nanoseconds; all durations/times and counts are bounded and validated. No runtime callback, plugin, network call or tool execution is accepted as input. No CPU sharing, dynamic capacity, batching, GPU/KV/cache model, streaming dependencies, conditional topology or shared-outage generator is claimed in the reference slice.

## Total ordering

Heap key is `(time_ns, microstep, phase, insertion_sequence)`. Phases: 0 completion/release and external-wait finish; 1 deadline/cancellation; 2 new arrival/readiness/retry; 3 resource admission. At the same time, scheduling an earlier phase advances one microstep; otherwise retain the current microstep. At a future time microstep resets to zero. Sequence is strictly increasing. This preserves a globally nondecreasing event key even for zero-duration work and prevents Python object comparison or unordered-set iteration from deciding races. Template nodes, arrivals and pool iteration have canonical ID ordering.

An already-scheduled completion at a deadline wins; if it finishes the whole session, the deadline becomes stale. A zero-duration successor only made ready at that timestamp is subject to the deadline before its admission. An arrival at its own deadline times out before service. Explicit cancellation and timeout at the same time use deterministic insertion sequence (timeout scheduled first). At the horizon, process all events at that time, then right-censor any unfinished sessions; future arrivals are not offered sessions.

## Resource and termination semantics

FIFO uses enqueue insertion order. Release occurs exactly once, on completion or cancellation acknowledgment; cancellation lag can delay release beyond the originally planned completion. Once cancellation is requested, the old completion becomes stale and cannot release early. Queued cancellation removes the request immediately. During retry backoff, external wait and queueing no slot is held. A failure draws once per attempt from its named stream. Retries enqueue anew after constant backoff; no hidden immediate retry or infinite loop. Queue-full terminates the session as rejected. Free slots take ready work even with queue capacity zero; simultaneous excess admissions are rejected deterministically.

Admission/release maintain occupied<=capacity and queue>=0. Occupancy and queue depth are time integrals over [0,horizon]; cancellation lag extending past the horizon is right-censored, with outstanding allocations reported. Requested cancellation ends session latency at request time, but occupied work can continue until acknowledgment. Failed, timed-out, cancelled, rejected and censored sessions stay in the offered denominator. Completed-only p50/p95/p99 are labeled, never substituted for all-session SLO success. Throughput counts successful completions over the stated observation window.

## Randomness and reproducibility

Named streams derive a 64-bit state from SHA-256 of `seed:name`, then use SplitMix64 and the upper 53 bits for uniform draws. Names contain session ID, node ID, attempt and purpose (service/external/failure). This isolates unrelated nodes and provides a future language-portable definition. Arrival schedules are explicit inputs; analytical Poisson generation uses its own stream. Every output names simulator version, seed, complete model configuration and SIMULATED provenance. No measured hardware claim follows from a generated service distribution.

## Acceptance before performance work

Serial sum; fan-out/join maximum; one/multiple FIFO workers; zero-duration races; deadline completion; finite-queue rejection; bounded retry timeline; cancellation lag; horizon censoring; deterministic replays and input permutations; random DAG resource invariants; independent SimPy FIFO comparisons. Generated M/M/1 must agree with W=1/(mu-lambda) and utilization=lambda/mu after warmup across repeated seeds; Little's Law is checked on the same steady-state window with clipped residence-time accounting. It is not a model assumption for real agents.
