# ADR-0003 OpenTelemetry ingestion

Status: ACCEPTED

Date: 2026-09-28

## Context
Vendor formats vary and GenAI conventions are evolving.
## Requirements
Local modular import, content allowlist, explicit supported shape and diagnostics.
## Alternatives considered
Vendor JSON; SDK/protobuf dependency; bounded OTLP JSON subset.
## Decision
Accept ExportTraceServiceRequest JSON and JSONL envelopes with a documented mapping snapshot.
## Why
Gives a common boundary without a collector or framework installation.
## Consequences
No live receiver/protobuf; generic links do not become edges; extensions use workload_lab.*.
## Risks
Schema drift and missing attributes limit compatibility.
## Evidence
[OTLP](https://opentelemetry.io/docs/specs/otlp/), [mapping](../design/otel-mapping.md).
## Reversal conditions
Adopt an official decoder when compatibility/security maintenance exceeds the benefit of the small parser.
