from dataclasses import replace
from pathlib import Path

import pytest
from conftest import make_span

from workload_lab import analyze, compile_workload, ingest
from workload_lab.analysis import interval_union
from workload_lab.ir import Dataset, NodeKind, Provenance, ValidationError

EXAMPLE = Path(__file__).parents[1] / "examples/research-workflow.otlp.json"


def test_hand_derived_fork_join_example():
    workflow = compile_workload(ingest(EXAMPLE))[0]
    report = analyze(workflow)
    assert report.origin == "synthetic"
    assert report.graph_complete
    assert report.critical_path_elapsed.value == 11_000_000_000
    assert report.total_elapsed_work.value == 14_000_000_000
    assert report.covered_wall_time.value == 11_000_000_000
    assert report.observed_envelope.value == 12_000_000_000
    assert report.unattributed_wall_time.value == 1_000_000_000
    assert report.critical_path_nodes == tuple(f"{n:016x}" for n in (2, 4, 5, 6))
    assert report.unknown_queue_nodes == report.unknown_service_nodes == 3
    assert report.known_queue_components.value == 1_000_000_000
    assert report.critical_path_elapsed.evidence.provenance == Provenance.ESTIMATED
    assert sum(c.chosen_path_elapsed.value for c in report.contributions) == 11_000_000_000
    assert report.gpu_utilization is None and report.capacity_recommendation is None


def test_nested_containers_not_double_counted():
    spans = (
        make_span(1, 0, 20, kind=NodeKind.WORKFLOW, graph_complete=True),
        make_span(2, 1, 19, parent=1),
        make_span(3, 2, 7, parent=2),
        make_span(4, 7, 10, parent=2, dependencies=(3,)),
    )
    report = analyze(compile_workload(Dataset("b" * 64, "observed", spans))[0])
    assert report.total_elapsed_work.value == 8
    assert report.critical_path_elapsed.value == 8
    assert report.unattributed_wall_time.value == 12
    assert report.known_queue_components.value is None
    assert report.unknown_service_nodes == 2


def test_no_dependency_is_inferred_from_timestamps_or_parent():
    spans = (
        make_span(1, 0, 9, kind=NodeKind.WORKFLOW),
        make_span(2, 0, 4, parent=1),
        make_span(3, 4, 9, parent=1),
    )
    report = analyze(compile_workload(Dataset("b" * 64, "observed", spans))[0])
    assert not report.graph_complete
    assert report.critical_path_elapsed.value == 5
    assert report.unattributed_wall_time.value == 0


def test_exact_epoch_nanoseconds_are_not_floats():
    base = 1_800_000_000_000_000_001
    report = analyze(
        compile_workload(Dataset("b" * 64, "observed", (make_span(1, base, base + 7),)))[0]
    )
    assert report.observed_envelope.value == 7


def test_ties_and_input_permutation():
    spans = (
        make_span(1, 0, 10, kind=NodeKind.WORKFLOW, graph_complete=True),
        make_span(2, 0, 5, parent=1),
        make_span(3, 0, 5, parent=1),
        make_span(4, 5, 10, parent=1, dependencies=(2, 3)),
    )
    first = compile_workload(Dataset("b" * 64, "synthetic", spans))[0]
    second = compile_workload(Dataset("b" * 64, "synthetic", tuple(reversed(spans))))[0]
    assert first == second
    assert analyze(first) == analyze(second)
    assert analyze(first).critical_path_nodes == (f"{2:016x}", f"{4:016x}")


def test_large_graph_is_iterative(serial_factory):
    report = analyze(serial_factory([1] * 5000))
    assert report.critical_path_elapsed.value == 5000


def test_zero_duration_suffix_is_included(serial_factory):
    report = analyze(serial_factory([5, 0, 0]))
    assert report.critical_path_nodes == tuple(f"{n:016x}" for n in (2, 3, 4))


def test_root_only_workflow_is_incomplete():
    workflow = compile_workload(
        Dataset(
            "b" * 64, "observed", (make_span(1, 0, 5, kind=NodeKind.WORKFLOW, graph_complete=True),)
        )
    )[0]
    assert not workflow.graph_complete
    assert "no_atomic_work" in workflow.diagnostics
    assert analyze(workflow).critical_path_elapsed.value is None


@pytest.mark.parametrize(
    "spans,match",
    [
        ((make_span(1, 0, 1, parent=2), make_span(2, 0, 1, parent=1)), "cycle"),
        ((make_span(1, 0, 1, dependencies=(2,)),), "endpoint"),
        ((make_span(1, 0, 0, dependencies=(2,)), make_span(2, 0, 0, dependencies=(1,))), "cycle"),
        ((make_span(1, 0, 5), make_span(2, 2, 7, dependencies=(1,))), "overlaps"),
        ((make_span(1, 0, 5, role="work"), make_span(2, 1, 3, parent=1)), "atomic work"),
        ((make_span(1, 0, 5), make_span(2, 4, 6, parent=1)), "outside parent"),
    ],
)
def test_invalid_graphs_fail(spans, match):
    with pytest.raises(ValidationError, match=match):
        compile_workload(Dataset("b" * 64, "observed", spans))


def test_orphan_is_preserved_as_incomplete():
    workflow = compile_workload(Dataset("b" * 64, "observed", (make_span(2, 0, 1, parent=1),)))[0]
    assert "missing_parent" in workflow.diagnostics
    assert not workflow.graph_complete


def test_workflow_direct_construction_validates_edges(serial_factory):
    workflow = serial_factory([1, 2])
    with pytest.raises(ValidationError, match="disagree"):
        replace(workflow, edges=())


def test_interval_union():
    assert interval_union([(0, 3), (1, 7), (7, 10), (12, 15), (14, 14)]) == 13
    assert interval_union([]) == 0
