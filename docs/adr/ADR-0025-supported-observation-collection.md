# ADR-0025: supported collection before another performance study

Date: 2026-10-14. Status: accepted direction; implementation not delivered.

The maintainer requested research for a concrete next requirement after the
completed experimental scope. The codebase has strict evidence consumers and
several application-specific collectors, but no reusable collection interface.
A fresh locked Pydantic probe confirms standard spans still lack the explicit
pool lease and dependency fields required for supported observations.

Research found existing OTel framework instrumentation, generic evaluations and
agent tracing. Complement those systems with a small caller-owned observation
primitive and an optional OTel bridge, starting with pinned Pydantic AI 2.51.0.
Native waiting observability is useful but cannot establish lease release or
finish-to-start topology. Reviewed upstream and locked versions differ in token
ownership, so do not monkeypatch scheduling or assume universal compatibility.

Preserve dependency-free core imports, current wire names, bounded output,
content-free collection and all earlier evidence. Explicitly supplied boundaries
and closed scopes can improve claim support; untouched native spans retain
partial/unsupported coverage. Local occupancy does not identify GPU demand,
trusted chronology, backend cancellation or a valid performance prediction.

Do not reopen failed FRAMES/HotpotQA studies or select a larger model merely
because RAM increased. A later application study needs a separate purpose,
quality gate, preregistration and cheap baseline. No new backend/UI, serving
simulator, paid/cloud service or outreach is needed for this phase.

Consequence: [V10](../../PROJECT_V10.md) has four finite gates. A covers research;
B/C/D cover collection, framework integration and qualification. Ship a smaller
documented hook/recipe if that is sufficient. Package remains 0.7.1 until actual
implemented capability passes its acceptance gates.
