# Experimental 0.6.0 closeout

Published 2026-10-14: [v0.6.0](https://github.com/G26karthik/tracewarrant/releases/tag/v0.6.0).
Qualified source/tag target `086123bc5bf3b3f8b114716de2f337f0bfa6ef81`, merged
through [PR #3](https://github.com/G26karthik/tracewarrant/pull/3). V7's four scoped
stages are complete: strict plan/receipt formats and exact binding; CLI/refusal/
compatibility/retained-data integration; installed/hosted qualification;
documentation and a verified public prerelease.

`freeze-quality` binds exact application plan/policy bytes. Optional qualification
flags enforce workload/sample identity and entire declared task membership.
Changed policies/plans, missing/substituted/additional tasks and malformed receipt
dates are refused before reports. Existing sample/policy formats and unbound JSON
decision fields stay compatible; core runtime remains dependency-free.

## Exact-source evidence

All five [source CI jobs](https://github.com/G26karthik/tracewarrant/actions/runs/38537748030)
and [tag CI jobs](https://github.com/G26karthik/tracewarrant/actions/runs/38538161522)
passed the exact release source. Windows/Ubuntu Python 3.11/3.13 each ran 260 tests
with zero failures/errors/skips, lint/format, distribution builds, fresh installed
module/CLI/schema/bound/unbound qualification and preservation/workflow checks.
Ubuntu Python 3.12 analytical validation passed. Source CI artifacts are attached
permanently in the evidence ZIP.

A separate clean checkout was explicitly pinned to the merge SHA before build.
Its wheel/source archive/current-source bytes matched; fresh installed qualification
verified both CLI aliases, receipt creation, exact bound negative replay and all
historical paths without runtime dependencies or simulator imports. All 64
protected files and the byte-exact original V3 evaluation were preserved.

## Public verification

Release ID `412511475`, published UTC `2026-10-14T08:53:30Z`, prerelease true,
draft false. Ten uploaded asset sizes/GitHub digests matched local qualified
payloads before publication. After publication, all ten assets were independently
downloaded with no Authorization header (HTTP 200), identical sizes/bytes/SHA256.
SHA256SUMS verified all nine payloads. [Public proof](public-release-0.6.0.json).

Assets: wheel, source archive, checksums, package/workflow qualification, offline
audit, source provenance, hosted CI evidence ZIP, quality example ZIP and notes.
The downloaded wheel alone was installed into a fresh environment without pip,
source checkout or extra distributions. Bound example JSON/HTML matched qualified
source bytes exactly, with expected exit 1: binding verified for eight tasks, but
original exact/F1 floors failed. Removing one declared row produced exit 2 and
no report directory. A separate fresh check also qualified the downloaded
wheel/source pair against exact source and all installed historical/new paths.

The example roster/receipt was created after the V5 study and is **retrospective**.
It is not the historical preregistration or a new successful experiment. All V5
scores, thresholds and records stay unchanged. Binding verifies only supplied
bytes and declared membership; it cannot prove trusted chronology, collector
honesty, execution, completeness of an initial plan or semantic answer quality.
Reports retain `chronology: not_authenticated` and the original uncertainty limits.

Prior release/research tags remain unchanged. Public evidence excludes private
answer text. No model rerun, PyPI upload, paid/cloud resource or outreach occurred.
Production readiness, adoption and added model decision value remain unestablished.
[Quality-plan guide](quality-plans.md), [V7](../../PROJECT_V7.md),
[preserved V5 result](../v5/results.md).
