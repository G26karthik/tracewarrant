# TraceWarrant 0.3.1 public release closeout

Published and verified 2026-09-30; closeout documentation recorded 2026-10-01 (Asia/Kolkata). The scoped V3 experimental toolkit and first public GitHub prerelease are complete. [Repository](https://github.com/G26karthik/tracewarrant), [prerelease `v0.3.1`](https://github.com/G26karthik/tracewarrant/releases/tag/v0.3.1), [machine-readable verification](public-release-0.3.1.json).

Release source: `b0d5c5dc2a23589245ad1c6fabdf4d07dd2b51b6`. The annotated `v0.3.1` tag points to that exact source. Later closeout documentation on `main` does not change the tag or replace the assets. The earlier local `tracewarrant-0.3.1` tag and all research tags remain unchanged.

## Verified completion gates

| Gate | Evidence |
| --- | --- |
| Public source | Public `G26karthik/tracewarrant`, default branch `main`, Apache-2.0, private vulnerability reporting enabled |
| Exact-source hosted checks | [Run 36757290326](https://github.com/G26karthik/tracewarrant/actions/runs/36757290326): all five jobs successful; four OS/Python jobs each passed 150 tests, lint/format, build, installed qualification, preservation audit and CLI smoke checks; Ubuntu analytical validation passed |
| Tagged-source verification | [Run 36758043469](https://github.com/G26karthik/tracewarrant/actions/runs/36758043469) also passed on the same source after the new tag was pushed |
| Final local package pair | Fresh separate checkout, Windows Python 3.13.15; clean metadata; wheel/archive code and reproduction inputs match checkout |
| Uploaded artifacts | Eight assets; all GitHub-reported SHA-256 values and sizes match local files; seven payloads bound in `SHA256SUMS` |
| Public access | All eight assets downloaded through unauthenticated HTTP with status 200; all bytes match the upload source and checksum manifest |
| Public-download installation | Fresh isolated installation of the downloaded wheel; installed module hashes match wheel, both CLI names work, schema/check/conformance work, evaluation reproduces byte for byte without simulation/calibration/SimPy imports |
| Historical evidence | 64 protected files accepted; original pilot tag unchanged; all 72 adapted FRAMES graphs complete; exact frozen evaluation reproduced |

The release retains hosted evidence in `hosted-ci-evidence.zip`; it does not depend on the workflow artifact service's 14-day retention. `source-provenance.json`, `package-qualification.json` and `offline-audit.json` bind qualification to the exact source. These generated reports retain their original metadata; publication does not convert them into independent maintainer review.

Main distribution checksums:

| Asset | SHA-256 |
| --- | --- |
| `tracewarrant-0.3.1-py3-none-any.whl` | `78a03bd51c4015500528e449a115c0536fff8d1966f90fc8654179edf7c13c7b` |
| `tracewarrant-0.3.1.tar.gz` | `2f2fcde7cbac92f04c8ead7cac3a88221423fdf070d975c64397aa016060ebec` |

## What is complete

V3-A/B/C/E deliver the observation contract and research/preservation record, three-source conformance, neutral bounded artifacts and freezes, independent evaluation with cheap baselines, reproducibility and release qualification. V3-D executed its preregistered external-workload study and retained the negative findings. No stage requires a model victory. The initial [V3 report](../../V3_PROJECT_REPORT.md), [local completion report](completion-0.3.1.md) and frozen raw evidence remain historical records.

There is no pending required core feature or release action. The toolkit remains experimental. FRAMES had 1.50% median mean-latency prediction error and 2/2 material rankings, but utilization chose the same intervention and strict exact-answer quality passed 0/48 held-out sessions. This does not establish a quality-qualified agent, production capacity planning, identified GPU service demand, added decision value, independent adoption or scientific uniqueness.

No PyPI upload, paid inference, cloud provisioning, outreach, native/CUDA rewrite or optimizer expansion was performed. A future scientific or product expansion needs a separately justified scope; it is not unfinished work for this release.
