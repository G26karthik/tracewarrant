# Offline validation jobs

TraceWarrant 0.4.0 evaluates a directory of neutral evidence against an explicit policy and produces a CI decision, standalone HTML and JSON. It never executes your application, a model producer or a plugin.

## Run the retained real example

```sh
uv sync --locked
python -c "from pathlib import Path; Path('artifacts').mkdir(exist_ok=True)"
uv run tracewarrant validate-job examples/validation/frames/job.json --output artifacts/strict-report
```

Expected exit **1**. Open `artifacts/strict-report/report.html`. The strict policy fails: original exact-match quality was 0/48, interventions extrapolated beyond calibration, and added decision value over every baseline was not established. The quality adapter verifies raw-source lineage and exports the original boolean labels into separate measurement copies. It does not reassess answers or replace historical evidence.

The explicitly narrower numerical replay passes:

```sh
uv run tracewarrant validate-job examples/validation/frames/performance-job.json --output artifacts/performance-report
uv run tracewarrant bundle-job examples/validation/frames/performance-job.json --output artifacts/evidence-bundle
uv run tracewarrant verify-bundle artifacts/evidence-bundle --output artifacts/replayed-report
```

These return **0**. That policy explicitly allows the declared extrapolations and does not require quality or added choice value. The report still displays envelope violations and says quality was not assessed. `missing-quality-job.json` instead demonstrates a required unavailable metric returning unsupported. None is a newly preregistered experiment or a useful-agent claim.

Output directories must not exist; their parent must exist. Use new names for another run. Reports escape dynamic content, load no scripts or remote assets, and omit source paths. Caller-supplied identifiers still need review before sharing.

## Manifest

Paths are relative to the manifest, independent of the shell working directory. All fields are required; unknown fields and invalid/nonfinite values are refused. [Job schema](../../schemas/validation-job-v1.schema.json), also emitted by `tracewarrant job-schema`:

```json
{
  "schema_version": "1.0",
  "artifact_type": "validation_job",
  "protocol": "protocol.json",
  "freeze": "freeze.json",
  "predictions": ["model.json", "baseline.json"],
  "measurements": ["measured-r0.json", "measured-r1.json"],
  "model_id": "my-model",
  "policy": {
    "maximum_primary_relative_error": 0.15,
    "minimum_replications": 2,
    "require_within_envelope": true,
    "minimum_material_pairs": 1,
    "minimum_ranking_accuracy": 1,
    "require_added_decision_value": true,
    "quality": {
      "metric_id": "answer.exact",
      "population": "offered",
      "minimum_value": 0.95,
      "minimum_samples": 20
    }
  }
}
```

Thresholds above are illustrative. Select one prediction with role `model` and supply a baseline. Create the inputs through the existing [artifact contract](../v3/artifacts-and-validation.md), freezing predictions before intervention collection. Job policy is separate from the prediction freeze; a policy chosen after seeing outcomes is retrospective. Neither hashes nor declared timestamps attest experimental honesty. Artifact schema 1.0 and compatibility interfaces remain unchanged.

## Acceptance gates

| Gate | Rule |
| --- | --- |
| Baseline | At least one prediction has baseline role |
| Replications | Distinct validated run IDs meet the threshold; independence is caller-declared |
| Primary error | Every scenario/replication has a comparable primary metric; **worst individual relative error** meets the limit. Zero reference denominators are unsupported, not zero error |
| Environment | All selected model/measurement scenarios have matching declared environments |
| Envelope | When required, every scenario/replication is within calibration; UNKNOWN and EXTRAPOLATED cannot pass |
| Material pairs | Enough consistently material pairs across replications |
| Ranking | Material-pair accuracy meets the threshold; no eligible pair is unsupported |
| Added decision value | When requested, `model_choice_better` against **every supplied baseline in every group**; equality, baseline wins and insufficient evidence cannot pass |
| Quality | When requested, every scenario/replication has the named MEASURED ratio/fraction metric with matching population, enough samples and value meeting the threshold |

Explicit `quality: null` means quality not assessed and limits the result to a performance-only policy. Requested gates can be passed, failed or unsupported; deliberately omitted gates are `not_required`. Overall acceptance requires all requested gates to pass. There is no weighted score hiding failures.

## CI and portable replay

| Exit | Meaning |
| --- | --- |
| 0 | Explicit policy passed within its stated scope |
| 1 | Valid job/evidence, but requested gates failed or were unsupported; reports still exist |
| 2 | Invalid evidence, freeze/checksum violation, unsafe path or I/O error |

The [application CI example](../../examples/ci/tracewarrant.yml) installs the pinned experimental release, runs your committed `validation/job.json` and retains reports on failure. It does not collect measurements or send them to TraceWarrant. Review what your own CI artifacts disclose.

`bundle-job` snapshots input bytes once, preserves evidence exactly, rewrites job paths to portable names, evaluates the rewritten manifest and checksums every payload. Failed policies can also be exported; their exit code remains 1.

`verify-bundle` checks every checksum, rejects missing/unlisted entries and unsafe references, snapshots verified bytes, reruns the job and checks the bundled report against recomputation. No source checkout or application runtime is required. Checksums detect changes, not author identity or measurement truth.

As of 0.7.1, both the JSON decision and exact rendered HTML must match replay;
an edited HTML report remains invalid even with an updated checksum. Use the
exporting package version for verification. Earlier releases checked HTML hashes
but did not recompute its presentation. [Final acceptance](../v9/acceptance.md).

Rewritten paths change the portable manifest digest. Its report retains the source manifest digest separately. Replay preserves input digests, gates and the underlying evaluation; export provenance can make full reports differ.

Limits: manifest 1 MiB; individual evidence file 16 MiB; total source inputs 64 MiB including manifest; at most 32 predictions and 32 runs; existing evaluation comparison budgets. JSON output is capped at 64 MiB, HTML at 16 MiB, checksum listing at 128 KiB and bundle entries at 70. Files remain under the manifest directory after resolving symlinks. Absolute paths, URLs, parent traversal and Windows drive/stream paths are refused.

## Qualification

```sh
uv run python -m benchmarks.validate_workflow --output artifacts/workflow-new.json
uv run python -m benchmarks.v3_audit --output artifacts/preservation-new.json
uv run pytest -q
```

Installed-wheel qualification covers strict failure, numerical acceptance, HTML/JSON and verified portable replay without simulation/calibration/SimPy imports. The V4 workflow preserves all 64 protected files and original frozen studies.
