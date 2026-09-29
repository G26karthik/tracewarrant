"""Bounded artifacts and integrity receipts; no model execution or remote references."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

from .artifact_schema import SCHEMA
from .ingest import DEFAULT_MAX_BYTES, _decode
from .ir import ValidationError


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_time(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError:
        raise ValidationError("invalid UTC timestamp") from None


def _matches(value, schema) -> bool:
    """Interpret only our fixed schema vocabulary, never user-supplied schemas."""
    if "$ref" in schema:
        return _matches(value, SCHEMA["$defs"][schema["$ref"].split("/")[-1]])
    if "oneOf" in schema:
        return sum(_matches(value, s) for s in schema["oneOf"]) == 1
    if "anyOf" in schema:
        return any(_matches(value, s) for s in schema["anyOf"])
    if "enum" in schema:
        return any(type(value) is type(x) and value == x for x in schema["enum"])
    kind = schema.get("type")
    if kind == "null":
        return value is None
    if kind == "boolean":
        return type(value) is bool
    if kind in ("integer", "number"):
        if type(value) not in (int, float):
            return False
        if not -1e30 <= value <= 1e30 or not math.isfinite(value):
            return False
        if kind == "integer" and value != int(value):
            return False
        return (
            value >= schema.get("minimum", -1e30)
            and value <= schema.get("maximum", 1e30)
            and value > schema.get("exclusiveMinimum", -math.inf)
            and value < schema.get("exclusiveMaximum", math.inf)
        )
    if kind == "string":
        return (
            isinstance(value, str)
            and schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 128)
            and ("pattern" not in schema or re.search(schema["pattern"], value) is not None)
        )
    if kind == "array":
        return (
            isinstance(value, list)
            and schema.get("minItems", 0) <= len(value) <= schema["maxItems"]
            and all(_matches(v, schema["items"]) for v in value)
        )
    if kind == "object":
        if not isinstance(value, dict) or len(value) > schema.get("maxProperties", 128):
            return False
        properties = schema.get("properties", {})
        if not set(schema.get("required", [])) <= value.keys():
            return False
        for key, item in value.items():
            if not isinstance(key, str) or (
                "propertyNames" in schema and not _matches(key, schema["propertyNames"])
            ):
                return False
            child = properties.get(key, schema.get("additionalProperties", False))
            if child is False or not _matches(item, child):
                return False
        return True
    raise AssertionError("unsupported internal schema vocabulary")


def validate_artifact(data: dict, expected: str | None = None) -> dict:
    try:
        valid = _matches(data, SCHEMA)
    except RecursionError:
        valid = False
    if not valid or (expected is not None and data["artifact_type"] != expected):
        raise ValidationError("artifact schema violation")
    kind = data["artifact_type"]
    if kind == "freeze":
        parse_time(data["created_at"])
        if len(set(data["prediction_sha256s"])) != len(data["prediction_sha256s"]):
            raise ValidationError("duplicate frozen prediction")
    if kind == "protocol" and len(set(data["scenario_ids"])) != len(data["scenario_ids"]):
        raise ValidationError("duplicate protocol scenario")
    if kind == "measurement":
        if parse_time(data["finished_at"]) < parse_time(data["started_at"]):
            raise ValidationError("measurement time order")
        c = data["counts"]
        if c["offered"] != c["completed"] + c["failed"] + c["censored"]:
            raise ValidationError("measurement outcome conservation")
    if kind == "prediction":
        for bound in data["calibration_envelope"].values():
            if "minimum" in bound and bound["minimum"] > bound["maximum"]:
                raise ValidationError("invalid calibration envelope")
    scenarios = data.get("scenarios", [])
    if len({s["id"] for s in scenarios}) != len(scenarios):
        raise ValidationError("duplicate scenario identity")
    for scenario in scenarios:
        if set(scenario["configuration"]) & set(scenario["environment"]):
            raise ValidationError("ambiguous envelope dimension")
        metrics = scenario["metrics"]
        if len({m["id"] for m in metrics}) != len(metrics):
            raise ValidationError("duplicate metric identity")
        for metric in metrics:
            unknown = metric["provenance"] == "UNKNOWN"
            if unknown != (metric["value"] is None):
                raise ValidationError("UNKNOWN requires null metric value")
            if kind == "prediction" and metric["provenance"] == "MEASURED":
                raise ValidationError("predicted metric cannot be MEASURED")
            if (
                kind == "measurement"
                and metric["provenance"] == "MEASURED"
                and metric["sample_count"] == 0
            ):
                raise ValidationError("measured metric requires samples")
            if metric["unit"] == "ratio" and metric["value"] is not None and metric["value"] > 1:
                raise ValidationError("ratio metric exceeds one")
            interval = metric["interval"]
            if interval and (
                unknown or not interval["lower"] <= metric["value"] <= interval["upper"]
            ):
                raise ValidationError("interval does not contain point value")
        b = scenario["bottleneck"]
        if kind == "prediction" and b["provenance"] == "MEASURED":
            raise ValidationError("predicted bottleneck cannot be MEASURED")
        if (b["provenance"] == "UNKNOWN") != (not b["resources"]):
            raise ValidationError("unknown bottleneck must have no resource assertion")
        if len(set(b["resources"])) != len(b["resources"]):
            raise ValidationError("duplicate bottleneck resource")
    if kind == "prediction":
        seen = set()
        for ranking in data["rankings"]:
            key = (ranking["comparison_group"], ranking["metric_id"])
            order = [x for tie in ranking["order"] for x in tie]
            eligible = [s for s in scenarios if s["comparison_group"] == key[0]]
            if (
                key in seen
                or len(set(order)) != len(order)
                or set(order) != {s["id"] for s in eligible}
            ):
                raise ValidationError("ranking must cover its comparison group exactly once")
            if any(key[1] not in {m["id"] for m in s["metrics"]} for s in eligible):
                raise ValidationError("ranking metric missing")
            if ranking["provenance"] in ("MEASURED", "UNKNOWN"):
                raise ValidationError("invalid predicted ranking provenance")
            seen.add(key)
    return data


def load_artifact(path: str | Path, expected: str | None = None) -> tuple[dict, str]:
    with Path(path).open("rb") as stream:
        raw = stream.read(DEFAULT_MAX_BYTES + 1)
    if len(raw) > DEFAULT_MAX_BYTES:
        raise ValidationError("artifact exceeds byte limit")
    try:
        data = _decode(raw.decode("utf-8-sig"))
    except UnicodeError:
        raise ValidationError("artifact must be UTF-8") from None
    return validate_artifact(data, expected), sha256(raw)


def write_new(path: str | Path, data: dict) -> None:
    raw = canonical_bytes(data)
    with Path(path).open("xb") as stream:
        stream.write(raw)


def freeze_predictions(protocol_path: str | Path, prediction_paths: list[str | Path]) -> dict:
    if not 1 <= len(prediction_paths) <= 32:
        raise ValidationError("prediction bundle size")
    if sum(Path(p).stat().st_size for p in [protocol_path, *prediction_paths]) > 64 * 1024 * 1024:
        raise ValidationError("prediction bundle exceeds byte budget")
    protocol, protocol_sha = load_artifact(protocol_path, "protocol")
    predictions = [load_artifact(p, "prediction") for p in prediction_paths]
    validate_bundle(protocol, [p for p, _ in predictions])
    receipt = {
        "schema_version": "1.0",
        "artifact_type": "freeze",
        "created_at": timestamp(),
        "protocol_sha256": protocol_sha,
        "prediction_sha256s": sorted(h for _, h in predictions),
        "integrity_method": "sha256_raw_bytes",
    }
    return validate_artifact(receipt, "freeze")


def validate_bundle(protocol: dict, predictions: list[dict]) -> None:
    if not predictions or len(predictions) > 32:
        raise ValidationError("prediction bundle size")
    if len({p["model"]["id"] for p in predictions}) != len(predictions):
        raise ValidationError("duplicate model identity")
    if protocol["require_baseline"] and not any(
        p["model"]["role"] == "baseline" for p in predictions
    ):
        raise ValidationError("protocol requires a baseline")
    primary_definitions = {}
    environments = {}
    identities = {}
    for prediction in predictions:
        if prediction["workload_id"] != protocol["workload_id"]:
            raise ValidationError("workload identity mismatch")
        if {s["id"] for s in prediction["scenarios"]} != set(protocol["scenario_ids"]):
            raise ValidationError("prediction scenario set mismatch")
        for scenario in prediction["scenarios"]:
            identity = (scenario["configuration"], scenario["comparison_group"])
            if scenario["id"] in identities and identities[scenario["id"]] != identity:
                raise ValidationError("prediction scenario identity mismatch")
            identities[scenario["id"]] = identity
            primary = next(
                (m for m in scenario["metrics"] if m["id"] == protocol["primary_metric"]), None
            )
            if primary is None:
                raise ValidationError("primary metric missing from prediction")
            definition = tuple(primary[k] for k in ("unit", "statistic", "population"))
            group = scenario["comparison_group"]
            if group in environments and environments[group] != scenario["environment"]:
                raise ValidationError("prediction environments differ within comparison group")
            environments[group] = scenario["environment"]
            if group in primary_definitions and primary_definitions[group] != definition:
                raise ValidationError("primary metric semantics differ within comparison group")
            primary_definitions[group] = definition
