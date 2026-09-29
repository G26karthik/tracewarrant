# ADR-0018: Controlled comparisons and local release qualification

Status: accepted, 2026-09-29. Extends V3; no change to the frozen research conclusion.

## Context

The completion review reproduced four defects: producers could freeze different environments into one comparison group; the material-effect calculation imposed an undocumented `1e-30` denominator floor; a single available scenario could establish "no added decision value"; and an unserializable output could leave an empty, exclusively created file behind.

These defects were demonstrated with failing regression tests before correction. The FRAMES study does not exercise them, and its exact-byte evaluation must remain reproducible.

## Decision

Within each comparison group, every prediction producer must declare the same environment across scenarios. Deliberately changed variables belong in `configuration`; different environmental strata require different comparison groups. Measurement drift still disqualifies intervention decisions while retaining descriptive error rows and envelope diagnostics. This checks declared controls only; it cannot detect omitted confounders.

Compute relative material effects without a unit-dependent positive floor. Equal observations, including two zeros, are nonmaterial before division. Single-scenario groups can support metric-error analysis but cannot establish intervention decision value. Serialize a complete JSON output before exclusively creating its path.

Keep the artifact schema and valid report format at 1.0; tighten cross-artifact semantics in package 0.3.1. Explicit ordinal rankings remain separately declared forecasts and take precedence over numeric point rankings, as in 0.3.0. They are not silently reconciled or re-derived from point estimates; producers must document their ranking rule in model method/assumptions.

Qualify the local distribution in a fresh environment with no runtime dependencies. Verify installed module bytes against the wheel, compare wheel code with the source archive, exercise the installed CLI and reproduce frozen evaluation without importing the reference simulator. Run existing tests on Windows and the available Ubuntu WSL installation. Add the installed-package check to CI; a local WSL result is not a hosted-CI or independent-maintainer result.

## Consequences

Previously accepted bundles with conflicting declared controls now fail before freezing or evaluation. The patch does not change existing valid research results. Public publication still needs a chosen identity, destination and private reporting contact. The failed quality gate and lack of added simulator decision value remain preserved, not targets for post-hoc repair.
