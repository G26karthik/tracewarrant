# ADR-0011 Cloud validation

Status: PROPOSED

Date: 2026-09-28

## Context
Some interventions need multiple workers; available credits are finite and unverified.
## Requirements
Preregister predictions, cost ceiling, TTL, reproducibility and verified teardown.
## Alternatives considered
Local processes; containers; Azure VMs/Container Apps; Kubernetes.
## Decision
Start local; later select the simplest Azure topology for a specific held-out experiment.
## Why
Cloud should validate the model rather than become a product dependency.
## Consequences
No deployment now; paid actions/credentials need human involvement.
## Risks
Cold starts, autoscaling, quotas and failed cleanup confound measurements or cost.
## Evidence
[Validation plan](../validation/plan.md), [roadmap](../../ROADMAP.md).
## Reversal conditions
Stay local if cloud supplies no distinct validation cell or cannot fit verified budget/quota.
