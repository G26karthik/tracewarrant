"""Fit only calibration cells and freeze all primary/baseline predictions before holdout."""

from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from dataclasses import replace
from pathlib import Path

from benchmarks.controlled_experiment import CONFIGS
from benchmarks.provenance import metadata, sha
from workload_lab import compile_workload, ingest
from workload_lab.calibration import fit_cohort, scenario_for
from workload_lab.simulation import simulate


def workflows_for(cell):
    with tempfile.TemporaryDirectory(prefix="workload-lab-") as directory:
        path = Path(directory) / "trace.json"
        path.write_text(json.dumps(cell["trace"], sort_keys=True), encoding="utf-8", newline="\n")
        if sha(path) != cell["trace_sha256"]:
            raise ValueError("captured trace digest mismatch")
        return compile_workload(ingest(path))


def freeze(training_path):
    training = json.loads(training_path.read_text(encoding="utf-8"))
    if training["metadata"]["configuration"]["stage"] != "calibration":
        raise ValueError("cannot train on held-out data")
    models = []
    for rate in (2, 9):
        selected = [cell for cell in training["cells"] if cell["rate"] == rate]
        if len(selected) != 2 or any(cell["cohort"] != selected[0]["cohort"] for cell in selected):
            raise ValueError("mixed or missing calibration cohorts")
        models.append(
            fit_cohort(
                [w for cell in selected for w in workflows_for(cell)],
                selected[0]["cohort"],
                sum(c["offered"] for c in selected),
            )
        )
    cells = []
    start = time.perf_counter()
    for rate in (6, 8):
        model = min(models, key=lambda m: abs(m["cohort"]["rate"] - rate))
        for name, pools in CONFIGS.items():
            forecasts = {}
            for variant in ("independent", "paired", "fixed_tool_delay"):
                samples = []
                for seed in range(1000, 1030):
                    spec = scenario_for(
                        model, pools, rate, 60, seed, fixed_tool=variant == "fixed_tool_delay"
                    )
                    if variant == "paired":
                        spec = replace(spec, sample_coupling="session")
                    result = simulate(spec)
                    end = max(r["end_ns"] for r in result["sessions"])
                    samples.append(
                        {
                            "seed": seed,
                            **result["completed_latency_ns"],
                            "throughput_per_second": result["outcomes"]["completed"] * 1e9 / end,
                            "outcomes": result["outcomes"],
                            "pool_queue_ns_per_session": {
                                k: v["queue_ns"] / 60 for k, v in result["pools"].items()
                            },
                            "pool_utilization": {
                                k: v["busy_ns"] / (end * v["capacity"])
                                for k, v in result["pools"].items()
                            },
                        }
                    )
                forecasts[variant] = {
                    "samples": samples,
                    "p95_ns": statistics.median(r["p95"] for r in samples),
                    "p50_ns": statistics.median(r["p50"] for r in samples),
                    "p99_ns": statistics.median(r["p99"] for r in samples),
                    "seed_p95_range_ns": [
                        min(r["p95"] for r in samples),
                        max(r["p95"] for r in samples),
                    ],
                }
            cells.append(
                {
                    "rate": rate,
                    "configuration": name,
                    "pools": pools,
                    "training_rate": model["cohort"]["rate"],
                    "forecasts": forecasts,
                }
            )
    demands = {}
    for node in models[-1]["nodes"]:
        if node["pool"]:
            demands[node["pool"]] = demands.get(node["pool"], 0) + node["evidence"]["mean_ns"]
    pressure = {k: v / models[-1]["cohort"]["pools"][k] for k, v in demands.items()}
    return {
        "schema_version": "1",
        "artifact_type": "frozen_controlled_predictions",
        "metadata": metadata(
            __file__, {"rates": [6, 8], "sessions": 60, "seeds": [1000, 1029]}, 1000
        ),
        "training_sha256": sha(training_path),
        "models": models,
        "cells": cells,
        "simulation_wall_seconds": time.perf_counter() - start,
        "baselines": {
            "inference_only_choice": "MODEL+",
            "naive_total_slots_choice": ["MODEL+", "RETRIEVAL+"],
            "utilization_heuristic_pool": max(pressure, key=pressure.get),
            "offered_demand_per_slot_ns": pressure,
        },
        "uncertainty": "seed range is scenario variability; not a 95% prediction interval",
        "envelope": {
            "loads": [2, 9],
            "configurations": CONFIGS,
            "workload": "controlled-v2 only",
            "hardware": models[0]["cohort"]["hardware"],
        },
        "qualification": "unvalidated interventions; no optimizer or infrastructure recommendation",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.training)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
    print(
        json.dumps(
            {
                "cells": len(result["cells"]),
                "seconds": result["simulation_wall_seconds"],
                "heuristic": result["baselines"]["utilization_heuristic_pool"],
            }
        )
    )
