# First public release

The maintainer authorized creation and publication of the repository, documentation and experimental release on 2026-09-29. Completed and verified 2026-09-30: [experimental prerelease `v0.3.1`](https://github.com/G26karthik/tracewarrant/releases/tag/v0.3.1), qualified source `b0d5c5dc2a23589245ad1c6fabdf4d07dd2b51b6`, all five hosted CI jobs successful, eight public assets verified and a fresh downloaded-wheel installation qualified. Private vulnerability reporting is enabled. [Closeout](docs/v3/public-release-0.3.1.md), [machine-readable verification](docs/v3/public-release-0.3.1.json).

| Item | Exact scope |
| --- | --- |
| Public repository | `G26karthik/tracewarrant` |
| Default branch | `main`, containing the completed V3 toolkit |
| History | Existing commits and research tags preserved, including failed studies and historical handoffs |
| License | Apache-2.0 |
| First GitHub release | Published experimental prerelease `v0.3.1`; source `b0d5c5d` |
| Release assets | Eight attached assets: qualified wheel, source distribution, checksums, installed qualification, offline audit, hosted evidence ZIP, source provenance and release notes |
| Private security reports | GitHub private vulnerability reporting enabled and verified |
| CI | All five release-source jobs successful; evidence ZIP attached permanently to the release |
| Package registry | No PyPI upload; the upload-prevention classifier remains |

The repository is [G26karthik/tracewarrant](https://github.com/G26karthik/tracewarrant). Publication includes tracked code, documentation, synthetic/content-free trace artifacts, historical handoffs and normal Git author metadata. Ignored environments, local model data and private working artifacts are outside the committed source.

The reviewable release description is [release notes](docs/v3/releases/0.3.1.md). Engineering evidence is in the [completion report](docs/v3/completion-0.3.1.md) and [clean-checkout release rehearsal](docs/v3/release-rehearsal.md).

## Completed release procedure

Created the public repository, enabled private vulnerability reporting, attached `origin`, pushed completed source to `main` with preserved tags, and passed [release-source run 36757290326](https://github.com/G26karthik/tracewarrant/actions/runs/36757290326). The tag-triggered run also passed on that same source.

Built and qualified a fresh wheel/source pair from a separate clean checkout of `b0d5c5d`. Bound seven payloads in `SHA256SUMS`, created the distinct `v0.3.1` tag at that source, uploaded eight assets to a draft, verified GitHub digests, and published it as an experimental prerelease. All eight assets then passed unauthenticated public download, size and hash checks; the downloaded pair passed fresh installed-wheel qualification. The active closeout documentation follows in a later main-branch commit and does not move the immutable release tag. PyPI, paid resources and outreach were not part of this action.

The earlier `tracewarrant-0.3.1` candidate tag remains unchanged. The distinct public `v0.3.1` tag points to the qualified source. Older files under `dist/` and `artifacts/release-0.3.1/candidate/` were not uploaded; exact final checksums and download URLs are in the release verification record.

No release gate remains pending. Scientific findings and prior frozen tags remain unchanged; this completed public release does not establish external adoption or production suitability.
