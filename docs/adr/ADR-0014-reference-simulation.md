# ADR-0014 Reference simulation

Status: ACCEPTED (bounded implementation of ADR-0005; extends ADR-0004)

Date: 2026-09-29

## Context
M1.5 supports explicit instrumentation, not universal trace identifiability. SimPy and distributed simulation engines already provide the general mechanism.
## Requirements
Inspectable race/termination semantics, exact time, finite queues, independent checks and no executed source tools.
## Alternatives considered
Permanent SimPy engine; queue formulas; small Python heap reference; immediate native port.
## Decision
Implement the preregistered Python reference contract and compare standard FIFO behavior with SimPy. Keep a replaceable batch scenario boundary and no third-party core dependencies.
## Why
The research concerns the calibration/validation boundary, not heap novelty. Explicit contracts are easier to inspect before optimization.
## Consequences
Separate execution IR and generative scenario JSON. SIMULATED outputs name input provenance. SimPy is optional validation tooling. Native/CUDA remain conditional.
## Risks
Maintenance may exceed the custom contract's value; generated mathematical agreement is not real predictive validity. Independent marginal samples miss correlated sessions.
## Evidence
[Preregistered semantics](../design/simulation-semantics.md), [M2 checks](../validation/milestone-2.md).
## Reversal conditions
Prefer SimPy/upstream if no domain benefit emerges. Native requires a measured experiment bottleneck plus parity and material advantage.
