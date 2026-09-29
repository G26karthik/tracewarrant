# First public release

The maintainer authorized creation and publication of the repository, documentation and experimental release on 2026-09-29. The public repository has been created and private vulnerability reporting enabled. Hosted CI and release assets are verified before publishing the prerelease.

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

Create the public repository, enable and verify private vulnerability reporting, attach `origin`, and push the completed branch as `main` with the preserved tags. Update the active documentation from prospective to published status without rewriting frozen records. Run hosted CI and resolve actual failures before creating the GitHub prerelease. Build and qualify release assets from the exact committed release source, bind their checksums, and attach them with the release notes. Verify repository visibility, default branch, release tag and uploaded asset digests. PyPI, paid resources and outreach are not part of this action.

Public upload and routine release fixes are now authorized. No additional approval is required for these steps. Scientific findings and prior frozen tags remain unchanged; a public release does not establish external adoption or production suitability.
