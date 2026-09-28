# ADR-0016: Make observation and model validation the product

Status: accepted, 2026-09-29.

## Context

The frozen V2 pilot found accurate controlled predictions but no added intervention choice value over utilization, and unidentified real inference service demand. The maintainer explicitly accepts the pivot and requests a framework- and simulator-neutral toolkit. ADR-0015 remains the historical evidence-based recommendation.

## Decision

V3 implements an observation contract, conformance inspection, independent prediction/measurement artifacts, freeze/evaluation workflow and baseline comparison. The existing DES remains a reference backend, not a required dependency of the validation API. Preserve all old results. Reject unsupported claims without assigning a fake confidence score.

## Alternatives

Continue the planner/optimizer: rejected because its gate remains unmet. Replace established simulators or observability backends: rejected because adapters and small interchange artifacts are cheaper and easier to independently adopt. Documentation-only pivot: rejected because an external user needs runnable inspection and validation.

## Consequences

Schemas require explicit metric meanings, units, denominators, scenario lineage and calibration boundaries. Integrity receipts provide tamper evidence, not proof of chronology or ground truth. External workload selection is recorded before intervention results. Null/missing results, heuristic wins and feasibility failures are first-class outputs.

## Validation

V3-A through V3-E in `PROJECT_V3.md`; separate claim support from numeric provenance; two independent model sources and multiple trace sources must exercise the public interfaces.

## Supersession

This adopts ADR-0015's recommended product direction and supersedes V2's prospective planner roadmap only. It does not modify the pilot's evidence, classifications or previously accepted simulator semantics.
