"""Common metadata for measured experiments; no automatic network access."""

import hashlib
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from benchmarks.analysis_benchmark import git, memory_bytes

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata(harness, configuration, seed):
    cpu = platform.processor()
    if os.name == "nt":
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
            capture_output=True,
            text=True,
            check=False,
        )
        cpu = result.stdout.strip() or cpu
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*.py")):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    return {
        "date_utc": datetime.now(UTC).isoformat(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "source_tree_sha256": digest.hexdigest(),
        "harness_sha256": sha(harness),
        "dependency_lock_sha256": sha(ROOT / "uv.lock"),
        "os": platform.platform(),
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "ram_bytes": memory_bytes(),
        "gpu": "not used",
        "driver": "not applicable",
        "cuda": "not applicable",
        "python": sys.version,
        "compiler": platform.python_compiler(),
        "cpp_compiler": "not applicable",
        "configuration": configuration,
        "seed": seed,
    }
