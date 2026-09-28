"""Independent SimPy/heuristic producers and measurement conversion for V3."""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from benchmarks.provenance import metadata, sha
from examples.frames_workload import CONFIGURATIONS, DATASET_SHA
from workload_lab.artifacts import freeze_predictions, load_artifact, validate_artifact, write_new
from workload_lab.validation import evaluate

WORKLOAD = "frames-oracle-eight-v1"
SCENARIOS = list(CONFIGURATIONS)


def percentile(values, q):
    return sorted(values)[max(0, math.ceil(len(values) * q) - 1)]


def metric(identity, value, unit, statistic, count, provenance, population="completed"):
    return {
        "id": identity,
        "unit": unit,
        "statistic": statistic,
        "population": population,
        "value": value,
        "sample_count": count,
        "provenance": provenance if value is not None else "UNKNOWN",
        "interval": None,
    }


def cell_metrics(cell, provenance="MEASURED"):
    completed = [s for s in cell["sessions"] if s["error_type"] is None]
    latencies = [s["latency_ns"] for s in completed]
    window = cell["end_ns"] - cell["start_ns"]
    count = len(completed)
    metrics = [
        metric(
            "latency.mean",
            statistics.mean(latencies) if count else None,
            "ns",
            "mean",
            count,
            provenance,
        ),
        metric(
            "latency.p50",
            percentile(latencies, 0.5) if count else None,
            "ns",
            "p50",
            count,
            provenance,
        ),
        metric("latency.p95", None, "ns", "p95", count, "UNKNOWN"),
        metric("latency.p99", None, "ns", "p99", count, "UNKNOWN"),
        metric(
            "throughput.drain",
            count / (window / 1e9),
            "requests/s",
            "rate",
            len(cell["sessions"]),
            provenance,
            "offered_batch_window",
        ),
    ]
    capacities = dict(
        zip(("fetch", "inference-client"), CONFIGURATIONS[cell["configuration"]], strict=True)
    )
    for pool, capacity in capacities.items():
        stages = [t for s in cell["sessions"] for t in s["stages"] if t["pool"] == pool]
        metrics.extend(
            [
                metric(
                    pool + ".queue.mean",
                    sum(s["queue_ns"] for s in stages) / len(cell["sessions"]),
                    "ns",
                    "mean",
                    len(cell["sessions"]),
                    provenance,
                    "offered_observed_stages",
                ),
                metric(
                    pool + ".utilization",
                    sum(s["occupied_ns"] for s in stages) / (window * capacity),
                    "ratio",
                    "fraction",
                    len(cell["sessions"]),
                    provenance,
                    "offered_batch_window",
                ),
            ]
        )
    return metrics


def scenario(name, metrics, model_digest):
    fetch, clients = CONFIGURATIONS[name]
    return {
        "id": name,
        "comparison_group": "burst-8",
        "configuration": {"fetch_workers": fetch, "client_slots": clients},
        "environment": {
            "batch_sessions": 8,
            "model_digest": model_digest,
            "dataset_sha256": DATASET_SHA,
        },
        "metrics": metrics,
        "extrapolations": (["fetch_workers"] if fetch > 1 else [])
        + (["client_slots"] if clients > 1 else []),
        "bottleneck": {
            "resources": [],
            "provenance": "UNKNOWN",
            "method": "backend_not_identified",
        },
    }


def simulate_with_simpy(samples, configuration, seed):
    import simpy

    rng = random.Random(seed)
    env = simpy.Environment()
    fetch, clients = CONFIGURATIONS[configuration]
    resources = {
        name: simpy.Resource(env, capacity)
        for name, capacity in (
            ("fetch", fetch),
            ("inference-client", clients),
            ("retrieval", 1),
            ("database", 1),
        )
    }
    sessions = []

    def session(task_id, sample):
        stages = []
        by_stage = {s["stage"]: s for s in sample["stages"]}

        def work(name):
            saved = by_stage[name]
            resource = resources[saved["pool"]]
            enqueue = env.now
            with resource.request() as request:
                yield request
                acquire = env.now
                yield env.timeout(saved["occupied_ns"])
                stages.append(
                    {
                        "stage": name,
                        "pool": saved["pool"],
                        "queue_ns": acquire - enqueue,
                        "occupied_ns": env.now - acquire,
                        "outcome": "completed",
                    }
                )

        yield env.process(work("plan"))
        yield env.all_of(
            [env.process(work(name)) for name in sorted(by_stage) if name.startswith("fetch-")]
        )
        for name in ("retrieve", "database", "inference"):
            yield env.process(work(name))
        sessions.append(
            {"task_id": task_id, "latency_ns": env.now, "error_type": None, "stages": stages}
        )

    for task_id, candidates in samples.items():
        env.process(session(task_id, rng.choice(candidates)))
    env.run()
    return {"configuration": configuration, "start_ns": 0, "end_ns": env.now, "sessions": sessions}


