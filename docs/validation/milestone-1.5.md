# Milestone 1.5 — PASS within the documented contract

Date: 2026-09-29. Baseline: [verified record](baseline-2026-09-29.md). Actual local execution, not fabricated timestamp fixtures. The application is deliberately a controlled non-coding stub workload; it does not establish task intelligence or real LLM capacity.

Source A: [controlled capture](../../examples/traces/controlled-v1.otlp.json), SHA-256 `49244670659129b2e5e6b78fa24818b50e17a7a60bf510fb7060fec7e0ced5e0`. Eight concurrent sessions, 77 spans, eight asserted-complete graphs and 77 explicit edges. Planning/synthesis use a two-slot stub-model pool; retrieval, tool and SQLite operations fan out within a nested container, then explicitly join. The tool pool has one slot. Largest observed queue wait: 31,147,100 ns. External waits own no worker. Additional recorded attempts include one failure, retry after backoff, timeout and cancellation with release after the request. Elapsed clocks are monotonic mapped once to epoch per session.

Source B: [PydanticAI 2.51.0 capture](../../examples/traces/pydantic-ai-2.51.0.otlp.json), SHA-256 `7251357859d23938a6bc2d33e637d3445cc3760d8ea585d2fea3510e0c983181`. Genuine Agent/TestModel execution invokes two local tools (one SQLite), using OTel SDK 1.45.0 and instrumentation v5. Model requests are disabled. An in-memory exporter writes only allowlisted fields; no collector, Logfire backend or paid API is configured. Five spans, one incomplete graph, **zero declared dependency edges**. All four atomic nodes have UNKNOWN queue/service. Three spans have zero recorded duration; no timing resolution or causality is invented to repair them. A production model was not used. No framework patch was necessary to ingest the observation; sufficient contention modeling would require extra instrumentation.

| Required gate | Evidence |
| --- | --- |
| Actual execution creates valid graph | Both captures ingest/compile; A is asserted complete |
| Sequential/fan-out/fan-in without parent abuse | A explicit predecessor IDs and join; nested parent excluded from work |
| Missing semantics UNKNOWN | B all queue/service absent; A external waits have no occupied service |
| Only identified separation | Lifecycle timestamps derive queue/occupancy; conflict rejection tests |
| Content exclusion | Importer sentinel tests, exporter allowlist; raw prompts/results/SQL/names absent |
| Incomplete topology reported | B remains incomplete, no guessed edges |
| Finite-pool trace | A configured tool=1, stub-model=2, retrieval=2, database=1 |
| Minimum instrumentation contract | [Contract](../design/instrumentation-contract.md) |
| Tests | 75 local tests pass, including actual concurrent capture, lifecycle bounds, depth cap and external fixture |
| V2/ADRs | ADR-0013 and V2 addendum document evidence and limitations |

Reproduce with fresh output paths:

```sh
uv sync --locked
uv run python -m examples.capture_controlled --output artifacts/controlled.json
uv run --group integration python -m examples.capture_pydantic_ai --output artifacts/pydantic.json
uv run workload-lab analyze artifacts/controlled.json --format json
uv run workload-lab analyze artifacts/pydantic.json --format json
uv run pytest -q
```

Create the `artifacts` directory first. Live timestamps/IDs differ on rerun; assertions test semantics, not exact timings. The committed examples were captured during development and are compatibility observations, not clean-commit performance benchmarks. Hardware verified locally: Ryzen 9 8945HS, eight cores/16 logical CPUs; RTX 4060 Laptop GPU, 8,188 MiB reported VRAM, driver 616.56 (unused). GPU/CUDA performance is unmeasured.

**Gate permits M2 reference semantics only.** It does not establish generic trace identifiability, cross-host clocks, production adoption cost, model intelligence or infrastructure prediction accuracy. M1.5 discovered the expected counterexample: ordinary OTel agent telemetry alone does not identify this resource model.
