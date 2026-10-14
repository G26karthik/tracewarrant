# Verified experimental collection release 0.8.0

[TraceWarrant 0.8.0](https://github.com/G26karthik/tracewarrant/releases/tag/v0.8.0) is published and publicly verified.
All four [V10 gates](../../PROJECT_V10.md) are complete. A bounded stdlib recorder
now collects explicitly owned operation/resource boundaries and known edges;
an optional caller-supplied SDK exporter and pinned Pydantic AI companion example
use the same primitive. Scheduling remains caller-owned; public recording accepts
no prompts, outputs, arguments, SQL strings, exception messages or arbitrary labels.
[Interface and limits](collection.md), [machine-readable public proof](public-release-0.8.0.json).

Qualified clean source/peeled tag: `c8ae1af15e8d3e60972e72c5bcca27ad30775714`. Annotated tag object:
`7fc5eaa66c29546c1fe7be4536e833040e207607`. [PR #7](https://github.com/G26karthik/tracewarrant/pull/7) merged
the implementation. Main includes later closeout documentation; never move the tag.
[Source CI 38592818864](https://github.com/G26karthik/tracewarrant/actions/runs/38592818864) and [tag CI 38593907594](https://github.com/G26karthik/tracewarrant/actions/runs/38593907594)
passed all five jobs: Windows/Ubuntu Python 3.11/3.13 plus analytical validation.
Each source matrix has **317 tests, zero failures/errors/skips**, fresh installed
core/locked-SDK qualification, collection-cost measurement and preservation audit.

All thirteen draft asset sizes/digests were verified before publication. All
thirteen unauthenticated downloads returned HTTP 200 and exactly match qualified
local bytes and GitHub SHA256 digests. SHA256SUMS binds twelve payloads; source
provenance binds eleven. hosted-ci-evidence.zip permanently retains all five
source job artifacts. collection-example.zip supplies a runnable stdlib collector,
two content-free traces, their exact inspection reports and instructions.

A fresh environment containing only the downloaded wheel, outside any checkout,
collected new actual SQLite work and inspected it. Both downloaded trace inspection
reports replayed byte for byte. The explicitly closed plain example has one
declared dependency and resource coverage 2/2. The framework example retains
two companion traces, eight total spans and four atomic operations: owned queue,
occupancy and capacity coverage is **2/4, partial**, dependency graph and prediction
suitability unsupported, and GPU service demand UNKNOWN. Model calls remain
uninstrumented. Pydantic AI 2.51.0 TestModel/OTel SDK 1.45.0 execution is interface
qualification, not real task quality, a new service run or external adoption.

The wheel-only environment has no core runtime dependencies or SDK/simulator
imports. A separate fresh install of the public wheel/source pair against exact
clean source verified all installed module bytes, commands and existing workflows.
Another separately supplied locked-SDK fresh environment verified exported IDs,
timestamps, roles/edges, refusal on exporter failure, unchanged global provider
and model permissions, and correct partial native coverage using that downloaded
wheel. Source examples are harness inputs; the core in those SDK checks is installed.

The existing downloaded portable performance bundle still replays with exit 0
and explicit performance-only scope; quality replays with exit 1 and its original
failed gates/retrospective binding. Rehashed false HTML in both bundles and omitted
quality membership still return exit 2 and create no report. Hashes and replay
do not authenticate authors, scores or chronology.

## Collection cost and memory

The exact-source local microbenchmark uses five alternating paired fresh-process
runs, each with 500 real SQLite operations on 10,000 generated rows and the same
actual semaphore work. Median added collection time is **114.919 microseconds
per operation**, with **29.21% elapsed loop overhead**. This is material
for short operations. Final serialization is excluded from the loop and measured
separately in the raw asset. Maximum measured process peak is **35.29 MiB**;
the original installed SDK probe peaks at **116.07 MiB**. Public
download SDK qualification has its own recorded peak in the machine-readable proof.

| Hosted source matrix | Added microseconds/operation | Elapsed loop overhead | SDK process peak MiB |
| --- | ---: | ---: | ---: |
| qualification-ubuntu-latest-py3.11 | 149.199 | 37.13% | 100.94 |
| qualification-ubuntu-latest-py3.13 | 96.595 | 24.32% | 106.90 |
| qualification-windows-latest-py3.11 | 108.194 | 42.00% | 104.83 |
| qualification-windows-latest-py3.13 | 82.248 | 28.67% | 114.95 |

All measured local/hosted processes met the provisional 2 GiB ceiling. This
machine actually reports about 31.2 GiB physical RAM; no 16 GiB hardware run is
claimed. Peaks include the interpreter/dependencies/database; the ceiling is not
a universal guarantee at maximum configured capture size. These timings do not
establish negligible overhead, speedup, useful-agent capacity or general workload
performance. Use bounded operation-level captures and measure your workload.

Cancellation before acquisition fabricates no release; acquired-body failures
perform real cleanup and preserve the original exception. Cleanup/clock faults,
abandoned captures, limits and contradictory capacity are tested/refused. Caller
callbacks, capacity and completeness remain declarations. Local cleanup does not
prove remote cancellation; a span tree does not prove a complete causal graph.

All 64 protected files, ten historical tag targets, original frozen evaluation
bytes and negative studies are preserved. HotpotQA remains 4/8 exact, mean F1
0.541667, failed; FRAMES still establishes no added intervention decision value.
No model rerun, regrading, private answer publication, paid/cloud resource or
PyPI upload occurred. Core remains dependency-free, Python 3.11+, Apache-2.0.

**Remaining required V10 stages: zero.** V3–V9 acceptance remains unchanged.
The agreed experimental toolkit plus this separately authorized increment is
complete. Production readiness, external adoption and model superiority remain
unestablished. Further work requires a new concrete requirement or maintenance.
