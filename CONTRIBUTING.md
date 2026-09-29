# Contributing

Read [PROJECT_STATUS.md](PROJECT_STATUS.md) and [PROJECT_V3.md](PROJECT_V3.md) before changing scope. TraceWarrant is the selected public name; Workload Lab remains in compatible interfaces and historical evidence. V2 and `research-pilot-1` are frozen research history. Native/cloud/optimization work must earn a measured V3 requirement. Preserve historical handoffs, frozen predictions and failed observations. The preservation test checks the 64-file V2 manifest.

Use Python 3.11+ and `uv sync --locked`. Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest`. The runtime has no third-party dependencies. Dev dependencies are locked in `uv.lock`. Keep changes small; add a dependency only with alternatives and a measured requirement. Do not commit environments, raw user traces, credentials or generated private reports.

Before handing off a distribution, run the [installed-package qualification and offline preservation audit](docs/v3/release-qualification.md). A test from an editable checkout is not proof that the built wheel works. Report local OS/Python checks separately from hosted CI and independent review.

Domain code belongs in the library, file/argument handling in the CLI, vendor interpretation in importers. Use immutable typed records, explicit units, deterministic ordering and actionable errors without payload text. Never equate parentage with causality or elapsed span duration with service demand. Unknown metrics remain null with evidence. Public IR changes require versioning and contract fixtures.

Add meaningful unit/property/contract tests for new semantics. Test failure and incomplete-data paths. For algorithms, include a simple independent baseline or hand-solvable case. Benchmark metadata and raw data are mandatory for performance claims; negative results are welcome. Hardware/compiler/CUDA claims require measurements on the named hardware.

Use Apache-2.0 for new contributions and preserve external attribution. Inspect licenses before importing code or data; citation alone is not redistribution permission. The reviewed competitors are not dependencies. Update ADRs and docs with implementation changes. Confirm no sensitive content before publishing any trace/profile/artifact.
