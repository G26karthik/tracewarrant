# ADR-0015 Narrow the next product step to instrumentation and validation

Status: ACCEPTED

Date: 2026-09-29

## Context
The controlled pilot passed latency/ranking thresholds, but a utilization heuristic selected the same material intervention. The real-model application was inference dominated and client occupancy changed under concurrency. Ordinary framework spans still lack the necessary queue/join contract.
## Requirements
Avoid infrastructure advice without service identifiability, real-workload validation and incremental decision value. Preserve negative results and the working offline research tools.
## Alternatives considered
Build optimizer/C++/CUDA/cloud for portfolio breadth; hunt for artificially slow tools; add backend instrumentation and validate models on an existing simulator; continue a standalone capacity product unchanged.
## Decision
Recommend a pivot toward a content-free instrumentation/validation toolkit and possible upstream adapters. Keep the reference simulator as an oracle. Defer standalone optimization, custom native/GPU engines, cloud topology and predictive regression CI until a real target workload establishes need and predictive value beyond simple baselines.
## Why
The evidence supports measurement/model qualification, not the broader planner product. A correct smaller artifact is more valuable than unvalidated infrastructure recommendations.
## Consequences
M1.5/M2 pass; M3 is assessed and deferred; M4 is a controlled pass with general calibration partial; M6 is a functioning exploratory application, not a full scientific gate. M5/M7/M8/M9 are intentionally gated. No cloud spend or publication.
## Risks
One controlled and one small real application do not prove simulation lacks value elsewhere. An actual tool-heavy workload could reverse the decision. External adoption/maintainer demand remains unmeasured.
## Evidence
[M4](../validation/milestone-4.md), [M6](../validation/milestone-6.md), raw artifacts, [adversarial review](../research/adversarial-review.md). AgentServeSim/AISimulate/SimPy already cover substantial engine/planning scope.
## Reversal conditions
A repeatable non-coding production-like workload with materially contended non-LLM pools, independently identified inference behavior and preregistered held-out decisions that justify the calibration effort beyond a utilization heuristic. A maintained upstream engine may remain preferable even if this gate passes.
