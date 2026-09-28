from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from workload_lab.ir import ValidationError
from workload_lab.simulation import Arrival, PoolSpec, RandomStream, Scenario, Task, simulate

DEFAULT_ARRIVALS = (Arrival("s", 0),)


def run(tasks, pools=(), arrivals=DEFAULT_ARRIVALS, horizon=1000, **kwargs):
    return simulate(Scenario(tuple(tasks), tuple(pools), tuple(arrivals), horizon, **kwargs))


@given(st.lists(st.integers(0, 50), min_size=1, max_size=30))
def test_serial_and_parallel(durations):
    serial = [
        Task(str(i), (d,), predecessors=(str(i - 1),) if i else ()) for i, d in enumerate(durations)
    ]
    assert run(serial, horizon=2000)["sessions"][0]["end_ns"] == sum(durations)
    parallel = [Task(str(i), (d,)) for i, d in enumerate(durations)]
    parallel.append(Task("join", (3,), predecessors=tuple(t.id for t in parallel)))
    assert run(parallel)["sessions"][0]["end_ns"] == max(durations) + 3


def test_known_single_worker_queue():
    result = run(
        [Task("t", (5,), pool="p")],
        [PoolSpec("p", 1)],
        [Arrival(str(i), i) for i in range(3)],
        horizon=15,
    )
    assert [s["end_ns"] for s in result["sessions"]] == [5, 10, 15]
    assert [a["acquire_ns"] - a["enqueue_ns"] for a in result["attempts"]] == [0, 4, 8]
    assert result["pools"]["p"]["queue_ns"] == 12
    assert result["pools"]["p"]["busy_ns"] == 15


def test_multi_worker_and_external_release():
    result = run(
        [Task("t", (5,), pool="p", external_ns=(10,))],
        [PoolSpec("p", 2)],
        [Arrival(str(i), 0) for i in range(4)],
    )
    assert [s["end_ns"] for s in result["sessions"]] == [15, 15, 20, 20]
    assert result["pools"]["p"]["busy_ns"] == 20
    assert result["pools"]["p"]["max_occupied"] == 2


def test_retry_failure_timeline():
    result = run(
        [Task("t", (3,), "p", failure_probability=1, max_attempts=3, backoff_ns=2)],
        [PoolSpec("p", 1)],
    )
    assert [(a["acquire_ns"], a["release_ns"]) for a in result["attempts"]] == [
        (0, 3),
        (5, 8),
        (10, 13),
    ]
    assert result["outcomes"]["failed"] == 1
    assert result["sessions"][0]["end_ns"] == 13
    assert result["completed_latency_ns"]["p95"] is None


def test_completion_deadline_and_zero_successor_rule():
    assert run([Task("t", (5,))], arrivals=[Arrival("s", 0, 5)])["outcomes"]["completed"] == 1
    result = run(
        [Task("a", (5,)), Task("b", (0,), predecessors=("a",))], arrivals=[Arrival("s", 0, 5)]
    )
    assert result["outcomes"]["timeout"] == 1
    assert run([Task("t", (0,))], arrivals=[Arrival("s", 5, 5)])["outcomes"]["timeout"] == 1


def test_cancellation_lag_supersedes_old_completion():
    result = run(
        [Task("t", (5,), "p", cancellation_lag_ns=10)],
        [PoolSpec("p", 1)],
        [Arrival("a", 0, cancel_ns=2), Arrival("b", 1)],
        horizon=30,
    )
    assert result["sessions"][0]["status"] == "cancelled"
    assert result["sessions"][0]["end_ns"] == 2
    assert result["attempts"][0]["release_ns"] == 12
    assert result["attempts"][1]["acquire_ns"] == 12
    assert result["pools"]["p"]["busy_ns"] == 17
    assert result["pools"]["p"]["acquisitions"] == result["pools"]["p"]["releases"] == 2


def test_queue_rejection_censoring_and_denominators():
    result = run(
        [Task("t", (10,), "p")],
        [PoolSpec("p", 1, 0)],
        [Arrival("a", 0), Arrival("b", 0), Arrival("c", 100)],
        horizon=5,
    )
    assert result["offered"] == 2 and result["not_yet_arrived"] == 1
    assert result["outcomes"]["censored"] == result["outcomes"]["rejected"] == 1
    assert result["pools"]["p"]["occupied_at_horizon"] == 1
    assert result["completed_fraction"] == 0


def test_failed_branch_cancels_running_and_queued_siblings():
    result = run(
        [Task("a", (2,), failure_probability=1), Task("b", (100,), "p"), Task("c", (100,), "p")],
        [PoolSpec("p", 1)],
    )
    assert result["outcomes"]["failed"] == 1
    assert result["pools"]["p"]["queued_at_horizon"] == 0
    assert result["pools"]["p"]["releases"] == 1


@given(st.lists(st.integers(0, 50), min_size=1, max_size=15), st.integers(1, 6))
def test_resource_conservation_and_monotone_ideal_capacity(durations, capacity):
    tasks = [Task(str(i), (d,), "p") for i, d in enumerate(durations)]
    result = run(tasks, [PoolSpec("p", capacity)])
    pool = result["pools"]["p"]
    assert pool["busy_ns"] == sum(durations)
    assert pool["max_occupied"] <= capacity
    assert pool["acquisitions"] == pool["releases"] == len(durations)
    # Identical-duration FIFO jobs have the required ideal monotonicity property.
    equal = [Task(str(i), (5,), "p") for i in range(len(durations))]
    slow = run(equal, [PoolSpec("p", capacity)])
    faster = run(equal, [PoolSpec("p", capacity + 1)])
    assert faster["sessions"][0]["end_ns"] <= slow["sessions"][0]["end_ns"]


def test_seed_streams_and_input_permutation():
    tasks = (
        Task("a", (1, 2, 5), "p", failure_probability=0.2, max_attempts=2),
        Task("b", (3, 7), "p", predecessors=("a",)),
    )
    scenario = Scenario(
        tasks, (PoolSpec("p", 2),), tuple(Arrival(str(i), i) for i in range(10)), 500, 91
    )
    first = simulate(scenario)
    assert first == simulate(scenario)
    assert first == simulate(
        replace(scenario, tasks=tuple(reversed(tasks)), arrivals=tuple(reversed(scenario.arrivals)))
    )
    stream = RandomStream(91, "a")
    assert [stream.uniform() for _ in range(3)] == [
        0.5108435647673725,
        0.5891684775441164,
        0.7372721156792833,
    ]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Task("a", (-1,)),
        lambda: Task("a", failure_probability=float("nan")),
        lambda: PoolSpec("p", 0),
        lambda: Arrival("a", True),
        lambda: Scenario((Task("a", pool="p"),), (), (), 10),
        lambda: Scenario((Task("a", predecessors=("a",)),), (), (), 10),
    ],
)
def test_invalid_models(factory):
    with pytest.raises(ValidationError):
        factory()


def test_event_budget():
    with pytest.raises(ValidationError, match="event budget"):
        simulate(Scenario((Task("a"),), (), (Arrival("a", 0),), 1), max_events=1)
