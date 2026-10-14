"""Bounded caller-owned observation boundaries; no scheduling or payload capture."""

from __future__ import annotations

import asyncio
import inspect
import secrets
import time
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path

from .artifacts import canonical_bytes
from .ingest import DEFAULT_MAX_BYTES, DEFAULT_MAX_SPANS
from .ir import MAX_NS, NodeKind, Observation, Span, ValidationError, integer

_active_operation = ContextVar("tracewarrant_active_operation", default=None)
__all__ = ["ObservationRecorder", "OwnedPool", "AttemptGroup"]


def _identity(width):
    while True:
        value = secrets.token_hex(width // 2)
        if int(value, 16):
            return value


def _attribute(key, value):
    if type(value) is bool:
        wire = {"boolValue": value}
    elif type(value) is int:
        wire = {"intValue": str(value)}
    elif isinstance(value, tuple):
        wire = {"arrayValue": {"values": [{"stringValue": v} for v in value]}}
    else:
        wire = {"stringValue": value}
    return {"key": "workload_lab." + key, "value": wire}


def _span_wire(span: Span) -> dict:
    attrs = {
        "node.kind": span.kind.value,
        "node.role": span.role,
        "depends_on": span.depends_on,
        "outcome": span.observation.outcome,
    }
    if span.parent_id is None:
        attrs["graph.complete"] = span.graph_complete
    for name in Observation.__dataclass_fields__:
        value = getattr(span.observation, name)
        if value is not None and name != "outcome":
            attrs[name] = value
    return {
        "traceId": span.trace_id,
        "spanId": span.span_id,
        **({"parentSpanId": span.parent_id} if span.parent_id else {}),
        "startTimeUnixNano": str(span.start_ns),
        "endTimeUnixNano": str(span.end_ns),
        "attributes": [_attribute(k, v) for k, v in attrs.items()],
        "status": {"code": 2 if span.status == "ERROR" else 1},
    }


@dataclass(frozen=True)
class OwnedPool:
    """Immutable identity/configuration handle, not a semaphore or physical device."""

    identity: str
    capacity: int


@dataclass(frozen=True)
class AttemptGroup:
    identity: str


class ObservationRecorder:
    """Single event-loop/thread recorder. Export only fully closed, bounded captures."""

    def __init__(self, *, max_spans=10_000, max_bytes=DEFAULT_MAX_BYTES):
        integer(max_spans, "max_spans", DEFAULT_MAX_SPANS)
        integer(max_bytes, "max_bytes", DEFAULT_MAX_BYTES)
        if not max_spans or not max_bytes:
            raise ValidationError("collection limits must be positive")
        self._max_spans, self._max_bytes = max_spans, max_bytes
        self._epoch, self._base = time.time_ns(), time.perf_counter_ns()
        self._spans, self._pools = [], {}
        self._reserved = self._active = self._bytes = 0
        self._handles = 0
        self._invalid = False

    def _now(self):
        value = self._epoch + time.perf_counter_ns() - self._base
        integer(value, "collection clock", MAX_NS)
        return value

    def _reserve(self):
        if self._invalid or self._reserved >= self._max_spans:
            self._invalid = True
            raise ValidationError("observation capture is incomplete or exceeds span budget")
        self._reserved += 1
        self._active += 1

    def _finish(self, span):
        self._active -= 1
        self._bytes += len(canonical_bytes(_span_wire(span)))
        if self._bytes > self._max_bytes:
            self._invalid = True
        else:
            self._spans.append(span)

    def pool(self, capacity: int) -> OwnedPool:
        integer(capacity, "pool capacity", 1_000_000)
        if not capacity or self._handles >= self._max_spans:
            raise ValidationError("invalid capacity or pool handle budget exceeded")
        pool = OwnedPool(_identity(32), capacity)
        self._pools[pool.identity] = pool
        self._handles += 1
        return pool

    def run(self, *, complete: bool = False):
        if type(complete) is not bool:
            raise ValidationError("closed scope assertion must be boolean")
        return _RecordedRun(self, complete)

    def spans(self) -> tuple[Span, ...]:
        if self._invalid or self._active or not self._spans:
            raise ValidationError("observation capture is incomplete, active or empty")
        return tuple(self._spans)

    def envelope(self) -> dict:
        spans = self.spans()
        result = {
            "resourceSpans": [
                {
                    "resource": {"attributes": []},
                    "scopeSpans": [
                        {
                            "scope": {"name": "tracewarrant.collection", "version": "1"},
                            "spans": [_span_wire(span) for span in spans],
                        }
                    ],
                }
            ],
        }
        if len(canonical_bytes(result)) > self._max_bytes:
            raise ValidationError("observation envelope exceeds byte budget")
        return result

    def write(self, path):
        raw = canonical_bytes(self.envelope())
        with Path(path).open("xb") as stream:
            stream.write(raw)


class _RecordedRun:
    def __init__(self, recorder, complete):
        self._recorder, self._complete = recorder, complete
        self._trace, self._id = _identity(32), _identity(16)
        self._start = self._end = None
        self._operations = 0
        self._groups = {}
        self._incomplete = False

    def __enter__(self):
        if self._start is not None:
            raise ValidationError("recorded run cannot be reused")
        self._recorder._reserve()
        self._start = self._recorder._now()
        return self

    def __exit__(self, typ, exc, tb):
        try:
            if self._start is None or self._end is not None:
                raise ValidationError("recorded run exit requires one active run")
            self._end = self._recorder._now()
            if self._operations:
                self._recorder._invalid = True
            span = Span(
                self._trace,
                self._id,
                None,
                self._start,
                self._end,
                kind=NodeKind.WORKFLOW,
                role="container",
                graph_complete=self._complete and not self._incomplete and exc is None,
                status="ERROR" if exc else "OK",
            )
            self._recorder._finish(span)
        except BaseException:
            self._recorder._invalid = True
            if exc is None:
                raise
        return False

    def attempt_group(self):
        if self._start is None or self._end is not None:
            raise ValidationError("attempt group requires an active run")
        if self._recorder._handles >= self._recorder._max_spans:
            raise ValidationError("attempt group budget exceeded")
        group = AttemptGroup(_identity(32))
        self._groups[group.identity] = group
        self._recorder._handles += 1
        return group

    def operation(self, kind: NodeKind, *, depends_on=(), attempt_group=None, attempt=None):
        if not isinstance(kind, NodeKind) or kind == NodeKind.WORKFLOW:
            raise ValidationError("operation requires an atomic node kind")
        if type(depends_on) is not tuple or len(depends_on) > 128:
            raise ValidationError("dependencies require a bounded tuple of finished operations")
        if (attempt_group is None) != (attempt is None):
            raise ValidationError("retry observation requires group and attempt")
        if attempt_group is not None:
            if (
                not isinstance(attempt_group, AttemptGroup)
                or self._groups.get(attempt_group.identity) is not attempt_group
            ):
                raise ValidationError("attempt group belongs to another run")
            integer(attempt, "attempt", 1_000_000)
            if not attempt:
                raise ValidationError("attempt must be positive")
        return _RecordedOperation(self, kind, depends_on, attempt_group, attempt)


class _RecordedOperation:
    def __init__(self, run, kind, dependencies, group, attempt):
        self._run, self._kind = run, kind
        self._deps, self._id = dependencies, _identity(16)
        self._start = self._end = None
        self._observation = {}
        self._lease_used = False
        self._lease_active = False
        self._context_token = None
        if group:
            self._observation.update(attempt_group=group.identity, attempt=attempt)

    @property
    def identity(self):
        return self._id

    def __enter__(self):
        run = self._run
        if self._start is not None or run._start is None or run._end is not None:
            raise ValidationError("operation requires an active run and cannot be reused")
        current = _active_operation.get()
        if current is not None and current._end is None:
            run._incomplete = True
            raise ValidationError("atomic operations cannot be nested")
        if any(
            not isinstance(d, _RecordedOperation) or d._run is not run or d._end is None
            for d in self._deps
        ):
            run._incomplete = True
            raise ValidationError("dependencies must be finished operations in the same run")
        if len({d.identity for d in self._deps}) != len(self._deps):
            raise ValidationError("duplicate operation dependency")
        run._recorder._reserve()
        run._operations += 1
        self._start = run._recorder._now()
        self._context_token = _active_operation.set(self)
        return self

    def __exit__(self, typ, exc, tb):
        recorder = self._run._recorder
        try:
            if self._start is None or self._end is not None:
                raise ValidationError("operation exit requires one active operation")
            self._end = recorder._now()
            if self._lease_active:
                recorder._invalid = True
            outcome = (
                "cancelled"
                if isinstance(exc, asyncio.CancelledError)
                else (
                    "timeout" if isinstance(exc, TimeoutError) else "failed" if exc else "completed"
                )
            )
            if outcome == "cancelled":
                self._observation.setdefault("cancel_requested_ns", self._end)
            self._run._operations -= 1
            span = Span(
                self._run._trace,
                self._id,
                self._run._id,
                self._start,
                self._end,
                kind=self._kind,
                role="work",
                depends_on=tuple(d.identity for d in self._deps),
                observation=Observation(**self._observation, outcome=outcome),
                status="ERROR" if exc else "OK",
            )
            recorder._finish(span)
        except BaseException:
            recorder._invalid = True
            if exc is None:
                raise
        finally:
            if self._context_token is not None:
                try:
                    _active_operation.reset(self._context_token)
                except ValueError:
                    recorder._invalid = True
                    if exc is None:
                        raise ValidationError(
                            "operation must exit in its entering context"
                        ) from None
                finally:
                    self._context_token = None
        return False

    def lease(self, pool: OwnedPool, acquire, release):
        recorder = self._run._recorder
        if self._start is None or self._end is not None or self._lease_used:
            raise ValidationError("lease requires an active operation with no prior lease")
        if not isinstance(pool, OwnedPool) or recorder._pools.get(pool.identity) is not pool:
            raise ValidationError("pool belongs to another recorder")
        if not callable(acquire) or not callable(release):
            raise ValidationError("lease requires caller acquire and release functions")
        if inspect.iscoroutinefunction(release):
            raise ValidationError("lease release must be synchronous")
        self._lease_used = True
        return _ObservedLease(self, pool, acquire, release)


class _ObservedLease:
    """Async acquisition and synchronous release; caller retains actual pool ownership."""

    def __init__(self, operation, pool, acquire, release):
        self._op, self._pool = operation, pool
        self._acquire, self._release = acquire, release
        self._entered = False

    async def __aenter__(self):
        if self._entered or self._op._end is not None or self._op._run._end is not None:
            raise ValidationError("lease requires an active operation and cannot be reused")
        self._entered = True
        op = self._op
        recorder = op._run._recorder
        op._observation.update(
            pool=self._pool.identity,
            queue=self._pool.identity,
            capacity=self._pool.capacity,
            enqueued_ns=recorder._now(),
        )
        await self._acquire()
        try:
            now = recorder._now()
            op._observation.update(acquired_ns=now, service_start_ns=now)
            op._lease_active = True
        except BaseException:
            recorder._invalid = True
            self._release()
            raise
        return self

    async def __aexit__(self, typ, exc, tb):
        op = self._op
        if not op._lease_active:
            raise ValidationError("lease exit requires an acquired resource")
        recorder = op._run._recorder
        recording_error = None
        try:
            now = recorder._now()
            op._observation["service_end_ns"] = now
            if isinstance(exc, asyncio.CancelledError):
                op._observation["cancel_requested_ns"] = now
        except BaseException as error:
            recorder._invalid = True
            recording_error = error
        try:
            result = self._release()
            if inspect.isawaitable(result):
                if inspect.iscoroutine(result):
                    result.close()
                raise ValidationError("lease release must be synchronous")
        except BaseException as cleanup:
            recorder._invalid = True
            if exc is not None:
                raise exc from cleanup
            raise
        finally:
            op._lease_active = False
        try:
            op._observation["released_ns"] = recorder._now()
        except BaseException as error:
            recorder._invalid = True
            recording_error = recording_error or error
        if recording_error is not None:
            if exc is not None:
                raise exc from recording_error
            raise recording_error
        return False
