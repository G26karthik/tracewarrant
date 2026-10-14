import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from examples.hotpot_quality import convert
from workload_lab.artifacts import canonical_bytes
from workload_lab.cli import main
from workload_lab.ir import ValidationError
from workload_lab.qualification import (
    POLICY_SCHEMA,
    SAMPLE_SCHEMA,
    qualification_html,
    qualify_application,
    write_qualification_report,
)

ROOT = Path(__file__).parents[1]
EXAMPLE = ROOT / "examples/qualification/hotpot"


@pytest.fixture
def inputs(tmp_path):
    sample = json.loads((EXAMPLE / "sample.json").read_bytes())
    policy = json.loads((EXAMPLE / "policy.json").read_bytes())
    return tmp_path, sample, policy


def evaluate(inputs):
    root, sample, policy = inputs
    (root / "sample.json").write_bytes(canonical_bytes(sample))
    (root / "policy.json").write_bytes(canonical_bytes(policy))
    return qualify_application(root / "sample.json", root / "policy.json")


def test_real_study_has_two_failed_quality_gates_without_predictions(inputs):
    result = evaluate(inputs)
    assert result["result"] == "failed"
    assert [g["status"] for g in result["gates"]] == ["passed", "passed", "failed", "failed"]
    assert [r["value"] for r in result["quality_evidence"]] == [0.5, 13 / 24]
    assert all(r["offered"] == r["observed_scores"] == 8 for r in result["quality_evidence"])
    assert "performance_model_not_assessed" in result["limitations"]


def test_adapter_preserves_original_scores_and_thresholds():
    sample, policy = convert(ROOT / "docs/v5/feasibility.json", ROOT / "docs/v5/selection.json")
    assert sample == json.loads((EXAMPLE / "sample.json").read_bytes())
    assert policy == json.loads((EXAMPLE / "policy.json").read_bytes())
    assert policy["metrics"][0]["minimum_value"] == policy["metrics"][1]["minimum_value"] == 0.75


def test_sample_pass_is_only_explicit_quality_policy(inputs):
    for row in inputs[1]["rows"]:
        for metric in row["metrics"]:
            metric["value"] = 1
    result = evaluate(inputs)
    assert result["result"] == "passed"
    assert result["claim_scope"] == "application_sample_quality_policy_only"
    assert "scores_not_independently_graded" in result["limitations"]
    assert result["counts"] == {"offered": 8, "completed": 8, "failed": 0, "censored": 0}
    root = inputs[0]
    assert (
        main(
            [
                "qualify-application",
                str(root / "sample.json"),
                "--policy",
                str(root / "policy.json"),
                "--output",
                str(root / "passed"),
            ]
        )
        == 0
    )


def test_failed_rows_cannot_vanish_from_completion_or_quality(inputs):
    row = inputs[1]["rows"][0]
    row["outcome"] = "failed"
    for metric in row["metrics"]:
        metric["value"] = 0
    report = evaluate(inputs)
    assert report["counts"]["offered"] == 8 and report["counts"]["failed"] == 1
    assert report["gates"][1]["observed"] == 7 / 8
    assert report["quality_evidence"][0]["value"] == 3 / 8
    row["metrics"][0]["value"] = 1
    with pytest.raises(ValidationError, match="unsuccessful"):
        evaluate(inputs)


@pytest.mark.parametrize("null_or_missing", ["null", "missing"])
def test_missing_quality_is_unsupported_not_an_eligible_subset(inputs, null_or_missing):
    row = inputs[1]["rows"][0]
    if null_or_missing == "null":
        row["metrics"][0]["value"] = None
    else:
        row["metrics"].pop(0)
    report = evaluate(inputs)
    assert report["gates"][2]["status"] == "unsupported"
    assert report["gates"][2]["observed"] is None
    assert report["quality_evidence"][0]["observed_scores"] == 7
    assert report["quality_evidence"][0]["offered"] == 8


def test_censored_quality_is_not_silently_assigned_a_score(inputs):
    row = inputs[1]["rows"][0]
    row.update(outcome="censored", metrics=[])
    report = evaluate(inputs)
    assert report["counts"]["censored"] == 1
    assert report["gates"][1]["status"] == "failed"
    assert report["gates"][2]["status"] == "unsupported"


def test_mean_scores_cannot_be_mislabeled_as_binary_fractions(inputs):
    inputs[2]["metrics"][1]["statistic"] = "fraction"
    report = evaluate(inputs)
    assert report["gates"][3]["status"] == "unsupported"
    assert report["gates"][3]["reason"] == "fraction_requires_binary_offered_scores"


