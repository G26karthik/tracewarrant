# Verified final experimental patch 0.7.1

Published 2026-10-14: [TraceWarrant 0.7.1](https://github.com/G26karthik/tracewarrant/releases/tag/v0.7.1). All four
[V9 gates](../../PROJECT_V9.md) passed. Performance bundle verification now
requires its supplied HTML to match recomputation, even when a changed report
has an updated checksum. Four regression cases reproduced the defect before the
fix. Existing wire formats, policies, report generation and JSON decisions remain
compatible. Quality bundles already check JSON and HTML.

Qualified source/immutable peeled tag: `ecc0ebe1c224a9345b355d38ef44a0a0c6f1ac61`. Annotated tag object:
`a976ff9075680d297336bd65a80dbeaf717d9e74`. [PR #5](https://github.com/G26karthik/tracewarrant/pull/5) merged
the patch. Main includes later acceptance documentation; do not move the tag.

[Source CI 38579068103](https://github.com/G26karthik/tracewarrant/actions/runs/38579068103) and [tag CI 38579595599](https://github.com/G26karthik/tracewarrant/actions/runs/38579595599)
passed all five jobs: Windows/Ubuntu Python 3.11/3.13 plus analytical validation.
Each source matrix artifact contains 292 tests with zero failures/errors/skips,
fresh installed package/workflow qualification and the preservation audit.
The fresh installed probe explicitly refuses rehashed false performance HTML
with exit 2 and no output, without a checkout, simulator or runtime dependency.

All ten draft asset sizes/SHA256 digests were verified before publication. All ten
unauthenticated public downloads returned HTTP 200 and match qualified local
bytes/GitHub digests. SHA256SUMS binds nine payloads. Permanent hosted evidence
is attached in hosted-ci-evidence.zip; portable-evidence-examples.zip contains
native FRAMES performance and HotpotQA quality bundles.

A fresh environment containing only the downloaded wheel, outside any checkout,
replayed performance with exit 0 and its explicit performance-only scope, and
quality with exit 1 and the original failed gates/binding. Rehashed false HTML in
both bundles and a rehashed omitted quality task were refused with exit 2 and no
report. A separate fresh install qualified the downloaded wheel/source pair
against the exact clean source, matching installed module bytes, both commands,
all existing workflows and the frozen evaluation. [Public proof](public-release-0.7.1.json).

All 64 protected files, prior tags and failed studies remain preserved. No model
was run, answer regraded, private data published or paid/cloud service used. Core
runtime remains dependency-free and Apache-2.0. No PyPI upload occurred.
The quality result is still 4/8 exact and mean F1 0.541667, failed; its binding is
retrospective. The FRAMES performance pass does not assess task quality or prove
model superiority. Hashes/replay do not authenticate authors, scores or chronology.

The original ten V3 criteria and bounded V4–V8 increments are accounted for in
[final acceptance](acceptance.md), with [machine-readable scope closure](acceptance.json).
**Required remaining stages: zero.** This closes the agreed experimental toolkit,
not production readiness, independent adoption or stronger scientific success.
Further work is a new requirement or maintenance, not an unfinished stage.
