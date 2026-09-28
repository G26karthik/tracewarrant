"""Bounded local OTLP/JSON import with content exclusion by allowlist."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from .ir import MAX_NS, Dataset, Metadata, NodeKind, Span, ValidationError, integer, origin_check

DEFAULT_MAX_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_SPANS = 50_000
_STRING_KEYS = {
    "service.name",
    "gen_ai.operation.name",
    "gen_ai.request.model",
    "gen_ai.provider.name",
    "gen_ai.tool.name",
    "db.system.name",
    "http.request.method",
    "workload_lab.node.kind",
    "workload_lab.node.role",
    "workload_lab.data.origin",
}
_INT_KEYS = {
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "gen_ai.retrieval.top_k",
    "workload_lab.queue_ns",
    "workload_lab.service_ns",
}
_KINDS = {
    "chat": NodeKind.LLM,
    "generate_content": NodeKind.LLM,
    "text_completion": NodeKind.LLM,
    "embeddings": NodeKind.EMBEDDING,
    "retrieval": NodeKind.RETRIEVAL,
    "execute_tool": NodeKind.TOOL,
    "invoke_agent": NodeKind.WORKFLOW,
    "invoke_workflow": NodeKind.WORKFLOW,
    "create_agent": NodeKind.WORKFLOW,
    "plan": NodeKind.WORKFLOW,
}


def _object(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be an array")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) > 1024:
        raise ValidationError(f"{label} must be a string of at most 1024 characters")
    return value


def _number(value: Any, label: str, maximum: int = MAX_NS) -> int:
    if isinstance(value, str):
        if not re.fullmatch(r"[0-9]{1,20}", value):
            raise ValidationError(f"{label} must be a nonnegative integer")
        value = int(value)
    return integer(value, label, maximum)


def _attributes(raw: Any) -> dict:
    values, seen = {}, set()
    for item in _array(raw, "attributes"):
        item = _object(item, "attribute")
        key = _string(item.get("key"), "attribute key")
        if key in seen:
            raise ValidationError("duplicate attribute key")
        seen.add(key)
        if key not in _STRING_KEYS | _INT_KEYS | {
            "workload_lab.depends_on",
            "workload_lab.graph.complete",
        }:
            continue  # Do not decode or retain payload-bearing unknown values.
        value = _object(item.get("value"), "attribute value")
        if len(value) != 1:
            raise ValidationError("known attribute requires one typed value")
        if key in _STRING_KEYS:
            values[key] = _string(value.get("stringValue"), "string attribute")
        elif key in _INT_KEYS:
            values[key] = _number(value.get("intValue"), "integer attribute")
        elif key == "workload_lab.graph.complete":
            if type(value.get("boolValue")) is not bool:
                raise ValidationError("completeness attribute must be boolean")
            values[key] = value["boolValue"]
        else:
            array = _object(value.get("arrayValue"), "dependency array")
            values[key] = tuple(
                _string(_object(v, "dependency").get("stringValue"), "dependency ID")
                for v in _array(array.get("values", []), "dependency values")
            )
    return values


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate JSON object key")
        result[key] = value
    return result


def _nonfinite(_: str) -> None:
    raise ValidationError("nonfinite JSON values are unsupported")


def _float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValidationError("nonfinite JSON values are unsupported")
    return result


def _decode(text: str) -> dict:
    try:
        return _object(
            json.loads(
                text, object_pairs_hook=_pairs, parse_constant=_nonfinite, parse_float=_float
            ),
            "input",
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError("invalid or excessively nested JSON") from None


def _classify(attrs: dict) -> NodeKind:
    explicit = attrs.get("workload_lab.node.kind")
    if explicit is not None:
        try:
            return NodeKind(explicit)
        except ValueError:
            raise ValidationError("unsupported explicit node kind") from None
    if attrs.get("gen_ai.operation.name") in _KINDS:
        return _KINDS[attrs["gen_ai.operation.name"]]
    if "db.system.name" in attrs:
        return NodeKind.DATABASE
    if "http.request.method" in attrs:
        return NodeKind.EXTERNAL_API
    return NodeKind.UNKNOWN


def _dropped(obj: dict) -> bool:
    return any(
        _number(obj.get(key, 0), "dropped count") > 0
        for key in (
            "droppedAttributesCount",
            "droppedEventsCount",
            "droppedLinksCount",
        )
    )


def ingest(
    path: str | Path,
    *,
    origin: str = "observed",
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_spans: int = DEFAULT_MAX_SPANS,
) -> Dataset:
    """Read one OTLP JSON file or JSONL envelopes; never persist raw input."""
    origin_check(origin)
    integer(max_bytes, "max_bytes")
    integer(max_spans, "max_spans")
    if max_bytes == 0 or max_spans == 0:
        raise ValidationError("input limits must be positive")
    path = Path(path)
    with path.open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValidationError("input exceeds byte limit; split it or raise the explicit limit")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeError:
        raise ValidationError("input must be UTF-8") from None
    documents = (
        (_decode(line) for line in content.splitlines() if line.strip())
        if path.suffix.lower() == ".jsonl"
        else (_decode(content),)
    )
    spans = []
    for document in documents:
        resources = _array(document.get("resourceSpans"), "resourceSpans")
        for resource_span in resources:
            resource_span = _object(resource_span, "resource span")
            resource = _object(resource_span.get("resource", {}), "resource")
            resource_attrs = _attributes(resource.get("attributes", []))
            marker = resource_attrs.get("workload_lab.data.origin")
            if marker is not None:
                if marker != "synthetic":
                    raise ValidationError("resource origin marker may only declare synthetic")
                origin = "synthetic"  # A fixture can downgrade, never upgrade, evidence.
            for scope in _array(resource_span.get("scopeSpans", []), "scopeSpans"):
                scope = _object(scope, "scope span")
                urls = tuple(
                    sorted(
                        {
                            _string(s["schemaUrl"], "schema URL")
                            for s in (resource_span, scope)
                            if s.get("schemaUrl")
                        }
                    )
                )
                scope_info = _object(scope.get("scope", {}), "scope")
                for raw_span in _array(scope.get("spans", []), "spans"):
                    if len(spans) >= max_spans:
                        raise ValidationError("input exceeds span limit")
                    span = _object(raw_span, "span")
                    attrs = _attributes(span.get("attributes", []))
                    diagnostics = []
                    if urls:
                        diagnostics.append("schema_url_unverified")
                    if _array(span.get("links", []), "links"):
                        diagnostics.append("links_not_interpreted")
                    if _dropped(span) or _dropped(resource) or _dropped(scope_info):
                        diagnostics.append("source_reports_dropped_data")
                    code = _object(span.get("status", {}), "status").get("code", 0)
                    integer(code, "status code", 2)
                    if "kind" in span:
                        integer(span["kind"], "span kind", 5)
                    parent = span.get("parentSpanId")
                    if parent in (None, "", "0" * 16):
                        parent = None
                    spans.append(
                        Span(
                            trace_id=span.get("traceId"),
                            span_id=span.get("spanId"),
                            parent_id=parent,
                            start_ns=_number(span.get("startTimeUnixNano"), "start timestamp"),
                            end_ns=_number(span.get("endTimeUnixNano"), "end timestamp"),
                            kind=_classify(attrs),
                            service=resource_attrs.get("service.name", "unknown"),
                            role=attrs.get("workload_lab.node.role"),
                            depends_on=attrs.get("workload_lab.depends_on", ()),
                            graph_complete=attrs.get("workload_lab.graph.complete", False),
                            queue_ns=attrs.get("workload_lab.queue_ns"),
                            service_ns=attrs.get("workload_lab.service_ns"),
                            status=("UNSET", "OK", "ERROR")[code],
                            metadata=Metadata(
                                model=attrs.get("gen_ai.request.model"),
                                provider=attrs.get("gen_ai.provider.name"),
                                tool=attrs.get("gen_ai.tool.name"),
                                input_tokens=attrs.get("gen_ai.usage.input_tokens"),
                                output_tokens=attrs.get("gen_ai.usage.output_tokens"),
                                cached_input_tokens=attrs.get(
                                    "gen_ai.usage.cache_read.input_tokens"
                                ),
                                retrieval_top_k=attrs.get("gen_ai.retrieval.top_k"),
                            ),
                            schema_urls=urls,
                            diagnostics=tuple(diagnostics),
                        )
                    )
    return Dataset(hashlib.sha256(raw).hexdigest(), origin, tuple(spans))
