import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from workload_lab.artifacts import canonical_bytes
from workload_lab.cli import main
from workload_lab.ir import ValidationError
from workload_lab.jobs import JOB_SCHEMA, bundle_job, run_job, verify_bundle, write_job_report
from workload_lab.reporting import job_html

ROOT = Path(__file__).parents[1]


@pytest.fixture
def job(tmp_path):
    for folder, names in (
        (
            "frames-frozen",
            ["protocol.json", "freeze.json", "simpy.json", "fixed.json", "utilization.json"],
        ),
        ("frames-evaluation", ["measured-r0.json", "measured-r1.json"]),
    ):
        for name in names:
            (tmp_path / name).write_bytes((ROOT / "docs/v3" / folder / name).read_bytes())
    manifest = {
        "schema_version": "1.0",
        "artifact_type": "validation_job",
        "protocol": "protocol.json",
        "freeze": "freeze.json",
        "predictions": ["simpy.json", "fixed.json", "utilization.json"],
        "measurements": ["measured-r0.json", "measured-r1.json"],
        "model_id": "simpy-whole-workflow",
        "policy": {
            "maximum_primary_relative_error": 0.15,
            "minimum_replications": 2,
            "require_within_envelope": False,
            "minimum_material_pairs": 1,
            "minimum_ranking_accuracy": 1,
            "require_added_decision_value": False,
            "quality": None,
        },
    }
    path = tmp_path / "job.json"
    path.write_bytes(canonical_bytes(manifest))
    return path


def edit_job(path, update):
    data = json.loads(path.read_bytes())
    update(data)
    path.write_bytes(canonical_bytes(data))


def gate(report, name):
    return next(g for g in report["gates"] if g["id"] == name)


def test_actual_frames_performance_replay_is_explicitly_not_quality_evidence(job, tmp_path):
    assert JOB_SCHEMA == json.loads((ROOT / "schemas/validation-job-v1.schema.json").read_bytes())
    report = run_job(job)
    assert report["result"] == "passed"
    assert report["claim_scope"] == "performance_only_policy"
    assert "quality_not_assessed" in report["limitations"]
    assert gate(report, "measured_quality")["status"] == "not_required"
    assert gate(report, "calibration_envelope")["status"] == "not_required"
    frozen = json.loads((ROOT / "docs/v3/frames-evaluation/validation.json").read_bytes())
    assert report["evaluation"] == frozen
    assert main(["validate-job", str(job), "--output", str(tmp_path / "report")]) == 0
    assert "Quality was not assessed" in (tmp_path / "report/report.html").read_text()


def test_missing_quality_and_absent_added_value_fail_closed(job, tmp_path):
    edit_job(
        job,
        lambda j: j["policy"].update(
            quality={
                "metric_id": "answer.exact",
                "population": "offered",
                "minimum_value": 0.95,
                "minimum_samples": 8,
            },
            require_added_decision_value=True,
        ),
    )
    report = run_job(job)
    assert report["result"] == "failed"
    assert gate(report, "measured_quality")["status"] == "unsupported"
    assert gate(report, "added_decision_value")["status"] == "failed"
    assert gate(report, "added_decision_value")["reason"] == "baseline_not_improved"
    assert main(["validate-job", str(job), "--output", str(tmp_path / "failed")]) == 1
    assert json.loads((tmp_path / "failed/report.json").read_bytes())["result"] == "failed"


@pytest.mark.parametrize(
    "defect,expected",
    [
        (None, "passed"),
        ("low", "failed"),
        ("unknown", "unsupported"),
        ("samples", "unsupported"),
        ("population", "unsupported"),
        ("unit", "unsupported"),
        ("statistic", "unsupported"),
        ("missing", "unsupported"),
    ],
)
def test_quality_requires_every_scenario_and_replication(job, defect, expected):
    edit_job(
        job,
        lambda j: j["policy"].update(
            quality={
                "metric_id": "quality",
                "population": "offered",
                "minimum_value": 0.95,
                "minimum_samples": 8,
            }
        ),
    )
    for name in ["measured-r0.json", "measured-r1.json"]:
        path = job.parent / name
        data = json.loads(path.read_bytes())
        for scenario in data["scenarios"]:
            metric = {
                "id": "quality",
                "unit": "ratio",
                "statistic": "fraction",
                "population": "offered",
                "value": 1,
                "provenance": "MEASURED",
                "sample_count": 8,
                "interval": None,
            }
            if name == "measured-r1.json" and scenario["id"] == "BASE":
                if defect == "missing":
                    continue
                if defect == "low":
                    metric["value"] = 0.5
                elif defect == "unknown":
                    metric.update(value=None, provenance="UNKNOWN")
                elif defect == "samples":
                    metric["sample_count"] = 7
                elif defect in ("population", "unit", "statistic"):
                    metric[defect] = {
                        "population": "completed",
                        "unit": "count",
                        "statistic": "value",
                    }[defect]
            scenario["metrics"].append(metric)
        path.write_bytes(canonical_bytes(data))
    report = run_job(job)
    assert gate(report, "measured_quality")["status"] == expected
    assert report["result"] == ("passed" if expected == "passed" else "failed")


