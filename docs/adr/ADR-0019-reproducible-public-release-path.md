# ADR-0019: Rehearse publication from committed source

Status: accepted, 2026-09-29. Public upload awaits the maintainer's release decision.

## Context

The 0.3.1 candidate was qualified in the working checkout and installed environments. A new contributor must also be able to reproduce it from committed files alone. The configured CI did not run the complete preservation audit or retain machine-readable evidence, and a shallow checkout would omit the historical tag that audit verifies.

## Decision

Rehearse from a separate local Git clone with fresh dependencies. Preserve historical files/tags, run tests, build the distributions, qualify the installed wheel, reproduce the frozen evaluation and run the existing independent analytical checks. Generated evidence belongs under ignored `artifacts/` paths, so producing reports does not itself mark the source dirty.

CI fetches full history for the preservation audit, selects each matrix interpreter explicitly, records JUnit and qualification outputs, and uploads those reports for 14 days even when a later check fails. Official checkout/setup-python/upload-artifact actions are pinned to the resolved commits of their existing major versions. CI permissions remain read-only; the workflow contains no publication step or provider credentials. The analytical job retains its separate result.

The first proposed public action is a GitHub repository and experimental release, with private vulnerability reporting. It is not a PyPI release. Keep the existing PyPI upload-prevention classifier. Publish normal research history, including unfavorable observations, rather than rewriting it for presentation.

## Consequences

The public decision can be made against a concrete repository identity, release description, asset list and reproducible evidence. The original V3 brief's public-release boundary still applies. Hosted Actions and independent community review remain unperformed until their results actually exist.
