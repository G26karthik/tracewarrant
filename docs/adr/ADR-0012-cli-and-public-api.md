# ADR-0012 CLI and public API

Status: ACCEPTED

Date: 2026-09-28

## Context
Users need local artifacts and a library independent of UI.
## Requirements
Deterministic output, clear errors, small commands and no implied future features.
## Alternatives considered
Notebook only; dashboard; library plus argparse CLI.
## Decision
Expose ingest, compile_workload and analyze; CLI ingest/analyze; internal codename only.
## Why
Standard-library tooling suffices without runtime dependencies.
## Consequences
Version JSON; malformed input exits 2; no simulate/plan stubs; API experimental.
## Risks
Schema evolution can break consumers; public naming remains unresolved.
## Evidence
[README](../../README.md), [naming research](../research/competitive-landscape.md).
## Reversal conditions
Stabilize after an external adapter; choose a public name only after fresh clearance.