@pytest.mark.parametrize(
    "policy,gate_id",
    [
        ({"minimum_replications": 3}, "replications"),
        ({"maximum_primary_relative_error": 0.01}, "primary_relative_error"),
        ({"minimum_material_pairs": 3}, "material_pairs"),
    ],
)
def test_policy_thresholds_are_applied_to_all_required_evidence(job, policy, gate_id):
    edit_job(job, lambda j: j["policy"].update(policy))
    report = run_job(job)
    assert report["result"] == "failed"
    assert gate(report, gate_id)["status"] == "failed"


def test_declared_extrapolation_cannot_pass_a_required_envelope_gate(job):
    edit_job(job, lambda j: j["policy"].update(require_within_envelope=True))
    report = run_job(job)
    assert report["result"] == "failed"
    assert gate(report, "calibration_envelope")["status"] == "failed"
    assert any(
        row["status"] == "EXTRAPOLATED"
        for row in report["evaluation"]["models"][0]["envelope_checks"]
    )


@pytest.mark.parametrize(
    "reference",
    [
        "../outside.json",
        "/absolute.json",
        "C:/secret.json",
        "..\\secret.json",
        "https://example.com/data.json",
        "bad\nname",
    ],
)
def test_paths_cannot_escape_or_request_network(job, reference):
    edit_job(job, lambda j: j.update(protocol=reference))
    with pytest.raises(ValidationError, match="relative"):
        run_job(job)


def test_symlink_cannot_escape_job_root(job, tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "-outside.json")
    outside.write_bytes((job.parent / "protocol.json").read_bytes())
    link = job.parent / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("host does not permit creating symlinks")
    edit_job(job, lambda j: j.update(protocol="linked.json"))
    with pytest.raises(ValidationError, match="escapes"):
        run_job(job)


@pytest.mark.parametrize(
    "change",
    [
        lambda j: j.update(schema_version="2.0"),
        lambda j: j.update(execute="anything"),
        lambda j: j["policy"].update(maximum_primary_relative_error=True),
        lambda j: j["policy"].update(minimum_replications=0),
        lambda j: j["policy"].update(quality={"metric_id": "q"}),
    ],
)
def test_job_schema_matches_external_validator_and_refuses_unknown_fields(job, change):
    Draft202012Validator.check_schema(JOB_SCHEMA)
    data = json.loads(job.read_bytes())
    Draft202012Validator(JOB_SCHEMA).validate(data)
    change(data)
    assert not Draft202012Validator(JOB_SCHEMA).is_valid(data)
    job.write_bytes(canonical_bytes(data))
    with pytest.raises(ValidationError, match="schema"):
        run_job(job)


def test_tampered_frozen_predictions_do_not_produce_policy_reports(job, tmp_path):
    path = job.parent / "simpy.json"
    path.write_bytes(path.read_bytes() + b" ")
    output = tmp_path / "invalid"
    assert main(["validate-job", str(job), "--output", str(output)]) == 2
    assert not output.exists()


def test_inputs_are_captured_once_before_evaluation(job, monkeypatch):
    from workload_lab import jobs

    evaluate = jobs.evaluate

    def change_original(*args):
        (job.parent / "simpy.json").write_bytes(b"{}")
        return evaluate(*args)

    monkeypatch.setattr(jobs, "evaluate", change_original)
    assert run_job(job)["result"] == "passed"


