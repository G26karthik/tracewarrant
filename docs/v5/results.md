# HotpotQA result — application quality floor failed

The next application study is complete under its preregistered stopping rule.
All eight requests ran successfully, but the application did not meet the fixed
quality policy. Calibration and held-out performance modeling were not unlocked.
This is evidence about one local pipeline on eight development-set questions,
not a verdict about all HotpotQA tasks, Llama models or TraceWarrant correctness.

## Registered and measured identity

Design, collector and fixed 24-row selection were committed and pushed at
`7d1ab8d0d372141a4e8799c6f43a17fc4fdff4c9` before any scored request.
A metadata-only correction stopped falsely labeling the local backend as
CPU-only; measured source was clean at
`f023348ac27e4725707de37f79e6710e08136155`. No sample, prompt, scorer, option or
quality rule changed after collection. [Design](preregistration.md),
[selection](selection.json), [raw public evidence](feasibility.json).

Authors' dataset mirror revision `1908d6afbbead072334abe2965f91bd2709910ab`,
fixed first eight distractor validation rows, with no eligibility replacement.
Gold and supporting facts never entered the application's evidence. All ten
supplied candidate paragraphs entered real SQLite storage and context assembly;
the local application called Ollama Llama 3.1 8B Q4_K_M, digest
`46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`,
Ollama 0.34.0. Its recorded residency reports 5,812,781,055 bytes of VRAM and
context length 8192. Prompt token counts ranged 1,134–3,063; no context hit the
24,000-character cap. No artificial delays or repeated CPU work were introduced.

Collection UTC `2026-10-14T06:13:12.830209Z` to
`2026-10-14T06:15:03.697068Z` includes the unscored cold-start warmup. The
eight-question finite burst itself lasted approximately 11.18 seconds.
Model setup initially had registry transport failures, then succeeded with
Ollama's local streaming pull API before any scored request. Setup failures did
not become quality labels or cause a different model to be selected.

## All-result quality policy

| Measure | Required | Observed | Disposition |
| --- | --- | --- | --- |
| Completed / offered | 8/8 | 8/8 | Passed |
| Official normalized answer exact match | At least 6/8 | 4/8 | Failed |
| Mean official answer token F1 | At least 0.75 | 0.5416667 | Failed |

The source row-order exact-match flags were true, false, true, false, false,
true, true, false. F1 scores were 1, 0, 1, 0, 1/3, 1, 1, 0. Failed answers
were not removed from the denominator. Exact match and token overlap are
benchmark proxies, not human semantic evaluation or evidence attribution. This
application emits no supporting-fact predictions; no joint/fact score is claimed.
Do not soften these criteria retrospectively or relabel the failed application
as qualified on the basis of completed requests.

## Verification and performance limits

[Verification](verification.json) binds exact raw/selection SHA256 and committed
collector/dependency/preregistration bytes. All eight dependency graphs and owned
resource clocks replay. Locally, all eight retained answers were rescored against
the exact official evaluator source digest, with agreement. Public evidence has
no answer or dataset passage strings. Scalar-only offline replay recomputes the
gate and checks trace/source identities; it cannot independently rescore missing
answers or authenticate an honest collector. [Reproduction](reproduce.md).

Observed completed-session mean latency was 5.514 seconds, including burst queue
time. Owned inference-client occupancy was 99.91% of the finite drain window;
database 0.106% and context assembly 0.282%. These are ordinary measured owned
slot clocks, not intrinsic GPU service demand, sustainable capacity or confidence
intervals. The application is inference-dominated and does not establish a
difficult heterogeneous intervention decision. Eight observations are insufficient
for a validated tail claim. No performance model or baseline comparison was run
after the failed feasibility gate; no added decision value is asserted.

## Disposition

The toolkit remains a usable experimental validator and package 0.4.0. This
study's useful result is the correctly enforced quality boundary and inspectable
evidence. It does not establish a useful QA application, external adoption,
production readiness, scientific superiority or a reason for native/CUDA/
optimizer/cloud expansion. A later application improvement or independently
motivated workload must have a separate design and preserve this result.

Both preregistration/source CI runs passed all five jobs (214 tests per matrix
job): [initial design](https://github.com/G26karthik/tracewarrant/actions/runs/38519331992),
[measured source](https://github.com/G26karthik/tracewarrant/actions/runs/38520913887).
Final evidence replay is also a network-free regression test in the repository.
The 64-file historical preservation and byte-exact V3 evaluation checks passed.
Historical release tags stay unchanged. Published records exclude private answer
text. No paid/cloud request or outreach was made.

Dataset attribution and official evaluation:
[HotpotQA authors](https://hotpotqa.github.io/), CC BY-SA 4.0;
[official scorer](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py), Apache-2.0.
