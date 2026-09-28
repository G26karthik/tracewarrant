# Project status

Updated: 2026-09-29. Internal codename: Workload Lab.

- Current milestone: M4 controlled calibration/prediction pilot; holdout not yet collected.
- Last completed: M2 reference semantics and M3 native assessment (C++ deferred on measured evidence).
- Canonical references: `m1.5`, `m2`; pilot prediction freeze tag `pilot-1-freeze` is created before holdout. Source for predictions: `f73a806`.
- Verified baseline commit: `9e15d8cf70046597e3614975c03627d680751c98`; clean before work.
- Thesis: NOT VALIDATED. No predictive intervention evidence yet.
- Validated: 94 local tests; lifecycle graphs, incomplete PydanticAI import, generated M/M/1/Little's Law, exact SimPy FIFO checks; million-event median 3.361 s and peak 280 MB. 160 actual controlled calibration sessions at 2/9 offered sessions/s, with load cohorts kept separate. Historical hashes preserved.
- Unvalidated: ordinary trace identifiability, resource simulation, calibration, infrastructure recommendations, native acceleration, cloud transfer and external usability.
- Closest reviewed alternatives: AgentServeSim, AISimulate, Vidur, PerfSim; SimPy/SimGrid/WRENCH are engine alternatives.
- Scientific risks: unobserved queue/service boundaries, incomplete joins, correlated delays, selection/censoring bias, simple heuristics matching simulation, direct load testing being cheaper.
- External actions: none needed for M1.5/M2; no account, publication, paid API or cloud action authorized by this record.
- Next gate: collect all eight preregistered held-out cells and score the committed predictions, including simpler baselines. No optimizer before this evidence. Meaningful real-model agent validation remains distinct from this stub pilot.

Reproduce baseline: `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest -q`, `uv build --no-build-isolation`.
