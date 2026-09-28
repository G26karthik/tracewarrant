# ADR-0007 Performance provenance

Status: ACCEPTED

Date: 2026-09-28

## Context
A number without evidence is unsuitable for infrastructure decisions.
## Requirements
Lineage, synthetic distinction, unknown values, methods and honest bounds.
## Alternatives considered
Bare floats; single confidence score; provenance plus independent origin/method/assumptions.
## Decision
Attach evidence to timing/report quantities; do not rank provenance as confidence.
## Why
Measured does not mean representative; simulated does not specify input reliability.
## Consequences
Synthetic timestamps are ESTIMATED, null bounds are unestablished, derivations state method.
## Risks
Point estimates can be overread; correlated model error needs scenario treatment.
## Evidence
[Contract](../concepts/provenance.md).
## Reversal conditions
Version the evidence schema when calibration needs richer intervals or multiple input models; never silently upgrade evidence.
