# Benchmark methodology

Results are measurements or explicitly labeled model outputs. Targets are not results. Commit/publish machine-readable raw samples; never substitute screenshots.

Required metadata: UTC date, commit (or null if unborn), dirty state, source-tree hash, CPU/platform/RAM, OS, Python, compiler/C++/CUDA versions or explicit not-applicable, dependency-lock hash, workload version/hash, seed, warmups, repetitions and raw observations. Record workload origin separately from the fact that benchmark runtime is measured. Re-run publication benchmarks at a clean named commit; dirty/unborn runs are local smoke evidence only.

| Class | Measurement | Baselines / exclusions |
| --- | --- | --- |
| M1 analysis microbenchmark | Parse/compile/analyze runtime and Python allocation peak across graph sizes | Separate stages; no end-to-end agent claims; tracemalloc is not process RSS |
| Simulation benchmark (M2+) | events/sec, memory/event, scaling, deterministic seed | Python/SimPy then C++; identical semantics and workload |
| Application benchmark (M4+) | p50/p95/p99, throughput, queue wait, errors, task success | Same workload/version/model and quality floor |
| Deployment validation (M8) | Predicted versus measured intervention effect | Held-out loads/resources, frozen prediction, absolute/relative errors and intervals |

Run warmups, retain all timed samples, report median and spread; do not discard slow runs without a declared reason. Time measurement and allocation profiling run separately because profiling distorts runtime. Shared CI runs correctness, not noisy performance thresholds. CI may upload smoke artifacts with full limitations.

Do not infer queue demand from elapsed trace weights. The synthetic M1 fixture has hand-derived expected graph values only. Do not call that hardware calibration or a simulator validation. Real validation requires independently measured deployments and a preregistered prediction.