def prediction_base(model_id, role, method, training, training_path):
    return {
        "schema_version": "1.0",
        "artifact_type": "prediction",
        "workload_id": WORKLOAD,
        "model": {"id": model_id, "version": "1", "role": role, "method": method},
        "lineage": [
            {"sha256": sha(training_path), "role": "calibration"},
            {"sha256": sha(__file__), "role": "producer_source"},
            {"sha256": DATASET_SHA, "role": "external_workload"},
        ],
        "calibration_envelope": {
            "fetch_workers": {"minimum": 1, "maximum": 1},
            "client_slots": {"minimum": 1, "maximum": 1},
            "batch_sessions": {"minimum": 8, "maximum": 8},
            "model_digest": {"values": [training["model_digest"]]},
            "dataset_sha256": {"values": [DATASET_SHA]},
        },
        "assumptions": ["same_task_mix", "stable_network", "owned_clocks_comparable"],
        "unsupported_dimensions": [
            "gpu_service_demand",
            "quality",
            "sustainable_capacity",
            "latency.p95",
            "latency.p99",
        ],
        "scenarios": [],
        "rankings": [],
    }


def forecast(training_path, output):
    if output.exists():
        raise ValueError("use a fresh forecast directory")
    training = json.loads(training_path.read_text())
    samples = defaultdict(list)
    for cell in training["cells"]:
        for session in cell["sessions"]:
            if session["error_type"]:
                raise ValueError("incomplete calibration cohort")
            samples[session["task_id"]].append(session)
    if len(samples) != 8 or any(len(s) != 2 for s in samples.values()):
        raise ValueError("unexpected calibration population")
    protocol = {
        "schema_version": "1.0",
        "artifact_type": "protocol",
        "workload_id": WORKLOAD,
        "experiment_id": "frames-pilot-v3-1",
        "scenario_ids": SCENARIOS,
        "primary_metric": "latency.mean",
        "direction": "minimize",
        "material_relative_difference": 0.1,
        "minimum_samples": 8,
        "require_baseline": True,
        "assumptions": [
            "preregistered_in_frames_preregistration",
            "quality_gate_in_separate_study_report",
        ],
        "unsupported_dimensions": ["p95", "p99", "sustainable_capacity", "gpu_service_demand"],
    }
    complex_model = prediction_base(
        "simpy-whole-workflow", "model", "paired_task_empirical_fifo", training, training_path
    )
    complex_model["assumptions"] += [
        "client_occupancy_invariant_under_concurrency",
        "seeds_2000_through_2029",
    ]
    complex_model["model"]["version"] = "simpy-4.1.1-producer-v1"
    raw_forecasts = {}
    for name in SCENARIOS:
        repeats = [
            cell_metrics(simulate_with_simpy(samples, name, seed), "SIMULATED")
            for seed in range(2000, 2030)
        ]
        raw_forecasts[name] = repeats
        metrics = copy.deepcopy(repeats[0])
        for index, m in enumerate(metrics):
            values = [r[index]["value"] for r in repeats if r[index]["value"] is not None]
            if values:
                m["value"] = statistics.median(values)
                m["sample_count"] = 240
                m["interval"] = {
                    "lower": percentile(values, 0.05),
                    "upper": percentile(values, 0.95),
                    "level": 0.9,
                    "kind": "range",
                    "method": "simulation_seed_quantiles",
                }
        complex_model["scenarios"].append(scenario(name, metrics, training["model_digest"]))
    baseline_metrics = [cell_metrics(c, "CALIBRATED") for c in training["cells"]]
    fixed = prediction_base(
        "fixed-delay", "baseline", "unchanged_baseline_point", training, training_path
    )
    unchanged = copy.deepcopy(baseline_metrics[0])
    for index, m in enumerate(unchanged):
        values = [r[index]["value"] for r in baseline_metrics if r[index]["value"] is not None]
        if values:
            m["value"] = statistics.mean(values)
            m["sample_count"] = 16
    fixed["scenarios"] = [
        scenario(name, copy.deepcopy(unchanged), training["model_digest"]) for name in SCENARIOS
    ]
    heuristic = prediction_base(
        "utilization-heuristic",
        "baseline",
        "highest_baseline_owned_utilization",
        training,
        training_path,
    )
    fractions = {
        pool: statistics.mean(
            next(m["value"] for m in row if m["id"] == pool + ".utilization")
            for row in baseline_metrics
        )
        for pool in ("fetch", "inference-client")
    }
    choices = [
        name
        for pool, name in (("fetch", "FETCH2"), ("inference-client", "CLIENT2"))
        if fractions[pool] == max(fractions.values())
    ]
    for name in SCENARIOS:
        metrics = copy.deepcopy(unchanged)
        for m in metrics:
            m.update(value=None, provenance="UNKNOWN", interval=None, sample_count=0)
        heuristic["scenarios"].append(scenario(name, metrics, training["model_digest"]))
    heuristic["rankings"] = [
        {
            "comparison_group": "burst-8",
            "metric_id": "latency.mean",
            "order": [choices, [n for n in SCENARIOS if n not in choices]],
            "provenance": "ESTIMATED",
        }
    ]
    run_metadata = metadata(__file__, {"seeds": list(range(2000, 2030))}, 2000)
    output.mkdir(parents=True)
    for name, artifact in (
        ("protocol", protocol),
        ("simpy", complex_model),
        ("fixed", fixed),
        ("utilization", heuristic),
    ):
        validate_artifact(artifact)
        write_new(output / f"{name}.json", artifact)
    predictions = [output / f"{n}.json" for n in ("simpy", "fixed", "utilization")]
    write_new(
        output / "forecast-evidence.json",
        {
            "metadata": run_metadata,
            "case_origin": "SIMULATED_from_external_measured_calibration",
            "replicates": raw_forecasts,
            "baseline_utilization": fractions,
        },
    )
    write_new(output / "freeze.json", freeze_predictions(output / "protocol.json", predictions))
    print(
        json.dumps(
            {
                "frozen": True,
                "heuristic_choices": choices,
                "simpy_mean_latency_seconds": {
                    s["id"]: s["metrics"][0]["value"] / 1e9 for s in complex_model["scenarios"]
                },
            }
        )
    )


