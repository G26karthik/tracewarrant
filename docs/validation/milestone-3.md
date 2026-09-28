# Milestone 3 — native gate assessed, C++ deferred

Date: 2026-09-29. [Raw fresh-process scale measurements](../benchmarks/results/simulation-scale.json), clean source `06fb978`. Three repeats at each size, full configuration/source/lock/harness hashes and measured hardware included.

| Target events | Actual events | Median events/s | Largest process peak |
| --- | --- | --- | --- |
| 1,000 | 1,002 | 481,546 | 24,358,912 bytes |
| 100,000 | 100,002 | 390,666 | 49,623,040 bytes |
| 1,000,000 | 1,000,002 | 297,514 | 280,354,816 bytes |

The million-event median is 3.361 s. This D/D/4 burst case is a scale probe, not a representative production agent benchmark. Peak is whole-process working set high-water, not heap bytes/event; timing excludes scenario construction/hash, recorded separately. 10 million would require 1,666,667 sessions, above the explicit 250,000 session bound; not run because no current experiment needs it. State scales with sessions and tasks. A first memory-counter call failed because the Windows HANDLE type was omitted; the corrected harness was smoke-tested and committed before the published run.

Decision: **retain Python**. No demonstrated experiment bottleneck justifies native ownership/parity/sanitizer cost. No C++ throughput advantage has been claimed or measured. Reopen only with a concrete workload that makes this cost material; consider SimPy or existing engine integration first. CUDA is likewise not needed for the current explicit-slot hypotheses.
