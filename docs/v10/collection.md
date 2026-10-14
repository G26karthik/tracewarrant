# Collect owned observation boundaries

Experimental 0.8.0 adds `workload_lab.collection.ObservationRecorder`. Core use
requires only Python 3.11+. It creates bounded content-free OTLP JSON that the
existing `tracewarrant inspect` and `analyze` commands can read. The recorder
observes your acquire/release functions; it does not implement a semaphore,
change scheduling or discover a resource's real capacity.

```python
import asyncio
from workload_lab.collection import ObservationRecorder
from workload_lab.ir import NodeKind

recorder = ObservationRecorder()
pool = recorder.pool(capacity=1)
slots = asyncio.Semaphore(1)  # Your actual resource limit.


async def run():
    with recorder.run() as observed_run:  # Incomplete by default.
        with observed_run.operation(NodeKind.TOOL) as operation:
            async with operation.lease(pool, slots.acquire, slots.release):
                # Execute your real owned operation here.
                pass


asyncio.run(run())
recorder.write("new-trace.json")  # Existing output is refused.
```

Only an explicitly closed, fully instrumented scope may set `run(complete=True)`.
Declare `depends_on=(finished_operation,)` when actual finish-to-start semantics
exist. Predecessors must be finished operations in that same run. The library
never derives them from containment, overlap, span names or tool order.
Operations are atomic: nested atomic contexts are refused, while parallel
siblings created directly under a run are supported. Root/container time is not
added to atomic work. A handled instrumentation refusal may downgrade completeness.

Use one recorder/opaque pool handle for each actual shared pool in a capture.
Pool identity is generated, capacity is fixed and handles cannot be borrowed
from another recorder. A new handle declares another pool; do not create handles
per session for a shared semaphore or rename a pool to hide configuration drift.
Separate changed configurations into explicit cohorts. Identity is a collector
declaration, not authenticated discovery or correlation across independent files.

`lease` requires asynchronous acquisition and synchronous release. Acquire must
return only after ownership is obtained, or raise on failure; release must
perform the actual release and return synchronously. Caller callbacks are trusted
boundary declarations. The recorded queue interval includes callback overhead,
and service interval means the owned body interval, not intrinsic CPU/GPU demand.
The same task performs acquisition/release in normal `async with` use. No native
Pydantic limiter is replaced or monkeypatched.

Cancellation before successful acquisition records no fabricated acquired/released
timestamps and never releases someone else's token. After acquisition, actual
caller cleanup runs before leaving the lease. Original body exceptions are
preserved; cleanup failure becomes their cause. Clock/recording faults also mark
capture invalid without bypassing release or masking an existing body exception.
An uncertain release or abandoned operation prevents export. Local release is not
proof of cancellation at a remote backend. A caught timeout can be recorded as
`timeout`; deadlines and remote acknowledgement remain unsupported in IR 0.2.

For explicit retries, create `group = observed_run.attempt_group()`, then use
`operation(..., attempt_group=group, attempt=1)` and a new operation for each
attempt. The existing inspector flags missing/duplicate sequences; it cannot
discover hidden retries. Failure outcomes are observations, not quality scores.

The recorder uses one epoch anchored to a monotonic clock, suitable for its
single event-loop/thread capture. It does not correct cross-host skew. Default
limits are 10,000 spans and 16 MiB; configured spans cannot exceed 50,000 and the
byte limit cannot exceed 16 MiB. Runs consume a span. Pool and attempt handles
share a recorder-wide budget bounded by the span budget. Span exhaustion refuses the next boundary
before its body executes; byte exhaustion invalidates export. Entire-envelope
serialization is checked before writing. Active, empty, invalid or truncated
captures are never exported as a certified subset. Use a new recorder per bounded
batch/cohort. A capture assertion cannot prove that an application omitted nothing.

No application labels, prompts, answers, arguments, SQL, URLs, exception strings
or arbitrary metadata are accepted by the public recording API. Generated IDs,
known node kinds, counts, timestamps and outcomes are persisted. This is not a
security boundary against caller code modifying private internals or inventing
measurements. Output writes are exclusive; an I/O failure may leave a partial
new file, which must not be treated as evidence.

## Optional OpenTelemetry export

`workload_lab.otel_collection.export_observations(recorder, exporter)` accepts a
caller-supplied SDK `SpanExporter`. The integration is tested with OTel SDK
1.45.0; the caller supplies that optional package (for checkout work, use
`uv sync --locked --group integration`). Core imports and CLIs require no SDK.

The bridge constructs SDK readable spans from the closed capture, preserving
identities, parentage, timestamps, roles, edges and typed observation attributes.
It exports only generated fixed names/metadata, with no events or raw content.
Bounds are checked before export; explicit exporter failure is refused. Each
invocation exports a batch; repeated calls may duplicate it. No provider,
processor, global tracing setting, retry or network connection is installed.
Your exporter may send records remotely if you choose to configure it that way.
The bridge does not sanitize an application's separate native exporter.

```sh
uv run python -m examples.collect_observations --output artifacts/owned-new.json
uv run tracewarrant inspect artifacts/owned-new.json --output artifacts/owned-inspection.json
uv run --group integration python -m examples.collect_pydantic_observations --output artifacts/framework-new.json
uv run tracewarrant inspect artifacts/framework-new.json --output artifacts/framework-inspection.json
```

The plain SQLite example explicitly records two closed serial operations and a
real predecessor edge. The pinned Pydantic AI 2.51.0 example uses TestModel,
disables remote model requests and restores that setting afterwards. It records
two owned local tool operations and retains standard native model spans as a
separate companion trace. The known outer tool spans are containers to avoid
double counting. It does not fabricate a merged causal graph: queue/occupancy/
capacity coverage is **2/4, partial**, and graph/prediction suitability remain
unsupported. Model service demand stays UNKNOWN. This is interface execution,
not real task quality or external adoption.

## Qualification and collection cost

`benchmarks.qualify_collection_package` installs the wheel into a fresh isolated
environment with separately supplied, locked optional dependencies, checks module
bytes, then executes the bridge and framework example. Existing package
qualification also checks installed stdlib collection and absence of SDK imports
in a dependency-free wheel-only environment.

`benchmarks.measure_collection` measures paired fresh-process loops with real
local SQLite work, a caller-owned semaphore, 500 operations, 10,000 generated
rows and five repetitions in alternating order. It records raw elapsed/CPU time,
separate final serialization cost, bytes and peak process working set. Windows
uses [GetProcessMemoryInfo](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo);
Unix uses peak resident-set data. This is a microbenchmark, not an agent capacity
study. Collector overhead is material for short operations; use boundaries at the
resource-operation level and measure it for your workload. No negligible-overhead
or general speedup claim is made. The final exact-source report is attached to
the qualified release; preliminary timings are not a release claim.
