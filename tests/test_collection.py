import asyncio
import json
import sys

import pytest

from workload_lab.collection import ObservationRecorder, OwnedPool
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import ingest
from workload_lab.ir import NodeKind, ValidationError


def inspect(recorder, tmp_path):
    path = tmp_path / "trace.json"
    recorder.write(path)
    return inspect_observations(ingest(path))


def test_explicit_serial_collection_preserves_unknowns_and_excludes_payloads(tmp_path):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)

    async def work():
        with recorder.run(complete=True) as run:
            previous = None
            for _ in range(2):
                with run.operation(
                    NodeKind.DATABASE, depends_on=(previous,) if previous else ()
                ) as op:
                    async with op.lease(pool, semaphore.acquire, semaphore.release):
                        secret = "PRIVATE_PROMPT_RESULT_SQL_URL"
                        assert secret
                previous = op

    asyncio.run(work())
    report = inspect(recorder, tmp_path)
    for name in ("dependency_graph", "queue_wait", "resource_occupancy", "finite_pool_capacity"):
        assert report["claims"][name]["support"] == "supported"
    assert report["claims"]["prediction_suitability"]["support"] == "unsupported"
    assert report["claims"]["inference_service_demand"]["value"] is None
    assert "PRIVATE" not in (tmp_path / "trace.json").read_text()
    assert "opentelemetry" not in sys.modules


def test_default_graph_remains_incomplete_and_uninstrumented_work_keeps_denominator(tmp_path):
    recorder = ObservationRecorder()
    with recorder.run() as run:
        with run.operation(NodeKind.TOOL):
            pass
    report = inspect(recorder, tmp_path)
    assert report["claims"]["dependency_graph"]["support"] == "unsupported"
    assert report["claims"]["queue_wait"]["observed"] == 0
    assert report["claims"]["queue_wait"]["eligible"] == 1


@pytest.mark.parametrize("kind", [RuntimeError, TimeoutError, asyncio.CancelledError])
def test_application_exception_preserved_and_owned_token_released(tmp_path, kind):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    original = kind("PRIVATE_EXCEPTION")

    async def work():
        with recorder.run(complete=True) as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, semaphore.acquire, semaphore.release):
                    raise original

    with pytest.raises(kind) as caught:
        asyncio.run(work())
    assert caught.value is original and semaphore._value == 1
    report = inspect(recorder, tmp_path)
    assert report["claims"]["dependency_graph"]["support"] == "unsupported"
    observation = next(span.observation for span in recorder.spans() if span.role == "work")
    assert observation.released_ns is not None
    if kind is asyncio.CancelledError:
        assert observation.cancel_requested_ns <= observation.released_ns
    assert "PRIVATE" not in json.dumps(recorder.envelope())


def test_cancellation_while_queued_never_claims_acquisition_or_release(tmp_path):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)

    async def work():
        await semaphore.acquire()
        with recorder.run() as run:

            async def waiter():
                with run.operation(NodeKind.TOOL) as op:
                    async with op.lease(pool, semaphore.acquire, semaphore.release):
                        pytest.fail("unavailable token acquired")

            task = asyncio.create_task(waiter())
            await asyncio.sleep(0)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert semaphore._value == 0
        semaphore.release()

    asyncio.run(work())
    observation = next(span.observation for span in recorder.spans() if span.role == "work")
    assert observation.enqueued_ns is not None and observation.outcome == "cancelled"
    assert observation.acquired_ns is None and observation.released_ns is None
    assert inspect(recorder, tmp_path)["claims"]["queue_wait"]["support"] == "unsupported"


def test_actual_shared_pool_contention_and_cleanup(tmp_path):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    entered, release = asyncio.Event(), asyncio.Event()

    async def work():
        with recorder.run(complete=True) as run:

            async def holder():
                with run.operation(NodeKind.TOOL) as op:
                    async with op.lease(pool, semaphore.acquire, semaphore.release):
                        entered.set()
                        await release.wait()

            async def waiter():
                with run.operation(NodeKind.TOOL) as op:
                    async with op.lease(pool, semaphore.acquire, semaphore.release):
                        pass

            first = asyncio.create_task(holder())
            await entered.wait()
            second = asyncio.create_task(waiter())
            await asyncio.sleep(0)
            release.set()
            await asyncio.gather(first, second)

    asyncio.run(work())
    assert semaphore._value == 1
    report = inspect(recorder, tmp_path)
    assert not report["violations"]
    assert report["claims"]["finite_pool_capacity"]["support"] == "supported"
    assert all(span.queue_ns is not None for span in recorder.spans() if span.role == "work")


