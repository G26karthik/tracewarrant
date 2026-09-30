# Project status

Updated: 2026-09-30. Selected public name: **TraceWarrant**; former internal codename: Workload Lab.

**Active direction: [PROJECT_V3.md](PROJECT_V3.md)** — simulator-neutral observation and performance-model validation. Public project: [G26karthik/tracewarrant](https://github.com/G26karthik/tracewarrant); experimental package 0.3.1. [Completion report](docs/v3/completion-0.3.1.md), [short project refresher](START_HERE.md). The initial 0.3.0 report and `validation-toolkit-v3` tag remain preserved.

**Completion assessment:** the scoped V3 implementation and local qualification are delivered. The public repository is live and all five hosted CI jobs passed on `cede1a4`. The project is not fully closed out: no GitHub release exists yet, and final release assets still need qualification and upload from their exact source commit. Production suitability, added decision value over the heuristic and external adoption remain unestablished. [Verified continuation checkpoint](CONTINUATION.md), [autonomous completion prompt](CONTINUE_PROMPT.md).

- V3-A/B/C/E delivered locally: contract/research, three-source conformance, neutral artifacts, independent validation, baselines, packaging and reproducibility. `inspect`, `schema`, `check`, `freeze`, `evaluate` load no reference simulator.
- V3-D executed with negative limits: FRAMES 16 calibration + 48 held-out sessions; SimPy median mean-latency error 1.50%, 2/2 material rankings. Utilization selected the same intervention. Strict exact answers passed 0/48 held-out; no useful-agent capacity claim. Hard-decision workload and external adoption remain unestablished.
- Real conformance finding: incorrect collector completeness key refused; original traces preserved and explicit binding adapter supplied. All 72 feasibility/calibration/holdout graphs validate structurally after adaptation; inference service demand remains UNKNOWN.
- Frozen V3 experiment: `af36005` / `v3-frames-freeze`. [Results](docs/v3/results.md), [reproduction](docs/v3/reproduce.md), [verification](docs/v3/verification.md).
- 150 tests pass on Windows Python 3.11/3.12.12/3.13 and Ubuntu WSL Python 3.12.3. Fresh installed wheels pass qualification on Windows and Linux: source/archive bytes, both command names, no runtime dependencies, no simulator import and exact evaluation reproduction. [Hosted run 36533108249](https://github.com/G26karthik/tracewarrant/actions/runs/36533108249) passed Windows/Ubuntu Python 3.11/3.13 plus Ubuntu analytical validation on `cede1a4`. A fresh local 2026-09-30 check passed 150 tests, lint/format and the offline audit.
- Completion review fixed conflicting declared environments, scale-dependent material comparisons, single-option decision conclusions and empty files after serialization failure. [ADR-0018](docs/adr/ADR-0018-controlled-comparisons-and-release-qualification.md). Public `tracewarrant` naming preserves `workload-lab`/`workload_lab` compatibility and frozen wire formats.
- Release rehearsal passed from a separate committed-source clone with fresh dependencies: 150 tests, distributions, installed qualification, preservation/evaluation and analytical checks. CI now retains evidence and runs the history audit. [Rehearsal](docs/v3/release-rehearsal.md), [exact public-release proposal](PUBLIC_RELEASE.md).
- Baseline `c0fad29`, `research-pilot-1`, V2, its final report, all predictions and 64 protected files remain unchanged. GitHub publication is authorized; the public repository and private vulnerability reporting are enabled. No paid calls, cloud provisioning or outreach. No C++/CUDA/optimizer investment justified.

## Frozen V2 pilot summary (historical)

The entries below preserve the prior research state and are not the active roadmap.

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

## Current reproduction

Reproduce: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv build --no-build-isolation`. Use the [distribution qualification procedure](docs/v3/release-qualification.md) to verify the installed wheel.

Run `uv run tracewarrant inspect examples/traces/controlled-v1.otlp.json` or `uv run python -m benchmarks.v3_audit --output audit-new.json`. Use fresh output names. The reference backend remains available as `workload-lab simulate`. TraceWarrant naming and local qualification are complete; [GitHub release procedure](PUBLIC_RELEASE.md).
