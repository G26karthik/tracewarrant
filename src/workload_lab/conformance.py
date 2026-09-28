"""Observation contract inspection. No simulator or application execution."""

from collections import Counter, defaultdict

from .graph import compile_workload
from .ir import Dataset, NodeKind


def inspect_observations(dataset: Dataset) -> dict:
    """Return content-free coverage; completeness is a collector assertion, not proof."""
    workflows = compile_workload(dataset)
    spans = [n.span for w in workflows for n in w.nodes if n.role == "work"]
    claims = {}

    def claim(name, items, fields, category="identifiable_with_instrumentation", note=None):
        missing = Counter()
        observed = 0
        for span in items:
            absent = [f for f in fields if getattr(span.observation, f) is None]
            missing.update(absent)
            observed += not absent
        claims[name] = {
            "support": (
                "supported"
                if items and observed == len(items)
                else "partial"
                if observed
                else "unsupported"
            ),
            "classification": category if observed else "unsupported",
            "observed": observed,
            "eligible": len(items),
            "missing_fields": dict(sorted(missing.items())),
            "required_extensions": [f"workload_lab.{f}" for f in fields],
            "note": note,
        }

    complete = sum(w.graph_complete for w in workflows)
    claims["dependency_graph"] = {
        "support": "supported"
        if complete == len(workflows)
        else "partial"
        if complete
        else "unsupported",
        "classification": "identifiable_with_instrumentation" if complete else "unsupported",
        "observed": complete,
        "eligible": len(workflows),
        "required_extensions": [
            "workload_lab.depends_on",
            "workload_lab.graph.complete",
            "workload_lab.node.role",
        ],
        "note": (
            "Explicit finish-to-start edges and collector completeness assertions; "
            "parentage is containment. Missing entire traces cannot be detected."
        ),
    }
    fan_in = fan_out = 0
    for workflow in workflows:
        incoming = Counter(e.successor for e in workflow.edges)
        outgoing = Counter(e.predecessor for e in workflow.edges)
        fan_in += sum(v > 1 for v in incoming.values())
        fan_out += sum(v > 1 for v in outgoing.values())
    claims["fan_out_fan_in"] = {
        "support": claims["dependency_graph"]["support"],
        "classification": claims["dependency_graph"]["classification"],
        "explicit_fan_out_nodes": fan_out,
        "explicit_fan_in_nodes": fan_in,
        "note": ("Counts describe declared edges; concurrent spans establish no synchronization."),
    }
    claim("queue_wait", spans, ("enqueued_ns", "acquired_ns"))
    claim("resource_occupancy", spans, ("pool", "acquired_ns", "released_ns"))
    claim(
        "service_interval",
        spans,
        ("service_start_ns", "service_end_ns"),
        note="Observed interval only; nested waits or shared hardware may remain.",
    )
    claim(
        "finite_pool_capacity",
        spans,
        ("pool", "capacity"),
        "directly_observable",
        note="Collector-reported owned capacity; not physical device capacity.",
    )
    claim(
        "retry_attempts",
        spans,
        ("attempt_group", "attempt"),
        note="Explicit attempts only; sampling can hide retries and terminal outcomes.",
    )
    cancelled = [
        s
        for s in spans
        if s.observation.outcome == "cancelled" or s.observation.cancel_requested_ns is not None
    ]
    claim(
        "cancellation_release",
        cancelled,
        ("cancel_requested_ns", "released_ns"),
        note="Owned release is not proof of cancellation at a remote inference backend.",
    )
    claim(
        "external_wait",
        spans,
        ("external_wait_ns",),
        "directly_observable",
        note="Explicit duration; overlap and placement need an application contract.",
    )
    llm = [s for s in spans if s.kind == NodeKind.LLM]
    claim(
        "inference_client_occupancy",
        llm,
        ("pool", "acquired_ns", "released_ns"),
        note="Client occupancy includes unknown backend queue and service.",
    )
    claims["inference_service_demand"] = {
        "support": "unsupported",
        "classification": "not_identifiable",
        "provenance": "UNKNOWN",
        "value": None,
        "required_extensions": [
            "backend_queue_boundary",
            "backend_execution_boundary",
            "shared_device_schedule",
        ],
        "note": "Client timestamps and token counts cannot identify invariant GPU service demand.",
    }
    timeouts = sum(s.observation.outcome == "timeout" for s in spans)
    claims["timeout_semantics"] = {
        "support": "partial" if timeouts else "unsupported",
        "classification": "directly_observable" if timeouts else "unsupported",
        "reported_timeouts": timeouts,
        "required_extensions": [
            "deadline_ns",
            "terminal_outcome",
            "backend_release_acknowledgement",
        ],
        "note": (
            "Outcome labels are observable; IR 0.2 lacks deadlines "
            "and remote release acknowledgements."
        ),
    }
    violations = []
    pools = defaultdict(list)
    attempts = defaultdict(list)
    for span in spans:
        obs = span.observation
        if obs.pool is not None:
            pools[obs.pool].append(span)
        if obs.attempt_group is not None and obs.attempt is not None:
            attempts[span.trace_id, obs.attempt_group].append(obs.attempt)
    for group in attempts.values():
        if sorted(group) != list(range(1, len(group) + 1)):
            violations.append("attempt_sequence_incomplete_or_duplicate")
    for group in pools.values():
        capacities = {s.observation.capacity for s in group if s.observation.capacity is not None}
        if len(capacities) > 1:
            violations.append("pool_capacity_changes_without_epoch")
            continue
        events = []
        for span in group:
            o = span.observation
            if (
                o.acquired_ns is not None
                and o.released_ns is not None
                and o.acquired_ns < o.released_ns
            ):
                events.extend(((o.acquired_ns, 1), (o.released_ns, -1)))
        active = 0
        if capacities:
            for _, delta in sorted(events):
                active += delta
                if active > next(iter(capacities)):
                    violations.append("observed_occupancy_exceeds_declared_capacity")
                    break
    if any(v.startswith(("pool_", "observed_occupancy")) for v in violations):
        claims["finite_pool_capacity"]["support"] = "unsupported"
        claims["finite_pool_capacity"]["classification"] = "unsupported"
    if "attempt_sequence_incomplete_or_duplicate" in violations:
        claims["retry_attempts"]["support"] = "partial"
    candidate = (
        dataset.origin == "observed"
        and not violations
        and all(
            claims[c]["support"] == "supported"
            for c in (
                "dependency_graph",
                "queue_wait",
                "resource_occupancy",
                "finite_pool_capacity",
            )
        )
    )
    claims["prediction_suitability"] = {
        "support": "unsupported",
        "classification": "calibratable_under_assumptions" if candidate else "unsupported",
        "provenance": "UNKNOWN",
        "note": (
            "Inspection does not validate predictions. Require offered/completed counts, clocks, "
            "sampling, stable cohorts, identifiability and held-out intervention evidence."
        ),
    }
    return {
        "schema_version": "1.0",
        "artifact_type": "observation_conformance",
        "contract_version": "1.0",
        "source_sha256": dataset.source_sha256,
        "origin": dataset.origin,
        "trace_count": len(workflows),
        "atomic_spans": len(spans),
        "claims": claims,
        "violations": dict(sorted(Counter(violations).items())),
        "privacy": "No application labels, span names, payloads or raw attribute values emitted.",
    }