def test_bundle_is_self_contained_and_keeps_original_frozen_bytes(job, tmp_path, monkeypatch):
    original = run_job(job)
    exported = tmp_path / "bundle"
    bundled = bundle_job(job, exported)
    assert bundled["evaluation"] == original["evaluation"]
    assert (exported / "freeze-000.json").read_bytes() == (job.parent / "freeze.json").read_bytes()
    assert (exported / "predictions-000.json").read_bytes() == (
        job.parent / "simpy.json"
    ).read_bytes()
    for line in (exported / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert hashlib.sha256((exported / name).read_bytes()).hexdigest() == expected
    monkeypatch.chdir(tmp_path.parent)
    replay = run_job(exported / "job.json")
    assert replay["gates"] == original["gates"]
    assert replay["evaluation"] == original["evaluation"]
    assert replay["job_manifest_sha256"] == bundled["job_manifest_sha256"]


def test_output_never_overwrites_and_cleanup_removes_only_owned_files(job, tmp_path, monkeypatch):
    report = run_job(job)
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "keep.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        write_job_report(existing, report)
    assert (existing / "keep.txt").read_text() == "keep"
    output = tmp_path / "partial"
    original_open = Path.open

    def fail_html(self, *args, **kwargs):
        if self == output / "report.html":
            raise OSError("test write failure")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_html)
    with pytest.raises(OSError):
        write_job_report(output, report)
    assert not output.exists()
    assert (existing / "keep.txt").read_text() == "keep"


def test_report_escapes_dynamic_html_and_excludes_source_paths(job):
    report = run_job(job)
    target = next(
        m for m in report["evaluation"]["models"] if m["model"]["id"] == report["model_id"]
    )
    report["model_id"] = '<script>alert("x")</script>'
    target["model"]["id"] = report["model_id"]
    html = job_html(report)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "default-src 'none'" in html
    assert str(job.parent) not in html
    assert str(job.parent) not in json.dumps(report)


def test_bounds_duplicate_keys_and_duplicate_files(job, monkeypatch):
    from workload_lab import jobs

    raw = job.read_bytes()
    job.write_bytes(b'{"artifact_type":"x","artifact_type":"y"}')
    with pytest.raises(ValidationError):
        run_job(job)
    job.write_bytes(raw)
    edit_job(job, lambda j: j["predictions"].append(j["predictions"][0]))
    with pytest.raises(ValidationError, match="repeats"):
        run_job(job)
    job.write_bytes(raw)
    monkeypatch.setattr(jobs, "BUNDLE_MAX_BYTES", len(raw) + 10)
    with pytest.raises(ValidationError, match="byte"):
        run_job(job)


def test_verified_bundle_replay_and_tamper_refusal(job, tmp_path):
    exported = tmp_path / "exported"
    bundle_job(job, exported)
    replay = verify_bundle(exported)
    assert replay["bundle_checksums_verified"] is True
    assert replay["result"] == "passed"
    assert main(["verify-bundle", str(exported), "--output", str(tmp_path / "verified")]) == 0
    target = exported / "measurements-000.json"
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValidationError, match="checksum mismatch"):
        verify_bundle(exported)


def test_bundle_checksums_cannot_reference_outside_files_or_omit_payloads(job, tmp_path):
    exported = tmp_path / "exported"
    bundle_job(job, exported)
    sums = exported / "SHA256SUMS"
    raw = sums.read_bytes()
    sums.write_bytes(raw + b"a" * 64 + b"  ../outside.json\n")
    with pytest.raises(ValidationError, match="invalid bundle checksum"):
        verify_bundle(exported)
    sums.write_bytes(raw)
    (exported / "extra.txt").write_text("unlisted")
    with pytest.raises(ValidationError, match="unlisted"):
        verify_bundle(exported)


def test_committed_replay_inputs_are_exact_copies_of_original_evidence():
    example = ROOT / "examples/validation/frames"
    for folder, names in (
        (
            "frames-frozen",
            ["protocol.json", "freeze.json", "simpy.json", "fixed.json", "utilization.json"],
        ),
        ("frames-evaluation", ["measured-r0.json", "measured-r1.json"]),
    ):
        for name in names:
            assert (example / name).read_bytes() == (ROOT / "docs/v3" / folder / name).read_bytes()


