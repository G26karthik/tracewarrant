# ADR-0026: owned boundaries and explicit SDK export

Date: 2026-10-14. Status: accepted for V10 implementation.

Implement a narrow stdlib recorder with opaque generated identities, explicit
atomic operations/finished predecessor handles and optional owned resource leases.
Delegate acquisition and synchronous release to caller functions. Do not replace
framework scheduling, infer dependencies or assert graph completeness by default.
Reject atomic nesting; preserve parallel sibling capture and real denominators.

Timestamp each capture on a monotonic clock anchored to one epoch. Fixed pool
handles are collector assertions, not physical-capacity discovery. Export only
fully closed, bounded captures. Buffer exhaustion, uncertain cleanup and abandoned
operations invalidate export instead of silently producing an accepted subset.
Run cleanup despite observer faults, preserve application exceptions and record
no exception messages. Caller code remains capable of inventing observations.

An optional explicit exporter bridge constructs OTel SDK readable spans from
closed neutral observations. This preserves IDs/times without installing global
providers or swapping the SDK's ID generator/sampling. Exporter selection and
transport remain the caller's responsibility. Separate native framework spans are
not merged into a fabricated causal graph. The pinned TestModel example retains
unowned model operations and partial 2/4 coverage, with fixed known outer tool
containers to prevent double counting.

Measure overhead and peak working set against the same real SQLite loop without
recording, including raw repetitions and separately reported serialization. The
collector has material cost for short operations; do not claim free tracing or
generalize this probe to agent/model throughput. Fresh core-only and SDK-supplied
installed environments plus hosted OS/Python checks qualify distribution.

Keep all earlier wire formats, failed studies and release tags immutable. This
implements the scoped collection requirement, not model superiority, independent
adoption or production certification. [Usage and limits](../v10/collection.md).
