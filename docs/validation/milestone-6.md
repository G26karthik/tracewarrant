# Milestone 6 — real application applicability probe, partial

The [design](../experiments/real-model-probe-design.md) was written before execution. This is an exploratory non-coding facility/supplier report agent using PydanticAI 2.51.0, real local Ollama inference, parallel retrieval and SQLite tools, and two independently configured owned pools. No artificial tool delay was added. Planning is deterministic; synthesis uses a real LLM. It is not an autonomous research-quality benchmark.

First attempt: cached Qwen3-VL 4B / Ollama 0.34.0 emitted empty answer content under this structured-output request. PydanticAI exhausted output retries. [Failure artifact](../experiments/real-model-probe.json) preserves the failed warmup and structural timings, without prompts, outputs or reasoning text. A direct diagnostic found empty content and nonempty thinking despite `think=false`; the exact backend cause is not established. It was not reclassified as a successful answer.

The amended exploratory probe used already-cached **Llama 3.1 8B, Q4_K_M**, digest `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`. Local Ollama 0.34.0 reported model residency of 5,271,715,839 bytes in VRAM and context 4096. Host GPU is RTX 4060 Laptop, 8,188 MiB, driver 616.56. These are backend/device observations, not a CUDA throughput profile. No weights were downloaded or redistributed. Source: `8f37629`; [raw successful probe](../experiments/real-model-probe-llama.json).

One warmup (8.01 s) is separate. Two blocks of eight concurrent sessions per configuration produced **48/48 exact fact checks**, zero recorded errors, and complete owned-boundary graphs. Quality checks cover site ID, supplier share and stock days plus nonempty risk text; reasoning quality is not established.

| Configuration | Median session latency, repetition 0 / 1 | Mean client occupancy per session, repetition 0 / 1 |
| --- | --- | --- |
| BASELINE (tool 1 / client 1) | 3.375 / 3.670 s | 0.832 / 0.923 s |
| TOOL+ (tool 2 / client 1) | 3.289 / 3.457 s | 0.816 / 0.869 s |
| CLIENT+ (tool 1 / client 2) | 3.210 / 3.408 s | 1.487 / 1.545 s |

Adding client slots increased average occupied time per call by about **1.73×**, consistent with hidden shared-backend contention. The experiment does not isolate backend scheduling from cache/prefill/decoding effects. A client slot is not a GPU worker; using response occupancy as invariant GPU service demand would be unjustified. In baseline runs, measured tool occupancy was only about 3.1–3.5 ms/session, with tool queue about 26–35 ms versus client queue about 2.9–3.2 s. Tool capacity was not materially dominant in this workload. Small latency changes are not assigned statistical significance.

This probe tests applicability and exposes missing service identification. **No capacity predictions were frozen for this workload**, so it cannot establish real-agent prediction accuracy or count toward the controlled pilot's confirmatory score. Tails are underpowered. A richer backend queue contract or an existing inference model would be needed before calibration/optimization. The controlled stub-model fit must not be transferred to this application.
