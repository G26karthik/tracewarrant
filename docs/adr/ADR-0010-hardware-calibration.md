# ADR-0010 Hardware calibration

Status: PROPOSED

Date: 2026-09-28

## Context
Peak GPU figures do not identify application service curves.
## Requirements
Hardware provenance, shape envelope, real-serving anchors and reproducible profiles.
## Alternatives considered
Published specifications; CUDA microbenchmarks; serving measurements; community profiles.
## Decision
Prefer serving anchors; add CUDA experiments only when service-model sensitivity requires them.
## Why
Hardware properties cannot replace batching/cache/queue behavior.
## Consequences
No guessed RTX profile or CUDA dependency now; record exact SKU/software/clocks later.
## Risks
Thermal/power drift and GPU variants impair transferability.
## Evidence
[Calibration](../concepts/calibration.md).
## Reversal conditions
Skip custom kernels when maintained benchmarks provide sufficient evidence.
