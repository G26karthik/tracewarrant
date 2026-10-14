# Portable application quality evidence

TraceWarrant 0.7.0 exports a self-contained directory for offline reviewers. It
captures each bounded regular input once, checks that snapshot and writes exact
input bytes, deterministic JSON/HTML reports and SHA256SUMS. No source checkout,
model, simulator, grading service or network is needed for verification.

```sh
tracewarrant bundle-quality examples/qualification/hotpot-frozen/sample.json --policy examples/qualification/hotpot-frozen/policy.json --plan examples/qualification/hotpot-frozen/plan.json --freeze examples/qualification/hotpot-frozen/freeze.json --output quality-bundle
tracewarrant verify-quality-bundle quality-bundle --output verified-quality
```

Both commands return **1** for this example: all eight offered tasks bind, but
exact match 0.5 and mean F1 0.541667 fail the original 0.75 floors. The example
roster/receipt was created after the failed V5 study, so it is retrospective.
The original sample, policy, plan and receipt bytes are preserved. Omit both
`--plan` and `--freeze` to export unbound quality evidence with existing semantics.

Exit codes: **0** policy passed, **1** failed/unsupported policy, **2** invalid
input, integrity/refusal or filesystem failure. Output directories must be new;
their parent must exist for export. Existing outputs are never adopted. Invalid
verification creates no report. A failed quality decision is still a valid bundle.

The bundle has exactly five files when unbound: sample.json, policy.json,
report.json, report.html and SHA256SUMS; binding adds plan.json and freeze.json.
Do not put READMEs or other files inside the bundle. Move/copy the whole directory,
or archive it with your preferred tool and extract it before verification. The
verifier does not extract archives, execute commands or follow bundle references.
No absolute paths are stored. Sample IDs/scores/lineage are present; review your
declared input before sharing, since checksums are not redaction.

The checksum manifest is bounded to 1 KiB with fixed flat names and four or six
unique entries. Limits: sample 8 MiB, policy/receipt 64 KiB each, plan 2 MiB,
each report 16 MiB. Missing/extra entries, symlink files/root, changed hashes and
partial binding are refused. Replaying a private byte snapshot enforces existing
schema, identity, exact policy/plan hashes and population checks. Both serialized
JSON and HTML must match recomputation byte for byte, so a rehashed false report
is refused. Verify using the same TraceWarrant version that exported the bundle;
a future renderer change may intentionally require a new export.

Verified output adds `bundle_checksums_verified`, the checksum-manifest hash and
`bundle_checksums_do_not_authenticate_author`; its normal quality result, scope,
gates and optional binding remain unchanged. The original bundle is not modified.
Legacy unbound/bound qualification and performance bundle interfaces are unchanged.

Checksums authenticate neither authors nor scores, and local timestamps do not
prove preregistration. Replacing all inputs with consistently changed evidence
can produce a different valid bundle. Retain an independently published digest,
raw collection evidence and trusted chronology separately when required. Bundle
verification is not semantic rescoring or production/performance certification.
