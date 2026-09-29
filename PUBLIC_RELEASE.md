# Proposed first public release

The local candidate is prepared. This file specifies the public action for approval; it does not claim the repository or release already exists.

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

The current active personal GitHub account was verified as `G26karthik`. The destination did not exist at the last read-only check. Publication exposes tracked code, documentation, synthetic/content-free trace artifacts, historical handoffs and normal Git author metadata. Ignored environments, local model data and private working artifacts are outside the committed source.

The reviewable release description is [release notes](docs/v3/releases/0.3.1.md). Engineering evidence is in the [completion report](docs/v3/completion-0.3.1.md) and [clean-checkout release rehearsal](docs/v3/release-rehearsal.md).

## Execution after approval

Create the public repository, enable and verify private vulnerability reporting, attach `origin`, and push the completed branch as `main` with the preserved tags. Update the active documentation from prospective to published status without rewriting frozen records. Run hosted CI and resolve actual failures before creating the GitHub prerelease. Build and qualify release assets from the exact committed release source, bind their checksums, and attach them with the release notes. Verify repository visibility, default branch, release tag and uploaded asset digests. PyPI, paid resources and outreach are not part of this action.

The earlier V3 brief explicitly reserved irreversible public release decisions for the maintainer. Git committing and ordinary local work are already authorized; public upload is the remaining confirmation.
