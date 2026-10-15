# Verified collector maintenance release 0.8.1

[TraceWarrant 0.8.1](https://github.com/G26karthik/tracewarrant/releases/tag/v0.8.1) is published and publicly verified.
The [remaining-work review](maintenance-0.8.1.md) found no unfinished milestone
or open GitHub issue/PR, but reproduced exception handling defects. The patch
closes those defects with eleven new cases and fresh installed failure checks.

Raised exceptions that evaluate to False now produce ERROR status and the proper
failed/timeout/cancelled outcome. Boolean conversion of caller exceptions is
never invoked. If recording and cleanup fail after acquisition or during release,
the original application error takes priority; otherwise the first observer error
is retained, with cleanup failure as its cause. Both paths validate synchronous
cleanup and close invalid returned coroutines. Real cleanup is called once and
uncertain captures refuse export. Public formats, APIs and scheduling are unchanged.

Eight new cases failed against original source; two further release-clock/cleanup
cases failed before the priority fix. The success-cleanup control passed before/
after. This is internal regression evidence, not independent review. Prior
[V10 acceptance](acceptance.json), releases/tags and negative studies are unchanged.

The same 36 collector cases were also run in separate fresh environments
containing each verified public wheel, outside the checkout. The 0.8.0 wheel
reproduces ten failures and 26 passes; 0.8.1 passes all 36, with zero errors or
skips. Wheel/test-source SHA256 digests and failing case names are recorded in
the public proof. This verifies the regressions against the actual distributions.

Qualified clean source/peeled tag: `4a2577524924bded8daa9d51eea240812e65c2b2`. Annotated tag object:
`e8eed3c07f3deb96c81e5e487e5137b66d4a6657`. [PR #8](https://github.com/G26karthik/tracewarrant/pull/8) merged
the implementation. Main contains later closeout documentation; never move the tag.
[Source CI 38596956524](https://github.com/G26karthik/tracewarrant/actions/runs/38596956524) and [tag CI 38597483063](https://github.com/G26karthik/tracewarrant/actions/runs/38597483063)
passed all five jobs. Each Windows/Ubuntu Python 3.11/3.13 source matrix has
**328 tests, zero failures/errors/skips**, fresh core/SDK installed checks,
collection cost/memory and preservation audit; the fifth job checks analytical
validation. The installed-wheel probe explicitly verifies a false-valued body
failure, ERROR status, failed outcome, original exception identity and token release.

All thirteen draft sizes/digests were verified. All thirteen unauthenticated
public downloads returned HTTP 200 and match qualified bytes/GitHub SHA256.
SHA256SUMS binds twelve payloads; source provenance binds eleven. Permanent
source CI evidence, portable performance/quality bundles, new collector examples,
installed qualification, raw cost measurements and notes are attached.

A fresh wheel-only environment outside a checkout generated actual local SQLite
capture and replayed both downloaded inspection reports byte for byte, with no
SDK/simulator import. Closed plain graph/resource coverage is supported (2/2);
framework resource coverage remains **2/4, partial**, its graph and prediction
suitability unsupported, GPU demand UNKNOWN. A separate fresh public wheel/source
install matches installed module bytes and qualifies existing workflows and the
new failure case. Separately supplied locked-SDK fresh installation qualifies
export identity/timestamps/roles/edges, exporter refusal, native partial coverage
and unchanged global provider/model permissions. TestModel is not real task quality.

Public performance/quality bundle replay retains exits 0/1, its performance-only
scope and original failed quality gates. Rehashed false HTML and omitted quality
membership return exit 2 and create no report. [Machine-readable proof](public-release-0.8.1.json).

## Measured cost and limits

The exact-source five paired fresh-process SQLite runs use 500 actual operations
on 10,000 generated rows per run. Median added collection cost is
**101.958 us/operation**, **24.38% elapsed loop overhead**,
with **34.48 MiB process peak**; SDK qualification peaks at
**115.48 MiB**. Final serialization is measured separately. The
short-operation recording cost remains material; these individual microbenchmark
runs do not establish a general overhead, speedup or agent-capacity result.

| Hosted source matrix | Added us/operation | Loop overhead | SDK peak MiB |
| --- | ---: | ---: | ---: |
| qualification-ubuntu-latest-py3.11 | 153.089 | 39.15% | 99.75 |
| qualification-ubuntu-latest-py3.13 | 62.999 | 19.33% | 107.80 |
| qualification-windows-latest-py3.11 | 167.402 | 47.12% | 105.29 |
| qualification-windows-latest-py3.13 | 92.154 | 25.46% | 116.00 |

All measured processes met the provisional 2 GiB ceiling. Actual local physical
RAM is about 31.2 GiB; a 16 GiB machine was not tested. The ceiling is not a
guarantee at maximum capture size. Caller callbacks/capacity/completeness remain
declarations; local release is not remote cancellation. Hashes/replay do not
authenticate authors, scores or chronology. No model run/regrading, paid/cloud
service, private answer publication or PyPI upload occurred.

All 64 protected files, eleven historical tag targets and original frozen
evaluation bytes are preserved. HotpotQA remains failed (4/8 exact; mean F1
0.541667); FRAMES established no added intervention decision value. Core remains
dependency-free, Python 3.11+, Apache-2.0. Production readiness, external adoption
and model superiority remain unestablished.

**All four maintenance gates complete; required remaining stages: zero.**
No new feature/study is queued. Further maintenance or a concrete new requirement
is separate from the preserved completed experimental scope.
