# Project status

Updated: 2026-09-29. Internal codename: Workload Lab.

**Active direction: [PROJECT_V3.md](PROJECT_V3.md)** — simulator-neutral observation and performance-model validation. V3-A/B passed; V3-C interfaces implemented; V3-D external FRAMES study preregistered. Current suite: 131 tests. `inspect`, `schema`, `check`, `freeze`, `evaluate` work without importing the reference simulator. [V3 contracts and evidence](docs/v3/artifacts-and-validation.md), [study design](docs/v3/frames-preregistration.md). Baseline `c0fad29`, tag and 64 historical files are preserved. The entries below describe the frozen V2 pilot; they are not the active roadmap.

- Current milestone: evidence reassessment/local handoff complete; package 0.2.0. No optimizer/cloud deployment queued.
- Last completed gates: M1.5 and M2. M3 assessed and native deferred. M4 controlled pilot passed; general calibration partial. M6 real-model applicability probe completed; predictive gate partial.
- Canonical handoff: local tag `research-pilot-1` (resolve with `git rev-parse research-pilot-1`). Historical boundaries: `m1.5`, `m2`; prediction freeze `377180c` / `pilot-1-freeze`; successful real-probe source `8f37629`. Raw artifacts contain exact source/lock/harness hashes.
- Verified baseline commit: `9e15d8cf70046597e3614975c03627d680751c98`; clean before work.
- **Thesis: PIVOT RECOMMENDED**, toward content-free instrumentation/validation and upstream adapters. [Decision](docs/adr/ADR-0015-narrow-to-validation.md), [final report](FINAL_PROJECT_REPORT.md).
- Validated: 102 tests on Windows Python 3.12.12/3.13; lint/format/build and isolated runtime-wheel simulation. Lifecycle graphs, unknown framework semantics, generated M/M/1/Little's Law, 20 exact SimPy checks; million-event median 3.361 s / peak about 280 MB. Historical hashes preserved.
- Controlled evidence: 160 training + 960 held-out sessions; median p95 error 1.70%, 2/2 material rankings, one clear bottleneck correct. Utilization heuristic chose the same intervention; no saturation threshold identified.
- Real evidence: 48/48 exact fact checks with local Llama 3.1 8B; client occupancy increased 1.73x with doubled client slots; tool work small. Qwen failed warmup retained. No real-model predictions frozen.
- Unvalidated: production-agent intervention accuracy, GPU service identification, arbitrary framework operation alignment, unseen tails/outages/censor-aware fitting, sustainable capacity, optimizer value, cloud transfer and external adoption.
- Closest reviewed alternatives: AgentServeSim, AISimulate, Vidur, PerfSim; SimPy/SimGrid/WRENCH are engine alternatives.
- Scientific risks: unobserved queue/service boundaries, incomplete joins, correlated delays, selection/censoring bias, simple heuristics matching simulation, direct load testing being cheaper.
- External actions: no upload/publication/paid API/cloud spend. Azure CLI account exists; future justified provisioning still needs explicit capped-spend authorization. [External requirement](HUMAN_ACTION_REQUIRED.md). Offline reproduction needs no Azure action.
- Next reversal gate: an independently motivated non-coding workload with materially contended non-LLM pools and identified inference behavior, followed by frozen held-out decisions that justify modeling effort beyond a utilization heuristic. Prefer an existing engine when appropriate.

Reproduce baseline: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv build --no-build-isolation`.

Run `uv run workload-lab simulate examples/scenario.json`; analytical validation: `uv run --group validation python -m benchmarks.validate_simulation --output artifacts/new-validation.json`. Create `artifacts/` and use fresh paths. [Full experiment commands](docs/experiments/README.md). Hosted CI has not run; Linux/Python 3.11 remain configured, not locally verified. Public name/contact/release qualification remains unfinished.
