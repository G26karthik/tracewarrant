"""Versioned observed execution types. Containment and dependency are distinct."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

SCHEMA_VERSION = "0.2"
MAX_NS = 2**64 - 1


class ValidationError(ValueError):
    """Invalid or unsupported input; messages must not expose trace payloads."""


class Provenance(StrEnum):
    MEASURED = "MEASURED"
    CALIBRATED = "CALIBRATED"
    INTERPOLATED = "INTERPOLATED"
    EXTRAPOLATED = "EXTRAPOLATED"
    SIMULATED = "SIMULATED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class NodeKind(StrEnum):
    WORKFLOW = "workflow"
    LLM = "llm"
    EMBEDDING = "embedding"
    RETRIEVAL = "retrieval"
    RERANKER = "reranker"
    TOOL = "tool"
    COMPUTE = "compute"
    DATABASE = "database"
    QUEUE = "queue"
    EXTERNAL_API = "external_api"
    HUMAN_GATE = "human_gate"
    UNKNOWN = "unknown"


def integer(value: object, label: str, maximum: int | None = None) -> int:
    if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
        raise ValidationError(f"{label} must be a nonnegative integer in range")
    return value


def identifier(value: object, width: int, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(f"[0-9a-fA-F]{{{width}}}", value):
        raise ValidationError(f"{label} must be a hexadecimal identifier of length {width}")
    if int(value, 16) == 0:
        raise ValidationError(f"{label} must be nonzero")
    return value.lower()


def origin_check(origin: str) -> None:
    if origin not in ("observed", "synthetic"):
        raise ValidationError("origin must be observed or synthetic")


@dataclass(frozen=True)
class Evidence:
    provenance: Provenance
    origin: str
    method: str
    sources: tuple[str, ...]
    assumptions: tuple[str, ...] = ()
    uncertainty: None = None  # M1 establishes no statistical interval.

    def __post_init__(self) -> None:
        origin_check(self.origin)
        if not isinstance(self.provenance, Provenance) or not self.method or not self.sources:
            raise ValidationError("evidence requires a category, method and sources")
        if self.origin == "synthetic" and self.provenance == Provenance.MEASURED:
            raise ValidationError("synthetic workload values cannot be MEASURED")
        if self.uncertainty is not None:
            raise ValidationError("statistical bounds are unsupported in IR v0")


@dataclass(frozen=True)
class Quantity:
    value: int | None
    unit: str
    evidence: Evidence

    def __post_init__(self) -> None:
        if self.unit != "ns":
            raise ValidationError("v0 time quantities require ns units")
        if (self.value is None) != (self.evidence.provenance == Provenance.UNKNOWN):
            raise ValidationError("UNKNOWN must have null value; known values need evidence")
        if self.value is not None:
            integer(self.value, "quantity")


def quantity(
    value: int | None,
    origin: str,
    method: str,
    sources: tuple[str, ...],
    assumptions: tuple[str, ...] = (),
) -> Quantity:
    category = Provenance.MEASURED if origin == "observed" else Provenance.ESTIMATED
    if value is None:
        category = Provenance.UNKNOWN
    return Quantity(value, "ns", Evidence(category, origin, method, sources, assumptions))


@dataclass(frozen=True)
class Metadata:
    model: str | None = None
    provider: str | None = None
    tool: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    retrieval_top_k: int | None = None

    def __post_init__(self) -> None:
        for field in (self.model, self.provider, self.tool):
            if field is not None and (not isinstance(field, str) or len(field) > 1024):
                raise ValidationError("metadata label must be a string of at most 1024 characters")
        for value in (
            self.input_tokens,
            self.output_tokens,
            self.cached_input_tokens,
            self.retrieval_top_k,
        ):
            if value is not None:
                integer(value, "metadata count", MAX_NS)
        if (
            self.input_tokens is not None
            and self.cached_input_tokens is not None
            and self.cached_input_tokens > self.input_tokens
        ):
            raise ValidationError("cached input tokens cannot exceed total input tokens")


@dataclass(frozen=True)
class Observation:
    """Optional direct instrumentation; absence never identifies a zero."""

    pool: str | None = None
    queue: str | None = None
    capacity: int | None = None
    enqueued_ns: int | None = None
    acquired_ns: int | None = None
    service_start_ns: int | None = None
    service_end_ns: int | None = None
    released_ns: int | None = None
    cancel_requested_ns: int | None = None
    external_wait_ns: int | None = None
    attempt_group: str | None = None
    attempt: int | None = None
    outcome: str = "unknown"

    def __post_init__(self) -> None:
        for label in (self.pool, self.queue, self.attempt_group):
            if label is not None and (not isinstance(label, str) or not 1 <= len(label) <= 128):
                raise ValidationError("observation label must contain 1 to 128 characters")
        for field in ("capacity", "attempt"):
            value = getattr(self, field)
            if value is not None and not 1 <= integer(value, field, 1_000_000):
                raise ValidationError("capacity and attempt must be positive")
        for field in (
            "enqueued_ns",
            "acquired_ns",
            "service_start_ns",
            "service_end_ns",
            "released_ns",
            "cancel_requested_ns",
            "external_wait_ns",
        ):
            if getattr(self, field) is not None:
                integer(getattr(self, field), field, MAX_NS)
        if self.outcome not in ("unknown", "completed", "failed", "timeout", "cancelled"):
            raise ValidationError("invalid observed outcome")
        ordered = [
            getattr(self, k)
            for k in (
                "enqueued_ns",
                "acquired_ns",
                "service_start_ns",
                "service_end_ns",
                "released_ns",
            )
            if getattr(self, k) is not None
        ]
        if ordered != sorted(ordered):
            raise ValidationError("resource lifecycle timestamps are out of order")
        if self.capacity is not None and self.pool is None:
            raise ValidationError("capacity requires an explicit pool identity")


@dataclass(frozen=True)
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    start_ns: int
    end_ns: int
    kind: NodeKind = NodeKind.UNKNOWN
    service: str = "unknown"
    role: str | None = None
    depends_on: tuple[str, ...] = ()
    graph_complete: bool = False
    queue_ns: int | None = None
    service_ns: int | None = None
    status: str = "UNSET"
    metadata: Metadata = Metadata()
    schema_urls: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()
    observation: Observation = Observation()

    def __post_init__(self) -> None:
        for field, width in (("trace_id", 32), ("span_id", 16)):
            object.__setattr__(self, field, identifier(getattr(self, field), width, field))
        if self.parent_id is not None:
            object.__setattr__(self, "parent_id", identifier(self.parent_id, 16, "parent ID"))
        object.__setattr__(
            self, "depends_on", tuple(identifier(x, 16, "dependency ID") for x in self.depends_on)
        )
        integer(self.start_ns, "start timestamp", MAX_NS)
        integer(self.end_ns, "end timestamp", MAX_NS)
        if self.end_ns < self.start_ns:
            raise ValidationError("span end precedes start")
        if not isinstance(self.kind, NodeKind) or self.role not in (None, "work", "container"):
            raise ValidationError("unsupported node kind or role")
        if not isinstance(self.service, str) or not self.service or len(self.service) > 1024:
            raise ValidationError("service label must contain 1 to 1024 characters")
        if type(self.graph_complete) is not bool or self.status not in ("UNSET", "OK", "ERROR"):
            raise ValidationError("invalid completeness or status")
        if self.graph_complete and self.parent_id is not None:
            raise ValidationError("graph completeness may only be asserted on a root")
        if len(set(self.depends_on)) != len(self.depends_on):
            raise ValidationError("duplicate dependency")
        for component in (self.queue_ns, self.service_ns):
            if component is not None:
                integer(component, "timing component", MAX_NS)
        if (self.queue_ns or 0) + (self.service_ns or 0) > self.end_ns - self.start_ns:
            raise ValidationError("queue/service components exceed elapsed span time")
        obs = self.observation
        if not isinstance(obs, Observation):
            raise ValidationError("invalid observation")
        for value in (
            obs.enqueued_ns,
            obs.acquired_ns,
            obs.service_start_ns,
            obs.service_end_ns,
            obs.released_ns,
            obs.cancel_requested_ns,
        ):
            if value is not None and not self.start_ns <= value <= self.end_ns:
                raise ValidationError("resource timestamp outside span")
        if obs.external_wait_ns is not None and obs.external_wait_ns > self.end_ns - self.start_ns:
            raise ValidationError("external wait exceeds elapsed span")
        # These quantities mean waiting for acquisition and occupied worker time,
        # respectively. They are not CPU time or intrinsic future service demand.
        for field, left, right in (
            ("queue_ns", obs.enqueued_ns, obs.acquired_ns),
            ("service_ns", obs.acquired_ns, obs.released_ns),
        ):
            if left is not None and right is not None:
                supplied = getattr(self, field)
                if supplied is not None and supplied != right - left:
                    raise ValidationError("reported component conflicts with lifecycle interval")
                object.__setattr__(self, field, right - left)
        if (self.queue_ns or 0) + (self.service_ns or 0) > self.end_ns - self.start_ns:
            raise ValidationError("identified components exceed span")


@dataclass(frozen=True)
class Dataset:
    source_sha256: str
    origin: str
    spans: tuple[Span, ...]

    def __post_init__(self) -> None:
        origin_check(self.origin)
        if not re.fullmatch(r"[0-9a-f]{64}", self.source_sha256):
            raise ValidationError("source digest must be SHA-256")
        if not self.spans:
            raise ValidationError("input contains no spans")
        keys = [(s.trace_id, s.span_id) for s in self.spans]
        if len(keys) != len(set(keys)):
            raise ValidationError("duplicate trace/span identity")


@dataclass(frozen=True)
class Node:
    span: Span
    role: str
    elapsed: Quantity
    queue: Quantity
    service_time: Quantity

    def __post_init__(self) -> None:
        if self.role not in ("work", "container"):
            raise ValidationError("invalid node role")
        if self.elapsed.value != self.span.end_ns - self.span.start_ns:
            raise ValidationError("elapsed quantity disagrees with span interval")
        if (
            self.queue.value != self.span.queue_ns
            or self.service_time.value != self.span.service_ns
        ):
            raise ValidationError("component quantity disagrees with reported span component")

    @property
    def id(self) -> str:
        return self.span.span_id


@dataclass(frozen=True)
class Edge:
    predecessor: str
    successor: str
    relation: str = "finish_to_start"

    def __post_init__(self) -> None:
        if self.relation != "finish_to_start":
            raise ValidationError("unsupported dependency relation")


@dataclass(frozen=True)
class Workflow:
    trace_id: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    graph_complete: bool
    diagnostics: tuple[str, ...]
    source_sha256: str
    origin: str

    def __post_init__(self) -> None:
        from .graph import validate_workflow

        validate_workflow(self)


class TraceImporter(Protocol):
    def __call__(self, path: str, *, origin: str = "observed") -> Dataset: ...


class WorkloadCompiler(Protocol):
    def __call__(self, dataset: Dataset) -> tuple[Workflow, ...]: ...
