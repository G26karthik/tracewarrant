"""Validate and summarize content-free real-model probe traces."""

import argparse
import json
import statistics
import tempfile
from collections import defaultdict
from pathlib import Path

from benchmarks.provenance import sha
from workload_lab import compile_workload, ingest


def summarize(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    with tempfile.TemporaryDirectory(prefix="workload-lab-") as folder:
        trace_path = Path(folder) / "trace.json"
        for cell in data["cells"]:
            totals = defaultdict(lambda: {"queue_ns": 0, "occupied_ns": 0})
            complete = 0
            for session in cell["sessions"]:
                trace_path.write_text(json.dumps(session["trace"]), encoding="utf-8")
                graph = compile_workload(ingest(trace_path))[0]
                complete += graph.graph_complete
                for node in graph.nodes:
                    if pool := node.span.observation.pool:
                        totals[pool]["queue_ns"] += node.queue.value
                        totals[pool]["occupied_ns"] += node.service_time.value
            count = len(cell["sessions"])
            rows.append(
                {
                    "configuration": cell["configuration"],
                    "repetition": cell["repetition"],
                    "sessions": count,
                    "valid_complete_graphs": complete,
                    "fact_successes": cell["fact_successes"],
                    "errors": cell["errors"],
                    "median_latency_ns": cell["median_latency_ns"],
                    "mean_pool_ns_per_session": {
                        k: {metric: value / count for metric, value in v.items()}
                        for k, v in totals.items()
                    },
                }
            )
    grouped = {
        name: [r for r in rows if r["configuration"] == name]
        for name in ("BASELINE", "TOOL+", "CLIENT+")
    }
    means = {
        name: statistics.mean(
            r["mean_pool_ns_per_session"]["inference-client"]["occupied_ns"] for r in group
        )
        for name, group in grouped.items()
    }
    return {
        "schema_version": "1",
        "artifact_type": "real_model_probe_summary",
        "source_sha256": sha(path),
        "provenance": "MEASURED",
        "cells": rows,
        "total_sessions": sum(r["sessions"] for r in rows),
        "total_fact_successes": sum(r["fact_successes"] for r in rows),
        "client_occupancy_ratio_two_vs_one": means["CLIENT+"] / means["BASELINE"],
        "limitations": [
            "48 sessions, exploratory, no p95/p99 accuracy or significance claim",
            "client occupancy includes unknown backend queue/service components",
            "no frozen prediction for this workload; no full-thesis validation",
            "fact extraction checks do not validate reasoning quality",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.input)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "total_sessions",
                    "total_fact_successes",
                    "client_occupancy_ratio_two_vs_one",
                )
            }
        )
    )
