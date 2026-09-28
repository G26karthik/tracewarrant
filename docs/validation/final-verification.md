# Final local verification

2026-09-29, Windows. Internal release 0.2.0; not published.

- 102 tests pass on CPython 3.12.12 (4.16 s observed run) and isolated CPython 3.13 (4.75 s). Includes Hypothesis semantics, bounded random JSON, scenario/CLI contracts, actual concurrent capture, lifecycle, calibration refusal and paired-vector checks.
- Ruff lint and formatting pass. Wheel/sdist build; isolated wheel-only `simulate` command completes the example. Wheel has no `Requires-Dist` runtime entries and no unexpected files.
- Final committed source `944e20d` independently reran the five analytical M/M/1 cases and all 20 SimPy cross-checks: [raw final verification](../benchmarks/results/m2-validation-final.json), clean source metadata, unchanged 1.6237% aggregate analytical error. The earlier gate artifact remains intact.
- Local Markdown link audit reports zero broken targets; `git diff --check` passes.
- Both historical handoff SHA-256 values match the original preservation manifest.
- Frozen predictions retain SHA-256 `d1ddf4a4be7372c7426e3c260a40215d715a443c8d41191c01720e15d1d360c4`. Criteria and predictions precede held-out collection in Git. No post-holdout refit or threshold change.
- The real-model summary reimports every successful probe trace through the core compiler; 48 complete graphs, 48 fact checks and the 1.728 client-occupancy ratio are reproducible from raw observations.
- Optional integration/validation dependency license metadata refreshed; core remains dependency-free. The exact environment/software/hardware of each experiment is in its raw artifact.

Hosted CI is configured, not executed here. Linux/Python 3.11 are unverified locally. No public release or remote repository exists. Generated mathematical agreement, controlled predictive accuracy and real application feasibility are distinct claims; none substitutes for production-agent validation.
