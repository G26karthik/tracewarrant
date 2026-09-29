# Qualifying the local 0.3.1 distribution

These checks establish local engineering readiness, not production suitability, independent review or public publication. The artifact format remains 1.0; the package is `tracewarrant` 0.3.1. Keep the `Private :: Do Not Upload` classifier until the prospective public upload is requested. The public name is chosen; the proposed destination and security channel are recorded in the [naming decision](naming-2026-09-29.md).

## Repeatable checks

Run from the repository with Python 3.11+ and uv 0.9.26:

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build --no-build-isolation
uv run python -m benchmarks.qualify_package --wheel dist/tracewarrant-0.3.1-py3-none-any.whl --sdist dist/tracewarrant-0.3.1.tar.gz --output qualification-new.json
uv run python -m benchmarks.v3_audit --output audit-new.json
```

Use new output names and inspect their `metadata.git_commit`, `git_dirty`, source/lock hashes and OS/Python fields. Qualification is offline after the development tools are installed. Its temporary environment is removed automatically. Pass `--uv /absolute/path/to/uv` if uv is not on PATH.

The package check verifies:

- Wheel, source archive and current checkout contain identical package code; missing modules and stale builds are refused before installation. The source archive includes current schema, lockfile, license, tests, qualification harness and frozen reproduction inputs.
- A fresh virtual environment installs only the wheel, without an index, runtime dependencies or package-manager cache reuse.
- Every installed package module has the same SHA-256 as the wheel member, preventing stale-cache or source-checkout imports from masquerading as installed-package verification.
- The installed CLI reports the built version, emits the schema, checks a valid artifact and refuses a missing artifact with exit code 2. Both `tracewarrant` and the compatible `workload-lab` entry points run.
- Installed conformance checks produce the expected support/refusal for controlled, PydanticAI and original FRAMES traces.
- The installed validator reproduces the frozen evaluation byte for byte without importing simulation, calibration or SimPy.

CI runs qualification after building on both configured OS/Python matrix combinations. Hosted CI requires a remote repository; local results must not be described as hosted-CI results.

## Linux on the existing Windows host

The available Ubuntu WSL distribution can run the same checkout, but use an independent Linux virtual environment. Never let Linux uv replace the Windows `.venv`. Set `UV_PROJECT_ENVIRONMENT` to a Linux-only path, such as a directory under the user's cache, and pass the Linux interpreter explicitly. This host clears `/tmp` across WSL shutdowns, so persistent tools/environments belong outside `/tmp`. Build into a separate output directory if both platforms are being qualified concurrently. No Docker service or cloud machine is necessary.

For `uv build --no-build-isolation`, pass `--python` pointing to the Linux development environment's `bin/python`. Setting only `UV_PROJECT_ENVIRONMENT` did not make this uv build command select that environment on this host; the first attempt could not import hatchling. Explicit interpreter selection fixed the build without changing dependency requirements.

## Scientific record

The offline audit protects the 64-file V2 manifest, `research-pilot-1`, the 72 original/adapted FRAMES sessions and the exact frozen evaluation. The 0.3.1 fixes do not change the published FRAMES result. The failed quality gate remains failed. A local package check is not evidence of external adoption or better intervention decisions than the heuristic.
