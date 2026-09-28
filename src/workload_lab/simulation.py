"""Pure integer-time reference DES. Never executes a source application's tools."""

from __future__ import annotations

import hashlib
import heapq
import math
from collections import Counter, deque
from dataclasses import asdict, dataclass, field

from .graph import topological_order
from .ir import MAX_NS, Edge, ValidationError, integer

SIMULATOR_VERSION = "reference-1"


def label(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 128:
        raise ValidationError("simulation IDs require 1 to 128 characters")


class RandomStream:
    """SplitMix64; SHA-256 named seeds, stable independently of Python hash salt."""

    def __init__(self, seed, name):
        self.state = int.from_bytes(
            hashlib.sha256(f"{seed}:{name}".encode()).digest()[:8], "little"
        )

    def uniform(self):
        mask = (1 << 64) - 1
        self.state = (self.state + 0x9E3779B97F4A7C15) & mask
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & mask
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & mask
        return ((z ^ (z >> 31)) >> 11) / (1 << 53)

    def exponential_ns(self, mean):
        integer(mean, "exponential mean", MAX_NS)
        return max(1, round(-math.log1p(-self.uniform()) * mean))


@dataclass(frozen=True)
class Task:
    id: str
    service_ns: tuple[int, ...] = (0,)
    pool: str | None = None
    predecessors: tuple[str, ...] = ()
    external_ns: tuple[int, ...] = (0,)
    failure_probability: float = 0.0
    max_attempts: int = 1
    backoff_ns: int = 0
    cancellation_lag_ns: int = 0
    service_exponential_mean_ns: int | None = None

    def __post_init__(self):
        label(self.id)
        if self.service_exponential_mean_ns is not None:
            if not 1 <= integer(self.service_exponential_mean_ns, "exponential mean", MAX_NS):
                raise ValidationError("exponential mean must be positive")
            if self.service_ns != (0,):
                raise ValidationError("choose empirical or exponential service, not both")
        if self.pool is not None:
            label(self.pool)
        for values in (self.service_ns, self.external_ns):
            if not isinstance(values, tuple) or not 1 <= len(values) <= 100_000:
                raise ValidationError("service/external empirical sample count outside bounds")
            for value in values:
                integer(value, "duration", MAX_NS)
        for value in (self.backoff_ns, self.cancellation_lag_ns):
            integer(value, "duration", MAX_NS)
        if not 1 <= integer(self.max_attempts, "max attempts", 1000):
            raise ValidationError("attempt bound must be positive")
        if (
            type(self.failure_probability) not in (int, float)
            or not math.isfinite(self.failure_probability)
            or not 0 <= self.failure_probability <= 1
        ):
            raise ValidationError("failure probability must be finite in [0,1]")
        if len(self.predecessors) != len(set(self.predecessors)):
            raise ValidationError("duplicate prerequisite")
        for predecessor in self.predecessors:
            label(predecessor)


@dataclass(frozen=True)
class PoolSpec:
    id: str
    capacity: int
    queue_limit: int | None = None

    def __post_init__(self):
        label(self.id)
        if not 1 <= integer(self.capacity, "capacity", 1_000_000):
            raise ValidationError("capacity must be positive")
        if self.queue_limit is not None:
            integer(self.queue_limit, "queue limit", 1_000_000)


@dataclass(frozen=True)
class Arrival:
    id: str
    at_ns: int
    deadline_ns: int | None = None
    cancel_ns: int | None = None

    def __post_init__(self):
        label(self.id)
        integer(self.at_ns, "arrival", MAX_NS)
        for value in (self.deadline_ns, self.cancel_ns):
            if value is not None:
                integer(value, "termination", MAX_NS)
                if value < self.at_ns:
                    raise ValidationError("termination precedes arrival")


@dataclass(frozen=True)
class Scenario:
    tasks: tuple[Task, ...]
    pools: tuple[PoolSpec, ...]
    arrivals: tuple[Arrival, ...]
    horizon_ns: int
    seed: int = 0
    input_provenance: str = "ESTIMATED"
    sources: tuple[str, ...] = ()
    sample_coupling: str = "independent"

    def __post_init__(self):
        integer(self.horizon_ns, "horizon", MAX_NS)
        integer(self.seed, "seed", MAX_NS)
        if self.sample_coupling not in ("independent", "session"):
            raise ValidationError("unsupported sample coupling")
        if self.sample_coupling == "session":
            sizes = {
                len(v) for t in self.tasks for v in (t.service_ns, t.external_ns) if len(v) > 1
            }
            if len(sizes) > 1 or any(t.service_exponential_mean_ns for t in self.tasks):
                raise ValidationError("joint samples must be aligned empirical session vectors")
        if self.horizon_ns == 0 or not 1 <= len(self.tasks) <= 1000:
            raise ValidationError("positive horizon and 1 to 1000 tasks required")
        if len(self.arrivals) > 250_000 or len(self.tasks) * len(self.arrivals) > 2_000_000:
            raise ValidationError("scenario exceeds session/state budget")
        if len(self.pools) > 1000:
            raise ValidationError("scenario exceeds pool budget")
        if self.input_provenance not in ("ESTIMATED", "CALIBRATED"):
            raise ValidationError("scenario input provenance must be ESTIMATED or CALIBRATED")
        if self.input_provenance == "CALIBRATED" and not self.sources:
            raise ValidationError("calibrated scenario needs source evidence")
        for values in (self.pools, self.arrivals):
            if len({v.id for v in values}) != len(values):
                raise ValidationError("duplicate scenario identity")
        pool_ids = {p.id for p in self.pools}
        if any(t.pool is not None and t.pool not in pool_ids for t in self.tasks):
            raise ValidationError("task pool missing")
        topological_order(
            [t.id for t in self.tasks],
            tuple(Edge(p, t.id) for t in self.tasks for p in t.predecessors),
        )


@dataclass
class _Work:
    state: str = "pending"
    attempt: int = 0
    token: int = 0
    queued: int = 0
    acquired: int | None = None
    record: dict | None = None


@dataclass
class _Session:
    arrival: Arrival
    work: dict[str, _Work]
    remaining: dict[str, int]
    status: str = "active"
    end: int | None = None
    done: int = 0


@dataclass
class _Pool:
    spec: PoolSpec
    queue: deque = field(default_factory=deque)
    waiting: int = 0
    busy: int = 0
    last: int = 0
    busy_area: int = 0
    queue_area: int = 0
    maximum_queue: int = 0
    maximum_busy: int = 0
    acquisitions: int = 0
    releases: int = 0

    def advance(self, now):
        self.busy_area += (now - self.last) * self.busy
        self.queue_area += (now - self.last) * self.waiting
        self.last = now


def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


class _Engine:
    def __init__(self, scenario, detail, max_events):
        self.spec, self.detail, self.max_events = scenario, detail, max_events
        self.tasks = {t.id: t for t in sorted(scenario.tasks, key=lambda t: t.id)}
        self.pools = {p.id: _Pool(p) for p in sorted(scenario.pools, key=lambda p: p.id)}
        self.children = {t: [] for t in self.tasks}
        for task in self.tasks.values():
            for parent in task.predecessors:
                self.children[parent].append(task.id)
        self.heap, self.sessions, self.attempt_records = [], {}, []
        self.now, self.round, self.phase, self.sequence, self.events = 0, 0, -1, 0, 0

    def schedule(self, at, phase, kind, sid, tid="", token=0):
        if at > MAX_NS:
            raise ValidationError("simulation timestamp exceeds uint64")
        if at < self.now:
            raise AssertionError("event scheduled in the past")
        microstep = self.round + (phase < self.phase) if at == self.now else 0
        self.sequence += 1
        heapq.heappush(self.heap, (at, microstep, phase, self.sequence, kind, sid, tid, token))

    def draw(self, sid, tid, attempt, purpose, values):
        if len(values) == 1:
            return values[0]
        name = (
            f"{sid}/joint/{attempt}"
            if self.spec.sample_coupling == "session"
            else f"{sid}/{tid}/{attempt}/{purpose}"
        )
        stream = RandomStream(self.spec.seed, name)
        return values[min(len(values) - 1, int(stream.uniform() * len(values)))]

    def release(self, task, work):
        if task.pool is not None and work.acquired is not None:
            pool = self.pools[task.pool]
            pool.advance(self.now)
            pool.busy -= 1
            pool.releases += 1
            if work.record is not None:
                work.record["release_ns"] = self.now
            work.acquired = None
            self.schedule(self.now, 3, "admit", task.pool)
            assert 0 <= pool.busy <= pool.spec.capacity

    def terminate(self, sid, status):
        session = self.sessions[sid]
        if session.status != "active":
            return
        session.status, session.end = status, self.now
        for tid, work in session.work.items():
            task = self.tasks[tid]
            work.token += 1
            if work.state == "queued":
                pool = self.pools[task.pool]
                pool.advance(self.now)
                pool.waiting -= 1
            if work.state in ("running", "external", "queued", "backoff", "pending"):
                work.state = "cancelled"
                if work.record is not None and work.record["end_ns"] is None:
                    work.record.update(end_ns=self.now, outcome=status)
                if work.acquired is not None:
                    self.schedule(
                        self.now + task.cancellation_lag_ns,
                        0,
                        "cancel_release",
                        sid,
                        tid,
                        work.token,
                    )

    def ready(self, sid, tid):
        session, task = self.sessions[sid], self.tasks[tid]
        work = session.work[tid]
        if session.status != "active":
            return
        work.attempt += 1
        work.token += 1
        work.queued = self.now
        work.record = {
            "session": sid,
            "task": tid,
            "attempt": work.attempt,
            "enqueue_ns": self.now,
            "acquire_ns": None,
            "release_ns": None,
            "end_ns": None,
            "outcome": "censored",
        }
        if self.detail:
            self.attempt_records.append(work.record)
        if task.pool is None:
            self.start(sid, tid)
            return
        pool = self.pools[task.pool]
        pool.advance(self.now)
        # Queued requests include those about to consume still-free slots.
        reserved = max(0, pool.waiting - max(0, pool.spec.capacity - pool.busy))
        if (
            pool.spec.queue_limit is not None
            and pool.busy + pool.waiting >= pool.spec.capacity
            and reserved >= pool.spec.queue_limit
        ):
            work.state = "pending"
            work.record.update(end_ns=self.now, outcome="rejected")
            self.terminate(sid, "rejected")
            return
        work.state = "queued"
        pool.queue.append((sid, tid))
        pool.waiting += 1
        pool.maximum_queue = max(pool.maximum_queue, pool.waiting)
        self.schedule(self.now, 3, "admit", task.pool)

    def start(self, sid, tid):
        task, work = self.tasks[tid], self.sessions[sid].work[tid]
        work.state = "running"
        if task.pool is not None:
            pool = self.pools[task.pool]
            pool.advance(self.now)
            pool.waiting -= 1
            pool.busy += 1
            pool.acquisitions += 1
            pool.maximum_busy = max(pool.maximum_busy, pool.busy)
            work.acquired = self.now
            work.record["acquire_ns"] = self.now
        duration = self.draw(sid, tid, work.attempt, "service", task.service_ns)
        if task.service_exponential_mean_ns is not None:
            duration = RandomStream(
                self.spec.seed, f"{sid}/{tid}/{work.attempt}/service"
            ).exponential_ns(task.service_exponential_mean_ns)
        self.schedule(self.now + duration, 0, "finish", sid, tid, work.token)

    def handle(self, kind, sid, tid, token):
        if kind == "arrival":
            arrival = self.arrivals[sid]
            self.sessions[sid] = _Session(
                arrival,
                {t: _Work() for t in self.tasks},
                {t.id: len(t.predecessors) for t in self.tasks.values()},
            )
            for at, outcome in ((arrival.deadline_ns, "timeout"), (arrival.cancel_ns, "cancelled")):
                if at is not None:
                    # Same-time arrival terminates before any admission (next microstep).
                    if at == self.now:
                        self.terminate(sid, outcome)
                    else:
                        self.schedule(at, 1, outcome, sid)
            for task in self.tasks.values():
                if not task.predecessors:
                    self.schedule(self.now, 2, "ready", sid, task.id)
            return
        if kind == "admit":
            pool = self.pools[sid]
            while pool.busy < pool.spec.capacity and pool.queue:
                job, node = pool.queue.popleft()
                if self.sessions[job].work[node].state == "queued":
                    self.start(job, node)
            return
        if kind in ("timeout", "cancelled"):
            self.terminate(sid, kind)
            return
        session, task = self.sessions[sid], self.tasks[tid]
        work = session.work[tid]
        if kind == "cancel_release":
            if token == work.token:
                self.release(task, work)
            return
        if session.status != "active":
            return
        if kind == "ready":
            self.ready(sid, tid)
            return
        if token != work.token:
            return
        if kind == "finish":
            self.release(task, work)
            work.state = "external"
            duration = self.draw(sid, tid, work.attempt, "external", task.external_ns)
            self.schedule(self.now + duration, 0, "outcome", sid, tid, token)
            return
        if kind == "outcome":
            failure = RandomStream(self.spec.seed, f"{sid}/{tid}/{work.attempt}/failure").uniform()
            if failure < task.failure_probability:
                work.record.update(end_ns=self.now, outcome="failed")
                if work.attempt < task.max_attempts:
                    work.state = "backoff"
                    self.schedule(self.now + task.backoff_ns, 2, "ready", sid, tid)
                else:
                    work.state = "failed"
                    self.terminate(sid, "failed")
                return
            work.record.update(end_ns=self.now, outcome="completed")
            work.state = "done"
            session.done += 1
            if session.done == len(self.tasks):
                session.status, session.end = "completed", self.now
            for child in self.children[tid]:
                session.remaining[child] -= 1
                if session.remaining[child] == 0:
                    self.schedule(self.now, 2, "ready", sid, child)

    def run(self):
        self.arrivals = {
            a.id: a
            for a in sorted(self.spec.arrivals, key=lambda a: (a.at_ns, a.id))
            if a.at_ns <= self.spec.horizon_ns
        }
        for arrival in self.arrivals.values():
            self.schedule(arrival.at_ns, 2, "arrival", arrival.id)
        while self.heap and self.heap[0][0] <= self.spec.horizon_ns:
            self.now, self.round, self.phase, _, kind, sid, tid, token = heapq.heappop(self.heap)
            self.events += 1
            if self.events > self.max_events:
                raise ValidationError("simulation event budget exhausted")
            self.handle(kind, sid, tid, token)
        self.now = self.spec.horizon_ns
        rows, pools = [], {}
        for sid, session in sorted(self.sessions.items()):
            if session.status == "active":
                session.status, session.end = "censored", self.now
            rows.append(
                {
                    "id": sid,
                    "arrival_ns": session.arrival.at_ns,
                    "end_ns": session.end,
                    "status": session.status,
                    "latency_ns": session.end - session.arrival.at_ns,
                }
            )
        for key, pool in self.pools.items():
            pool.advance(self.now)
            assert pool.acquisitions == pool.releases + pool.busy
            assert pool.waiting >= 0 and 0 <= pool.busy <= pool.spec.capacity
            pools[key] = {
                "capacity": pool.spec.capacity,
                "busy_ns": pool.busy_area,
                "queue_ns": pool.queue_area,
                "max_occupied": pool.maximum_busy,
                "max_queue": pool.maximum_queue,
                "acquisitions": pool.acquisitions,
                "releases": pool.releases,
                "occupied_at_horizon": pool.busy,
                "queued_at_horizon": pool.waiting,
                "utilization": pool.busy_area / (self.now * pool.spec.capacity),
                "mean_queue_depth": pool.queue_area / self.now,
            }
        counts = {
            status: 0
            for status in ("completed", "failed", "timeout", "cancelled", "rejected", "censored")
        }
        counts.update(Counter(r["status"] for r in rows))
        latencies = [r["latency_ns"] for r in rows if r["status"] == "completed"]
        return {
            "schema_version": "1",
            "artifact_type": "simulation",
            "simulator_version": SIMULATOR_VERSION,
            "provenance": "SIMULATED",
            "input_provenance": self.spec.input_provenance,
            "sources": self.spec.sources,
            "seed": self.spec.seed,
            "horizon_ns": self.now,
            "events_processed": self.events,
            "offered": len(rows),
            "not_yet_arrived": len(self.spec.arrivals) - len(rows),
            "outcomes": counts,
            "completed_fraction": counts["completed"] / len(rows) if rows else None,
            "throughput_per_second": counts["completed"] * 1e9 / self.now,
            "completed_latency_ns": {
                p: percentile(latencies, q) for p, q in (("p50", 0.5), ("p95", 0.95), ("p99", 0.99))
            },
            "pools": pools,
            "sessions": rows if self.detail else None,
            "attempts": self.attempt_records if self.detail else None,
            "assumptions": [
                "explicit fixed DAG and supplied distributions",
                "FIFO slots",
                "no hardware capacity claim without held-out calibration",
            ],
        }


def simulate(scenario: Scenario, *, detail=True, max_events=20_000_000):
    """Pure reference simulation; scenario values are hypotheses, not measured truth."""
    integer(max_events, "event budget", 20_000_000)
    return _Engine(scenario, detail, max_events).run()


def scenario_from_dict(data):
    """Strict small JSON model boundary; callers bound byte size before decoding."""
    if (
        not isinstance(data, dict)
        or set(data)
        - {
            "schema_version",
            "tasks",
            "pools",
            "arrivals",
            "horizon_ns",
            "seed",
            "input_provenance",
            "sources",
            "sample_coupling",
        }
        or data.get("schema_version") != "1"
    ):
        raise ValidationError("unsupported scenario shape/version")
    try:
        tasks = []
        for row in data["tasks"]:
            row = dict(row)
            for key in ("service_ns", "external_ns", "predecessors"):
                if key in row:
                    row[key] = tuple(row[key])
            tasks.append(Task(**row))
        return Scenario(
            tuple(tasks),
            tuple(PoolSpec(**r) for r in data["pools"]),
            tuple(Arrival(**r) for r in data["arrivals"]),
            data["horizon_ns"],
            data.get("seed", 0),
            data.get("input_provenance", "ESTIMATED"),
            tuple(data.get("sources", ())),
            data.get("sample_coupling", "independent"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError("invalid scenario fields") from None


def scenario_dict(scenario):
    return {"schema_version": "1", **asdict(scenario)}
