"""Content-free application sample qualification, independent of performance models."""

from __future__ import annotations

import hashlib
import statistics
from html import escape
from pathlib import Path

from .artifact_schema import SHA, TOKEN, array, enum, nullable, obj
from .artifacts import _matches, canonical_bytes
from .ingest import _decode
from .ir import ValidationError

MAX_SAMPLE_BYTES = 8 * 1024 * 1024
MAX_POLICY_BYTES = 64 * 1024
FRACTION = {"type": "number", "minimum": 0, "maximum": 1}
COUNT = {"type": "integer", "minimum": 1, "maximum": 10_000}
SAMPLE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:tracewarrant:application-sample:1.0",
    **obj(
        {
            "schema_version": enum(["1.0"]),
            "artifact_type": enum(["application_sample"]),
            "workload_id": TOKEN,
            "sample_id": TOKEN,
            "provenance": enum(["MEASURED"]),
            "lineage": array(obj({"role": TOKEN, "sha256": SHA}), 1, 16),
            "rows": array(
                obj(
                    {
                        "id": TOKEN,
                        "outcome": enum(["completed", "failed", "censored"]),
                        "metrics": array(obj({"id": TOKEN, "value": nullable(FRACTION)}), 0, 16),
                    }
                ),
                1,
                10_000,
            ),
            "limitations": array(TOKEN, 0, 32),
        }
    ),
}
POLICY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:tracewarrant:application-quality-policy:1.0",
    **obj(
        {
            "schema_version": enum(["1.0"]),
            "artifact_type": enum(["application_quality_policy"]),
            "minimum_samples": COUNT,
            "minimum_completion_fraction": FRACTION,
            "metrics": array(
                obj(
                    {
                        "id": TOKEN,
                        "statistic": enum(["fraction", "mean"]),
                        "minimum_value": FRACTION,
                    }
                ),
                1,
                16,
            ),
        }
    ),
}


def _load(path, schema, limit):
    path = Path(path)
    if not path.is_file():
        raise ValidationError("application qualification input must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValidationError("application qualification input exceeds byte limit")
    try:
        value = _decode(raw.decode("utf-8-sig"))
    except UnicodeError:
        raise ValidationError("application qualification input must be UTF-8") from None
    if not _matches(value, schema):
        raise ValidationError("application qualification schema violation")
    return value, hashlib.sha256(raw).hexdigest()


def qualify_application(sample_path, policy_path):
    sample, sample_sha = _load(sample_path, SAMPLE_SCHEMA, MAX_SAMPLE_BYTES)
    policy, policy_sha = _load(policy_path, POLICY_SCHEMA, MAX_POLICY_BYTES)
    rows = sample["rows"]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValidationError("duplicate offered-row identity")
    if len({m["id"] for m in policy["metrics"]}) != len(policy["metrics"]):
        raise ValidationError("duplicate quality-policy metric")
    for row in rows:
        if len({m["id"] for m in row["metrics"]}) != len(row["metrics"]):
            raise ValidationError("duplicate offered-row metric")
        if row["outcome"] != "completed" and any(
            m["value"] not in (None, 0) for m in row["metrics"]
        ):
            raise ValidationError("unsuccessful rows require zero or unknown quality")
    counts = {
        outcome: sum(r["outcome"] == outcome for r in rows)
        for outcome in ("completed", "failed", "censored")
    }
    offered = len(rows)
    gates = [
        {
            "id": "offered_samples",
            "status": "passed" if offered >= policy["minimum_samples"] else "failed",
            "observed": offered,
            "required": policy["minimum_samples"],
            "reason": None,
        },
        {
            "id": "completion_fraction",
            "status": "passed"
            if counts["completed"] / offered >= policy["minimum_completion_fraction"]
            else "failed",
            "observed": counts["completed"] / offered,
            "required": policy["minimum_completion_fraction"],
            "reason": None,
        },
    ]
    evidence = []
    for criterion in policy["metrics"]:
        values = [
            next((m["value"] for m in r["metrics"] if m["id"] == criterion["id"]), None)
            for r in rows
        ]
        eligible = sum(v is not None for v in values)
        supported = eligible == offered
        reason = None if supported else "missing_or_unknown_offered_quality"
        if criterion["statistic"] == "fraction" and any(v not in (None, 0, 1) for v in values):
            supported, reason = False, "fraction_requires_binary_offered_scores"
        observed = statistics.mean(values) if supported else None
        status = (
            "unsupported"
            if not supported
            else "passed"
            if observed >= criterion["minimum_value"]
            else "failed"
        )
        gates.append(
            {
                "id": "quality/" + criterion["id"],
                "status": status,
                "observed": observed,
                "required": criterion["minimum_value"],
                "reason": reason,
            }
        )
        evidence.append(
            {
                "metric_id": criterion["id"],
                "statistic": criterion["statistic"],
                "population": "offered",
                "offered": offered,
                "observed_scores": eligible,
                "value": observed,
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "application_qualification_report",
        "result": "passed" if all(g["status"] == "passed" for g in gates) else "failed",
        "claim_scope": "application_sample_quality_policy_only",
        "sample_sha256": sample_sha,
        "policy_sha256": policy_sha,
        "workload_id": sample["workload_id"],
        "sample_id": sample["sample_id"],
        "counts": {"offered": offered, **counts},
        "policy": policy,
        "gates": gates,
        "quality_evidence": evidence,
        "lineage": sample["lineage"],
        "limitations": sorted(
            set(sample["limitations"])
            | {
                "caller_declared_measurements_not_authenticated",
                "scores_not_independently_graded",
                "policy_chronology_not_proven",
                "performance_model_not_assessed",
                "population_completeness_not_authenticated",
                "production_readiness_not_established",
            }
        ),
    }


def qualification_html(report):
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{escape(str(g[k]))}</td>"
            for k in ("id", "status", "observed", "required", "reason")
        )
        + "</tr>"
        for g in report["gates"]
    )
    limits = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';
base-uri 'none'; form-action 'none'"><title>Application qualification</title>
<style>body{{font:16px/1.5 system-ui;max-width:1000px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%;overflow-wrap:anywhere}}
td,th{{border:1px solid #ccc;padding:.5rem}}
code{{overflow-wrap:anywhere}}</style></head><body>
<h1>Application quality policy: {escape(report["result"])}</h1>
<p>Scope: {escape(report["claim_scope"])}. Every offered row is in the denominator.</p>
<p>This result checks supplied scores and an explicit policy. It does not certify
semantic correctness, performance predictions or production readiness.</p>
<table><thead><tr><th>Gate</th><th>Status</th><th>Observed</th><th>Required</th><th>Reason</th></tr></thead>
<tbody>{rows}</tbody></table><h2>Counts</h2><p>{escape(str(report["counts"]))}</p>
<h2>Evidence</h2><p>Sample SHA256: <code>{escape(report["sample_sha256"])}</code><br>
Policy SHA256: <code>{escape(report["policy_sha256"])}</code></p>
<h2>Limits</h2><ul>{limits}</ul><p><a href="report.json">Machine-readable report</a></p>
</body></html>
"""


def write_qualification_report(output, report):
    root = Path(output)
    files = {
        "report.json": canonical_bytes(report),
        "report.html": qualification_html(report).encode("utf-8"),
    }
    # Serialize fully before reserving the directory; never adopt existing paths.
    root.mkdir(parents=True, exist_ok=False)
    created = []
    try:
        for name, raw in files.items():
            path = root / name
            with path.open("xb") as stream:
                created.append(path)
                stream.write(raw)
    except OSError:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        try:
            root.rmdir()
        except OSError:
            pass
        raise
