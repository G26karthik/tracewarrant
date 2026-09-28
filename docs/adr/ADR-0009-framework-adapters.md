# ADR-0009 Framework adapters

Status: ACCEPTED

Date: 2026-09-28

## Context
Framework APIs must not own domain semantics.
## Requirements
Core works with custom agents; one later non-coding integration.
## Alternatives considered
LangGraph profiler; many integrations immediately; OTLP with versioned adapters.
## Decision
Frameworks enter at import/export boundaries; no framework dependency in M1.
## Why
The same algorithm should analyze equivalent graphs from any runtime.
## Consequences
Require contract fixtures and loss diagnostics; Langfuse/Phoenix optional.
## Risks
Frameworks often omit queue and join information.
## Evidence
[Mapping](../design/otel-mapping.md), [V2](../../PROJECT_V2.md).
## Reversal conditions
Add one adapter when a validation workload needs it; change core only for general semantics.
