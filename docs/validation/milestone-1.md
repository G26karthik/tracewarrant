# Milestone 0 and 1 verification

Date: 2026-09-29 (maintainer local date). Environment: Windows, CPython 3.12.12, uv 0.9.26. Scope: research/spec foundation plus local deterministic trace analysis.

Delivered: 34-section canonical V2; dated competitive/adversarial review; historical mapping; 12 ADRs with explicit accepted/proposed status; domain/OTel/provenance contracts; testing/benchmark/calibration/optimization/cloud plans; Apache-2.0 license and resolved dependency inventory; locked pure-Python package; CI matrix; synthetic fork/join fixture; library and CLI.

Local validation:

- 63 passing tests, including five Hypothesis properties with deterministic settings and 100 examples per property. Tests include serial sums, ideal parallel maxima, monotonic reduced serial work, topological order and an exhaustive-path oracle for small random DAGs.
- Contract cases cover malformed/nonfinite/duplicate data, exact epoch nanoseconds, cycles, invalid clock/dependency relationships, nested containers, missing parents, content exclusion, loss diagnostics, input limits and evidence consistency.
- A 5,000-work-node chain is analyzed iteratively, without recursion overflow.
- CLI JSON is deterministic across processes; compiled IR output refuses overwrite and errors omit payload/path contents.
- Ruff lint and format checks pass; source distribution and wheel build successfully. Wheel metadata declares no third-party runtime dependencies; inspected archive contains only the library and distribution metadata/license.
- Both original handoff SHA-256 hashes still match [preservation evidence](../design/historical-sha256.json). All 12 ADRs contain the required fields; local documentation links are checked.

The [initial CPU smoke result](../benchmarks/results/analysis-smoke.json) records actual harness timing separately from synthetic workload values. It exposed allocation close to the byte limit on a tiny input; the importer now reads bounded chunks. Follow-up evidence is recorded separately. These runs are not simulator benchmarks, hardware calibration, real-agent runs or deployment validation. Git commit, dirty state, source/harness/lock/workload hashes, environment and raw samples are in each artifact.

Limits: GitHub-hosted CI has not run; its Windows/Linux and Python 3.11/3.13 matrix is configured, while local execution used Python 3.12.12. Only the documented OTLP JSON subset is supported. General vendor exports, compiled-IR reimport, live collection, metric ingestion, streaming dependencies and arbitrary asynchronous containment are unsupported. Complete dependency coverage is an instrumentation assertion. No statistical confidence interval or infrastructure recommendation is emitted.

Both handoffs were fully read as text/OOXML, including tables, header/footer and revision inspection. DOCX page-layout rendering could not run because bundled `soffice.exe` was unavailable; no historical document was edited. The project thesis remains unproven pending the later measured intervention loop.
