# Local raw benchmark evidence

The initial analysis harness results use the six-span synthetic fixture. Timing measures actual CPU execution of the parser/compiler/analyzer. Fixture durations are invented and are not agent performance results. No speedup or capacity claim follows from this smoke benchmark.

Each JSON contains raw samples, source commit/dirty state and hashes. Run the harness at a clean commit for the code under test; a later documentation-only commit may add its result. See [methodology](../methodology.md) and [reproduction command](../../../benchmarks/README.md).

## Initial measured allocation correction

Both runs used 20 timed repetitions after 3 warmups on the same local machine and six-span fixture. Allocation profiling ran separately. These are descriptive smoke measurements, not statistically established application speedups.

| Artifact | Code commit | Median parse/compile/analyze | Python allocation peak |
| --- | --- | --- | --- |
| [Initial read](analysis-smoke.json) | 65a5988 | 6.51505 ms | 16,786,663 bytes |
| [Bounded chunk read](analysis-smoke-bounded-read.json) | e4a1bb0 | 0.84595 ms | 84,860 bytes |

The initial `read(max_bytes + 1)` allocated near the 16 MiB input allowance even for this small file. Bounded chunks avoid that preallocation while retaining the byte limit. This result justified a small parser change; it supplies no evidence for native code, agent throughput, GPU capacity or infrastructure recommendations. Source and lock hashes are preserved in both raw artifacts.
