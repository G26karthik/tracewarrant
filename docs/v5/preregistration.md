# HotpotQA local application study — predeclared design

Created 2026-10-14 before any application answer or latency observations.
This is a new experiment; FRAMES artifacts and failed findings stay immutable.

## Motivation and selection

FRAMES' strict string equality did not establish useful answer quality. HotpotQA
provides natural multi-document questions, answer labels and an official scorer
with normalized exact match and token F1. This allows us to test answer quality
without a model judge. It does not supply semantic correctness or human approval.

Primary sources:

- [Authors' dataset documentation](https://hotpotqa.github.io/).
- [Authors' mirror, pinned revision](https://huggingface.co/datasets/hotpotqa/hotpot_qa/tree/1908d6afbbead072334abe2965f91bd2709910ab).
- [Official scorer, pinned commit](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py).
- [Local model](https://ollama.com/library/llama3.1:8b).

Original CMU download timed out before selection or scoring. Use the authors'
mirror distractor validation Parquet (27,452,575 bytes), SHA256
`c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6`.
Official scorer SHA256
`d35fc91a6db21d791dbdda11daf3856e9359f5701d54e3eefba20d88fecc02c0`.
Dataset is CC BY-SA 4.0; code is Apache-2.0. Raw dataset and generated answers
stay in ignored local storage; public evidence contains digests, numeric scores,
resource clocks and task IDs. No dataset passage is relicensed as Apache code.

Fixed row-order samples, with no outcome-based filtering: rows 0–7 feasibility,
8–15 calibration, 16–23 held out. Distinct source IDs are checked. Malformed
rows stop collection rather than being replaced. This small development-set
sample is not an official benchmark submission or evidence about the full set.
The code sees question and supplied distractor context only. Gold answers and
supporting facts never enter application context. This is the supplied-candidate
distractor task, not open-web research or autonomous agent planning.

## Fixed application

SQLite stores all ten supplied paragraphs. An owned database slot loads them;
an owned context-assembly slot constructs evidence; an owned inference-client
slot calls local Ollama with Llama 3.1 8B (Q4_K_M). No network source fetch,
artificial delay, replicated busy-work or custom inference kernel is introduced.
The model digest, backend version/residency, options, source SHA and source/lock
hashes are captured. Only loopback inference is allowed; no paid/cloud endpoint.
No alternative model is tried based on answer quality.

Temperature 0, seed 27, maximum 96 generated tokens, context 8192. Structured
output has one `answer` string. The system requests a concise answer based on
untrusted supplied evidence and UNKNOWN for insufficient evidence. Evidence
is capped at 24,000 characters; truncation and prompt token counts are recorded.
Prompt/template/model/scorer remain fixed after the first scored request.
One unscored arithmetic request warms the backend. Eight sessions arrive as a
single finite burst, client slots 1. No tail or sustainable-load claim.

## Quality and stopping rule

Every offered question is in the denominator. Failed requests score zero.
Gate: 8/8 completed, mean official-normalized answer token F1 >= 0.75, and
at least 6/8 official-normalized answer exact matches. EMPTY/UNKNOWN answers
are not exclusions. The threshold is an operational study policy, not a
universal definition of correctness. Answer F1 and EM are both reported; no
supporting-fact/joint score is claimed because this application emits no facts.

If feasibility fails, **stop calibration and held-out collection**, retain
the result and close the study. Do not tune the prompt, replace questions or
relax gates to rescue the experiment. Service/setup failures are recorded as
unexecuted/failed, never measured successful workloads.

## Conditional intervention study

Only if feasibility passes: two calibration bursts per configuration on rows
8–15, BASE (all ten paragraphs, client 1) and CONTEXT4 (lexical top four,
client 1), 32 sessions. Held out: two eight-question bursts for each of BASE,
CONTEXT4 and CLIENT2 (all ten, client 2), 48 sessions on rows 16–23. First
repetition configuration order BASE/CONTEXT4/CLIENT2; second reverses order.

Freeze protocol, policy and predictions in Git before held-out collection:
an independent SimPy FIFO whole-workflow model calibrated from stage occupancy,
a fixed-delay baseline and a highest-owned-utilization heuristic. Inference
occupancy is not GPU intrinsic service demand; concurrency invariance is an
explicit extrapolation. Context reduction changes evidence and must satisfy
the same quality gate in every held-out cell. Baselines are included even if
they make the same or a better decision.

Primary: completed-session mean latency. Worst-cell relative error <= 0.20;
material measured improvement >= 0.10; at least one material pair; ranking
accuracy 1.0; two replications. No p95/p99 confidence, sustainable capacity,
general application adoption, semantic grading or model superiority without
qualified held-out evidence. A cheap baseline matching the model is a valid
negative result. This application may be inference-dominated; there is no
prior claim that it supplies a difficult heterogeneous resource decision.
