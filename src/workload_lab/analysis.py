"""Fixed-weight instance analysis; no utilization or capacity inference."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .graph import longest_path
from .ir import Quantity, Workflow, quantity


@dataclass(frozen=True)
class Contribution:
    kind: str
    service: str
    elapsed_work: Quantity
    chosen_path_elapsed: Quantity
    node_count: int


@dataclass(frozen=True)
class AnalysisReport:
    trace_id: str
    origin: str
    graph_complete: bool
    diagnostics: tuple[str, ...]
    source_sha256: str
    span_count: int
    work_node_count: int
    observed_envelope: Quantity
    total_elapsed_work: Quantity
    covered_wall_time: Quantity
    unattributed_wall_time: Quantity
    critical_path_elapsed: Quantity
    critical_path_nodes: tuple[str, ...]
    contributions: tuple[Contribution, ...]
    known_queue_components: Quantity
    unknown_queue_nodes: int
    unknown_service_nodes: int
    gpu_utilization: None = None
    capacity_recommendation: None = None


def interval_union(intervals: list[tuple[int, int]]) -> int:
    """Measure the union, not the sum, of overlapping half-open intervals."""
    if not intervals:
        return 0
    ordered = sorted(intervals)
    start, end = ordered[0]
    covered = 0
    for left, right in ordered[1:]:
        if left > end:
            covered += end - start
            start, end = left, right
        else:
            end = max(end, right)
    return covered + end - start


def analyze(workflow: Workflow) -> AnalysisReport:
    nodes = [n for n in workflow.nodes if n.role == "work"]
    source = (f"sha256:{workflow.source_sha256}#trace/{workflow.trace_id}",)

    def metric(value: int | None, method: str, assumptions: tuple[str, ...] = ()) -> Quantity:
        return quantity(value, workflow.origin, method, source, assumptions)

    first = min(n.span.start_ns for n in workflow.nodes)
    last = max(n.span.end_ns for n in workflow.nodes)
    covered = interval_union([(n.span.start_ns, n.span.end_ns) for n in nodes])
    critical, path = longest_path(workflow)
    selected = set(path)
    grouped = defaultdict(list)
    for node in nodes:
        grouped[(node.span.kind.value, node.span.service)].append(node)
    contributions = tuple(
        Contribution(
            kind,
            service,
            metric(sum(n.span.end_ns - n.span.start_ns for n in group), "sum_atomic_elapsed"),
            metric(
                sum(n.span.end_ns - n.span.start_ns for n in group if n.id in selected),
                "sum_chosen_path_elapsed",
            ),
            len(group),
        )
        for (kind, service), group in sorted(grouped.items())
    )
    known_queues = [n.queue.value for n in nodes if n.queue.value is not None]
    diagnostics = set(workflow.diagnostics)
    diagnostics.add("elapsed_weights_are_not_service_demand")
    if not nodes:
        diagnostics.add("no_atomic_work")
    if any(n.span.kind.value == "unknown" for n in nodes):
        diagnostics.add("unclassified_work")
    return AnalysisReport(
        trace_id=workflow.trace_id,
        origin=workflow.origin,
        graph_complete=workflow.graph_complete,
        diagnostics=tuple(sorted(diagnostics)),
        source_sha256=workflow.source_sha256,
        span_count=len(workflow.nodes),
        work_node_count=len(nodes),
        observed_envelope=metric(
            last - first,
            "observed_span_envelope",
            ("not necessarily a complete end-to-end execution",),
        ),
        total_elapsed_work=metric(
            sum(n.span.end_ns - n.span.start_ns for n in nodes),
            "sum_atomic_elapsed",
            ("overlapping work is additive",),
        ),
        covered_wall_time=metric(covered, "union_atomic_intervals"),
        unattributed_wall_time=metric(
            last - first - covered,
            "envelope_minus_union",
            ("unattributed time is not identified queue delay",),
        ),
        critical_path_elapsed=metric(
            critical if nodes else None,
            "longest_path_of_declared_dag",
            (
                "fixed observed elapsed weights; zero inter-node gaps; unlimited resource model",
                "incomplete edges invalidate a complete-workflow causal claim",
                "one deterministic tied path; attribution may not be unique",
                "not a prediction under changed load or resources",
            ),
        ),
        critical_path_nodes=path,
        contributions=contributions,
        known_queue_components=metric(
            sum(known_queues) if known_queues else None,
            "sum_reported_queue_components",
            ("partial known subtotal",),
        ),
        unknown_queue_nodes=len(nodes) - len(known_queues),
        unknown_service_nodes=sum(n.service_time.value is None for n in nodes),
    )
