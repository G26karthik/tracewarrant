# ADR-0004 Simulator language boundary

Status: PROPOSED

Date: 2026-09-28

## Context
No simulation throughput bottleneck has been measured.
## Requirements
Correctness, reproducible throughput/memory evidence, batch bindings.
## Alternatives considered
Python/SimPy; C++20/pybind11; SimGrid/WRENCH; existing inference engine.
## Decision
M1 stays Python. Establish reference semantics before considering a C++20 DES port.
## Why
Native code must buy measurable experiment throughput or memory efficiency.
## Consequences
No compiler or pybind11 dependency now.
## Risks
Binding overhead and semantic drift can erase gains.
## Evidence
[Simulator design](../concepts/simulator.md), [benchmarks](../benchmarks/methodology.md).
## Reversal conditions
Retain Python or integrate upstream unless parity plus measured benefit justify a custom port.
