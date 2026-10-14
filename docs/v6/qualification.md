# Application-quality qualification before performance modeling

`qualify-application` checks supplied content-free scores and an explicit policy
without any prediction, simulator or performance freeze. It supports completion
and several quality criteria over the entire declared offered population.

```sh
uv run tracewarrant qualify-application examples/qualification/hotpot/sample.json \
  --policy examples/qualification/hotpot/policy.json --output artifacts/quality-report
```

The real retained V5 sample returns **1**. All eight requests completed, but
exact match was 0.5 and mean answer F1 0.541667 against the original 0.75 floors.
No model runs, answers are regraded or historical inputs changed. Open
`report.html`; `report.json` contains every gate, denominator, hash and limit.
Use a new output directory. Exit 0 means all requested sample-policy gates
passed; 1 means a valid sample failed or lacks required evidence; 2 means
invalid input or output/I/O failure. CI should upload reports even on exit 1.
[Copyable application CI](../../examples/ci/application-quality.yml) pins the
experimental release and uploads reports on failure; callers collect/grade their
own application outside the validator.

## Collect from your application

Use the exported fixed schemas:

```sh
tracewarrant quality-schema sample
tracewarrant quality-schema policy
```

A sample contains workload/sample tokens, `MEASURED` provenance, SHA256 lineage,
and a row for every offered task. Each row has a sanitized opaque ID, outcome
(`completed`, `failed` or `censored`) and named numeric quality scores in [0,1]
or null. No answer, question, document, exception text or plugin/configuration
payload field is accepted. Identifiers/lineage are caller-declared, not universal
PII detection or authenticated collection. You must ensure all offered tasks
are represented; the validator cannot prove that an omitted task existed.

The policy sets a positive minimum offered sample count, completion-fraction
floor, and 1–16 quality criteria. `fraction` requires every supplied score to be
binary 0/1; `mean` accepts bounded per-task graded scores such as token F1.
Several criteria must pass together. Neither kind is an automatic text grader.

Missing/null scores make a required criterion **unsupported**, with a null
aggregate and both offered/observed counts. They are never averaged over just
eligible tasks. Failed/censored rows can supply an explicit zero or unknown
quality, never a positive success score. An explicit zero is in the denominator;
unknown remains unsupported. Completion always uses completed/offered, including
failed and censored cases. Duplicate task, metric or criterion IDs are invalid.

Sample bound: 8 MiB, 10,000 rows, 16 scores per row. Policy bound: 64 KiB,
16 criteria. Formats reject unknown fields, invalid types, non-finite/out-of-range
scores and malformed identities. Reads capture bounded bytes once, and report
hashes bind those exact bytes. The command executes no caller code or network
reference and does not import the optional simulation backend.

## Scope and retained adapter

The report says `application_sample_quality_policy_only`. Passing a weak policy
is not scientific proof, semantic correctness, performance-model validation or
production readiness. Hashes do not authenticate an author or prove that the
policy was preregistered. Freeze/commit a design separately before collection.

`examples/hotpot_quality.py` checks the V5 source/sample/trace/gate identity before
exporting existing scalar scores. It copies the original completion/exact/F1
thresholds; the generated policy is a retrospective representation of the
predeclared rule, not a new successful experiment. Only local private V5 answer
verification rescored text against the official source. [V5 results](../v5/results.md).
Changing model, prompt or quality rules is a separate application study.
