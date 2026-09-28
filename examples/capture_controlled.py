"""Execute concurrent non-coding stub workflows and record actual lifecycle clocks."""

from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
import time
from pathlib import Path


def attribute(key, value):
    if type(value) is bool:
        wire = {"boolValue": value}
    elif type(value) is int:
        wire = {"intValue": str(value)}
    elif isinstance(value, (tuple, list)):
        wire = {"arrayValue": {"values": [{"stringValue": x} for x in value]}}
    else:
        wire = {"stringValue": value}
    return {"key": key, "value": wire}


def envelope(spans, service):
    return {
        "resourceSpans": [
            {
                "resource": {"attributes": [attribute("service.name", service)]},
                "scopeSpans": [
                    {"scope": {"name": "workload_lab.controlled", "version": "1"}, "spans": spans}
                ],
            }
        ]
    }


class Pool:
    def __init__(self, name, capacity):
        self.name, self.capacity = name, capacity
        self.semaphore = asyncio.Semaphore(capacity)


class Recorder:
    def __init__(self, number):
        self.trace = f"{number:032x}"
        self.spans = []
        self.counter = 1
        self.epoch, self.base = time.time_ns(), time.perf_counter_ns()

    def now(self):
        return self.epoch + time.perf_counter_ns() - self.base

    def new_id(self):
        result = f"{self.counter:016x}"
        self.counter += 1
        return result

    def record(self, identity, parent, start, end, kind, **attrs):
        attrs = {"workload_lab.node.kind": kind, **attrs}
        self.spans.append(
            {
                "traceId": self.trace,
                "spanId": identity,
                **({"parentSpanId": parent} if parent else {}),
                "startTimeUnixNano": str(start),
                "endTimeUnixNano": str(end),
                "attributes": [attribute(k, v) for k, v in attrs.items()],
                "status": {
                    "code": 2
                    if attrs.get("workload_lab.outcome") in ("failed", "timeout", "cancelled")
                    else 1
                },
            }
        )

    async def work(
        self,
        parent,
        kind,
        duration,
        deps=(),
        pool=None,
        action=None,
        outcome="completed",
        attempt=None,
        group=None,
        timeout=None,
        cancel_lag=0,
        acquired_event=None,
    ):
        identity, start = self.new_id(), self.now()
        attrs = {"workload_lab.depends_on": deps, "workload_lab.node.role": "work"}
        acquired = False
        if group:
            attrs.update({"workload_lab.attempt_group": group, "workload_lab.attempt": attempt})
        try:
            if pool:
                attrs.update(
                    {
                        "workload_lab.pool": pool.name,
                        "workload_lab.queue": pool.name,
                        "workload_lab.capacity": pool.capacity,
                        "workload_lab.enqueued_ns": self.now(),
                    }
                )
                await pool.semaphore.acquire()
                acquired = True
                attrs["workload_lab.acquired_ns"] = self.now()
                attrs["workload_lab.service_start_ns"] = self.now()
                if acquired_event:
                    acquired_event.set()
            if action:
                action()
            if timeout:
                try:
                    await asyncio.wait_for(asyncio.sleep(duration), timeout)
                except TimeoutError:
                    outcome = "timeout"
            else:
                await asyncio.sleep(duration)
        except asyncio.CancelledError:
            outcome = "cancelled"
            attrs["workload_lab.cancel_requested_ns"] = self.now()
            if acquired:
                attrs["workload_lab.service_end_ns"] = self.now()
            await asyncio.sleep(cancel_lag)
            raise
        finally:
            if acquired:
                attrs.setdefault("workload_lab.service_end_ns", self.now())
                attrs["workload_lab.released_ns"] = self.now()
                pool.semaphore.release()
            end = self.now()
            if not pool:
                attrs["workload_lab.external_wait_ns"] = end - start
            attrs["workload_lab.outcome"] = outcome
            self.record(identity, parent, start, end, kind, **attrs)
        return identity


async def capture(sessions=8, tool_workers=1, model_workers=2, edge_cases=True):
    tools = Pool("tool", tool_workers)
    inference = Pool("stub-model", model_workers)
    retrieval = Pool("retrieval", 2)
    database = Pool("database", 1)

    async def session(number):
        rec = Recorder(number)
        root, start = rec.new_id(), rec.now()
        plan = await rec.work(root, "llm", 0.003, pool=inference)
        nested, nested_start = rec.new_id(), rec.now()
        with sqlite3.connect(":memory:") as db:
            db.execute("create table evidence (value integer)")
            db.executemany("insert into evidence values (?)", [(n,) for n in range(10)])
            children = await asyncio.gather(
                rec.work(
                    nested,
                    "retrieval",
                    0.006,
                    (plan,),
                    retrieval,
                    action=lambda: sorted(["energy", "supply", "risk"]),
                ),
                rec.work(
                    nested,
                    "tool",
                    0.015,
                    (plan,),
                    tools,
                    action=lambda: "<title>Local evidence</title>".split("<"),
                ),
                rec.work(
                    nested,
                    "database",
                    0.002,
                    (plan,),
                    database,
                    action=lambda: db.execute("select sum(value) from evidence").fetchone(),
                ),
                rec.work(nested, "external_api", 0.005, (plan,)),
            )
        rec.record(nested, root, nested_start, rec.now(), "workflow")
        join = await rec.work(root, "compute", 0, children)
        final = await rec.work(root, "llm", 0.003, (join,), inference)
        if edge_cases and number == 1:
            failed = await rec.work(
                root, "tool", 0.002, (final,), tools, outcome="failed", attempt=1, group="fetch"
            )
            backoff = await rec.work(root, "external_api", 0.003, (failed,))
            retry = await rec.work(root, "tool", 0.002, (backoff,), tools, attempt=2, group="fetch")
            timed = await rec.work(root, "tool", 0.1, (retry,), tools, timeout=0.002)
            acquired_event = asyncio.Event()
            task = asyncio.create_task(
                rec.work(
                    root,
                    "tool",
                    1,
                    (timed,),
                    tools,
                    cancel_lag=0.004,
                    acquired_event=acquired_event,
                )
            )
            await acquired_event.wait()
            await asyncio.sleep(0.002)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        rec.record(
            root, None, start, rec.now(), "workflow", **{"workload_lab.graph.complete": True}
        )
        return rec.spans

    traces = await asyncio.gather(*(session(i + 1) for i in range(sessions)))
    return envelope([span for trace in traces for span in trace], "controlled-reference-v1")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sessions", type=int, default=8)
    args = parser.parse_args()
    if not 1 <= args.sessions <= 1000:
        parser.error("sessions must be between 1 and 1000")
    data = asyncio.run(capture(args.sessions))
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