@pytest.mark.parametrize("failure", ["acquire", "release", "async_release"])
def test_cleanup_fault_refusal_and_no_false_release(tmp_path, failure):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)

    async def acquire():
        if failure == "acquire":
            raise RuntimeError("PRIVATE_ACQUIRE")

    def release():
        raise RuntimeError("PRIVATE_RELEASE")

    async def async_release():
        pass

    async def work():
        with recorder.run() as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(
                    pool, acquire, async_release if failure == "async_release" else release
                ):
                    pass

    with pytest.raises((RuntimeError, ValidationError)):
        asyncio.run(work())
    if failure == "release":
        with pytest.raises(ValidationError):
            recorder.write(tmp_path / "invalid.json")
        assert not (tmp_path / "invalid.json").exists()
    else:
        report = inspect(recorder, tmp_path)
        assert report["claims"]["resource_occupancy"]["observed"] == 0


def test_cleanup_failure_preserves_original_body_exception(tmp_path):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    body = ValueError("PRIVATE_BODY")
    cleanup = RuntimeError("PRIVATE_CLEANUP")

    async def acquire():
        pass

    def release():
        raise cleanup

    async def work():
        with recorder.run() as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, acquire, release):
                    raise body

    with pytest.raises(ValueError) as caught:
        asyncio.run(work())
    assert caught.value is body and caught.value.__cause__ is cleanup
    with pytest.raises(ValidationError):
        recorder.write(tmp_path / "invalid.json")


@pytest.mark.parametrize(
    "limits", [{"max_spans": 0}, {"max_bytes": 0}, {"max_spans": True}, {"max_bytes": 2**30}]
)
def test_recorder_bounds(limits):
    with pytest.raises(ValidationError):
        ObservationRecorder(**limits)


@pytest.mark.parametrize("limit", ["spans", "bytes"])
def test_truncation_never_exports_a_certified_subset(tmp_path, limit):
    recorder = ObservationRecorder(**({"max_spans": 1} if limit == "spans" else {"max_bytes": 1}))
    with pytest.raises(ValidationError) if limit == "spans" else recorder.run():
        # The bytes case can execute the operation, but its output is refused.
        if limit == "spans":
            with recorder.run(complete=True) as run:
                with run.operation(NodeKind.TOOL):
                    pass
        else:
            pass
    with pytest.raises(ValidationError):
        recorder.write(tmp_path / "invalid.json")
    assert not (tmp_path / "invalid.json").exists()


def test_bad_dependencies_retries_and_foreign_handles_refused(tmp_path):
    recorder = ObservationRecorder()
    foreign = ObservationRecorder().pool(1)
    with recorder.run() as run:
        unfinished = run.operation(NodeKind.TOOL)
        with pytest.raises(ValidationError):
            with run.operation(NodeKind.TOOL, depends_on=(unfinished,)):
                pass
        with run.operation(NodeKind.TOOL) as finished:
            with pytest.raises(ValidationError):
                finished.lease(foreign, lambda: None, lambda: None)
        with pytest.raises(ValidationError):
            with run.operation(NodeKind.TOOL, depends_on=(finished, finished)):
                pass
        group = run.attempt_group()
        with pytest.raises(ValidationError):
            run.operation(NodeKind.TOOL, attempt_group=group)
        with run.operation(NodeKind.TOOL, attempt_group=group, attempt=1):
            pass
        with run.operation(NodeKind.TOOL, attempt_group=group, attempt=2):
            pass
    assert inspect(recorder, tmp_path)["claims"]["retry_attempts"]["observed"] == 2


