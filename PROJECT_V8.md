# V8 — portable application quality evidence

Authorized by the maintainer's next-stage request on 2026-10-14. V7 and its
verified 0.6.0 release are closed. Preserve every failed study and historical tag.

Concrete gap: quality qualification has no native portable export/replay, while
performance jobs do. A reviewer otherwise copies input files and trusts a supplied
report. Add `bundle-quality` and `verify-quality-bundle` for exact-byte snapshots
of sample/policy and optional plan/receipt. Recompute both JSON and HTML from a
private snapshot; reject changed inputs, false reports even with updated hashes,
missing/unlisted files, incomplete binding, arbitrary names and symlink entries.

Integrity cannot establish honest measurement, independent grading, authentic
chronology or initial roster completeness. A caller can replace all evidence and
produce a consistent new bundle. The retained failed HotpotQA sample demonstrates
the workflow retrospectively; no model is run or answer regraded.

Gates: A bounded snapshot/export/replay; B refusal/compatibility tests and example;
C installed and hosted qualification; D documentation and verified experimental
0.7.0 release. No cloud, model rerun or new performance experiment is needed.

Status: A/B implemented, 288 local tests passed. C/D in progress. This document
does not claim public release or external review until those gates pass.
