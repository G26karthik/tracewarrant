"""Small reproducible CPU benchmark. Raw samples, not capacity claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path

from workload_lab import analyze, compile_workload, ingest

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def memory_bytes():
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
                (name, ctypes.c_ulonglong)
                for name in (
                    "total",
                    "available",
                    "page_total",
                    "page_available",
                    "virtual_total",
                    "virtual_available",
                    "extended",
                )
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.total
        return None
    if hasattr(os, "sysconf"):
        try:
            return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (ValueError, OSError):
            pass
    return None


def run(path, runs, warmups):
    rows = []
    for index in range(warmups + runs):
        start = time.perf_counter_ns()
        dataset = ingest(path)
        parsed = time.perf_counter_ns()
        workflows = compile_workload(dataset)
        compiled = time.perf_counter_ns()
        reports = [analyze(w) for w in workflows]
        end = time.perf_counter_ns()
        if index >= warmups:
            rows.append(
                {
                    "run": index - warmups,
                    "ingest_ns": parsed - start,
                    "compile_ns": compiled - parsed,
                    "analyze_ns": end - compiled,
                    "total_ns": end - start,
                }
            )
    tracemalloc.start()
    profiled = [analyze(w) for w in compile_workload(ingest(path))]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(profiled) == len(reports)
    source_hash = hashlib.sha256()
    for source in sorted((ROOT / "src").rglob("*.py")):
        source_hash.update(source.relative_to(ROOT).as_posix().encode())
        source_hash.update(source.read_bytes())
    return {
        "schema_version": "1",
        "benchmark_class": "analysis_microbenchmark",
        "timing_provenance": "MEASURED",
        "workload_origin": dataset.origin,
        "date_utc": datetime.now(UTC).isoformat(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain")),
        "source_tree_sha256": source_hash.hexdigest(),
        "harness_sha256": digest(Path(__file__)),
        "hardware": {
            "cpu": platform.processor(),
            "logical_cpus": os.cpu_count(),
            "physical_ram_bytes": memory_bytes(),
            "gpu": "not used",
        },
        "os": platform.platform(),
        "python": sys.version,
        "compiler": platform.python_compiler(),
        "cpp_compiler": "not applicable",
        "cuda": "not applicable",
        "dependency_lock_sha256": digest(ROOT / "uv.lock"),
        "workload_version": (
            "synthetic-fork-join-v1"
            if path.resolve() == (ROOT / "examples/research-workflow.otlp.json").resolve()
            else "unspecified; identify this input before publication"
        ),
        "workload_sha256": digest(path),
        "span_count": len(dataset.spans),
        "seed": 0,
        "seed_note": "deterministic fixture; no random sampling",
        "runs": runs,
        "warmups": warmups,
        "raw_samples": rows,
        "median_total_ns": statistics.median(r["total_ns"] for r in rows),
        "python_allocation_peak_bytes": peak,
        "limitations": [
            "local smoke benchmark; not agent or capacity validation",
            "tracemalloc peak is not process RSS; measured separately from timing",
            "publication requires rerun at a clean named commit",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "examples/research-workflow.otlp.json")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.runs < 1 or args.warmups < 0:
        parser.error("runs must be positive and warmups nonnegative")
    data = run(args.input, args.runs, args.warmups)
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"Recorded {args.runs} raw samples; workload origin={data['workload_origin']}")
