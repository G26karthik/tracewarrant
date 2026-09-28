# Milestone 2 — reference semantics PASS

Date: 2026-09-29. M1.5 passed first. Event semantics were committed at `4c2e91f` before implementation. Development verification: **92 tests pass**; analytical and independent SimPy harness passes. Clean-commit raw results follow in an evidence commit.

Implemented: integer heap time, microstep/phase/sequence ordering; explicit DAG templates/arrivals; finite FIFO pools and bounded queues; empirical distributions plus explicitly selected exponential mathematical cases; named SplitMix64 streams; occupied service versus external wait; failures/bounded retries/backoff; timeout/cancellation/release lag; horizon censoring; all-session outcome denominators; utilization, queue integrals, throughput and completed-only latency quantiles; library and JSON CLI. No real tool execution.

Evidence includes serial sum, fan-in maximum, deterministic one/two-worker queues, retries at (0–3, 5–8, 10–13), deadline races, zero-time work, queue rejection, sibling cancellation, stale completion suppression, censoring, deterministic permutations and Hypothesis conservation cases. Twenty independently scheduled SimPy FIFO cases (2,000 jobs) match exact acquisition/release times.

Generated M/M/1: five seeds, 20,000 arrivals per seed, rho≈0.6, first 10% warmup excluded. Prerun tolerances: each seed mean latency error <10%, aggregate <5%, Little's Law common-window residual <1%, utilization error <0.03. Development aggregate mean error was 1.62%. This is a mathematical validation workload, not an assumption about real agents.

```sh
uv run pytest -q
uv run workload-lab simulate examples/scenario.json --output artifacts/simulation.json
uv run --group validation python -m benchmarks.validate_simulation --output artifacts/m2-validation.json
```

Create the artifact directory and use new output filenames. No infrastructure recommendations are justified. Unsupported: conditional topology, shared-outage generator, dynamic capacity, processor sharing, simultaneous multi-pool ownership, streaming completion, cross-host clock correction, GPU batching/KV/cache, priorities and rate limits. Completed quantiles exclude failures; the outcome denominator accompanies them. Future arrivals are not offered sessions; unfinished offered sessions are censored. Zero-duration ready requests can contribute to instantaneous maximum queue depth without positive queue-time area.
