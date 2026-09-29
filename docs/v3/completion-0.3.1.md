# TraceWarrant 0.3.1 completion report

2026-09-29. The authorized local V3 engineering and open-source preparation are complete. The selected public name is **TraceWarrant**, with Apache-2.0 licensing and the tagline **Check the evidence behind performance claims.** Public upload remains prospective. This is an experimental toolkit, not a validated production capacity planner.

## What changed

The completion review reproduced four defects with failing tests before fixing them:

1. Conflicting prediction environments could enter the same controlled comparison, including across model producers. Freeze and evaluation now refuse those bundles; intentional intervention variables belong in configuration.
2. A hardcoded `1e-30` denominator floor hid material differences at small numeric scales. Relative comparisons now use the actual denominator; equal and zero observations are handled without division.
3. One available scenario could incorrectly establish no added decision value. It now supports metric errors only, with insufficient evidence for a decision comparison.
4. JSON serialization failure could leave an empty output file. Serialization now finishes before the exclusive file creation.

The project now builds as `tracewarrant` 0.3.1 and supplies a `tracewarrant` command. The `workload-lab` alias, `workload_lab` Python API, `workload_lab.*` trace bindings, schema 1.0 identities and old commands remain compatible. Historical documents, raw observations and frozen predictions keep their original names and bytes.

A reusable distribution qualification harness checks a fresh dependency-free installation, installed module hashes, source archive contents, both CLI entry points, three trace sources and exact frozen evaluation without simulator imports. It is now part of the configured CI matrix. [Procedure](release-qualification.md), [ADR-0018](../adr/ADR-0018-controlled-comparisons-and-release-qualification.md).

## Verification

| Environment/check | Result |
| --- | --- |
| Windows Python 3.11 | 150 tests pass |
| Windows Python 3.12.12 | 150 tests pass |
| Windows Python 3.13 | 150 tests pass |
| Ubuntu 24.04 WSL, Python 3.12.3 | 150 tests pass |
| Ruff lint/format, diff whitespace | pass |
| Windows and Linux wheel/source builds and fresh installed-wheel qualification | pass |
| Frozen evaluation | reproduces byte for byte |
| V2 preservation | 64 protected files and original pilot tag retained |
| FRAMES reinspection | all 72 adapted graphs structurally complete; original misspelled assertion still refused |
| Hosted CI / independent maintainer review | not performed |

Clean-source machine-readable qualification records: [Windows](qualification-0.3.1/windows.json), [Linux](qualification-0.3.1/linux.json), [offline preservation/reproduction audit](qualification-0.3.1/offline-audit.json). Each includes source/lock/harness hashes and source commit. They qualify the named local builds; they are not independent scientific replication.

The first Linux build attempt used the wrong build interpreter and could not import hatchling. Explicit selection of the Linux development environment corrected it. WSL also cleared temporary tool files between shutdowns, so reusable Linux tools were installed under its user cache. These were environment setup issues; no hosted machine or Docker service was required.

## Research conclusion retained

The initial FRAMES study remains unchanged: 16 calibration sessions, 48 held-out sessions, 1.50% median mean-latency error, the same intervention choice as the utilization heuristic, and 0/48 strict held-out answer checks passing. Better end-task quality, an intervention choice that defeats cheap baselines and external adoption remain unestablished. No new study was selected to manufacture a positive result. [Original assessment](../../V3_PROJECT_REPORT.md).

## Handoff

[START_HERE.md](../../START_HERE.md) is the short refresher for returning to the project. Naming and the proposed `G26karthik/tracewarrant` destination are documented in the [naming decision](naming-2026-09-29.md). GitHub private vulnerability reporting avoids inventing or publishing a personal contact address. No remote was attached, repository created, package uploaded, paid resource provisioned or external message sent.

The public-release action remains prospective because the maintainer said they were considering release. The local upload-prevention classifier remains in place. No further user information is required for local use; see [HUMAN_ACTION_REQUIRED.md](../../HUMAN_ACTION_REQUIRED.md) for that boundary. Native/CUDA/optimizer/cloud work remains evidence-gated and is not part of this completion.
