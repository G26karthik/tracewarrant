# ADR-0022: separate application-quality qualification from model validation

Date: 2026-10-14. Status: accepted for V6.

V5's measured application qualification needed three simultaneous criteria:
completion, normalized exact-answer fraction and mean answer token F1. The V4
job format supports one fraction metric, and requires performance predictions
and a freeze. Using it before workload feasibility would need fabricated inputs.

Add a separate bounded sample/policy format and offline core CLI, with every
offered task in the denominator and explicit unsupported evidence. Keep V4 job
and V3 artifact schemas intact; do not widen frozen formats or silently reinterpret
mean F1 as binary fraction. A sample-quality pass does not assert model validity.

Prefer caller-provided evaluator scores to a grading service. No text capture,
model judge, cloud endpoint, plugin loader or framework dependency enters the
runtime. Reuse strict fixed-schema validation, safe new-directory reports and
the actual failed V5 scalar evidence. Missing scores remain unknown rather than
being filtered. Provenance is declared; hashes cannot authenticate the collector.

Existing performance validation remains useful after a separately designed,
qualified application sample. A new command supports that prerequisite without
reviving capacity planning or changing any historical quality outcome.
