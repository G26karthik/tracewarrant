import asyncio
import json
from dataclasses import asdict

import pytest
from conftest import make_span

from examples.capture_controlled import capture
from workload_lab import analyze, compile_workload, ingest
from workload_lab.ir import Observation, ValidationError


def test_direct_intervals_and_unknowns():
    obs = Observation(
        pool="p",
        capacity=1,
        enqueued_ns=1,
        acquired_ns=3,
        service_start_ns=4,
        service_end_ns=7,
        released_ns=9,
    )
    span = make_span(1, 0, 10, observation=obs)
    assert (span.queue_ns, span.service_ns) == (2, 6)
    assert make_span(1, 0, 10).queue_ns is None
    with pytest.raises(ValidationError, match="conflicts"):
        make_span(1, 0, 10, observation=obs, queue_ns=0)
    with pytest.raises(ValidationError, match="outside"):
        make_span(1, 2, 10, observation=obs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"capacity": 0},
        {"capacity": True},
        {"capacity": 1},
        {"attempt": 0},
        {"outcome": "invented"},
        {"pool": "x" * 129},
        {"enqueued_ns": 5, "acquired_ns": 4},
        {"external_wait_ns": -1},
    ],
)
def test_observation_bounds(kwargs):
    with pytest.raises(ValidationError):
        Observation(**kwargs)


def test_real_concurrent_capture(tmp_path):
    path = tmp_path / "actual.json"
    path.write_text(json.dumps(asyncio.run(capture(3, delay_scale=10))), encoding="utf-8")
    dataset = ingest(path)
    workflows = compile_workload(dataset)
    assert len(workflows) == 3 and all(w.graph_complete for w in workflows)
    assert all(w.edges for w in workflows)
    assert any(n.span.parent_id != w.nodes[0].id for w in workflows for n in w.nodes[1:])
    assert max(s.queue_ns or 0 for s in dataset.spans) > 1_000_000
    assert {s.observation.outcome for s in dataset.spans} >= {
        "completed",
        "failed",
        "timeout",
        "cancelled",
    }
    cancelled = next(s for s in dataset.spans if s.observation.outcome == "cancelled")
    assert cancelled.observation.released_ns > cancelled.observation.cancel_requested_ns
    assert any(s.observation.external_wait_ns and s.service_ns is None for s in dataset.spans)
    assert all(analyze(w).unknown_service_nodes > 0 for w in workflows)
    wire = json.dumps(asdict(dataset))
    assert "select sum" not in wire and "Local evidence" not in wire


def test_parser_explicit_nesting_bound(tmp_path):
    path = tmp_path / "deep.json"
    path.write_text('{"extra":' + "[" * 64 + "0" + "]" * 64 + "}")
    with pytest.raises(ValidationError, match="nesting limit"):
        ingest(path)


def test_pydantic_contract_fixture():
    from pathlib import Path

    path = Path(__file__).parents[1] / "examples/traces/pydantic-ai-2.51.0.otlp.json"
    dataset = ingest(path)
    workflows = compile_workload(dataset)
    assert len(workflows) == 1 and not workflows[0].graph_complete
    assert not workflows[0].edges
    assert all(s.queue_ns is None and s.service_ns is None for s in dataset.spans)
    assert "PRIVATE_" not in path.read_text()
