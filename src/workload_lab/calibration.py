"""Narrow empirical calibration of complete, single-acquisition, fixed-DAG cohorts."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import defaultdict

from .ir import ValidationError
from .simulation import Arrival, PoolSpec, Scenario, Task, percentile


def fit_cohort(workflows, cohort, expected_sessions):
    """Refuse missing/censored/mixed topology instead of silently selecting fast successes.

    Caller supplies ALL offered sessions and an independently recorded cohort manifest.
    This cannot prove that an upstream exporter has not lost whole traces.
    """
    required = {"application_sha256", "hardware", "python", "pools", "rate", "workload_version"}
    if set(cohort) != required or len(workflows) != expected_sessions or expected_sessions < 20:
        raise ValidationError("cohort manifest or offered-session accounting is incomplete")
    vectors, shape, sources = defaultdict(list), None, []
    seen = set()
    for workflow in workflows:
        identity = (workflow.source_sha256, workflow.trace_id)
        if identity in seen:
            raise ValidationError("duplicate session in calibration")
        seen.add(identity)
        if workflow.origin != "observed" or not workflow.graph_complete:
            raise ValidationError("calibration requires complete observed sessions")
        nodes = sorted((n for n in workflow.nodes if n.role == "work"), key=lambda n: n.id)
        current = [(n.id, n.span.observation.pool, n.span.depends_on) for n in nodes]
        if shape is None:
            shape = current
        elif shape != current:
            raise ValidationError("mixed topologies require separate cohorts")
        for node in nodes:
            obs = node.span.observation
            if obs.outcome != "completed" or node.span.status == "ERROR":
                raise ValidationError("failure/censoring model unsupported; retain the cohort")
            if obs.pool is not None:
                if (
                    obs.capacity != cohort["pools"].get(obs.pool)
                    or obs.acquired_ns is None
                    or obs.released_ns is None
                    or node.queue.value is None
                    or node.service_time.value is None
                ):
                    raise ValidationError("pool identity/capacity/lifecycle is incomplete")
                values = (node.service_time.value, 0)
            else:
                if obs.external_wait_ns is None:
                    raise ValidationError("non-pool duration is unidentifiable")
                values = (0, obs.external_wait_ns)
            vectors[node.id].append(values)
        sources.append(f"sha256:{workflow.source_sha256}#{workflow.trace_id}")
    nodes = []
    for tid, pool, predecessors in shape:
        service, external = zip(*vectors[tid], strict=True)
        values = service if pool else external
        mean = statistics.mean(values)
        nodes.append(
            {
                "id": tid,
                "pool": pool,
                "predecessors": predecessors,
                "service_ns": service,
                "external_ns": external,
                "evidence": {
                    "provenance": "CALIBRATED",
                    "method": "empirical whole-session cohort",
                    "samples": len(values),
                    "mean_ns": mean,
                    "p50_ns": percentile(values, 0.5),
                    "p95_ns": percentile(values, 0.95),
                    "max_ns": max(values),
                    "coefficient_of_variation": statistics.pstdev(values) / mean if mean else None,
                },
            }
        )
    correlations = []
    for i, left in enumerate(nodes):
        for right in nodes[i + 1 :]:
            a = [sum(v) for v in vectors[left["id"]]]
            b = [sum(v) for v in vectors[right["id"]]]
            if statistics.pstdev(a) and statistics.pstdev(b):
                correlations.append(
                    {
                        "left": left["id"],
                        "right": right["id"],
                        "pearson": statistics.correlation(a, b),
                        "sessions": len(a),
                    }
                )
    return {
        "schema_version": "1",
        "artifact_type": "empirical_cohort_model",
        "cohort": cohort,
        "cohort_sha256": hashlib.sha256(json.dumps(cohort, sort_keys=True).encode()).hexdigest(),
        "nodes": nodes,
        "sessions": expected_sessions,
        "sources": sources,
        "within_session_correlations": correlations,
        "missing_or_censored": 0,
        "assumptions": [
            "all offered sessions supplied by harness",
            "fixed topology",
            "service invariance under declared slot intervention is unvalidated",
            "empirical distribution preserves observed tails; unseen tails unknown",
            "not a branch/retry/outage/quality or real inference model",
        ],
        "parametric_comparison": "Exponential CV=1; compare node CVs. No automatic parametric fit.",
        "uncertainty": "sampling, model discrepancy and scenario uncertainty remain distinct",
    }


def scenario_for(model, pools, rate, sessions, seed, *, fixed_tool=False):
    """Explicit experimental intervention, not a recommended deployment."""
    if not math.isfinite(rate) or rate <= 0 or not 1 <= sessions <= 1000:
        raise ValidationError("invalid experimental arrival schedule")
    tasks = []
    for node in model["nodes"]:
        pool = node["pool"]
        if fixed_tool and pool != "stub-model":
            pool = None
        tasks.append(
            Task(
                node["id"],
                tuple(node["service_ns"]),
                pool,
                tuple(node["predecessors"]),
                tuple(node["external_ns"]),
            )
        )
    return Scenario(
        tuple(tasks),
        tuple(PoolSpec(k, v) for k, v in sorted(pools.items())),
        tuple(Arrival(f"{i:04d}", round(i * 1e9 / rate)) for i in range(sessions)),
        round(sessions * 1e9 / rate) + 60_000_000_000,
        seed,
        "CALIBRATED",
        ("cohort-sha256:" + model["cohort_sha256"],),
    )
