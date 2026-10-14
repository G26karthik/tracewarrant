# Retrospective validation jobs over the frozen FRAMES study

Seven neutral input files are byte-for-byte copies from `docs/v3/frames-frozen/` and `docs/v3/frames-evaluation/`. The two additional `quality-measured-r*.json` files are derived by `examples/frames_quality.py`: the adapter verifies raw-source lineage and adds the original exact-match fraction (0/8 in every cell) to separate measurement copies. It retains collection times, freeze links and all original numerical metrics. No model is retrained, label reassessed or original measurement replaced. Exact-match is not semantic answer quality.

- `job.json` requires measured exact-answer quality, the calibration envelope and added decision value. It deliberately fails: exact quality is 0/48, the interventions are declared extrapolations, and the model does not establish added choice value over every baseline.
- `missing-quality-job.json` uses the original unextended measurements and refuses missing quality evidence instead of treating it as a pass.
- `performance-job.json` explicitly checks only held-out numerical error and material ranking, allowing the already-declared extrapolations. It passes those narrow thresholds. Quality and added decision value are not assessed by that policy; passing is not approval of a useful agent.

The new policies are retrospective examples, not criteria bound by the historical freeze. See `docs/v4/workflow.md` for the job contract and CI exit codes. Run from the repository:

```sh
mkdir -p artifacts
uv run tracewarrant validate-job examples/validation/frames/job.json --output artifacts/strict-report
# Expected exit code 1, with a readable report explaining the failures.
uv run tracewarrant validate-job examples/validation/frames/performance-job.json --output artifacts/performance-report
# Expected exit code 0; report explicitly says quality was not assessed.
uv run tracewarrant bundle-job examples/validation/frames/performance-job.json --output artifacts/evidence-bundle
uv run tracewarrant verify-bundle artifacts/evidence-bundle --output artifacts/replayed-report
```

Use new output names. Both HTML and JSON reports are written in each report directory. The exported bundle contains its own portable job and checksum manifest; verify that exported directory, not this source folder with extra documentation and policies.
