# ADR-0002 Workload IR

Status: ACCEPTED

Date: 2026-09-28

## Context
A trace tree encodes containment, not scheduling dependencies.
## Requirements
Stable IDs, exact time, missingness, framework neutrality and no inclusive double counting.
## Alternatives considered
Raw OTel tree; universal workflow DSL; separate execution instances and workload templates.
## Decision
Implement v0 instances with atomic leaf work and separate explicit finish-to-start edges. Defer templates.
## Why
Keeps causality auditable without guessing joins.
## Consequences
Reject cycles/dangling edges; report incomplete topology; no streaming dependency support.
## Risks
Leaf selection omits uninstrumented parent work. Completeness is an input assertion.
## Evidence
[IR contract](../concepts/workload-ir.md), [mapping](../design/otel-mapping.md).
## Reversal conditions
If a real workload cannot be represented without invented edges, version the edge model before expanding adapters.