def test_opaque_handles_fixed_capacity_and_no_overwrite(tmp_path):
    recorder = ObservationRecorder()
    a, b = recorder.pool(1), recorder.pool(1)
    assert a.identity != b.identity and len(a.identity) == 32
    with pytest.raises(AttributeError):
        a.capacity = 3
    with recorder.run() as run:
        with run.operation(NodeKind.TOOL):
            pass
    path = tmp_path / "trace.json"
    recorder.write(path)
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        recorder.write(path)
    assert path.read_bytes() == original
    assert isinstance(a, OwnedPool)


def test_active_or_abandoned_operation_refuses_snapshot(tmp_path):
    recorder = ObservationRecorder()
    with recorder.run() as run:
        operation = run.operation(NodeKind.TOOL)
        operation.__enter__()
        with pytest.raises(ValidationError):
            recorder.envelope()
    operation.__exit__(None, None, None)
    with pytest.raises(ValidationError):
        recorder.write(tmp_path / "invalid.json")


def test_capacity_conflict_is_visible_despite_declared_fixed_handle(tmp_path):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(2)
    both, release = asyncio.Event(), asyncio.Event()
    active = 0

    async def work():
        with recorder.run(complete=True) as run:

            async def operation():
                nonlocal active
                with run.operation(NodeKind.TOOL) as op:
                    async with op.lease(pool, semaphore.acquire, semaphore.release):
                        active += 1
                        if active == 2:
                            both.set()
                        await release.wait()

            tasks = [asyncio.create_task(operation()) for _ in range(2)]
            await both.wait()
            release.set()
            await asyncio.gather(*tasks)

    asyncio.run(work())
    report = inspect(recorder, tmp_path)
    assert report["violations"]["observed_occupancy_exceeds_declared_capacity"] == 1
    assert report["claims"]["finite_pool_capacity"]["support"] == "unsupported"
    assert semaphore._value == 2


def test_late_or_unacquired_lease_cannot_acquire_or_release_tokens():
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    with recorder.run() as run:
        with run.operation(NodeKind.TOOL) as op:
            lease = op.lease(pool, semaphore.acquire, semaphore.release)
            with pytest.raises(ValidationError):
                asyncio.run(lease.__aexit__(None, None, None))
    with pytest.raises(ValidationError):
        asyncio.run(lease.__aenter__())
    assert semaphore._value == 1


def test_observer_clock_fault_still_releases_and_preserves_body_error(tmp_path, monkeypatch):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    body = ValueError("PRIVATE_BODY")

    async def work():
        with recorder.run() as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, semaphore.acquire, semaphore.release):

                    def fail():
                        raise RuntimeError("observer clock failed")

                    monkeypatch.setattr(recorder, "_now", fail)
                    raise body

    with pytest.raises(ValueError) as caught:
        asyncio.run(work())
    assert caught.value is body and semaphore._value == 1
    with pytest.raises(ValidationError):
        recorder.write(tmp_path / "invalid.json")


def test_atomic_nesting_refused_without_disguising_double_counted_work(tmp_path):
    recorder = ObservationRecorder()
    with recorder.run(complete=True) as run:
        with run.operation(NodeKind.TOOL):
            with pytest.raises(ValidationError, match="nested"):
                with run.operation(NodeKind.DATABASE):
                    pass
    report = inspect(recorder, tmp_path)
    assert report["atomic_spans"] == 1
    assert report["claims"]["dependency_graph"]["support"] == "unsupported"


def test_handle_budget_is_global_across_runs_and_pool_types():
    recorder = ObservationRecorder(max_spans=3)
    recorder.pool(1)
    with recorder.run() as first:
        first.attempt_group()
    with recorder.run() as second:
        second.attempt_group()
        with pytest.raises(ValidationError, match="budget"):
            second.attempt_group()
        with pytest.raises(ValidationError, match="budget"):
            recorder.pool(1)
    with pytest.raises(ValidationError, match="active run"):
        second.attempt_group()


