"""Fresh-process reference DES scale measurements, including whole-process peak memory."""

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.simulation import Arrival, PoolSpec, Scenario, Task, scenario_dict, simulate


def peak_bytes():
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "peak_working",
                    "working",
                    "peak_paged",
                    "paged",
                    "peak_nonpaged",
                    "nonpaged",
                    "pagefile",
                    "peak_pagefile",
                )
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel = ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        ]
        if ctypes.windll.psapi.GetProcessMemoryInfo(
            kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
        ):
            return counters.peak_working
        return None
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )


def sample(events):
    start = time.perf_counter_ns()
    jobs = math.ceil(events / 6)
    spec = Scenario(
        (Task("service", (1000,), "p"),),
        (PoolSpec("p", 4),),
        tuple(Arrival(f"{i:08d}", i * 100) for i in range(jobs)),
        (jobs + 1) * 1000,
        17,
    )
    sha = hashlib.sha256(json.dumps(scenario_dict(spec), sort_keys=True).encode()).hexdigest()
    setup = time.perf_counter_ns() - start
    start = time.perf_counter_ns()
    result = simulate(spec, detail=False)
    elapsed = time.perf_counter_ns() - start
    assert result["outcomes"]["completed"] == jobs
    return {
        "target_events": events,
        "events": result["events_processed"],
        "sessions": jobs,
        "simulation_ns": elapsed,
        "setup_and_hash_ns": setup,
        "events_per_second": result["events_processed"] * 1e9 / elapsed,
        "peak_process_bytes": peak_bytes(),
        "workload_sha256": sha,
    }


def benchmark():
    rows = []
    # Warmup only verifies the code path; each timed repeat starts in a fresh process.
    sample(100)
    for target in (1000, 100_000, 1_000_000):
        for repetition in range(3):
            output = subprocess.run(
                [sys.executable, "-m", "benchmarks.simulation_benchmark", "--child", str(target)],
                capture_output=True,
                text=True,
                check=True,
            )
            rows.append({"repetition": repetition, **json.loads(output.stdout)})
    return {
        "metadata": metadata(
            __file__,
            {
                "scales": [1000, 100_000, 1_000_000],
                "repetitions": 3,
                "workload_version": "dd4-burst-v1",
                "detail": False,
                "warmup_events": 100,
            },
            17,
        ),
        "provenance": "MEASURED",
        "workload_origin": "synthetic",
        "raw_samples": rows,
        "summary": [
            {
                "target_events": target,
                "median_events_per_second": statistics.median(
                    r["events_per_second"] for r in rows if r["target_events"] == target
                ),
            }
            for target in (1000, 100_000, 1_000_000)
        ],
        "not_run": {
            "10000000": (
                "requires 1,666,667 sessions beyond declared 250,000 session bound; "
                "not needed for current experiments"
            )
        },
        "limitations": [
            "single FIFO template, not a representative production agent mix",
            "peak is whole process working-set/RSS high-water, not bytes per heap event",
            "three repeats on a shared workstation; no native speedup claim",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.child:
        print(json.dumps(sample(args.child)))
    else:
        if args.output is None:
            parser.error("--output is required")
        result = benchmark()
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
        print(json.dumps(result["summary"]))
