"""Qualify a built wheel and source archive in a fresh, dependency-free environment."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile

from benchmarks.provenance import metadata
from workload_lab.artifacts import write_new

ROOT = Path(__file__).resolve().parents[1]

# Run outside the checkout, under the new environment's Python in isolated mode.
# Importing this probe from the source tree would invalidate the packaging check.
PROBE = r"""
import hashlib
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

from workload_lab.artifact_schema import SCHEMA
from workload_lab.artifacts import canonical_bytes
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import ingest
from workload_lab.jobs import JOB_SCHEMA, bundle_job, run_job, verify_bundle
from workload_lab.qualification import (POLICY_SCHEMA, SAMPLE_SCHEMA,
    PLAN_SCHEMA, FREEZE_SCHEMA, freeze_application_quality, qualify_application)
from workload_lab.validation import evaluate
from workload_lab.quality_bundle import bundle_quality, verify_quality_bundle
from workload_lab.collection import ObservationRecorder
import workload_lab.otel_collection
from workload_lab.ir import NodeKind
import asyncio

root, wheel = map(Path, sys.argv[1:])
distribution = importlib.metadata.distribution("tracewarrant")
assert not distribution.requires, "unexpected runtime dependencies"
assert {d.metadata["Name"] for d in importlib.metadata.distributions()} == {
    "tracewarrant"
}, "runtime environment contains other distributions"
module_hashes = {}
with ZipFile(wheel) as archive:
    for name in archive.namelist():
        if name.startswith("workload_lab/") and name.endswith(".py"):
            installed = Path(distribution.locate_file(name)).resolve()
            assert not installed.is_relative_to(root), "source checkout import"
            digest = hashlib.sha256(installed.read_bytes()).hexdigest()
            assert digest == hashlib.sha256(archive.read(name)).hexdigest(), "stale installation"
            module_hashes[name] = digest
assert module_hashes
async def collect_owned():
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    with recorder.run(complete=True) as run:
        with run.operation(NodeKind.TOOL) as operation:
            async with operation.lease(pool, semaphore.acquire, semaphore.release):
                pass
    recorder.write("installed-observations.json")
    return recorder
asyncio.run(collect_owned())
owned = inspect_observations(ingest("installed-observations.json"))
assert owned["claims"]["queue_wait"]["support"] == "supported"
assert owned["claims"]["dependency_graph"]["support"] == "supported"
assert owned["claims"]["inference_service_demand"]["value"] is None
assert not any(name.startswith("opentelemetry") for name in sys.modules)
assert SCHEMA == json.loads((root / "schemas/validation-artifact-v1.schema.json").read_bytes())
assert JOB_SCHEMA == json.loads((root / "schemas/validation-job-v1.schema.json").read_bytes())
assert SAMPLE_SCHEMA == json.loads(
    (root / "schemas/application-sample-v1.schema.json").read_bytes())
assert POLICY_SCHEMA == json.loads(
    (root / "schemas/application-quality-policy-v1.schema.json").read_bytes())
quality_example = root / "examples/qualification/hotpot"
quality = qualify_application(quality_example / "sample.json", quality_example / "policy.json")
assert quality["result"] == "failed"
assert [g["status"] for g in quality["gates"]] == ["passed", "passed", "failed", "failed"]
assert quality["counts"]["offered"] == 8
frozen_quality = root / "examples/qualification/hotpot-frozen"
bound_quality = qualify_application(frozen_quality / "sample.json", frozen_quality / "policy.json",
    plan_path=frozen_quality / "plan.json", freeze_path=frozen_quality / "freeze.json")
assert bound_quality["result"] == "failed" and bound_quality["binding"]["status"] == "verified"
assert bound_quality["binding"]["chronology"] == "not_authenticated"
assert PLAN_SCHEMA == json.loads(
    (root / "schemas/application-quality-plan-v1.schema.json").read_bytes())
assert FREEZE_SCHEMA == json.loads(
    (root / "schemas/application-quality-freeze-v1.schema.json").read_bytes())
example = root / "examples/validation/frames"
assert run_job(example / "job.json")["result"] == "failed"
assert run_job(example / "performance-job.json")["result"] == "passed"
bundle = Path("portable-evidence")
bundle_job(example / "performance-job.json", bundle)
assert verify_bundle(bundle)["bundle_checksums_verified"]

