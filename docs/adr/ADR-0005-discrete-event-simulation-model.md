# ADR-0005 Discrete event model

Status: PROPOSED

Date: 2026-09-28

## Context
Changed resources require causal successor releases rather than fixed recorded timestamps.
## Requirements
Finite pools, explicit queues, deterministic seeds and total event order.
## Alternatives considered
Queueing formulas alone; time ticks; single-thread DES; parallel DES.
## Decision
Propose integer-time, single-thread DES with a binary heap for M2.
## Why
Simple inspectable semantics precede advanced data structures.
## Consequences
Specify same-time phases and PRNG streams before implementation; compare with SimPy.
## Risks
Correlation, retry feedback and cancellation can invalidate simple models.
## Evidence
[Design](../concepts/simulator.md), [SimPy](https://simpy.readthedocs.io/en/latest/).
## Reversal conditions
Change event structures only after profiling; use formulas only under tested assumptions.
