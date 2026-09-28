"""Iterative graph validation and deterministic longest path; no runtime IO."""

from __future__ import annotations

import heapq
from collections import defaultdict

from .ir import Dataset, Edge, Node, NodeKind, ValidationError, Workflow, identifier, quantity


def topological_order(ids: list[str], edges: tuple[Edge, ...]) -> tuple[str, ...]:
    if len(ids) != len(set(ids)):
        raise ValidationError("duplicate graph node")
    degree = dict.fromkeys(ids, 0)
    outgoing: dict[str, list[str]] = defaultdict(list)
    seen = set()
    for edge in edges:
        if edge.predecessor not in degree or edge.successor not in degree:
            raise ValidationError("dependency endpoint is missing or is not atomic work")
        pair = (edge.predecessor, edge.successor)
        if pair in seen:
            raise ValidationError("duplicate graph edge")
        seen.add(pair)
        degree[edge.successor] += 1
        outgoing[edge.predecessor].append(edge.successor)
    ready = [key for key, value in degree.items() if value == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        current = heapq.heappop(ready)
        result.append(current)
        for child in outgoing[current]:
            degree[child] -= 1
            if degree[child] == 0:
                heapq.heappush(ready, child)
    if len(result) != len(ids):
        raise ValidationError("graph contains a cycle")
    return tuple(result)


def validate_workflow(workflow: Workflow) -> None:
    identifier(workflow.trace_id, 32, "trace ID")
    Dataset(workflow.source_sha256, workflow.origin, tuple(n.span for n in workflow.nodes))
    if type(workflow.graph_complete) is not bool:
        raise ValidationError("workflow completeness must be boolean")
    by_id = {n.id: n for n in workflow.nodes}
    if len(by_id) != len(workflow.nodes):
        raise ValidationError("duplicate workflow node")
    containment = []
    for node in workflow.nodes:
        span = node.span
        if span.role is not None and span.role != node.role:
            raise ValidationError("node role disagrees with explicit span role")
        expected_source = (f"sha256:{workflow.source_sha256}#{span.trace_id}/{span.span_id}",)
        for timing in (node.elapsed, node.queue, node.service_time):
            if (
                timing.evidence.origin != workflow.origin
                or timing.evidence.sources != expected_source
            ):
                raise ValidationError("timing evidence disagrees with workflow source/origin")
        if span.trace_id != workflow.trace_id:
            raise ValidationError("cross-trace node in workflow")
        if span.parent_id in by_id:
            parent = by_id[span.parent_id]
            containment.append(Edge(parent.id, node.id))
            if parent.role == "work":
                raise ValidationError("atomic work cannot contain child spans")
            if not (parent.span.start_ns <= span.start_ns <= span.end_ns <= parent.span.end_ns):
                raise ValidationError("child interval outside parent; async/skew unsupported in v0")
    topological_order(list(by_id), tuple(containment))
    work = {key: node for key, node in by_id.items() if node.role == "work"}
    topological_order(list(work), workflow.edges)
    for edge in workflow.edges:
        if work[edge.predecessor].span.end_ns > work[edge.successor].span.start_ns:
            raise ValidationError("finish-to-start dependency overlaps; check clocks or semantics")
    declared = {(p, n.id) for n in workflow.nodes for p in n.span.depends_on}
    if declared != {(e.predecessor, e.successor) for e in workflow.edges}:
        raise ValidationError("workflow edges disagree with declared span dependencies")
    roots = [n for n in workflow.nodes if n.span.parent_id is None]
    if workflow.graph_complete and (
        len(roots) != 1
        or not roots[0].span.graph_complete
        or not work
        or workflow.diagnostics
        or any(n.span.diagnostics for n in workflow.nodes)
        or any(
            n.span.parent_id is not None and n.span.parent_id not in by_id for n in workflow.nodes
        )
    ):
        raise ValidationError(
            "complete graph lacks a valid root assertion or has incomplete evidence"
        )


def compile_workload(dataset: Dataset) -> tuple[Workflow, ...]:
    grouped = defaultdict(list)
    for span in dataset.spans:
        grouped[span.trace_id].append(span)
    workflows = []
    for trace_id, spans in sorted(grouped.items()):
        ids = {s.span_id for s in spans}
        parents = {s.parent_id for s in spans if s.parent_id in ids}
        roots = [s for s in spans if s.parent_id is None]
        diagnostics = {d for s in spans for d in s.diagnostics}
        if any(s.parent_id is not None and s.parent_id not in ids for s in spans):
            diagnostics.add("missing_parent")
        if len(roots) != 1:
            diagnostics.add("root_count_not_one")
        nodes, edges = [], []
        for span in sorted(spans, key=lambda s: s.span_id):
            role = span.role or (
                "container" if span.span_id in parents or span.kind == NodeKind.WORKFLOW else "work"
            )
            sources = (f"sha256:{dataset.source_sha256}#{trace_id}/{span.span_id}",)
            nodes.append(
                Node(
                    span,
                    role,
                    quantity(
                        span.end_ns - span.start_ns, dataset.origin, "timestamp_difference", sources
                    ),
                    quantity(
                        span.queue_ns,
                        dataset.origin,
                        "acquisition_minus_enqueue"
                        if span.observation.acquired_ns is not None
                        and span.observation.enqueued_ns is not None
                        else "reported_queue_component",
                        sources,
                    ),
                    quantity(
                        span.service_ns,
                        dataset.origin,
                        "release_minus_acquisition"
                        if span.observation.released_ns is not None
                        and span.observation.acquired_ns is not None
                        else "reported_service_component",
                        sources,
                    ),
                )
            )
            if role == "container" and span.depends_on:
                raise ValidationError("dependencies on container spans are unsupported")
            edges.extend(Edge(p, span.span_id) for p in span.depends_on)
        if not any(n.role == "work" for n in nodes):
            diagnostics.add("no_atomic_work")
        complete = len(roots) == 1 and roots[0].graph_complete and not diagnostics
        if not complete:
            diagnostics.add("dependency_graph_incomplete")
        workflows.append(
            Workflow(
                trace_id,
                tuple(nodes),
                tuple(sorted(edges, key=lambda e: (e.predecessor, e.successor))),
                complete,
                tuple(sorted(diagnostics)),
                dataset.source_sha256,
                dataset.origin,
            )
        )
    return tuple(workflows)


def longest_path(workflow: Workflow) -> tuple[int, tuple[str, ...]]:
    """O((V+E) log V) with deterministic ID tie-breaking and O(V+E) storage."""
    nodes = {n.id: n for n in workflow.nodes if n.role == "work"}
    order = topological_order(list(nodes), workflow.edges)
    incoming: dict[str, list[str]] = defaultdict(list)
    for edge in workflow.edges:
        incoming[edge.successor].append(edge.predecessor)
    distance: dict[str, int] = {}
    previous: dict[str, str | None] = {}
    for node_id in order:
        predecessor = min(incoming[node_id], key=lambda p: (-distance[p], p), default=None)
        previous[node_id] = predecessor
        weight = nodes[node_id].span.end_ns - nodes[node_id].span.start_ns
        distance[node_id] = weight + (distance[predecessor] if predecessor is not None else 0)
    non_sinks = {e.predecessor for e in workflow.edges}
    tail = min(
        (n for n in order if n not in non_sinks), key=lambda n: (-distance[n], n), default=None
    )
    total = distance[tail] if tail is not None else 0
    path = []
    while tail is not None:
        path.append(tail)
        tail = previous[tail]
    return total, tuple(reversed(path))