frozen = root / "docs/v3/frames-frozen"
measured = root / "docs/v3/frames-evaluation"
result = evaluate(
    frozen / "protocol.json", frozen / "freeze.json",
    [frozen / f"{name}.json" for name in ("simpy", "fixed", "utilization")],
    [measured / f"measured-r{r}.json" for r in range(2)],
)
assert canonical_bytes(result) == (measured / "validation.json").read_bytes()
sources = {}
for label, path, expected in (
    ("controlled", "examples/traces/controlled-v1.otlp.json", "supported"),
    ("pydantic_ai", "examples/traces/pydantic-ai-2.51.0.otlp.json", "unsupported"),
    ("frames_original", "examples/v3/frames-heldout-base.otlp.json", "unsupported"),
):
    report = inspect_observations(ingest(root / path))
    sources[label] = report["claims"]["dependency_graph"]["support"]
    assert sources[label] == expected
    assert report["claims"]["prediction_suitability"]["support"] == "unsupported"
for forbidden in ("workload_lab.simulation", "workload_lab.calibration", "simpy"):
    assert forbidden not in sys.modules, "simulator coupling"

command = [sys.executable, "-I", "-m", "workload_lab"]
version = subprocess.check_output([*command, "--version"], text=True).strip()
assert distribution.version in version
entry_points = {e.name for e in distribution.entry_points if e.group == "console_scripts"}
assert entry_points == {"tracewarrant", "workload-lab"}
for name in entry_points:
    executable = Path(sys.executable).parent / (name + (".exe" if sys.platform == "win32" else ""))
    assert subprocess.check_output([str(executable), "--version"], text=True).strip() == version
assert json.loads(subprocess.check_output([*command, "schema"])) == SCHEMA
assert json.loads(subprocess.check_output([*command, "quality-schema", "sample"])) == SAMPLE_SCHEMA
assert json.loads(subprocess.check_output([*command, "quality-schema", "policy"])) == POLICY_SCHEMA
quality_process = subprocess.run([
    *command, "qualify-application", str(quality_example / "sample.json"),
    "--policy", str(quality_example / "policy.json"), "--output", "application-quality-report"
], capture_output=True, text=True)
assert quality_process.returncode == 1
installed_quality = json.loads(Path("application-quality-report/report.json").read_bytes())
assert installed_quality["gates"] == quality["gates"]
assert "Every offered row" in Path("application-quality-report/report.html").read_text()
assert subprocess.run([*command, "freeze-quality", "--plan", str(frozen_quality / "plan.json"),
    "--policy", str(frozen_quality / "policy.json"), "--output", "new-quality-freeze.json"],
    capture_output=True).returncode == 0
assert subprocess.run([*command, "qualify-application", str(frozen_quality / "sample.json"),
    "--policy", str(frozen_quality / "policy.json"), "--plan", str(frozen_quality / "plan.json"),
    "--freeze", "new-quality-freeze.json", "--output", "frozen-quality-report"],
    capture_output=True).returncode == 1
assert json.loads(subprocess.check_output([
    *command, "check", str(frozen / "simpy.json")
]))["valid"]
assert subprocess.run([
    *command, "check", "missing.json"
], capture_output=True).returncode == 2
for manifest, code, output in (("job.json", 1, "strict-report"),
                               ("performance-job.json", 0, "performance-report")):
    process = subprocess.run([*command, "validate-job", str(example / manifest),
                              "--output", output], capture_output=True, text=True)
    assert process.returncode == code
    assert (Path(output) / "report.html").is_file()
assert subprocess.run([*command, "verify-bundle", str(bundle), "--output", "verified-report"],
                      capture_output=True).returncode == 0
(bundle / "report.html").write_bytes(b"<h1>certified</h1>")
sum_path = bundle / "SHA256SUMS"
sum_path.write_text("\n".join(
    hashlib.sha256((bundle / "report.html").read_bytes()).hexdigest() + "  report.html"
    if line.endswith("  report.html") else line
    for line in sum_path.read_text().splitlines()
) + "\n", encoding="ascii")
assert subprocess.run([*command, "verify-bundle", str(bundle), "--output", "forged-job-report"],
                      capture_output=True).returncode == 2
assert not Path("forged-job-report").exists()
assert subprocess.run([*command, "bundle-quality", str(frozen_quality / "sample.json"),
    "--policy", str(frozen_quality / "policy.json"), "--plan", str(frozen_quality / "plan.json"),
    "--freeze", str(frozen_quality / "freeze.json"), "--output", "quality-bundle"],
    capture_output=True).returncode == 1
assert subprocess.run([*command, "verify-quality-bundle", "quality-bundle", "--output",
    "quality-bundle-replay"], capture_output=True).returncode == 1
