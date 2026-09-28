# FRAMES local intervention study — preregistration

Written before timing calibration or intervention runs. This is a bounded experiment, not a full FRAMES quality benchmark or a claim that the desired hard workload has already been found.

## Independent task choice and real execution

Use the [recorded selection](frames-selection.json), first eight eligible FRAMES tasks in original order: 0, 1, 3, 4, 5, 6, 7, 9. Source revision and dataset hash are fixed. No task is removed based on latency, model error or answer correctness. Oracle-provided source URLs remove search-policy variation; this limitation is explicit.

The application fetches the listed public Wikipedia HTML with at most two concurrent network requests, parses visible paragraphs, ranks evidence by query-term overlap, records source metadata in SQLite, then invokes cached local `llama3.1:8b` via Ollama. Real document parsing, retrieval, database and inference are executed. No artificial sleeps/service delays are added. No public write, login, model download or paid API. Network requests are bounded, use a descriptive user agent, 20 s timeout and 4 MB response cap; stop on access denial/rate-limit rather than work around it. Task/document/prompt/answer text stays in ignored local inputs or memory; results contain IDs/counts/hashes/timings and exact-match booleans only.

Warm up the model separately. One feasibility batch precedes calibration and is retained. If access is blocked, report the external requirement. If quality or non-LLM demand is inadequate, do not hide the finding or rename the task a successful agent benchmark.

## Design and freeze

Owned pools: fetch workers (1 baseline, at most 2), inference client slots (1 baseline, at most 2), retrieval and SQLite boundaries. Client slots are not GPU replicas. Eight selected tasks launch as one finite burst; no sustainable arrival-rate/saturation claim. Collect two baseline calibration bursts of eight tasks. Fit per-task/per-stage occupancy from these 16 sessions only. No holdout data enters fitting.

Configurations: BASE (fetch 1 / client 1), FETCH2 (fetch 2 / client 1), CLIENT2 (fetch 1 / client 2). These are equal one-slot interventions on different resources, not equal monetary cost. Freeze all three scenarios and all producers before any intervention measurements. Then measure two replications of eight tasks per configuration, normal order first, reversed order second (48 held-out sessions). Keep task order, model/options, URL set and application revision fixed; record network failures rather than discarding a cell. Workstation/network load and current Wikipedia content remain confounds.

## Producers and baselines

- Whole-workflow SimPy: calibrated per-task stage occupancy, actual fan-out/join, FIFO owned pools, deterministic sampling seeds 2000–2029. Explicit assumption: sampled client occupancy is invariant under client-slot changes; this is unproven and may be refuted. Backend internals stay unsupported.
- Utilization heuristic: increase the baseline pool with the largest aggregate occupied fraction among fetch/client; tie remains a tie. Predict only intervention order, not fabricated latency.
- Fixed-delay baseline: use baseline mean completed latency for every configuration and tie all interventions. This tests whether added model detail helps beyond unchanged-demand predictions.

## Metrics and decision rule

Primary: mean session latency over completed sessions, minimum eight measured sessions per cell; failure/censoring disqualifies complete-population comparisons if fewer than eight finish. Report all offered outcomes and exact normalized answer match separately. Normalize by Unicode casefold and removal of whitespace/punctuation; no LLM judge and no subjective recoding after results. At least 6/8 correct in every cell is required for a quality-preserving workload success; performance numbers can still be reported if this fails, but no useful agent-capacity conclusion follows.

Secondary: p50, completed throughput over finite batch drain, average per-session pool queue time and occupied fraction over the batch window. p95/p99 remain UNKNOWN with eight sessions. Primary material ranking requires at least 10% relative difference in both replications with the same direction. Report per-cell signed/absolute/relative error and all eligible pairs. A complex model adds decision value only if its chosen intervention materially beats the heuristic choice in both replications and the quality gate passes. Matching or losing is a publishable result.

Nontrivial heterogeneity gate: non-LLM owned occupancy must be at least 20% of total measured owned occupancy in calibration, and more than one pool must exhibit measured queueing. Report whether it passes, never inflate delays to pass. If current utilization already resolves the held-out intervention, publish that result. Hardware-independent inference demand, steady-state capacity, quality reasoning beyond exact answers, cross-network transfer and economic superiority remain unsupported.

For intervals use empirical simulation quantiles across seeds labeled `range` rather than claiming calibrated confidence. Observed per-replication points remain separate; no iid bootstrap over correlated concurrent sessions is represented as a trustworthy confidence interval.
