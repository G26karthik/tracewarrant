# First public release

The maintainer authorized creation and publication of the repository, documentation and experimental release on 2026-09-29. Status checked 2026-09-30: the public repository has been created, private vulnerability reporting is enabled, and all five hosted CI jobs passed on `cede1a4`. No GitHub release exists yet. The remaining work is to qualify and publish the prerelease assets from their exact final source commit. [Continuation checkpoint](CONTINUATION.md).

| Item | Exact scope |
| --- | --- |
| Public repository | `G26karthik/tracewarrant` |
| Default branch | `main`, containing the completed V3 toolkit |
| History | Existing commits and research tags preserved, including failed studies and historical handoffs |
| License | Apache-2.0 |
| First GitHub release | Experimental prerelease `v0.3.1` |
| Release assets | Qualified wheel, source distribution, SHA-256 checksums and qualification/reproduction reports |
| Private security reports | Enable and verify GitHub private vulnerability reporting |
| CI | Run the pinned Windows/Linux correctness matrix and analytical validation, retain results for 14 days |
| Package registry | No PyPI upload; the upload-prevention classifier remains |

The repository is [G26karthik/tracewarrant](https://github.com/G26karthik/tracewarrant). Publication includes tracked code, documentation, synthetic/content-free trace artifacts, historical handoffs and normal Git author metadata. Ignored environments, local model data and private working artifacts are outside the committed source.

The reviewable release description is [release notes](docs/v3/releases/0.3.1.md). Engineering evidence is in the [completion report](docs/v3/completion-0.3.1.md) and [clean-checkout release rehearsal](docs/v3/release-rehearsal.md).

## Release procedure

Completed: create the public repository, enable private vulnerability reporting, attach `origin`, push completed source to `main` with the preserved tags, and pass [hosted run 36533108249](https://github.com/G26karthik/tracewarrant/actions/runs/36533108249).

Remaining: include the local continuation/status documentation in a clean source commit, push that commit and verify CI for the actual release source. Build and qualify fresh wheel/source assets from that exact commit, bind their SHA-256 checksums, and attach them with the release notes to experimental prerelease `v0.3.1`. Verify repository visibility, default branch, release tag, uploaded asset digests and an installation from a public download. See the detailed checklist in `CONTINUATION.md`. PyPI, paid resources and outreach are not part of this action.

The existing `tracewarrant-0.3.1` tag points to an earlier local candidate, not the final public release. Preserve it; create the distinct `v0.3.1` tag at the qualified release source. Older files under `dist/` and `artifacts/release-0.3.1/candidate/` must not be treated as current assets without rebuilding and qualification.

Public upload and routine release fixes are now authorized. No additional approval is required for these steps. Scientific findings and prior frozen tags remain unchanged; a public release does not establish external adoption or production suitability.
