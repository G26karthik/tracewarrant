import pytest
from hypothesis import settings

from workload_lab.graph import compile_workload
from workload_lab.ir import Dataset, NodeKind, Span

settings.register_profile("deterministic", max_examples=100, derandomize=True, deadline=None)
settings.load_profile("deterministic")

TRACE = "a" * 32


def make_span(number, start, end, parent=None, dependencies=(), **kwargs):
    return Span(
        TRACE,
        f"{number:016x}",
        f"{parent:016x}" if parent else None,
        start,
        end,
        depends_on=tuple(f"{n:016x}" for n in dependencies),
        **kwargs,
    )


def make_serial(durations):
    total = sum(durations)
    spans = [make_span(1, 0, total, kind=NodeKind.WORKFLOW, graph_complete=True)]
    now = 0
    for i, duration in enumerate(durations, start=2):
        spans.append(
            make_span(i, now, now + duration, parent=1, dependencies=(i - 1,) if i > 2 else ())
        )
        now += duration
    return compile_workload(Dataset("b" * 64, "synthetic", tuple(spans)))[0]


@pytest.fixture
def serial_factory():
    return make_serial
