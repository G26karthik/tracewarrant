"""Analytical M/M/1 and independent SimPy validation; generated mathematical cases only."""

import argparse
import json
import statistics
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.simulation import Arrival, PoolSpec, RandomStream, Scenario, Task, simulate


def mm1(seed, sessions=20_000):
    mean_service = 1_000_000
    mean_interarrival = 1_666_667  # generated rho approximately 0.6
    arrivals, now = [], 0
    rng = RandomStream(seed, "arrivals")
    for i in range(sessions):
        now += rng.exponential_ns(mean_interarrival)
        arrivals.append(Arrival(f"{i:06d}", now))
    result = simulate(
        Scenario(
            (Task("service", pool="p", service_exponential_mean_ns=mean_service),),
            (PoolSpec("p", 1),),
            tuple(arrivals),
            now + 100_000_000,
            seed,
        )
    )
    # Remove first 10% warmup; use one common time window for residence and occupancy.
    start, end = arrivals[sessions // 10].at_ns, arrivals[-1].at_ns
    rows = [r for r in result["sessions"] if start <= r["arrival_ns"] < end]
    complete = [r for r in rows if r["end_ns"] <= end]
    w = statistics.mean(r["latency_ns"] for r in complete)
    area = sum(
        max(0, min(r["end_ns"], end) - max(r["arrival_ns"], start)) for r in result["sessions"]
    )
    busy = sum(
        max(0, min(r["release_ns"], end) - max(r["acquire_ns"], start)) for r in result["attempts"]
    )
    length = area / (end - start)
    rate = len(complete) / (end - start)
    expected = mean_service / (1 - mean_service / mean_interarrival)
    return {
        "seed": seed,
        "sessions": sessions,
        "warmup_sessions": sessions // 10,
        "window_start_ns": start,
        "window_end_ns": end,
        "complete_in_window": len(complete),
        "mean_latency_ns": w,
        "expected_mean_latency_ns": expected,
        "relative_error": abs(w / expected - 1),
        "utilization": busy / (end - start),
        "expected_utilization": mean_service / mean_interarrival,
        "mean_system_size": length,
        "arrival_rate_per_ns": rate,
        "lambda_times_W": rate * w,
        "little_law_relative_residual": abs(length - rate * w) / length,
        "outcomes": result["outcomes"],
    }


def simpy_crosscheck(seed):
    import simpy

    rng = RandomStream(seed, "crosscheck")
    at = 0
    arrivals = []
    for i in range(100):
        at += 1 + int(rng.uniform() * 7)
        arrivals.append(Arrival(f"{i:03d}", at))
    capacity = 1 + seed % 4
    task = Task("task", (1, 3, 7, 11), "p")
    result = simulate(Scenario((task,), (PoolSpec("p", capacity),), tuple(arrivals), 10000, seed))
    env, measured = simpy.Environment(), {}
    resource = simpy.Resource(env, capacity)

    def job(arrival):
        yield env.timeout(arrival.at_ns)
        duration = task.service_ns[
            int(RandomStream(seed, f"{arrival.id}/task/1/service").uniform() * 4)
        ]
        with resource.request() as request:
            yield request
            acquired = env.now
            yield env.timeout(duration)
            measured[arrival.id] = (acquired, env.now)

    for arrival in arrivals:
        env.process(job(arrival))
    env.run()
    actual = {a["session"]: (a["acquire_ns"], a["release_ns"]) for a in result["attempts"]}
    assert actual == measured
    return {"seed": seed, "capacity": capacity, "sessions": len(arrivals), "exact_match": True}


def validate():
    mm = [mm1(seed) for seed in range(5)]
    cross = [simpy_crosscheck(seed) for seed in range(20)]
    average_error = abs(
        statistics.mean(r["mean_latency_ns"] for r in mm) / mm[0]["expected_mean_latency_ns"] - 1
    )
    # Tolerances fixed in this harness before the measured gate run.
    assert average_error < 0.05
    assert all(r["relative_error"] < 0.1 and r["little_law_relative_residual"] < 0.01 for r in mm)
    assert all(abs(r["utilization"] - 0.6) < 0.03 for r in mm)
    return {
        "metadata": metadata(
            __file__, {"mm1_seeds": 5, "sessions_per_seed": 20_000, "simpy_cells": 20}, 0
        ),
        "case_origin": "synthetic mathematical validation",
        "measurement": "SIMULATED",
        "mm1": mm,
        "simpy": cross,
        "aggregate_relative_error": average_error,
        "acceptance": {"mean_error_max": 0.05, "seed_error_max": 0.1, "little_residual_max": 0.01},
        "passed": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate()
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
    print(
        json.dumps({"passed": True, "aggregate_relative_error": result["aggregate_relative_error"]})
    )
