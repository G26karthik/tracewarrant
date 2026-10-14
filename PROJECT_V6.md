# V6 — reusable application-quality qualification

Authorized by the maintainer's continuation on 2026-10-14. V5 remains closed
with its failed quality gate; no prompt, task, model or threshold is retuned.

Measured product gap: V5 requires completion, exact match and mean answer F1,
but the core job policy only accepts one fraction metric and needs performance
predictions/freezes. A feasibility decision should not require fabricated
forecasts. Promote the useful gate to a small offline core interface.

Deliver: strict bounded sample/policy schemas, offered-population completion and
multiple quality gates, `qualify-application` CLI, JSON/HTML reports and a
lineage-checked adapter for the unchanged V5 evidence. Missing evidence must stay
unsupported; failed/censored cases must never vanish from denominators. Core
runtime remains dependency-free and cannot run a model, grade text or download
anything. Hashes record lineage, not author authenticity or semantic correctness.

Gates: A formats/decision semantics; B CLI/reports/privacy and adversarial tests;
C real retained-study adapter plus fresh installed-package/hosted qualification;
D documentation, integration and qualified experimental release 0.5.0.

**Status: all four scoped V6 stages complete; experimental 0.5.0 published and
publicly verified.** A/B delivered strict offered-population semantics, CLI and
escaped reports with refusal/adversarial coverage; C verified unchanged V5 export,
fresh installed code and all five hosted jobs (244 tests per matrix job); D
completed documentation/integration, exact-source release, all ten public asset
downloads and source-free installed example replay. [Closeout](docs/v6/public-release-0.5.0.md).

Existing schemas, freezes, 64 protected files
and public releases remain unchanged. A policy pass is only a sample-quality
decision, never performance-model acceptance or production certification.
