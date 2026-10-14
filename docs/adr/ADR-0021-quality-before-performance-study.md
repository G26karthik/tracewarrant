# ADR-0021: qualify application quality before performance-model work

Date: 2026-10-14. Status: accepted for V5.

The maintainer authorized another stage after the completed 0.4.0 workflow.
FRAMES demonstrated offline validation but failed its answer-quality policy.
Collecting another simulator comparison before task qualification would not
resolve that limitation.

Select one externally authored, non-coding multi-document QA dataset (HotpotQA)
because its authors publish both answer labels and a non-LLM evaluation script.
Pin a fixed row-order sample, local application, options and quality thresholds
before scoring. Store task/answer text locally in ignored storage; publish only
digests, scores and owned resource telemetry. Verify scorer parity against its
exact upstream source hash. Do not treat scalar-only replay as rescore evidence.

Run a finite eight-question feasibility burst. Failure terminates this study;
the design does not search for a model win or tune the failed application. Only
a qualifying application unlocks calibration, frozen baseline/model predictions
and held-out interventions. Whole-workflow value over a cheap heuristic remains
an empirical question. A negative result is a valid closeout, not production
readiness and not a reason to restore native/optimizer/cloud work.

Alternatives considered: regrade retained FRAMES with a model judge (changes its
historical rule); manufacture a CPU-heavy stub (not useful application evidence);
privately operated application (access not available); broad agent redesign
(larger product scope unsupported). This study uses the supplied distractor
candidates; no open-web or general agent-quality result is claimed.

Core package/version and release tags remain unchanged. New dataset/model setup
is optional outside the core. No paid/cloud call or outreach is required.
Design: [V5 preregistration](../v5/preregistration.md).
