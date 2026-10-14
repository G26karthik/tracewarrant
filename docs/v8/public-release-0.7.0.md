# Verified experimental 0.7.0 release

Published 2026-10-14: [TraceWarrant 0.7.0](https://github.com/G26karthik/tracewarrant/releases/tag/v0.7.0).
All four scoped [V8 stages](../../PROJECT_V8.md) are complete. Native portable
application quality export and checksum/JSON/HTML replay fill the manual evidence
sharing gap. Existing quality schemas/gates and performance workflows remain
compatible. [Workflow and budgets](quality-bundles.md).

Qualified source and immutable peeled tag:
`da3da5d799a7c1ed351c40ad45ffc8cd1e381119`; annotated tag object
`4c0ac1340988903d4f612e6fd25f8ccc2045946b`. [PR #4](https://github.com/G26karthik/tracewarrant/pull/4)
merged the feature. Current main includes later closeout documentation; never
move the release tag to that documentation commit.

[Exact-source CI 38569379493](https://github.com/G26karthik/tracewarrant/actions/runs/38569379493)
and [tag CI 38569663474](https://github.com/G26karthik/tracewarrant/actions/runs/38569663474)
passed all five jobs: Windows/Ubuntu Python 3.11/3.13 tests, fresh package/workflow
qualification and preservation, plus analytical validation. Each source matrix
artifact contains 288 tests, zero failures/errors/skips. 28 new tests cover
snapshot consistency, bound/unbound portability, rehashed false JSON/HTML, dropped
tasks, malformed/missing/extra/oversized inputs, links, exits and exclusive rollback.

Ten uploaded assets were verified by size/SHA256 before publication. All ten
unauthenticated public downloads returned HTTP 200 and matched qualified local
bytes and GitHub asset digests; SHA256SUMS binds nine payloads. Permanent hosted
evidence is in the release's hosted-ci-evidence.zip. The example ZIP contains a
native seven-file bound quality bundle with its own SHA256SUMS.

A fresh wheel-only environment outside any checkout verified the downloaded
bundle with exit 1 and matching original gates/binding. A rehashed false HTML
report and a rehashed omitted task both returned 2 without output. The downloaded
wheel/source pair passed a separate fresh installed qualification against the
exact clean source, including installed module hashes, both CLI names, bound/
unbound quality replay and old frozen evaluation. Core dependencies remain empty;
no simulator was imported. [Machine-readable public proof](public-release-0.7.0.json).

All 64 protected files and historical tags remain preserved. No model was run,
answer regraded or failed study changed. The original HotpotQA result is still
4/8 exact, mean F1 0.541667 and failed; its later roster is retrospective.
Checksums establish consistency, not authorship, independent grading, authentic
preregistration or honest initial roster completeness. Entirely replaced,
consistent evidence can form another valid bundle. Production readiness, adoption
and model superiority remain unestablished. No PyPI publication or paid/cloud work.

No V8 engineering/release gate remains. A further increment needs a distinct
demonstrated requirement; do not restart this release or resurrect closed studies.
