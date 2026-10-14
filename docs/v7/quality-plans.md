# Bind the declared population and quality policy

Prepare an application plan with opaque expected task IDs, workload identity and
sample identity. Export its schema with `tracewarrant quality-schema plan`.
Declare the quality policy using the existing 0.5.0 policy format, then:

```sh
tracewarrant freeze-quality --plan plan.json --policy policy.json --output freeze.json
```

Commit/publish plan, policy and receipt **before collecting** the corresponding
sample. The receipt contains exact-byte SHA256 bindings and a local timestamp.
Keep independent provenance for chronology; neither the hash nor that timestamp
authenticates a real preregistration, collector honesty or actual execution.

After collection:

```sh
tracewarrant qualify-application sample.json --policy policy.json \
  --plan plan.json --freeze freeze.json --output quality-report
```

Both optional flags are required together. Qualification first validates formats,
unique identities and exact plan/policy receipt hashes, then matches workload,
sample identity and the **entire** declared task membership. Order of observed
rows may vary; membership cannot. Dropped, additional, substituted or duplicate
tasks are refused. A byte change in policy or plan, even just whitespace, invalidates
the receipt. Do not generate a replacement receipt after seeing results and call
it the original design.

Binding/schema/membership errors return 2, with no report directory created and
no task names or source paths in errors. They must be resolved using truthful
evidence, not fabricated rows. Within a matching sample, completion and quality
retain 0.5.0 semantics: failures remain in offered denominators, missing/null
scores are unsupported, and the chosen floors apply to every declared task.
Accepted policy returns 0; failed/unsupported policy returns 1 with HTML/JSON.

Bound reports add `binding.status: verified`, exact plan/receipt/policy hashes,
expected/observed population sizes and `chronology: not_authenticated`. Verified
means byte identity and declared membership, not evidence that a timestamp was
honest or that tasks actually ran. The caller can still omit a task from the
initial plan; there is no universal population-completeness certificate. An
impossible minimum sample floor above planned membership is rejected at freeze.

The original unbound command/API remains valid with unchanged JSON decision
fields and scope. No prediction freeze, model, grading service or runtime
dependency is introduced. Plans are capped at 2 MiB/10,000 IDs; receipts/policies
at 64 KiB. Formats reject unknown fields and duplicate IDs. Empty cohorts are
invalid, and impossible calendar timestamps are refused. Missing actual observations
should be reported truthfully in the appropriate sample rather than silently
replacing planned tasks.

## Retrospective retained-data example

`examples/qualification/hotpot-frozen` copies the unchanged V5-derived sample and
policy, with a newly constructed roster/receipt. The binding is **retrospective**,
not a new preregistration. All eight tasks match, but exact match 0.5 and mean F1
0.541667 still fail the original 0.75 floors. Run the command above with those
four example paths. No historical sample/policy/freeze is changed, no answers
are rescored, and no conditional V5 performance experiment is unlocked.