@pytest.mark.parametrize("field,value", [("result", "failed"), ("claim_scope", "certified")])
def test_bundle_refuses_a_rehashed_report_that_disagrees_with_evidence(job, tmp_path, field, value):
    exported = tmp_path / "exported"
    bundle_job(job, exported)
    report = json.loads((exported / "report.json").read_bytes())
    report[field] = value
    changed = canonical_bytes(report)
    (exported / "report.json").write_bytes(changed)
    sums = exported / "SHA256SUMS"
    lines = sums.read_text().splitlines()
    sums.write_text(
        "\n".join(
            hashlib.sha256(changed).hexdigest() + "  report.json"
            if line.endswith("  report.json")
            else line
            for line in lines
        )
        + "\n"
    )
    with pytest.raises(ValidationError, match="disagrees"):
        verify_bundle(exported)


@pytest.mark.parametrize(
    "payload", [b"<h1>certified</h1>", b"<script>alert(1)</script>", b"", None]
)
def test_bundle_refuses_rehashed_html_and_creates_no_verified_output(job, tmp_path, payload):
    exported = tmp_path / "exported"
    bundle_job(job, exported)
    path = exported / "report.html"
    raw = payload if payload is not None else path.read_bytes() + b"\n"
    path.write_bytes(raw)
    sums = exported / "SHA256SUMS"
    sums.write_text(
        "\n".join(
            hashlib.sha256(raw).hexdigest() + "  report.html"
            if line.endswith("  report.html")
            else line
            for line in sums.read_text().splitlines()
        )
        + "\n",
        encoding="ascii",
    )
    with pytest.raises(ValidationError, match="HTML report disagrees"):
        verify_bundle(exported)
    output = tmp_path / "verified"
    assert main(["verify-bundle", str(exported), "--output", str(output)]) == 2
    assert not output.exists()


def test_actual_retained_quality_is_derived_without_rewriting_measurements():
    from examples.frames_quality import attach_quality

    for repetition in range(2):
        source = ROOT / f"docs/v3/frames-evaluation/measured-r{repetition}.json"
        raw = source.read_bytes()
        derived = attach_quality(source, ROOT / "docs/v3/frames-holdout.json")
        assert source.read_bytes() == raw
        for scenario in derived["scenarios"]:
            metric = next(m for m in scenario["metrics"] if m["id"] == "answer.exact")
            assert metric["value"] == 0 and metric["sample_count"] == 8
        assert derived == json.loads(
            (ROOT / f"examples/validation/frames/quality-measured-r{repetition}.json").read_bytes()
        )
    example = ROOT / "examples/validation/frames"
    assert gate(run_job(example / "job.json"), "measured_quality")["status"] == "failed"
    assert (
        gate(run_job(example / "missing-quality-job.json"), "measured_quality")["status"]
        == "unsupported"
    )


def test_quality_adapter_refuses_unlinked_sources_and_incomplete_labels(tmp_path):
    from examples.frames_quality import attach_quality

    source = ROOT / "docs/v3/frames-evaluation/measured-r0.json"
    raw_path = tmp_path / "raw.json"
    raw_path.write_text("{}")
    with pytest.raises(ValidationError, match="lineage"):
        attach_quality(source, raw_path)
    raw = json.loads((ROOT / "docs/v3/frames-holdout.json").read_bytes())
    raw["cells"][0]["sessions"][0]["exact_answer_match"] = None
    raw_path.write_bytes(canonical_bytes(raw))
    measurement = json.loads(source.read_bytes())
    measurement["lineage"][0]["sha256"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    mp = tmp_path / "measurement.json"
    mp.write_bytes(canonical_bytes(measurement))
    with pytest.raises(ValidationError, match="incomplete"):
        attach_quality(mp, raw_path)


def test_non_regular_input_and_environment_mismatch_cannot_pass(job):
    raw = job.read_bytes()
    edit_job(job, lambda j: j.update(protocol="."))
    with pytest.raises(ValidationError, match="regular"):
        run_job(job)
    job.write_bytes(raw)
    path = job.parent / "measured-r0.json"
    data = json.loads(path.read_bytes())
    data["scenarios"][0]["environment"]["region"] = "different"
    path.write_bytes(canonical_bytes(data))
    report = run_job(job)
    assert report["result"] == "failed"
    assert gate(report, "environment_alignment")["status"] == "failed"
