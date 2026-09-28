# Reproduce the analysis smoke benchmark

```sh
uv sync --locked
uv run python benchmarks/analysis_benchmark.py --runs 20 --warmups 3 --output artifacts-analysis.json
```

Output must be a new path. The harness records raw per-stage nanosecond samples, environment/lock/source/workload hashes, and a separately collected Python allocation peak. The example workload is synthetic; harness runtime is an actual CPU measurement. This tests the harness and analytical path, not an agent's capacity or simulator accuracy.

[Methodology](../docs/benchmarks/methodology.md) governs later scaling and native-engine comparisons. Initial raw evidence is under [docs/benchmarks/results](../docs/benchmarks/results/). Re-run at a clean named commit before making publication claims. No speedup claim is made without a baseline.
