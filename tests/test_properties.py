from conftest import make_serial, make_span
from hypothesis import given
from hypothesis import strategies as st

from workload_lab import analyze, compile_workload
from workload_lab.graph import topological_order
from workload_lab.ir import Dataset, Edge, NodeKind


@given(st.lists(st.integers(0, 10**6), min_size=1, max_size=100))
def test_serial_sum_property(durations):
    report = analyze(make_serial(durations))
    assert report.critical_path_elapsed.value == sum(durations)
    assert report.covered_wall_time.value == sum(durations)


@given(st.lists(st.integers(0, 1000), min_size=1, max_size=100))
def test_reducing_serial_work_never_increases_path(durations):
    reduced = [max(0, d - 1) for d in durations]
    assert (
        analyze(make_serial(reduced)).critical_path_elapsed.value
        <= analyze(make_serial(durations)).critical_path_elapsed.value
    )


@given(st.sets(st.tuples(st.integers(0, 20), st.integers(0, 20))))
def test_random_dag_order_obeys_all_dependencies(pairs):
    edges = tuple(Edge(str(a), str(b)) for a, b in pairs if a < b)
    ids = [str(n) for n in range(21)]
    order = topological_order(ids, edges)
    positions = {node: i for i, node in enumerate(order)}
    assert all(positions[e.predecessor] < positions[e.successor] for e in edges)
    assert order == topological_order(list(reversed(ids)), tuple(reversed(edges)))


@given(st.lists(st.integers(0, 1000), min_size=1, max_size=30))
def test_parallel_branches_equal_max(durations):
    spans = [make_span(1, 0, max(durations), kind=NodeKind.WORKFLOW, graph_complete=True)]
    spans += [make_span(i, 0, duration, parent=1) for i, duration in enumerate(durations, 2)]
    report = analyze(compile_workload(Dataset("b" * 64, "synthetic", tuple(spans)))[0])
    assert report.critical_path_elapsed.value == max(durations)
    assert report.total_elapsed_work.value == sum(durations)


@given(
    st.lists(st.integers(0, 50), min_size=5, max_size=5),
    st.sets(st.tuples(st.integers(2, 6), st.integers(2, 6))),
)
def test_longest_path_matches_exhaustive_path_enumeration(weights, pairs):
    pairs = {(a, b) for a, b in pairs if a < b}
    # Widely spaced timestamps satisfy all possible prerequisites; gaps are excluded.
    spans = [make_span(1, 0, 1000, kind=NodeKind.WORKFLOW, graph_complete=True)]
    spans += [
        make_span(
            i,
            i * 100,
            i * 100 + weights[i - 2],
            parent=1,
            dependencies=tuple(sorted(a for a, b in pairs if b == i)),
        )
        for i in range(2, 7)
    ]

    def enumerate_paths(path):
        yield sum(weights[i - 2] for i in path)
        for a, b in pairs:
            if a == path[-1]:
                yield from enumerate_paths([*path, b])

    expected = max(value for i in range(2, 7) for value in enumerate_paths([i]))
    workflow = compile_workload(Dataset("b" * 64, "synthetic", tuple(spans)))[0]
    assert analyze(workflow).critical_path_elapsed.value == expected
