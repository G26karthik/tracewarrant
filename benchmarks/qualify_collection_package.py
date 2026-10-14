"""Fresh installed-wheel SDK qualification with locked offline optional dependencies."""

import argparse
import hashlib
import json
import subprocess
import tempfile
import venv
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.artifacts import write_new

ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import importlib.metadata, json, sys
from pathlib import Path
from zipfile import ZipFile
import workload_lab.collection
import workload_lab.otel_collection
wheel, root, output = map(Path, sys.argv[1:])
distribution=importlib.metadata.distribution("tracewarrant")
assert not distribution.requires
hashes={}
with ZipFile(wheel) as archive:
    import hashlib
    for name in archive.namelist():
        if name.startswith("workload_lab/") and name.endswith(".py"):
            path=Path(distribution.locate_file(name)).resolve()
            assert not path.is_relative_to(root)
            assert path.read_bytes()==archive.read(name)
            hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
# Only source examples/harness are used; the core is already loaded from the wheel.
sys.path.append(str(root))
from benchmarks.qualify_collection import qualify
result=qualify()
from benchmarks.measure_collection import peak_memory_bytes
result["peak_process_bytes"]=peak_memory_bytes()
assert result["peak_process_bytes"] < 2*1024**3
result["provisional_2gib_process_ceiling_met"]=True
assert result["framework_conformance"]["claims"]["queue_wait"]["observed"]==2
assert "workload_lab.simulation" not in sys.modules and "simpy" not in sys.modules
result["installed_module_sha256"]=hashes
result["installed_wheel_sdk_verified"]=True
result["runtime_core_dependencies"]=[]
output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
"""


def qualify(wheel, uv):
    wheel = wheel.resolve()
    with tempfile.TemporaryDirectory(prefix="tracewarrant-sdk-package-") as folder:
        work = Path(folder)
        env = work / "runtime"
        venv.EnvBuilder(with_pip=False).create(env)
        python = env / ("Scripts/python.exe" if (env / "Scripts").is_dir() else "bin/python")
        requirements = work / "integration.txt"
        subprocess.run(
            [
                uv,
                "export",
                "--locked",
                "--only-group",
                "integration",
                "--no-emit-project",
                "--output-file",
                str(requirements),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            [
                uv,
                "pip",
                "install",
                "--offline",
                "--require-hashes",
                "--python",
                str(python),
                "-r",
                str(requirements),
            ],
            cwd=work,
            check=True,
            capture_output=True,
            timeout=60,
        )
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
        result = work / "result.json"
        subprocess.run(
            [str(python), "-I", str(probe), str(wheel), str(ROOT), str(result)],
            cwd=work,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        report = json.loads(result.read_bytes())
    return {
        "artifact_type": "installed_collection_qualification",
        "metadata": metadata(__file__, {"network": False, "model_execution": False}, 0),
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "checks": report,
        "limits": [
            "source_examples_use_installed_core",
            "optional_dependencies_supplied_separately",
            "testmodel_not_real_task_quality",
            "not_independent_review",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args()
    write_new(args.output, qualify(args.wheel, args.uv))
    print('{"installed_collection_qualified":true}')


if __name__ == "__main__":
    main()
