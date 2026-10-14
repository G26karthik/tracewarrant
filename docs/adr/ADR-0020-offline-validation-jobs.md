# ADR-0020: Explicit offline validation jobs and portable replay

Date: 2026-10-14. Status: accepted for V4.

The V3 library provides conformance, freezes and evaluation, but developers must assemble files and interpret acceptance manually. Add a strict job manifest selecting one model and explicit policy, reusing the independent evaluator without changing artifact schema 1.0 or historical receipts.

Capture bounded local input bytes once. Paths remain within the manifest directory; no application commands, URLs, plugins or model execution are accepted. Export preserves evidence bytes, rewrites job paths and binds every payload with SHA-256. Verification snapshots validated bytes before replay and checks report/evidence consistency. Hashes are integrity evidence, not authentication.

Return 0 for accepted policy, 1 for failed/unsupported requirements and 2 for invalid evidence or I/O. Expose every gate. Error limits apply to the worst primary comparison. Required measured quality must cover every scenario/replication. Omitted quality explicitly limits scope. Added decision value must beat every supplied baseline, including stronger heuristics.

Produce deterministic JSON and escaped standalone HTML without scripts or remote assets. Create outputs exclusively; on failed writes remove only owned files. Display calibration extrapolation even when a narrow policy permits it.

Use retained FRAMES evidence retrospectively. A separate adapter exports existing exact-match labels with verified source lineage; it invents no labels or measurements. Strict policy fails; numerical-only acceptance declines quality/added-value claims. This delivers a usable workflow, not external adoption, production certification or model superiority.
