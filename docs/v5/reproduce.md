# Reproduce the local application qualification

The toolkit runtime remains dependency-free. Dataset conversion uses optional
PyArrow outside the core; live collection uses a local Ollama installation.
No command below submits questions to a cloud provider. Dataset/model downloads
are separate explicit setup actions, not side effects of the collector.

Acquire the pinned Parquet from the authors' Hugging Face mirror described in
[preregistration](preregistration.md), into `artifacts/v5/inputs/validation.parquet`.
The `prepare` command verifies exact size and SHA256 before reading the data.
Model setup is `ollama pull llama3.1:8b`, then `ollama serve` if not running.
Record the downloaded model digest; this movable name alone is not reproducible.
Weights use Meta's Llama 3.1 license and are not part of TraceWarrant's package.

```sh
uv sync --locked
uv run --with pyarrow==23.0.1 python -m examples.hotpot_workload prepare \
  --parquet artifacts/v5/inputs/validation.parquet \
  --output artifacts/v5/inputs/sample
uv run python -m examples.hotpot_workload feasibility \
  --inputs artifacts/v5/inputs/sample --selection docs/v5/selection.json \
  --output artifacts/v5/feasibility.json \
  --private-output artifacts/v5/private-answers.json
```

Use fresh paths. Commit code/design before measurement; the collector refuses a
dirty source checkout and non-ignored private-answer output. Preparation must
produce exactly the committed selection and task digest. There is one unscored
arithmetic warmup. Failed application requests count as zero-quality offered
questions; they are not silently excluded. Inference timeout is 120 seconds per
request. Read the gate result before any further experiment.

Download the official scorer from its pinned upstream commit to ignored storage,
then verify recorded answer scores locally against its hash-pinned functions:

```sh
uv run python -m benchmarks.hotpot_validation \
  --raw artifacts/v5/feasibility.json --selection docs/v5/selection.json \
  --private artifacts/v5/private-answers.json \
  --official-scorer artifacts/v5/inputs/official_evaluator.py \
  --output artifacts/v5/verified-with-private-scorer.json
```

Offline replay omits both private arguments. It checks committed source,
selection/clock/graph identities and recomputes the gate from retained scalar
scores. Digests do not authenticate the collector, and scalar-only replay cannot
independently rescore an absent answer. Live reruns may differ because GPU/runtime
scheduling, model releases and nondeterministic kernels can change results.

Dataset attribution: Yang, Qi, Zhang, Bengio, Cohen, Salakhutdinov and Manning,
*HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering*,
EMNLP 2018. [Authors' dataset](https://hotpotqa.github.io/), CC BY-SA 4.0.
