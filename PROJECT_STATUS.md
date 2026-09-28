# Project status

Updated: 2026-09-29. Internal codename: Workload Lab.

- Current milestone: M2 passed locally; clean-commit analytical evidence and M3 performance gate next.
- Last completed: M2 reference semantics, see [validation](docs/validation/milestone-2.md).
- Canonical previous milestone: local tag `m1.5`; M2 source commit follows this status update.
- Verified baseline commit: `9e15d8cf70046597e3614975c03627d680751c98`; clean before work.
- Thesis: NOT VALIDATED. No predictive intervention evidence yet.
- Validated: 92 local tests; actual finite-pool graphs, lifecycle separation, incomplete PydanticAI import; generated M/M/1/Little's Law and exact SimPy FIFO cross-checks. Historical document hashes preserved.
- Unvalidated: ordinary trace identifiability, resource simulation, calibration, infrastructure recommendations, native acceleration, cloud transfer and external usability.
- Closest reviewed alternatives: AgentServeSim, AISimulate, Vidur, PerfSim; SimPy/SimGrid/WRENCH are engine alternatives.
- Scientific risks: unobserved queue/service boundaries, incomplete joins, correlated delays, selection/censoring bias, simple heuristics matching simulation, direct load testing being cheaper.
- External actions: none needed for M1.5/M2; no account, publication, paid API or cloud action authorized by this record.
- Next gate: benchmark event scales; retain Python unless actual experiment cost warrants native. Preregister prediction criteria before calibration/interventions.

Reproduce baseline: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv build --no-build-isolation`.