quality_replay = json.loads(Path("quality-bundle-replay/report.json").read_bytes())
assert quality_replay["bundle_checksums_verified"] and quality_replay["gates"] == quality["gates"]
bundle_quality(quality_example / "sample.json", quality_example / "policy.json", "unbound-bundle")
assert verify_quality_bundle("unbound-bundle")["result"] == "failed"
Path("quality-bundle/report.html").write_bytes(b"forged passed report")
assert subprocess.run([*command, "verify-quality-bundle", "quality-bundle", "--output",
    "invalid-quality-replay"], capture_output=True).returncode == 2
assert not Path("invalid-quality-replay").exists()
print(json.dumps({
    "distribution": distribution.metadata["Name"],
    "version": distribution.version,
    "python": sys.version,
    "runtime_dependencies": [],
    "installed_module_sha256": module_hashes,
    "installed_bytes_match_wheel": True,
    "evaluation_byte_exact": True,
    "simulator_not_imported": True,
    "cli_verified": True,
    "conformance_sources": sources,
    "installed_workflow_verified": True,
    "application_quality_verified": True,
    "frozen_quality_verified": True,
    "portable_quality_verified": True,
    "portable_bundle_verified": True,
    "rehashed_job_html_refused": True,
    "installed_collection_verified": True,
    "optional_otel_not_imported": True,
}))
"""


def qualify(wheel: Path, sdist: Path, uv: str) -> dict:
    wheel, sdist = wheel.resolve(), sdist.resolve()
    code_members = {}
    with ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("workload_lab/") and name.endswith(".py"):
                code_members[name] = archive.read(name)
    if not code_members:
        raise ValueError("wheel has no package code")
    source_members = {
        path.relative_to(ROOT / "src").as_posix(): path.read_bytes()
        for path in (ROOT / "src/workload_lab").rglob("*.py")
    }
    if code_members != source_members:
        raise ValueError("wheel code differs from current source checkout")
    # Inspect, never extract an archive into the checkout.
    with tarfile.open(sdist, "r:gz") as archive:
        roots = {name.split("/")[0] for name in archive.getnames()}
        if len(roots) != 1:
            raise ValueError("source archive must contain one root")
        prefix = roots.pop()
        for name, raw in code_members.items():
            member = archive.extractfile(f"{prefix}/src/{name}")
            if member is None or member.read() != raw:
                raise ValueError("wheel and source archive code differ")
        for relative in (
            "pyproject.toml",
            "uv.lock",
            "LICENSE",
            "schemas/validation-artifact-v1.schema.json",
            "schemas/validation-job-v1.schema.json",
            "examples/validation/frames/job.json",
            "examples/validation/frames/performance-job.json",
            "docs/v3/frames-frozen/freeze.json",
            "docs/v3/frames-evaluation/validation.json",
            "tests/test_v3_validation.py",
            "benchmarks/qualify_package.py",
        ):
            member = archive.extractfile(f"{prefix}/{relative}")
            if member is None or member.read() != (ROOT / relative).read_bytes():
                raise ValueError("source archive missing or stale reproducibility input")
    with tempfile.TemporaryDirectory(prefix="workload-package-check-") as folder:
        work = Path(folder)
        environment = work / "runtime"
        venv.EnvBuilder(with_pip=False).create(environment)
        python = environment / (
            "Scripts/python.exe" if (environment / "Scripts").is_dir() else "bin/python"
        )
        # Bypass package-manager caches and then verify installed bytes explicitly.
        subprocess.run(
            [
                uv,
                "pip",
                "install",
                "--no-cache",
                "--no-deps",
                "--no-index",
                "--python",
                str(python),
                str(wheel),
            ],
            cwd=work,
            check=True,
            capture_output=True,
            timeout=60,
        )
        probe = work / "probe.py"
        probe.write_text(PROBE, encoding="utf-8")
        process = subprocess.run(
            [str(python), "-I", str(probe), str(ROOT), str(wheel)],
            cwd=work,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        result = json.loads(process.stdout)
    return {
        "artifact_type": "local_package_qualification",
        "metadata": metadata(__file__, {"network": False, "model_execution": False}, 0),
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "sdist_sha256": hashlib.sha256(sdist.read_bytes()).hexdigest(),
        "sdist_code_matches_wheel": True,
        "wheel_code_matches_checkout": True,
        "sdist_reproducibility_inputs_verified": True,
        "checks": result,
        "limitations": ["local_qualification_not_independent_review", "not_publication"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--uv", default=shutil.which("uv") or "uv")
    args = parser.parse_args()
    try:
        result = qualify(args.wheel, args.sdist, args.uv)
    except subprocess.CalledProcessError as error:
        detail = error.stderr
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        print(detail or "Package qualification subprocess failed", file=sys.stderr)
        return error.returncode
    write_new(args.output, result)
    print(json.dumps({"version": result["checks"]["version"], "qualified": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
