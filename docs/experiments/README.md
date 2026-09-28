# Controlled pilot 1 artifacts

The [criteria](../validation/prediction-acceptance-criteria.md) were committed at `31bb58b` before calibration and holdout. Training collector source: `28a752a`. Forecast/evaluation code: `f73a806`. `pilot-1-freeze` commits the immutable predictions before any held-out run. These source and freeze commits are distinct; there is no circular self-hash.

- `pilot-training.json`: four actual baseline batches, 160 offered/completed sessions, content-free OTLP and clocks, application/hardware/cohort and source hashes. No held-out data enters fitting.
- `pilot-predictions-frozen.json`: empirical models, source/session lineage, raw samples, tail/CV/correlation diagnostics, all eight cell predictions for independent/paired/fixed-tool-delay variants, 30 seeds each, simpler planning choices and declared envelope. Source tree was clean. Simulation forecasts took about 6.26 seconds; this excludes engineering effort and training collection.
- Held-out data and evaluation are added only after this freeze. Do not regenerate the frozen file from later measurements.

```sh
uv run python -m benchmarks.controlled_experiment calibration --output artifacts/train.json
uv run python -m benchmarks.predict_controlled --training artifacts/train.json --output artifacts/frozen.json
# Commit the model and predictions before the next command.
uv run python -m benchmarks.controlled_experiment holdout --frozen artifacts/frozen.json --output artifacts/holdout.json
uv run python -m benchmarks.evaluate_controlled --frozen artifacts/frozen.json --holdout artifacts/holdout.json --output artifacts/evaluation.json
```

Use fresh paths, create `artifacts` first. Collection keeps a `.partial.json` checkpoint after each cell and refuses to overwrite a prior partial run. Raw telemetry is generated locally and has no application payloads. This is still a stub workload, not evidence of real LLM inference fidelity, task quality or a steady-state saturation threshold.

## Exploratory real-model probe

The [design and amendment](real-model-probe-design.md), [failed Qwen warmup](real-model-probe.json), [successful Llama observations](real-model-probe-llama.json), [derived summary](real-model-summary.json) and [M6 interpretation](../validation/milestone-6.md) are separate from the controlled holdout. No predictive score is claimed for this probe.

Recompute the summary without running a model:

```sh
uv run python -m benchmarks.summarize_real_probe --input docs/experiments/real-model-probe-llama.json --output artifacts/new-real-model-summary.json
```

To collect a new independent probe, use the command in the root README with an existing local Ollama server and cached model. The application never pulls weights. Keep a fresh output path and retain failures; new observations do not replace the published artifacts.
