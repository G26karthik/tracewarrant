# Reproduce V3

Offline validation needs only Python 3.11+ and the core package. Development checks use the locked optional tools. Use fresh output paths; published raw traces, criteria, predictions and receipts must not be overwritten.

```sh
uv sync --locked
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run workload-lab inspect examples/traces/controlled-v1.otlp.json
uv run workload-lab inspect examples/traces/pydantic-ai-2.51.0.otlp.json
uv run workload-lab inspect examples/v3/frames-heldout-base.otlp.json
uv run python -c "from pathlib import Path; Path('artifacts/v3-reproduction').mkdir(parents=True, exist_ok=True)"
uv run python -m benchmarks.v3_audit --output artifacts/v3-reproduction/audit.json
```

The audit verifies 64 preserved V2 files and the original tag; inspects three trace sources; applies the explicit FRAMES binding adapter to 72 real sessions; and reproduces the published evaluation byte for byte. It does not access the network or execute a model. The neutral CLI command is in the root [README](../../README.md).

Inspect the corrected binding separately:

```sh
uv run python -m examples.adapt_frames_trace examples/v3/frames-heldout-base.otlp.json --output artifacts/v3-reproduction/frames-adapted.json
uv run workload-lab inspect artifacts/v3-reproduction/frames-adapted.json
```

## Regenerate predictions, without recollecting

```sh
uv run --group validation python -m benchmarks.frames_validation forecast --input docs/v3/frames-calibration.json --output artifacts/v3-reproduction/new-forecast
```

This exercises independent SimPy, fixed-delay and utilization producers. Do not replace the original freeze: a new receipt has a new timestamp/hash. Source/lock/metadata can change on a fresh checkout; this is reproduction, not the original preregistered study.

## New real collection

Requires an already installed local Ollama server with cached `llama3.1:8b`; no model is pulled. Read [the preregistration](frames-preregistration.md) and [negative results](results.md) first. Fresh public network fetches are bounded to two concurrent requests and access denials halt the study. The application performs real inference on loopback, not a paid provider.

Download the [pinned public dataset](https://huggingface.co/datasets/google/frames-benchmark/resolve/58d9fb6330f3ab1316d1eca12e5e8ef23dcc22ef/test.tsv) into an ignored local file. Its SHA-256 must be `4255093c93b595b5b04c7c8dde290b48ec87d72ca0fb0b760d9dd02740d669ff`. The collector enforces this digest and fixed selection. Dataset card is Apache-2.0; webpage contents have their own licenses. Neither is redistributed in our telemetry.

```sh
uv run python -m examples.frames_workload feasibility --dataset artifacts/v3/frames-test.tsv --output artifacts/v3-reproduction/feasibility.json
uv run python -m examples.frames_workload calibration --dataset artifacts/v3/frames-test.tsv --output artifacts/v3-reproduction/calibration.json
uv run --group validation python -m benchmarks.frames_validation forecast --input artifacts/v3-reproduction/calibration.json --output artifacts/v3-reproduction/frozen
# Commit or independently timestamp the new protocol, predictions and receipt before collecting.
uv run python -m examples.frames_workload holdout --dataset artifacts/v3/frames-test.tsv --freeze artifacts/v3-reproduction/frozen/freeze.json --output artifacts/v3-reproduction/holdout.json
uv run python -m benchmarks.frames_validation evaluate --input artifacts/v3-reproduction/holdout.json --frozen artifacts/v3-reproduction/frozen --output artifacts/v3-reproduction/evaluation
```

The corrected collector differs from the frozen source only in the root-completeness binding. Use `af36005` in an isolated checkout to reproduce the original collector exactly; do not rewrite original artifacts. Model quality is not established; a strict answer-match failure must remain a failure. The Python DES is optional and is never required for this workflow.
