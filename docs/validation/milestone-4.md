# Milestone 4 — controlled pilot passed; general calibration remains partial

Predictions were frozen at `377180c` / tag `pilot-1-freeze`, before all 960 held-out sessions. SHA-256: `d1ddf4a4be7372c7426e3c260a40215d715a443c8d41191c01720e15d1d360c4`. Criteria were committed earlier at `31bb58b`. Training: 160 separate baseline sessions in two load cohorts. No holdout spans were used to fit parameters or choose primary model. [Training, predictions, holdout and evaluation](../experiments/README.md) preserve the chain.

| Offered/s | Configuration | Frozen p95 (ms) | Measured p95 (ms) | Relative error |
| --- | --- | --- | --- | --- |
| 6 | BASELINE | 234.40 | 234.1 | 0.1% |
| 6 | TOOL+ | 233.64 | 230.1 | 1.5% |
| 6 | MODEL+ | 234.40 | 232.2 | 0.9% |
| 6 | RETRIEVAL+ | 234.40 | 232.6 | 0.8% |
| 8 | BASELINE | 1809.93 | 1720.7 | 5.2% |
| 8 | TOOL+ | 233.64 | 229.4 | 1.9% |
| 8 | MODEL+ | 1809.93 | 1691.2 | 7.0% |
| 8 | RETRIEVAL+ | 1809.93 | 1641.8 | 10.2% |

Primary median p95 relative error **1.70%**, below preregistered 15%. Both material intervention pairs were correctly ordered (2/2; small denominator). The only clear bottleneck cell was tool contention at 8/s; its mean tool queue was 761 ms/session and the predicted pool agreed. The 6/s bottleneck was ambiguous and was not counted as correct. All other intervention comparisons remain ties/ambiguous under the predeclared 10%/replication rule. Per-cell p50/p99, outcomes, replications, whole-session bootstrap, paired-session sensitivity and fixed-tool-delay errors are in [evaluation](../experiments/pilot-evaluation.json). p99 is underpowered; seed ranges are not 95% prediction intervals. No steady-state saturation threshold was identified.

**Negative result:** the utilization heuristic chose TOOL+ too. The model differs from inference-only/naive-slot planning and predicts latency magnitude, but this pilot shows no added choice value over that heuristic. It is not sufficient evidence for a general optimizer or a distinct commercial/OSS planner. Direct measured holdout collection took 150.8 s, and the frozen 720 simulated scenarios took 6.26 s; training took 51.9 s. Engineering/calibration effort is not measured, so no economic break-even is claimed.

The narrow fitter preserves empirical samples and tails, records sample counts/cohorts/source IDs, rejects missing/failed/censored/mixed-topology sessions, and reports CV and within-session correlations. Paired-session empirical sampling is supported as a frozen sensitivity comparison. No automatic exponential fitting. Cohorts at 2/9 arrivals/s are kept separate; nearest observed load supplies parameters for 6/8/s, an explicit interpolation assumption. No pooled application/hardware/config versions.

Limits: workload v2 uses **stub inference**, actual local queues and SQLite. It has fixed topology and no failures. Unseen tails, shared outages, missing whole traces, nonstationary arrivals, generic retry/branch fitting and long-horizon saturation remain unsupported. Short Windows timer behavior was discovered during M1.5 and motivated longer v2 intervals before calibration. Shared-workstation measurements were not isolated: local model/account discovery occurred near the latter part of the holdout sweep; it did not change the application or predictions, but ancillary load remains a confound. Repeated directions are preserved rather than filtering a run.

Next responsible step: a bounded real-model non-coding application probe and adversarial reassessment. Do not turn a controlled pass into an infrastructure recommendation.
