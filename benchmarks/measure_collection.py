"""Paired fresh-process SQLite collection overhead; no agent/model performance claim."""

import argparse
import asyncio
import ctypes
import json
import os
import sqlite3
import statistics
import subprocess
import sys
import time

from benchmarks.provenance import metadata
from workload_lab.artifacts import canonical_bytes, write_new
from workload_lab.collection import ObservationRecorder
from workload_lab.ir import NodeKind


def peak_memory_bytes():
    if os.name != "nt":
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return value if sys.platform == "darwin" else value * 1024
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("faults", wintypes.DWORD),
            *[
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
            ],
        ]

    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    if not psapi.GetProcessMemoryInfo(
        kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    ):
        raise OSError("process memory measurement failed")
    return counters.peak_working


async def worker(mode, operations, rows):
    semaphore = asyncio.Semaphore(1)
    recorder = ObservationRecorder(max_spans=operations + 1)
    pool = recorder.pool(1)
    database = sqlite3.connect(":memory:")
    try:
        database.execute("create table reference(value integer)")
        database.executemany("insert into reference values (?)", ((i % 97,) for i in range(rows)))
        expected = sum(i % 97 for i in range(rows))

        def query():
            assert database.execute("select sum(value) from reference").fetchone()[0] == expected

        for _ in range(20):
            query()
        start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
        if mode == "recorded":
            with recorder.run() as run:
                for _ in range(operations):
                    with run.operation(NodeKind.DATABASE) as operation:
                        async with operation.lease(pool, semaphore.acquire, semaphore.release):
                            query()
        else:
            for _ in range(operations):
                await semaphore.acquire()
                try:
                    query()
                finally:
                    semaphore.release()
        elapsed, cpu = time.perf_counter_ns() - start, time.process_time_ns() - cpu_start
        assert semaphore._value == 1
        export_start = time.perf_counter_ns()
        size = len(canonical_bytes(recorder.envelope())) if mode == "recorded" else 0
        export_time = time.perf_counter_ns() - export_start
        return {
            "mode": mode,
            "elapsed_ns": elapsed,
            "cpu_ns": cpu,
            "operations": operations,
            "serialization_ns": export_time,
            "json_bytes": size,
            "peak_process_bytes": peak_memory_bytes(),
        }
    finally:
        database.close()


def measure(operations, rows, repetitions):
    samples = []
    for repetition in range(repetitions):
        # Alternate order to expose drift; each mode runs in a fresh process.
        modes = ("plain", "recorded") if repetition % 2 == 0 else ("recorded", "plain")
        pair = {}
        for mode in modes:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "benchmarks.measure_collection",
                    "--worker",
                    mode,
                    "--operations",
                    str(operations),
                    "--rows",
                    str(rows),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            pair[mode] = json.loads(result.stdout)
        samples.append({"repetition": repetition, **pair})
    differences = [
        (row["recorded"]["elapsed_ns"] - row["plain"]["elapsed_ns"]) / operations for row in samples
    ]
    fractions = [row["recorded"]["elapsed_ns"] / row["plain"]["elapsed_ns"] - 1 for row in samples]
    peak = max(row[mode]["peak_process_bytes"] for row in samples for mode in ("plain", "recorded"))
    assert peak < 2 * 1024**3
    return {
        "artifact_type": "collection_overhead_measurement",
        "metadata": metadata(
            __file__,
            {
                "operations": operations,
                "rows": rows,
                "repetitions": repetitions,
                "network": False,
                "model_execution": False,
            },
            0,
        ),
        "samples": samples,
        "median_added_ns_per_operation": statistics.median(differences),
        "median_loop_elapsed_overhead_fraction": statistics.median(fractions),
        "peak_process_bytes": peak,
        "provisional_2gib_process_ceiling_met": True,
        "limits": [
            "local_sqlite_microbenchmark_not_agent_capacity",
            "capture_loop_excludes_final_serialization",
            "serialization_reported_separately",
            "peak_includes_interpreter_and_database",
            "no_speedup_or_general_overhead_claim",
            "not_tested_on_a_16gib_machine",
        ],
    }


def main():
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("plain", "recorded"))
    parser.add_argument("--operations", type=int, default=500)
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (
        not 1 <= args.operations <= 5000
        or not 1 <= args.rows <= 100000
        or not 1 <= args.repetitions <= 20
    ):
        parser.error("measurement exceeds its fixed budget")
    if args.worker:
        print(json.dumps(asyncio.run(worker(args.worker, args.operations, args.rows))))
    else:
        if args.output is None:
            parser.error("--output is required")
        result = measure(args.operations, args.rows, args.repetitions)
        write_new(args.output, result)
        print(
            json.dumps(
                {
                    "added_ns_per_operation": result["median_added_ns_per_operation"],
                    "overhead_fraction": result["median_loop_elapsed_overhead_fraction"],
                    "peak_process_bytes": result["peak_process_bytes"],
                }
            )
        )


if __name__ == "__main__":
    main()
