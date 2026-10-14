# ADR-0023: optional exact-byte quality-plan binding

Date: 2026-10-14. Status: accepted for V7.

V6 reports hashes of supplied sample and quality policy, but cannot enforce a
previous declared rule or roster. Add a separate strict application plan and
quality freeze receipt; optional qualification flags require exact policy/plan
hashes, sample/workload identity and full expected membership before grading.

Preserve the existing sample/policy formats and unbound JSON semantics. Reject
identity, hash or membership mismatches as invalid bound inputs instead of
silently evaluating a smaller subset. Missing scores in matching rows remain
unsupported under V6. A duplicate/impossible roster cannot be frozen.

This is integrity binding, not cryptographic authentication or trusted time. A
caller can construct a later receipt, omit tasks from the initial design or
submit invented measurements. Reports must retain chronology/authenticity limits.
Prefer caller-controlled Git/publication records to introducing a timestamping
service or signatures without a threat model. Keep the failed V5 study unchanged
and label its example binding retrospective.
