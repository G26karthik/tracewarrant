# Project status

Updated: 2026-09-29. Internal codename: Workload Lab.

- Current milestone: M2 semantics design, after passing M1.5.
- Last completed: M1.5, see [validation](docs/validation/milestone-1.5.md).
- Canonical milestone reference: local tag `m1.5` (created at the validated boundary).
- Verified baseline commit: `9e15d8cf70046597e3614975c03627d680751c98`; clean before work.
- Thesis: NOT VALIDATED. No predictive intervention evidence yet.
- Validated: 75 local tests; actual finite-pool graphs, lifecycle separation and ordinary PydanticAI import with missing semantics preserved. Historical document hashes preserved.
- Unvalidated: ordinary trace identifiability, resource simulation, calibration, infrastructure recommendations, native acceleration, cloud transfer and external usability.
- Closest reviewed alternatives: AgentServeSim, AISimulate, Vidur, PerfSim; SimPy/SimGrid/WRENCH are engine alternatives.
- Scientific risks: unobserved queue/service boundaries, incomplete joins, correlated delays, selection/censoring bias, simple heuristics matching simulation, direct load testing being cheaper.
- External actions: none needed for M1.5/M2; no account, publication, paid API or cloud action authorized by this record.
- Next gate: define total same-time event ordering before coding; analytical/conservation and independent SimPy checks before M2 acceptance.

Reproduce baseline: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv build --no-build-isolation`.