def convert_and_evaluate(raw_path, frozen, output):
    if output.exists():
        raise ValueError("use a fresh evaluation directory")
    data = json.loads(raw_path.read_text())
    _, freeze_sha = load_artifact(frozen / "freeze.json", "freeze")
    if data["freeze_sha256"] != freeze_sha:
        raise ValueError("raw collection freeze mismatch")
    output.mkdir(parents=True)
    measurement_paths = []
    for repetition in range(2):
        cells = [c for c in data["cells"] if c["repetition"] == repetition]
        if {c["configuration"] for c in cells} != set(SCENARIOS):
            raise ValueError("missing intervention cell")
        sessions = [s for c in cells for s in c["sessions"]]
        complete = sum(s["error_type"] is None for s in sessions)
        measurement = {
            "schema_version": "1.0",
            "artifact_type": "measurement",
            "workload_id": WORKLOAD,
            "run_id": f"repetition-{repetition}",
            "lineage": [{"sha256": sha(raw_path), "role": "raw_observations"}],
            "freeze_sha256": freeze_sha,
            "started_at": data["started_at"],
            "finished_at": data["finished_at"],
            "scenarios": [
                scenario(c["configuration"], cell_metrics(c), data["model_digest"]) for c in cells
            ],
            "counts": {
                "offered": len(sessions),
                "completed": complete,
                "failed": len(sessions) - complete,
                "censored": 0,
            },
            "limitations": [
                "oracle_sources",
                "eight_sessions_per_cell",
                "quality_not_certified",
                "shared_workstation_and_network",
            ],
        }
        validate_artifact(measurement)
        path = output / f"measured-r{repetition}.json"
        write_new(path, measurement)
        measurement_paths.append(path)
    result = evaluate(
        frozen / "protocol.json",
        frozen / "freeze.json",
        [frozen / f"{n}.json" for n in ("simpy", "fixed", "utilization")],
        measurement_paths,
    )
    write_new(output / "validation.json", result)
    quality = [
        {
            "configuration": c["configuration"],
            "repetition": c["repetition"],
            "offered": len(c["sessions"]),
            "exact_matches": sum(s["exact_answer_match"] for s in c["sessions"]),
        }
        for c in data["cells"]
    ]
    write_new(
        output / "study-gates.json",
        {
            "quality": quality,
            "quality_gate_passed": all(c["exact_matches"] >= 6 for c in quality),
            "interpretation": (
                "Numerical decision comparisons are conditional; quality failure prohibits "
                "useful-agent capacity claims."
            ),
            "raw_sha256": sha(raw_path),
        },
    )
    print(
        json.dumps(
            {
                "quality_gate": all(c["exact_matches"] >= 6 for c in quality),
                "baseline_comparisons": result["baseline_comparisons"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("forecast", "evaluate"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--frozen", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.phase == "forecast":
        forecast(args.input, args.output)
    else:
        convert_and_evaluate(args.input, args.frozen, args.output)
