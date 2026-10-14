# V4 end-to-end workflow closeout

Completed and publicly verified 2026-10-14. [TraceWarrant 0.4.0 prerelease](https://github.com/G26karthik/tracewarrant/releases/tag/v0.4.0), [repository](https://github.com/G26karthik/tracewarrant), [machine-readable verification](public-release-0.4.0.json).

Qualified source: `a248708e203869a6efd529595a20988c57f35115`. The immutable annotated `v0.4.0` tag points to that commit. Later closeout documentation on `main` does not replace those assets or move the tag. The 0.3.1 release, research tags, original measurements/predictions and 64 protected files remain unchanged.

## Completed milestones

| Stage | Verified result |
| --- | --- |
| V4-A | Strict job schema; versioned bounded manifests; contained relative inputs; snapshot before evaluation; schema agreement and adversarial path/size tests |
| V4-B | Explicit error, replication, environment/envelope, ranking, baseline and quality gates; missing required evidence fails closed; known counterexamples cannot be hidden by another unsupported baseline |
| V4-C | Distinct CI exits, standalone escaped HTML/JSON, exclusive output, portable evidence and complete checksum/report recomputation; falsified report scope/result refused |
| V4-D | Original FRAMES numerical replay remains byte-exact; quality adapter verifies original source lineage and exports existing 0/48 labels separately; strict failures and missing-quality refusal verified; fresh installed-package and source-free portable replay passed |
| V4-E | Documentation/application CI example, clean-source wheel/archive, all five hosted jobs, published prerelease, ten public-download/checksum checks and fresh downloaded-wheel qualification |

[Release-source CI 38513195366](https://github.com/G26karthik/tracewarrant/actions/runs/38513195366) passed all five jobs. Each Windows/Ubuntu Python 3.11/3.13 job ran **190 tests, zero failures/errors/skips**, installed-package workflow verification, original preservation audit and CLI smoke checks. Ubuntu analytical validation passed. [Tag-source CI 38513664614](https://github.com/G26karthik/tracewarrant/actions/runs/38513664614) also passed the same source.

Ten assets were verified against GitHub SHA-256 digests and unauthenticated HTTP downloads. `SHA256SUMS` binds nine payloads: wheel, source archive, package/workflow qualification, offline audit, hosted evidence ZIP, portable examples ZIP, source provenance and release notes. The evidence ZIP retains reports beyond workflow artifact retention.

Distribution checksums:

| Asset | SHA-256 |
| --- | --- |
| `tracewarrant-0.4.0-py3-none-any.whl` | `79bc5e66cc07fa9985cd86df3e653bf83e1203a8e3fc6220801c7fe1875417c7` |
| `tracewarrant-0.4.0.tar.gz` | `200a70304ffc5755d0545ac4f8c6c5473c496bd9e1c4950ef7008fbf9abd6923` |

## Use the product without this checkout

Download and verify the wheel, `frames-validation-bundles.zip` and checksum manifest. Install the wheel in a fresh environment and extract the examples. No application, provider, simulator or source checkout is required:

```sh
python -m pip install ./tracewarrant-0.4.0-py3-none-any.whl
tracewarrant verify-bundle frames-performance --output performance-report
tracewarrant verify-bundle frames-strict --output strict-report
```

Both were tested in a fresh wheel-only environment from actual public downloads. Performance-only acceptance returns 0; the strict policy returns 1 with a report exposing original exact-match failure, calibration extrapolation and no established added choice value. Open each `report.html`. The separate source-based qualification also verifies a fresh installation of the downloaded wheel/archive pair and both compatible command names.

For your application, follow [the workflow guide](workflow.md): collect content-free evidence, create neutral predictions/measurements and freeze predictions before interventions, define an explicit job policy, run it in CI and export evidence for independent replay. Inputs are not executed or uploaded by the toolkit.

## Scope and remaining scientific limits

The end-to-end offline toolkit workflow and its V4 release are complete; no required engineering or release gate remains. Core runtime remains dependency-free, old commands/imports and artifact schema 1.0 remain compatible, and no planner/native/CUDA/optimizer/cloud work was resumed.

This is an experimental release. It does not establish production suitability, external adoption, scientific uniqueness, GPU service identification or model superiority. The new policies are retrospective; checksums do not attest author identity or measurement truth. Original FRAMES exact-answer quality remains 0/48 and utilization made the same intervention choice. Future research must earn a new scope rather than relabel those findings. No PyPI, paid calls, cloud provisioning or outreach was performed.
