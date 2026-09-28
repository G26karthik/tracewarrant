# External FRAMES feasibility result

Source `933596d`; [raw content-free evidence](frames-feasibility.json). All eight selected external tasks completed; exact normalized answers passed **1/8**, below the preregistered 6/8 quality gate. Preserve this failure. The executor uses oracle URLs and limited paragraph retrieval, so it is not a full benchmark implementation and does not establish useful research-agent quality.

The batch drained in 30.651 s. Owned occupancy totals: fetch 28.932 s, inference-client 12.537 s, retrieval 0.151 s, SQLite 0.015 s. Non-LLM fraction was 69.89%. Fetch queue totaled 440.64 s across all per-source operations; retrieval queue 0.060 s. This is real tool-heavy work, but current fetch utilization already suggests the obvious intervention. It has **not** established the desired case where current utilization is inadequate.

Continue the fixed preregistered performance comparison to exercise model-neutral validation on independently authored tasks. Do not alter prompts, extraction, task selection, thresholds or model to rescue this result during the study. Publish performance comparisons conditionally and keep the quality failure separate. No outcome can count as quality-preserving model decision value unless the stated gate passes. This finding is useful evidence for the toolkit; it is not a revived planner thesis.
