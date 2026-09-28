# ADR-0006 Optimization engine

Status: PROPOSED

Date: 2026-09-28

## Context
Search exploits simulator errors; no validated simulator exists.
## Requirements
Finite domains, budget horizon, feasibility/unknown distinction and exact baseline.
## Alternatives considered
Enumeration; greedy; MILP/CP-SAT; metaheuristics.
## Decision
M5 starts with tiny exhaustive replica search and Pareto filtering.
## Why
Exact cases expose constraint errors and establish an oracle for heuristics.
## Consequences
No solver now; abstain outside validation envelope; independent finalist seeds.
## Risks
Selection bias and task-quality regressions can make cheap candidates useless.
## Evidence
[Optimization](../concepts/optimization.md), [validation](../validation/plan.md).
## Reversal conditions
Add a solver only when enumeration cost is measured and its assumptions fit the model.
