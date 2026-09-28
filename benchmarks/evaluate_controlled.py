"""Score frozen predictions against every measured holdout cell, including failures."""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
from collections import defaultdict
from pathlib import Path

from benchmarks.predict_controlled import workflows_for
from benchmarks.provenance import metadata, sha
from workload_lab.simulation import RandomStream, percentile


def measured(cell):
    workflows = workflows_for(cell)
    if len(workflows) != cell["offered"] or any(not w.graph_complete for w in workflows):
        raise ValueError("incomplete holdout; cannot score by silently dropping sessions")
    latencies = []
    busy, queue = defaultdict(int), defaultdict(int)
    first = min(n.span.start_ns for w in workflows for n in w.nodes)
    last = max(n.span.end_ns for w in workflows for n in w.nodes)
    failures = 0
    for workflow in workflows:
        latencies.append(
            max(n.span.end_ns for n in workflow.nodes)
            - min(n.span.start_ns for n in workflow.nodes)
        )
        failed = False
        for node in workflow.nodes:
            obs = node.span.observation
            if node.role == "work" and obs.outcome != "completed":
                failed = True
            if obs.pool:
                if node.service_time.value is None or node.queue.value is None:
                    raise ValueError("missing measured resource components")
                busy[obs.pool] += node.service_time.value
                queue[obs.pool] += node.queue.value
        failures += failed
    return {
        "offered": len(workflows),
        "failures": failures,
        "latencies_ns": latencies,
        "p50_ns": percentile(latencies, 0.5),
        "p95_ns": percentile(latencies, 0.95),
        "p99_ns": percentile(latencies, 0.99),
        "window_ns": last - first,
        "throughput_per_second": (len(workflows) - failures) * 1e9 / (last - first),
        "queue_ns_per_session": {k: v / len(workflows) for k, v in queue.items()},
        "utilization": {k: v / (cell["pools"][k] * (last - first)) for k, v in busy.items()},
    }


def bootstrap_p95(values, name):
    rng = RandomStream(440, "observed-bootstrap/" + name)
    estimates = [
        percentile([values[int(rng.uniform() * len(values))] for _ in values], 0.95)
        for _ in range(500)
    ]
    return {
        "method": "percentile bootstrap of whole sessions, 500 resamples",
        "nominal_level": 0.95,
        "lower_ns": percentile(estimates, 0.025),
        "upper_ns": percentile(estimates, 0.975),
        "limitation": "temporal correlation/model discrepancy not covered; only two real batches",
    }