@pytest.mark.parametrize("base", [RuntimeError, TimeoutError, asyncio.CancelledError])
def test_falsey_exceptions_are_recorded_as_errors_and_cleanup_runs(tmp_path, base):
    class FalseyError(base):
        def __bool__(self):
            return False

    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    original = FalseyError("PRIVATE_EXCEPTION")

    async def work():
        with recorder.run(complete=True) as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, semaphore.acquire, semaphore.release):
                    raise original

    with pytest.raises(base) as caught:
        asyncio.run(work())
    assert caught.value is original and semaphore._value == 1
    spans = recorder.spans()
    assert all(span.status == "ERROR" for span in spans)
    operation = next(span for span in spans if span.role == "work")
    expected = {
        RuntimeError: "failed",
        TimeoutError: "timeout",
        asyncio.CancelledError: "cancelled",
    }
    assert operation.observation.outcome == expected[base]
    assert operation.observation.released_ns is not None
    assert inspect(recorder, tmp_path)["claims"]["dependency_graph"]["support"] == "unsupported"


def test_exception_truthiness_is_never_evaluated(tmp_path):
    class UnbooleanError(RuntimeError):
        def __bool__(self):
            raise AssertionError("exception truthiness must not be evaluated")

    recorder = ObservationRecorder()
    original = UnbooleanError("PRIVATE_EXCEPTION")
    with pytest.raises(UnbooleanError) as caught:
        with recorder.run(complete=True) as run:
            with run.operation(NodeKind.TOOL):
                raise original
    assert caught.value is original
    assert all(span.status == "ERROR" for span in recorder.spans())
    assert not inspect(recorder, tmp_path)["violations"]


@pytest.mark.parametrize("cleanup_failure", [False, True, "awaitable"])
def test_post_acquisition_clock_fault_preserves_original_and_checks_cleanup(
    tmp_path, monkeypatch, cleanup_failure
):
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    original = RuntimeError("observer clock failed")
    cleanup = ValueError("PRIVATE_CLEANUP")
    released = []
    pending = []
    clock = recorder._now

    def fail():
        raise original

    async def acquire():
        await semaphore.acquire()
        monkeypatch.setattr(recorder, "_now", fail)

    async def deferred_release():
        pytest.fail("async release cannot be used as synchronous cleanup")

    def release():
        released.append(True)
        semaphore.release()
        if cleanup_failure == "awaitable":
            pending.append(deferred_release())
            return pending[-1]
        if cleanup_failure:
            raise cleanup

    async def work():
        with recorder.run() as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, acquire, release):
                    pytest.fail("body ran after observer failure")

    try:
        with pytest.raises(RuntimeError) as caught:
            asyncio.run(work())
        assert caught.value is original and released == [True] and semaphore._value == 1
        if cleanup_failure is True:
            assert original.__cause__ is cleanup
        elif cleanup_failure == "awaitable":
            assert isinstance(original.__cause__, ValidationError)
            assert pending[0].cr_frame is None
        else:
            assert original.__cause__ is None
        monkeypatch.setattr(recorder, "_now", clock)
        with pytest.raises(ValidationError):
            recorder.write(tmp_path / "invalid.json")
        assert not (tmp_path / "invalid.json").exists()
    finally:
        for coroutine in pending:
            coroutine.close()


@pytest.mark.parametrize("boolean_raises", [False, True])
@pytest.mark.parametrize("cleanup_failure", [False, True])
def test_first_release_clock_fault_is_preserved_without_truthiness(
    tmp_path, monkeypatch, boolean_raises, cleanup_failure
):
    class ClockError(RuntimeError):
        def __bool__(self):
            if boolean_raises:
                raise AssertionError("exception truthiness must not be evaluated")
            return False

    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    first, second = ClockError("first clock fault"), RuntimeError("second clock fault")
    cleanup = ValueError("PRIVATE_CLEANUP")
    clock = recorder._now
    calls = 0

    def faulty_clock():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise first
        if calls == 2:
            raise second
        return clock()

    def release():
        semaphore.release()
        if cleanup_failure:
            raise cleanup

    async def work():
        with recorder.run() as run:
            with run.operation(NodeKind.TOOL) as op:
                async with op.lease(pool, semaphore.acquire, release):
                    monkeypatch.setattr(recorder, "_now", faulty_clock)

    with pytest.raises(RuntimeError) as caught:
        asyncio.run(work())
    assert caught.value is first and semaphore._value == 1
    if cleanup_failure:
        assert first.__cause__ is cleanup
    with pytest.raises(ValidationError):
        recorder.write(tmp_path / "invalid.json")
    assert not (tmp_path / "invalid.json").exists()
