"""Preregistered actual controlled traces. Calibration and holdout are separate commands."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import time
from pathlib import Path

from benchmarks.provenance import ROOT, metadata, sha
from examples.capture_controlled import capture

BASE = {"tool": 1, "stub-model": 2, "retrieval": 2, "database": 1}
CONFIGS = {
    "BASELINE": BASE,
    "TOOL+": {**BASE, "tool": 2},
    "MODEL+": {**BASE, "stub-model": 4},
    "RETRIEVAL+": {**BASE, "retrieval": 4},
}


async def collect(stage, frozen, checkpoint):
    setup = {
        "stage": stage,
        "workload_version": "controlled-v2",
        "delay_scale": 10,
        "sessions": 40 if stage == "calibration" else 60,
        "repetitions": 2,
    }
    meta = metadata(__file__, setup, 0)
    cells = []
    planned = (
        [(rate, "BASELINE", BASE) for rate in (2, 9)]
        if stage == "calibration"
        else [(row["rate"], row["configuration"], row["pools"]) for row in frozen["cells"]]
    )
    for repeat in range(2):
        # Reverse block order on repetition two to expose time/order drift.
        order = planned if repeat == 0 else list(reversed(planned))
        for rate, name, pools in order:
            start = time.perf_counter_ns()
            trace = await capture(
                setup["sessions"],
                pools["tool"],
                pools["stub-model"],
                False,
                pools["retrieval"],
                10,
                rate,
            )
            trace_sha = hashlib.sha256(json.dumps(trace, sort_keys=True).encode()).hexdigest()
            cells.append(
                {
                    "configuration": name,
                    "rate": rate,
                    "repetition": repeat,
                    "offered": setup["sessions"],
                    "pools": pools,
                    "trace": trace,
                    "trace_sha256": trace_sha,
                    "wall_seconds": (time.perf_counter_ns() - start) / 1e9,
                    "cohort": {
                        "application_sha256": sha(ROOT / "examples/capture_controlled.py"),
                        "hardware": meta["cpu"],
                        "python": meta["python"],
                        "pools": pools,
                        "rate": rate,
                        "workload_version": "controlled-v2",
                    },
                }
            )
            checkpoint.write_text(
                json.dumps(
                    {"metadata": meta, "cells": cells, "complete": False}, separators=(",", ":")
                ),
                encoding="utf-8",
                newline="\n",
            )
            print(f"Captured {stage}: {name}, {rate}/s, repetition {repeat}", flush=True)
    return {
        "schema_version": "1",
        "artifact_type": "controlled_measured_sessions",
        "provenance": "MEASURED",
        "workload": "stub inference, real local concurrency",
        "metadata": meta,
        "event_loop_clock_resolution_seconds": asyncio.get_running_loop()._clock_resolution,
        "perf_counter_resolution_seconds": time.get_clock_info("perf_counter").resolution,
        "cells": cells,
        "limitations": [
            "not a real inference or task-quality experiment",
            "timer and orchestration overhead included",
            "no steady-state saturation claim",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["calibration", "holdout"])
    parser.add_argument("--frozen", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    checkpoint = args.output.with_suffix(".partial.json")
    if checkpoint.exists():
        parser.error("partial capture already exists; preserve it and use a new output path")
    if args.stage == "holdout" and args.frozen is None:
        parser.error("holdout requires committed frozen predictions")
    frozen = json.loads(args.frozen.read_text()) if args.frozen else None
    result = asyncio.run(collect(args.stage, frozen, checkpoint))
    if args.frozen:
        result["frozen_prediction_sha256"] = sha(args.frozen)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, separators=(",", ":"))
    checkpoint.unlink(missing_ok=True)
