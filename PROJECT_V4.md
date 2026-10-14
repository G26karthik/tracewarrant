# V4 — a complete offline validation workflow

Authorized 2026-10-14: continue autonomously beyond the completed 0.3.1 release. The next product increment is a usable validation workflow for an application developer or CI job. It preserves the V3 pivot and every frozen research artifact. It does not resume the superseded planner roadmap.

**Status: all five V4 stages complete and publicly verified.** Experimental [0.4.0](https://github.com/G26karthik/tracewarrant/releases/tag/v0.4.0) is published from `a248708`; 190 tests per hosted matrix job, ten assets checked by public download, installed qualification and source-free portable replay passed. [Closeout](docs/v4/public-release-0.4.0.md), [verification](docs/v4/public-release-0.4.0.json).

## Product and completion boundary

Given a directory of neutral prediction/protocol/freeze/measurement files, one command evaluates an explicit acceptance policy, produces a machine-readable result and standalone HTML report, and returns a useful CI exit code. A second command exports a self-contained, checksummed evidence directory that another machine can replay offline. No service, JavaScript, model provider, simulator or runtime dependency is required.

The release remains experimental and is version 0.4.0. Completing this workflow does not prove production readiness, external adoption or model superiority. The existing FRAMES result stays negative. Neither paid/cloud work nor outreach was needed or performed in this increment.

## Acceptance milestones

| Stage | Acceptance gate |
| --- | --- |
| V4-A | Strict versioned job manifest and documented policy semantics, bounded local inputs, no traversal or external file references |
| V4-B | Independent replay with explicit gates for error, replications, environment/envelope, material rankings, baselines and optional measured quality; missing required evidence fails closed |
| V4-C | CI exit codes, escaped standalone HTML and JSON reports, exclusive outputs, portable bundle with intact freeze bytes and SHA-256 manifest |
| V4-D | Actual FRAMES replay showing numerical acceptance separately from missing quality/absent added decision value; positive/failure/adversarial contract tests; fresh installed-package replay |
| V4-E | Documentation and application-CI example, full Linux/Windows CI, clean-source distribution qualification, experimental GitHub release and public-download verification |

## Semantics to preserve

- Job manifests add a new format; artifact schema 1.0 and its freeze/measurement semantics do not change.
- Policy acceptance is explicit and narrow. It is not a universal certification. Quality omitted explicitly means quality not assessed; it must be visible in the report.
- Requested quality requires directly measured ratio/fraction metrics with matching population and sufficient samples in every scenario and replication. Missing, UNKNOWN or incompatible evidence cannot pass.
- Added decision value, when requested, must hold against every supplied baseline in every comparison group. A weaker baseline cannot conceal equality with a stronger one.
- Inputs are captured once into a bounded snapshot before evaluation. Bundle receipts and payloads are copied byte for byte; only job paths change during export.
- The policy file is not bound by the historical prediction freeze. Replay is retrospective and cannot be represented as a newly preregistered successful experiment.
- All outputs are newly created. Reports omit source filesystem paths, escape dynamic HTML, and load no remote assets or scripts.

Completion evidence is recorded in `PROJECT_STATUS.md`, `CONTINUATION.md` and the release closeout. All five gates and actual release verification passed; no additional engineering stage is queued for this scope.
