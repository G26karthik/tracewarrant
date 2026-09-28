# ADR-0013 Explicit observed resource lifecycle

Status: ACCEPTED

Date: 2026-09-29

## Context
M1.5 exercised actual asyncio resource contention and PydanticAI 2.51.0 TestModel instrumentation. Ordinary framework spans have no explicit joins or queue/service decomposition. Three captured spans even have zero recorded duration; the cause was not established and those values are not a service model.
## Requirements
Directly identified queue/occupancy intervals, explicit unknowns, bounded content-free fields and no guessed DAG edges.
## Alternatives considered
Infer queues from wall duration; patch a framework's scheduler; minimally instrument owned pools and retain framework traces as incomplete observations.
## Decision
Add optional Observation to instance schema 0.2. Derive queue only from enqueue/acquisition and occupancy only from acquisition/release, reject conflicting components. Keep active-operation and release boundaries distinct for cancellation lag. Keep the core free of runtime dependencies; pin one optional integration group.
## Why
The controlled execution establishes representability without abusing parentage. The external path demonstrates a real limitation, not universal compatibility.
## Consequences
The original 0.1 input shape remains accepted; output schema is 0.2. No automatic trace-to-service fitting is justified by this gate. Minimum contract is documented separately.
## Risks
Owned-pool wrappers cost integration effort. Clock/sampling issues and shared resources require experiment manifests. Model stubs do not validate inference fidelity.
## Evidence
[M1.5](../validation/milestone-1.5.md), [contract](../design/instrumentation-contract.md), checked-in actual trace artifacts and semantic tests.
## Reversal conditions
If production instrumentation is too invasive or additional lifecycles cannot fit one acquisition per node, narrow to validation/adapters or version the lifecycle model before predictive use.