def evaluate(frozen_path, holdout_path):
    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    holdout = json.loads(holdout_path.read_text(encoding="utf-8"))
    if holdout["frozen_prediction_sha256"] != sha(frozen_path):
        raise ValueError("holdout is not linked to these frozen predictions")
    rows = []
    for prediction in frozen["cells"]:
        selected = [
            c
            for c in holdout["cells"]
            if c["rate"] == prediction["rate"] and c["configuration"] == prediction["configuration"]
        ]
        if len(selected) != 2 or any(c["pools"] != prediction["pools"] for c in selected):
            raise ValueError("missing/changed holdout cell")
        if any(
            c["cohort"]["application_sha256"] != frozen["models"][0]["cohort"]["application_sha256"]
            or c["cohort"]["hardware"] != frozen["models"][0]["cohort"]["hardware"]
            for c in selected
        ):
            raise ValueError("application or hardware changed outside cohort")
        repeats = [measured(c) for c in selected]
        latencies = [v for r in repeats for v in r["latencies_ns"]]
        actual = percentile(latencies, 0.95)
        forecasts = prediction["forecasts"]
        rows.append(
            {
                "rate": prediction["rate"],
                "configuration": prediction["configuration"],
                "observed": {
                    "sessions": len(latencies),
                    "failures": sum(r["failures"] for r in repeats),
                    "p50_ns": percentile(latencies, 0.5),
                    "p95_ns": actual,
                    "p99_ns": percentile(latencies, 0.99),
                    "p99_status": "underpowered",
                    "bootstrap_p95": bootstrap_p95(
                        latencies, str(prediction["rate"]) + prediction["configuration"]
                    ),
                    "repetitions": repeats,
                },
                "predictions": {
                    variant: {
                        "p95_ns": f["p95_ns"],
                        "signed_error_ns": f["p95_ns"] - actual,
                        "relative_error": abs(f["p95_ns"] - actual) / actual,
                    }
                    for variant, f in forecasts.items()
                },
            }
        )
    ranking = []
    bottlenecks = []
    heuristic = []
    for rate in (6, 8):
        by_name = {r["configuration"]: r for r in rows if r["rate"] == rate}
        for a, b in itertools.combinations(("TOOL+", "MODEL+", "RETRIEVAL+"), 2):
            left, right = by_name[a], by_name[b]
            actual = left["observed"]["p95_ns"] - right["observed"]["p95_ns"]
            replicate_deltas = [
                x["p95_ns"] - y["p95_ns"]
                for x, y in zip(
                    left["observed"]["repetitions"], right["observed"]["repetitions"], strict=True
                )
            ]
            material = abs(actual) / max(
                left["observed"]["p95_ns"], right["observed"]["p95_ns"]
            ) >= 0.1 and all(d * actual > 0 for d in replicate_deltas)
            prediction = (
                left["predictions"]["independent"]["p95_ns"]
                - right["predictions"]["independent"]["p95_ns"]
            )
            ranking.append(
                {
                    "rate": rate,
                    "left": a,
                    "right": b,
                    "material": material,
                    "correct": prediction * actual > 0 if material else None,
                    "observed_delta_ns": actual,
                    "predicted_delta_ns": prediction,
                }
            )
        baseline = by_name["BASELINE"]
        queues = {
            k: statistics.mean(
                r["queue_ns_per_session"][k] for r in baseline["observed"]["repetitions"]
            )
            for k in baseline["observed"]["repetitions"][0]["queue_ns_per_session"]
        }
        ordered = sorted(queues, key=queues.get, reverse=True)
        clear = queues[ordered[0]] >= 5_000_000 and queues[ordered[0]] >= 2 * queues[ordered[1]]
        forecast = next(
            c for c in frozen["cells"] if c["rate"] == rate and c["configuration"] == "BASELINE"
        )
        predicted_queues = {
            k: statistics.mean(
                s["pool_queue_ns_per_session"][k]
                for s in forecast["forecasts"]["independent"]["samples"]
            )
            for k in queues
        }
        chosen = max(predicted_queues, key=predicted_queues.get)
        bottlenecks.append(
            {
                "rate": rate,
                "clear": clear,
                "observed": ordered[0],
                "predicted": chosen,
                "correct": ordered[0] == chosen if clear else None,
                "observed_queue_ns_per_session": queues,
            }
        )
        best = min(
            ("TOOL+", "MODEL+", "RETRIEVAL+"), key=lambda k: by_name[k]["observed"]["p95_ns"]
        )
        mapping = {"tool": "TOOL+", "stub-model": "MODEL+", "retrieval": "RETRIEVAL+"}
        heuristic.append(
            {
                "rate": rate,
                "observed_best": best,
                "heuristic_choice": mapping.get(frozen["baselines"]["utilization_heuristic_pool"]),
                "clear_bottleneck": clear,
            }
        )
    eligible = [r for r in ranking if r["material"]]
    error = statistics.median(r["predictions"]["independent"]["relative_error"] for r in rows)
    fraction = sum(r["correct"] for r in eligible) / len(eligible) if eligible else None
    return {
        "schema_version": "1",
        "artifact_type": "heldout_prediction_evaluation",
        "metadata": metadata(__file__, {"cells": 8, "repetitions": 2}, 440),
        "frozen_sha256": sha(frozen_path),
        "holdout_sha256": sha(holdout_path),
        "cells": rows,
        "ranking": ranking,
        "bottlenecks": bottlenecks,
        "heuristic_comparison": heuristic,
        "criteria": {
            "median_p95_relative_error": error,
            "p95_pass": error <= 0.15,
            "material_pairs": len(eligible),
            "ranking_fraction": fraction,
            "ranking_pass": fraction is not None and fraction >= 0.8,
            "saturation": "NOT IDENTIFIED: finite draining batches",
            "full_thesis": "NOT TESTED: stub inference; heuristic comparison remains necessary",
        },
        "baselines": frozen["baselines"],
        "cost": {
            "actual_collection_seconds": sum(c["wall_seconds"] for c in holdout["cells"]),
            "frozen_simulation_seconds": frozen["simulation_wall_seconds"],
            "engineering_effort": "not measured; do not claim economic break-even",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--holdout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.frozen, args.holdout)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result["criteria"]))
