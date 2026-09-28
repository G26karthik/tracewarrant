# ADR-0017: Data-only interchange and explicit integrity limits

Status: accepted, 2026-09-29.

## Context

V3 must work with any simulator and cheap heuristic, while protecting the distinction between prediction and observation. The prior DES and cohort fitter cannot be required by interchange consumers.

## Decision

Use a closed JSON Schema 2020-12 plus documented semantic checks for predictions, protocols, freeze receipts and measurements. IDs, metrics, interval meanings, populations, provenance and comparison groups are explicit. Preserve ordinal-only heuristics without fabricating numeric forecasts. Bind exact bytes by SHA-256 and require measurements to declare collection after the freeze and link its digest. Declare that this does not authenticate time or collector truth.

## Alternatives

Reuse DES Scenario types: rejected, because it couples model inputs with independent predictions. Execute producer plugins in the validator: rejected, because data-only interchange is sufficient. Depend on a remote registry/timestamping service: deferred until users require attestation. Runtime JSON-schema package: unnecessary for the small fixed vocabulary; use it as an independent development oracle and export a standard schema.

## Consequences

No automatic units/population conversions or aggregate confidence score. Tail samples, task quality and model economics remain study responsibilities. Baseline equality and negative results are valid outcomes. Bounded inputs and cross-product budgets limit comparison memory. Exporter/schema parity and adversarial mismatch tests are required before the gate.

## Validation

Tests cover a baseline beating a model, missing/non-measured references, inconsistent replications, schema interoperability, tampering, privacy, chronology, units and outcome conservation. End-to-end external collection will use a SimPy producer and simple independent heuristic producers.
