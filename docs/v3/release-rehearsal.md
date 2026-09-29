# Clean-checkout release rehearsal

2026-09-29. Rehearsed from a separate local Git clone of commit `f0233179c5012550295f3fcca3255e014b16fe32`, with a fresh Python 3.13.15 environment. The clone includes committed source and tags, without the existing environment or ignored local artifacts. This is a new-contributor reproduction on the same Windows host, not independent external review.

## Results

- 150 tests passed; Ruff lint/format and wheel/source builds passed.
- Fresh installed-wheel qualification passed, including both CLI names, exact installed module checks and frozen-study reproduction. [Raw qualification](release-rehearsal/package-qualification.json).
- The offline audit passed for all 64 protected files and all 72 FRAMES sessions. [Raw audit](release-rehearsal/offline-audit.json). Sixty-one files match the original working bytes exactly; three historical metadata JSON files use the already-recorded Git LF representation instead of the original Windows CRLF representation. The preservation manifest records both. Frozen prediction/evaluation bytes remain exact.
- Existing analytical validation passed, including the independent SimPy comparisons and queue checks; aggregate relative error was 0.016236629663909596. This repeats a reference-engine correctness check, not a new agent-performance experiment. [Raw validation](release-rehearsal/analytical-validation.json).
- A bounded credential-pattern screen examined 284 reachable Git blobs, including XML inside the historical DOCX, and found no matching private-key, GitHub-token, cloud-access-key or provider-token patterns. [Screen details and limits](release-rehearsal/history-screen.json). It is not a comprehensive privacy or ownership guarantee.

Qualification and the final audit recorded a clean source state. Initial generated root-level reports were moved into ignored `artifacts/ci/` before the final audit, so report generation no longer made Git appear dirty. The original working repository and research tags were not rewritten.

## CI completion

The workflow now fetches complete history for the preservation audit, explicitly selects each matrix interpreter, saves JUnit and qualification reports, and retains them for 14 days. It runs on push, pull request or manual dispatch. Official action versions are pinned to resolved commit IDs. Matrix failures do not cancel other platforms; stale workflow runs can be cancelled by a newer run on the same ref. These changes prepare hosted verification; no hosted run is claimed yet.

The proposed external step is specified in [PUBLIC_RELEASE.md](../../PUBLIC_RELEASE.md). The source and package remain experimental and the prior scientific limitations are unchanged.
