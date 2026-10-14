"""Bounded offline validation jobs and portable evidence directories."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path, PurePosixPath

from .artifact_schema import TOKEN, array, nullable, obj
from .artifacts import _matches, canonical_bytes, load_artifact
from .ingest import DEFAULT_MAX_BYTES, _decode
from .ir import ValidationError
from .validation import evaluate

JOB_MAX_BYTES = 1024 * 1024
BUNDLE_MAX_BYTES = 64 * 1024 * 1024
PATH = {"type": "string", "minLength": 1, "maxLength": 512}
FRACTION = {"type": "number", "minimum": 0, "maximum": 1}
POLICY = obj(
    {
        "maximum_primary_relative_error": {"type": "number", "minimum": 0, "maximum": 1e30},
        "minimum_replications": {"type": "integer", "minimum": 1, "maximum": 32},
        "require_within_envelope": {"type": "boolean"},
        "minimum_material_pairs": {"type": "integer", "minimum": 1, "maximum": 200_000},
        "minimum_ranking_accuracy": FRACTION,
        "require_added_decision_value": {"type": "boolean"},
        "quality": nullable(
            obj(
                {
                    "metric_id": TOKEN,
                    "population": TOKEN,
                    "minimum_value": FRACTION,
                    "minimum_samples": {"type": "integer", "minimum": 1, "maximum": 1_000_000_000},
                }
            )
        ),
    }
)
JOB_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:tracewarrant:validation-job:1.0",
    **obj(
        {
            "schema_version": {"enum": ["1.0"]},
            "artifact_type": {"enum": ["validation_job"]},
            "protocol": PATH,
            "freeze": PATH,
            "predictions": array(PATH, 1, 32),
            "measurements": array(PATH, 1, 32),
            "model_id": TOKEN,
            "policy": POLICY,
        }
    ),
}


def _read(path: Path, limit: int) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValidationError("job input exceeds byte limit")
    return raw


def _capture(path: Path) -> tuple[dict, str, dict[str, bytes]]:
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValidationError("job manifest must be a regular file")
    raw = _read(path, JOB_MAX_BYTES)
    try:
        job = _decode(raw.decode("utf-8-sig"))
    except UnicodeError:
        raise ValidationError("job must be UTF-8") from None
    if not _matches(job, JOB_SCHEMA):
        raise ValidationError("validation job schema violation")
    captured, seen, total = {}, set(), len(raw)
    portable = {**job, "predictions": [], "measurements": []}
    for role in ("protocol", "freeze", "predictions", "measurements"):
        references = job[role] if isinstance(job[role], list) else [job[role]]
        for index, reference in enumerate(references):
            relative = PurePosixPath(reference)
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or any(c in reference for c in ("\\", ":"))
                or any(ord(c) < 32 or ord(c) == 127 for c in reference)
            ):
                raise ValidationError("job inputs must be contained relative file paths")
            resolved = (path.parent / reference).resolve(strict=True)
            if not resolved.is_relative_to(path.parent) or resolved in seen:
                raise ValidationError("job input escapes root or repeats a file")
            if not resolved.is_file():
                raise ValidationError("job inputs must be regular files")
            seen.add(resolved)
            payload = _read(resolved, min(DEFAULT_MAX_BYTES, BUNDLE_MAX_BYTES - total))
            total += len(payload)
            name = f"{role}-{index:03d}.json"
            captured[name] = payload
            if isinstance(portable[role], list):
                portable[role].append(name)
            else:
                portable[role] = name
    return portable, hashlib.sha256(raw).hexdigest(), captured


def _gate(name, observed, required, supported=True, passed=True, reason=None):
    return {
        "id": name,
        "status": "unsupported" if not supported else "passed" if passed else "failed",
        "observed": observed,
        "required": required,
        "reason": reason,
    }


def _not_required(name):
    return {
        "id": name,
        "status": "not_required",
        "observed": None,
        "required": None,
        "reason": "not_requested_by_policy",
    }


def _quality_gate(policy, measurements):
    quality = policy["quality"]
    if quality is None:
        return _not_required("measured_quality"), []
    rows = []
    for measurement in measurements:
        for scenario in measurement["scenarios"]:
            metric = next((m for m in scenario["metrics"] if m["id"] == quality["metric_id"]), None)
            reason = None
            if metric is None:
                reason = "missing_quality_metric"
            elif (metric["unit"], metric["statistic"], metric["population"]) != (
                "ratio",
                "fraction",
                quality["population"],
            ):
                reason = "quality_semantics_mismatch"
            elif metric["provenance"] != "MEASURED" or metric["value"] is None:
                reason = "quality_not_measured"
            elif metric["sample_count"] < quality["minimum_samples"]:
                reason = "insufficient_quality_samples"
            rows.append(
                {
                    "scenario_id": scenario["id"],
                    "run_id": measurement["run_id"],
                    "value": metric["value"] if metric and reason is None else None,
                    "reason": reason,
                }
            )
    supported = bool(rows) and all(row["reason"] is None for row in rows)
    minimum = min(row["value"] for row in rows) if supported else None
    return _gate(
        "measured_quality",
        minimum,
        quality["minimum_value"],
        supported,
        supported and minimum >= quality["minimum_value"],
        "missing_or_incompatible_quality_evidence" if not supported else None,
    ), rows


def _evaluate(job, manifest_digest, captured, source_digest=None):
    with tempfile.TemporaryDirectory(prefix="tracewarrant-job-") as folder:
        root = Path(folder)
        for name, raw in captured.items():
            (root / name).write_bytes(raw)
        protocol_path, freeze_path = root / job["protocol"], root / job["freeze"]
        predictions = [root / name for name in job["predictions"]]
        measurements = [root / name for name in job["measurements"]]
        result = evaluate(protocol_path, freeze_path, predictions, measurements)
        protocol = load_artifact(protocol_path, "protocol")[0]
        measured = [load_artifact(p, "measurement")[0] for p in measurements]
    targets = [
        m
        for m in result["models"]
        if m["model"]["id"] == job["model_id"] and m["model"]["role"] == "model"
    ]
    if len(targets) != 1:
        raise ValidationError("job model must identify one model-role prediction")
    model, policy = targets[0], job["policy"]
    baselines = [m for m in result["models"] if m["model"]["role"] == "baseline"]
    gates = [
        _gate("baseline_presence", len(baselines), 1, bool(baselines), bool(baselines)),
        _gate(
            "replications",
            len(measured),
            policy["minimum_replications"],
            passed=len(measured) >= policy["minimum_replications"],
        ),
    ]
    primary = [r for r in model["metric_errors"] if r["metric_id"] == protocol["primary_metric"]]
    comparable = len(primary) == len(protocol["scenario_ids"]) * len(measured) and all(
        r["status"] == "compared" and r["relative_error"] is not None for r in primary
    )
    worst = max(r["relative_error"] for r in primary) if comparable else None
    gates.append(
        _gate(
            "primary_relative_error",
            worst,
            policy["maximum_primary_relative_error"],
            comparable,
            comparable and worst <= policy["maximum_primary_relative_error"],
            "missing_comparable_primary_error" if not comparable else None,
        )
    )
    aligned = all(r["matches_prediction_environment"] for r in model["envelope_checks"])
    gates.append(_gate("environment_alignment", aligned, True, passed=aligned))
    if policy["require_within_envelope"]:
        checks = model["envelope_checks"]
        known = bool(checks) and all(r["status"] != "UNKNOWN" for r in checks)
        within = all(r["status"] == "within_declared_envelope" for r in checks)
        gates.append(_gate("calibration_envelope", within if known else None, True, known, within))
    else:
        gates.append(_not_required("calibration_envelope"))
    gates.append(
        _gate(
            "material_pairs",
            model["material_pair_count"],
            policy["minimum_material_pairs"],
            passed=model["material_pair_count"] >= policy["minimum_material_pairs"],
        )
    )
    accuracy = model["ranking_accuracy"]
    gates.append(
        _gate(
            "ranking_accuracy",
            accuracy,
            policy["minimum_ranking_accuracy"],
            accuracy is not None,
            accuracy is not None and accuracy >= policy["minimum_ranking_accuracy"],
        )
    )
    if policy["require_added_decision_value"]:
        comparisons = [
            r for r in result["baseline_comparisons"] if r["model_id"] == job["model_id"]
        ]
        complete = bool(comparisons) and all(
            r["result"] != "insufficient_evidence" for r in comparisons
        )
        counterexample = any(
            r["result"]
            in (
                "baseline_choice_better",
                "no_added_decision_value",
                "no_material_decision_difference",
            )
            for r in comparisons
        )
        better = complete and all(r["result"] == "model_choice_better" for r in comparisons)
        gates.append(
            _gate(
                "added_decision_value",
                better if complete or counterexample else None,
                True,
                complete or counterexample,
                better,
                "baseline_not_improved" if counterexample else None,
            )
        )
    else:
        gates.append(_not_required("added_decision_value"))
    quality, quality_rows = _quality_gate(policy, measured)
    gates.append(quality)
    return {
        "schema_version": "1.0",
        "artifact_type": "validation_job_report",
        "result": "passed"
        if all(g["status"] in ("passed", "not_required") for g in gates)
        else "failed",
        "claim_scope": "performance_only_policy"
        if policy["quality"] is None
        else "quality_and_performance_policy",
        "job_manifest_sha256": manifest_digest,
        "source_manifest_sha256": source_digest or manifest_digest,
        "input_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in captured.items()},
        "model_id": job["model_id"],
        "policy": policy,
        "gates": gates,
        "quality_rows": quality_rows,
        "evaluation": result,
        "limitations": [
            "policy_not_bound_by_prediction_freeze",
            "caller_declared_measurements_not_authenticated",
            "policy_acceptance_is_not_production_certification",
            "quality_not_assessed"
            if policy["quality"] is None
            else "quality_is_caller_supplied_metric",
        ],
    }


def run_job(path: str | Path) -> dict:
    """Capture inputs once and evaluate the explicit job policy without executing tools."""
    job, digest, captured = _capture(Path(path))
    return _evaluate(job, digest, captured)


def _write_directory(path: Path, files: dict[str, bytes]) -> None:
    """Exclusive directory; prepare bytes first and remove only our files on failure."""
    path.mkdir()  # Parent must exist. An existing destination is never modified.
    created = []
    try:
        for name, raw in files.items():
            destination = path / name
            with destination.open("xb") as stream:
                created.append(destination)
                stream.write(raw)
    except OSError:
        for destination in reversed(created):
            try:
                destination.unlink()
            except OSError:
                pass
        try:
            path.rmdir()
        except OSError:
            pass
        raise


def _reports(report):
    from .reporting import job_html

    raw = canonical_bytes(report)
    if len(raw) > BUNDLE_MAX_BYTES:
        raise ValidationError("job report exceeds byte budget")
    rendered = job_html(report).encode("utf-8")
    if len(rendered) > DEFAULT_MAX_BYTES:
        raise ValidationError("HTML report exceeds byte budget")
    return {"report.json": raw, "report.html": rendered}


def write_job_report(path: str | Path, report: dict) -> None:
    files = _reports(report)
    checksums = "".join(
        f"{hashlib.sha256(raw).hexdigest()}  {name}\n" for name, raw in sorted(files.items())
    )
    files["SHA256SUMS"] = checksums.encode("ascii")
    _write_directory(Path(path), files)


def bundle_job(path: str | Path, output: str | Path) -> dict:
    """Export captured evidence, a portable manifest and its matching report."""
    job, original_digest, captured = _capture(Path(path))
    raw_job = canonical_bytes(job)
    report = _evaluate(job, hashlib.sha256(raw_job).hexdigest(), captured, original_digest)
    files = {"job.json": raw_job, **captured, **_reports(report)}
    checksums = "".join(
        f"{hashlib.sha256(raw).hexdigest()}  {name}\n" for name, raw in sorted(files.items())
    )
    files["SHA256SUMS"] = checksums.encode("ascii")
    _write_directory(Path(output), files)
    return report


def verify_bundle(path: str | Path) -> dict:
    """Verify all bundle bytes and replay a private snapshot; hashes are not signatures."""
    root = Path(path).resolve(strict=True)
    if (root / "SHA256SUMS").is_symlink() or not (root / "SHA256SUMS").is_file():
        raise ValidationError("bundle checksums must be a regular local file")
    raw_sums = _read(root / "SHA256SUMS", 128 * 1024)
    try:
        lines = raw_sums.decode("ascii").splitlines()
    except UnicodeError:
        raise ValidationError("bundle checksums must be ASCII") from None
    if not 4 <= len(lines) <= 70:
        raise ValidationError("invalid bundle entry count")
    captured, total = {}, 0
    for line in lines:
        digest, separator, name = line.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
            or not name
            or name in (".", "..", "SHA256SUMS")
            or any(c in name for c in ("/", "\\", ":"))
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or name in captured
        ):
            raise ValidationError("invalid bundle checksum entry")
        candidate = root / name
        if candidate.is_symlink() or not candidate.is_file():
            raise ValidationError("bundle entries must be regular local files")
        limit = BUNDLE_MAX_BYTES if name == "report.json" else DEFAULT_MAX_BYTES
        budget = 2 * BUNDLE_MAX_BYTES + DEFAULT_MAX_BYTES + JOB_MAX_BYTES
        payload = _read(candidate, min(limit, budget - total))
        total += len(payload)
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValidationError("bundle checksum mismatch")
        captured[name] = payload
    actual = set()
    for index, entry in enumerate(root.iterdir()):
        if index >= 71:
            raise ValidationError("bundle has too many entries")
        actual.add(entry.name)
    if actual != set(captured) | {"SHA256SUMS"} or not {
        "job.json",
        "report.json",
        "report.html",
    } <= set(captured):
        raise ValidationError("bundle has missing or unlisted entries")
    with tempfile.TemporaryDirectory(prefix="tracewarrant-bundle-") as folder:
        snapshot = Path(folder)
        for name, payload in captured.items():
            (snapshot / name).write_bytes(payload)
        report = run_job(snapshot / "job.json")
    try:
        bundled = _decode(captured["report.json"].decode("utf-8"))
    except UnicodeError:
        raise ValidationError("bundle report must be UTF-8") from None
    source = bundled.get("source_manifest_sha256") if isinstance(bundled, dict) else None
    if (
        not isinstance(source, str)
        or len(source) != 64
        or any(c not in "0123456789abcdef" for c in source)
    ):
        raise ValidationError("invalid source manifest digest in bundle report")
    normalized = {**bundled, "source_manifest_sha256": report["source_manifest_sha256"]}
    if canonical_bytes(normalized) != canonical_bytes(report):
        raise ValidationError("bundled report disagrees with evidence")
    report["bundle_checksums_verified"] = True
    report["bundle_checksums_sha256"] = hashlib.sha256(raw_sums).hexdigest()
    report["limitations"].append("bundle_checksums_do_not_authenticate_author")
    return report