@pytest.mark.parametrize("duplicate", ["row", "metric", "policy"])
def test_duplicate_identities_do_not_inflate_denominators(inputs, duplicate):
    if duplicate == "row":
        inputs[1]["rows"][1]["id"] = inputs[1]["rows"][0]["id"]
    elif duplicate == "metric":
        inputs[1]["rows"][0]["metrics"].append(copy.deepcopy(inputs[1]["rows"][0]["metrics"][0]))
    else:
        inputs[2]["metrics"].append(copy.deepcopy(inputs[2]["metrics"][0]))
    with pytest.raises(ValidationError, match="duplicate"):
        evaluate(inputs)


@pytest.mark.parametrize("bad", [True, -0.1, 1.1, "1", float("nan")])
def test_schema_rejects_wrong_score_types_and_ranges(inputs, bad):
    root, sample, policy = inputs
    sample["rows"][0]["metrics"][0]["value"] = bad
    (root / "sample.json").write_text(json.dumps(sample))
    (root / "policy.json").write_bytes(canonical_bytes(policy))
    with pytest.raises(ValidationError):
        qualify_application(root / "sample.json", root / "policy.json")


def test_empty_or_insufficient_offered_samples_are_not_accepted(inputs):
    inputs[1]["rows"] = inputs[1]["rows"][:1]
    assert evaluate(inputs)["gates"][0]["status"] == "failed"
    inputs[1]["rows"] = []
    with pytest.raises(ValidationError):
        evaluate(inputs)


def test_unknown_fields_and_non_measured_inputs_are_invalid(inputs):
    inputs[1]["raw_answer"] = "PRIVATE_ANSWER"
    with pytest.raises(ValidationError):
        evaluate(inputs)
    inputs[1].pop("raw_answer")
    inputs[1]["provenance"] = "SIMULATED"
    with pytest.raises(ValidationError):
        evaluate(inputs)


def test_exported_json_schemas_agree_with_native_validation(inputs):
    for schema, data, filename in (
        (SAMPLE_SCHEMA, inputs[1], "application-sample-v1.schema.json"),
        (POLICY_SCHEMA, inputs[2], "application-quality-policy-v1.schema.json"),
    ):
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(data)
        assert schema == json.loads((ROOT / "schemas" / filename).read_bytes())


def test_cli_exit_codes_reports_and_no_overwrite(inputs, capsys):
    report = evaluate(inputs)
    root = inputs[0]
    output = root / "reports"
    command = [
        "qualify-application",
        str(root / "sample.json"),
        "--policy",
        str(root / "policy.json"),
        "--output",
        str(output),
    ]
    assert main(command) == 1
    assert json.loads((output / "report.json").read_bytes()) == report
    assert "Every offered row" in (output / "report.html").read_text()
    before = (output / "report.json").read_bytes()
    assert main(command) == 2 and (output / "report.json").read_bytes() == before
    (root / "sample.json").write_text('{"private":"PRIVATE_PAYLOAD",bad}')
    assert main(command) == 2
    assert "PRIVATE_PAYLOAD" not in capsys.readouterr().err


def test_schema_cli_and_reports_omit_source_paths_and_row_names(inputs, capsys):
    assert main(["quality-schema", "sample"]) == 0
    assert json.loads(capsys.readouterr().out) == SAMPLE_SCHEMA
    inputs[1]["rows"][0]["id"] = "PRIVATE_ROW_IDENTIFIER"
    report = evaluate(inputs)
    rendered = qualification_html(report)
    assert "PRIVATE_ROW_IDENTIFIER" not in rendered and str(inputs[0]) not in rendered
    report["limitations"].append('<script>alert("injected")</script>')
    assert "<script>" not in qualification_html(report)
    assert "&lt;script&gt;" in qualification_html(report)


def test_byte_limits_and_serialization_fail_before_output_creation(inputs, monkeypatch):
    import workload_lab.qualification as module

    evaluate(inputs)
    monkeypatch.setattr(module, "MAX_SAMPLE_BYTES", 1)
    with pytest.raises(ValidationError, match="byte limit"):
        qualify_application(inputs[0] / "sample.json", inputs[0] / "policy.json")
    output = inputs[0] / "not-created"
    with pytest.raises(ValueError):
        write_qualification_report(output, {"invalid": float("nan")})
    assert not output.exists()


def test_report_write_failure_cleans_only_owned_files(inputs, monkeypatch):
    report = evaluate(inputs)
    output = inputs[0] / "failed-report"
    original = Path.open

    def fail_html(path, *args, **kwargs):
        if path.name == "report.html":
            raise OSError("PRIVATE_ERROR_PAYLOAD")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_html)
    with pytest.raises(OSError):
        write_qualification_report(output, report)
    assert not output.exists()


def test_nonregular_inputs_are_rejected_before_open(inputs, monkeypatch):
    evaluate(inputs)
    monkeypatch.setattr(Path, "is_file", lambda _: False)
    with pytest.raises(ValidationError, match="regular file"):
        qualify_application(inputs[0] / "sample.json", inputs[0] / "policy.json")
