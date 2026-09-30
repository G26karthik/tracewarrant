# Continuation checkpoint

Updated 2026-10-01. This is the current operational checkpoint; older reports retain their original dates and conclusions. Verify disk and GitHub state before acting. [Public release verification](docs/v3/public-release-0.3.1.json), [earlier inspection snapshot](docs/v3/inspection-2026-09-30.json).

## Completion and next deliverable

The scoped V3 experimental toolkit and first public release are complete. [Prerelease `v0.3.1`](https://github.com/G26karthik/tracewarrant/releases/tag/v0.3.1) was published and its public assets verified on 2026-09-30; this closeout documentation follows on 2026-10-01. No required engineering or release action remains. Completion of this scope does not establish production readiness, scientific superiority or external adoption. [Release closeout](docs/v3/public-release-0.3.1.md).

| Area | Verified state |
| --- | --- |
| Core toolkit | Content-free observation inspection, neutral artifacts, freeze/evaluate interfaces, baselines and explicit unsupported results implemented |
| Local inspection | 150 tests pass; Ruff lint/format pass; preservation and frozen evaluation reproduce |
| Historical preservation | 64 protected files accepted, all 64 original working bytes exact in this folder; `research-pilot-1` unchanged |
| External study | 72 sessions retained, all 72 adapted graphs structurally complete; 16 calibration and 48 held-out sessions |
| Public source | Public Apache-2.0 repository, default branch `main`, private vulnerability reporting enabled |
| Hosted verification | All five jobs passed on release source `b0d5c5d`: Ubuntu/Windows Python 3.11/3.13 and Ubuntu analytical validation; tag-triggered verification also passed |
| GitHub prerelease | Published `v0.3.1`, eight attached assets; all unauthenticated public downloads and checksums verified; fresh downloaded-wheel qualification passed |
| Scientific differentiation | Unestablished: model and utilization heuristic chose the same intervention; strict answer quality passed 0/48 held-out sessions |
| Production and adoption | Unestablished; neither hosted CI nor package qualification establishes these |

The inspection found no failing required check or known unfinished core feature. It does not create a requirement to find a model victory, revive the old planner, add native code, run paid experiments or obtain adoption before honestly releasing the scoped experimental toolkit.

## Exact source and remote checkpoint

- Workspace: `C:\Users\saita\OneDrive\Desktop\AI Everyday\Context - Aware`.
- Qualified release source: `b0d5c5dc2a23589245ad1c6fabdf4d07dd2b51b6`. The release tag remains at that source.
- Remote: `origin`, `https://github.com/G26karthik/tracewarrant.git`; default branch `main` contains the qualified source and subsequent closeout documentation.
- Resolve actual local HEAD, branch and `origin/main` with Git. Closeout documentation is a later commit than the release tag, not a replacement release build. The working checkout's `main` is fast-forwarded during closeout; the former work branch `codex/v3-completion` retains its history.
- GitHub account used for authorized publication: `G26karthik`. Check existing `gh auth status`; never print credentials or ask for tokens in chat.
- Release-source run: [36757290326](https://github.com/G26karthik/tracewarrant/actions/runs/36757290326), source `b0d5c5d`, five jobs successful. [Tag-triggered run 36758043469](https://github.com/G26karthik/tracewarrant/actions/runs/36758043469) also passed on the same source. Evidence is retained in the release's `hosted-ci-evidence.zip` beyond workflow artifact retention. Earlier evidence under `artifacts/public-release/initial-ci/` remains a separate snapshot.

Important immutable tag targets:

| Tag | Peeled commit | Meaning |
| --- | --- | --- |
| `research-pilot-1` | `c0fad29ca78cdaf6325357735d292066d844dcd9` | V2 pilot and accepted pivot conclusion |
| `v3-frames-freeze` | `af3600530774492b4f7be23ec78db93491ad3d5c` | V3 prediction freeze before measurements |
| `validation-toolkit-v3` | `4ffbd076a7b8c9bc5783b91550d3d708a816479f` | Initial V3 delivery |
| `tracewarrant-0.3.1` | `f0233179c5012550295f3fcca3255e014b16fe32` | Earlier local 0.3.1 candidate, preserve unchanged |
| `v0.3.1` | `b0d5c5dc2a23589245ad1c6fabdf4d07dd2b51b6` | Qualified published experimental release |

The public `v0.3.1` tag already exists. Verify it; do not recreate or move it, move a historical tag, or rewrite history.

## Reading order and code map

Read `PROJECT_STATUS.md`, `PROJECT_V3.md`, `PUBLIC_RELEASE.md`, `HUMAN_ACTION_REQUIRED.md`, then the contracts and qualification instructions linked below. `FINAL_PROJECT_REPORT.md` and V2 are frozen history, not the active backlog.

| Location | Responsibility |
| --- | --- |
| `src/workload_lab/ingest.py`, `graph.py`, `ir.py` | Bounded telemetry import, explicit graph semantics and evidence provenance |
| `src/workload_lab/conformance.py` | Observation support, missingness, contradictions and UNKNOWN claims |
| `src/workload_lab/artifact_schema.py`, `artifacts.py` | Artifact schema 1.0, bounded parsing, semantic checks and raw-byte freezes |
| `src/workload_lab/validation.py` | Independent metrics, envelopes, material intervention rankings and baseline decisions |
| `src/workload_lab/cli.py` | Compatible `tracewarrant` / `workload-lab` commands; simulator imported only when needed |
| `benchmarks/qualify_package.py` | Fresh installed-wheel verification against wheel, source distribution and checkout |
| `benchmarks/v3_audit.py` | Protected history, original/adapted traces and exact frozen evaluation reproduction |
| `tests/`, `.github/workflows/ci.yml` | 150 regressions, OS/Python matrix, installed qualification and analytical checks |

Public package: `tracewarrant` 0.3.1, Python >=3.11, no third-party runtime dependencies. Retain `workload_lab` imports, `workload-lab`, wire bindings and schema URNs. Keep `Private :: Do Not Upload`: PyPI publication is outside scope. Development dependencies are locked in `uv.lock`; this host uses uv 0.9.26 and Windows Python 3.12.12 in `.venv`.

## Completed release checklist

The [autonomous completion prompt](CONTINUE_PROMPT.md) uses an inspect → act → verify → checkpoint → repeat loop without routine approval stops. These gates are now complete: a continuation should first verify the current evidence, then report the completed scope without inventing further work. Diagnose an actual discrepancy if one exists; do not recreate the published release.

1. Inspected Git state, visibility/default branch, release list, CI and private reporting.
2. Pushed clean release source `b0d5c5d` to remote `main`; all five jobs passed that SHA.
3. Built a fresh wheel/source pair in a separate clean checkout; installed qualification and offline audit passed with clean source metadata. [Qualification procedure](docs/v3/release-qualification.md).
4. Bound seven payloads in `SHA256SUMS`; prepared notes, qualification, audit, hosted evidence ZIP and source provenance.
5. Created the distinct `v0.3.1` tag and published the verified draft as an experimental prerelease, with eight assets and no package-registry upload.
6. Verified tag, private reporting, GitHub digests and all eight unauthenticated public downloads. The downloaded pair passed a fresh installed-wheel qualification, including both CLIs and exact evaluation reproduction.
7. Recorded final URLs and source/checksum evidence in active closeout documentation, committed and pushed separately from the immutable release source.

The prerelease, asset verification and closeout are the completion gate. Additional research, cloud deployment, outreach, native/CUDA work and optimizer expansion are not required steps. A new scientific study needs its own clear question and frozen protocol; never run it merely to replace a negative result.

## Local artifact and environment cautions

- `artifacts/` and `dist/` are ignored. Keep useful evidence; do not commit environments, model data or credentials. Use new output names because artifact writers refuse overwrite. Create the parent directory before writing an output.
- `artifacts/handoff-2026-09-30/` retains the fresh local test XML and offline audit generated from clean `cede1a4` before these documentation changes.
- `artifacts/public-release/checkout/` is a separate clean public clone at qualified source `b0d5c5d`, with its own Windows Python 3.13 environment. It was used to build and qualify the final assets.
- `artifacts/public-release/final-b0d5c5d/` retains the uploaded bundle, hosted reports, draft/public digest checks, unauthenticated downloads and downloaded-wheel qualification. The release contains the portable evidence bundle; local ignored files are supplementary.
- `artifacts/release-0.3.1/candidate/` contains an older rehearsal bundle from `4844531`, before public metadata changes. `dist/` also contains older builds. Build new final assets rather than uploading these blindly.
- Package qualification checks installed module hashes and uses an uncached offline install. A reused cached same-version wheel previously gave misleading results; `uv --refresh` alone was insufficient. Trust the fresh qualification report and its digests.
- WSL Ubuntu is available, but do not let Linux uv replace the Windows `.venv`. Use a separate persistent Linux environment outside `/tmp`, and pass its interpreter explicitly to `uv build --no-build-isolation`. The host clears `/tmp` across WSL shutdowns. Hosted Linux CI already passed; repeating WSL runs is not necessary for documentation-only work.

## Evidence boundaries

Preserve every file in `docs/v3/preservation.json`, both historical ContextForge handoffs, V2/final reports, frozen predictions/receipts, raw measurements and failed studies. The audit accepts original working bytes or recorded Git representations for three historical metadata files; a fresh checkout can have 61 original-byte matches while all 64 files remain valid.

The FRAMES collector used `workload_lab.graph_complete` instead of `workload_lab.graph.complete`. Original traces remain preserved and refused. `examples/adapt_frames_trace.py` only renames the existing completeness assertion; it invents no dependency edge or timing. Structural completeness is not predictive certification.

FRAMES results: 1.50% median mean-latency relative error; 2/2 material pairs ranked correctly; utilization chose the same intervention (`no_added_decision_value`); strict exact answers passed 0/48 held-out. Inference GPU service demand remains UNKNOWN. Interval point containment is descriptive, not statistical confidence. Read [the results](docs/v3/results.md), [contracts](docs/v3/artifacts-and-validation.md) and [ADR-0018](docs/adr/ADR-0018-controlled-comparisons-and-release-qualification.md) before interpreting rankings or comparison eligibility.

There is no outstanding release gate or maintainer decision. Any future expansion needs a separate justified scope. Never request credentials in chat, silently broaden the product or reinterpret the negative findings as a scientific win.
