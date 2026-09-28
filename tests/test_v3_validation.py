import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from workload_lab.artifact_schema import SCHEMA
from workload_lab.artifacts import (
    _matches,
    freeze_predictions,
    load_artifact,
    sha256,
    validate_artifact,
    write_new,
)
from workload_lab.cli import main
from workload_lab.ir import ValidationError
from workload_lab.validation import evaluate, metric_error


def metric(value, provenance="SIMULATED"):
    return {
        "id": "latency",
        "unit": "ms",
        "statistic": "p95",
        "population": "completed",
        "value": value,
        "provenance": provenance,
        "sample_count": 100,
        "interval": None,
    }


def scenario(name, value, provenance="SIMULATED"):
    return {
        "id": name,
        "comparison_group": "same-load",
        "configuration": {"workers": 1 if name == "a" else 2},
        "environment": {"rate": 10},
        "metrics": [metric(value, provenance)],
        "extrapolations": [],
        "bottleneck": {"resources": [], "provenance": "UNKNOWN", "method": "not_identified"},
    }


def prediction(role="model"):
    return {
        "schema_version": "1.0",
        "artifact_type": "prediction",
        "workload_id": "external-task",
        "model": {"id": role, "version": "1", "role": role, "method": "test_fixture"},
        "lineage": [{"sha256": "a" * 64, "role": "calibration"}],
        "calibration_envelope": {"rate": {"minimum": 1, "maximum": 10}},
        "assumptions": ["stationary"],
        "unsupported_dimensions": ["quality"],
        "scenarios": [scenario("a", 100), scenario("b", 50)],
        "rankings": [],
    }


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    monkeypatch.setattr("workload_lab.artifacts.timestamp", lambda: "2026-01-01T00:00:00.000000Z")
    protocol = {
        "schema_version": "1.0",
        "artifact_type": "protocol",
        "workload_id": "external-task",
        "experiment_id": "test",
        "scenario_ids": ["a", "b"],
        "primary_metric": "latency",
        "direction": "minimize",
        "material_relative_difference": 0.1,
        "minimum_samples": 20,
        "require_baseline": True,
        "assumptions": [],
        "unsupported_dimensions": [],
    }
    pred, base = prediction(), prediction("baseline")
    for s in base["scenarios"]:
        s["metrics"][0].update(value=None, provenance="UNKNOWN")
    base["rankings"] = [
        {
            "comparison_group": "same-load",
            "metric_id": "latency",
            "order": [["a"], ["b"]],
            "provenance": "ESTIMATED",
        }
    ]
    pp, mp, bp, fp, op = [
        tmp_path / n
        for n in ("protocol.json", "model.json", "baseline.json", "freeze.json", "actual.json")
    ]
    for path, data in ((pp, protocol), (mp, pred), (bp, base)):
        write_new(path, data)
    write_new(fp, freeze_predictions(pp, [mp, bp]))
    observed = {
        "schema_version": "1.0",
        "artifact_type": "measurement",
        "workload_id": "external-task",
        "run_id": "r0",
        "lineage": [{"sha256": "b" * 64, "role": "raw"}],
        "freeze_sha256": sha256(fp.read_bytes()),
        "started_at": "2026-01-01T00:00:01.000000Z",
        "finished_at": "2026-01-01T00:01:00.000000Z",
        "scenarios": [scenario("a", 100, "MEASURED"), scenario("b", 120, "MEASURED")],
        "counts": {"offered": 200, "completed": 200, "failed": 0, "censored": 0},
        "limitations": [],
    }
    write_new(op, observed)
    return pp, fp, [mp, bp], [op]


def test_honest_baseline_win(bundle):
    result = evaluate(*bundle)
    assert result["baseline_comparisons"][0]["result"] == "baseline_choice_better"
    assert result["models"][0]["ranking_accuracy"] == 0
    assert result["models"][1]["ranking_accuracy"] == 1
    assert result["models"][1]["metric_errors"][0]["status"] == "unsupported"
    assert result["models"][0]["metric_errors"][1]["signed_error"] == -70


def test_schema_interoperability(bundle):
    Draft202012Validator.check_schema(SCHEMA)
    exported = Path(__file__).parents[1] / "schemas/validation-artifact-v1.schema.json"
    assert json.loads(exported.read_text()) == SCHEMA
    for path in [bundle[0], bundle[1], *bundle[2], *bundle[3]]:
        data, _ = load_artifact(path)
        Draft202012Validator(SCHEMA).validate(data)
        assert _matches(data, SCHEMA)


@pytest.mark.parametrize(
    "value", [True, -1, float("nan"), float("inf"), 10**1000, "PRIVATE_secret"]
)
def test_untrusted_numeric_values_rejected(value):
    data = prediction()
    data["scenarios"][0]["metrics"][0]["value"] = value
    with pytest.raises(ValidationError, match="schema"):
        validate_artifact(data)


@pytest.mark.parametrize(
    "change",
    [
        "unknown",
        "measured_prediction",
        "duplicate_scenario",
        "interval",
        "duplicate_rank",
        "extra_field",
    ],
)
def test_semantic_refusals(change):
    data = prediction()
    m = data["scenarios"][0]["metrics"][0]
    if change == "unknown":
        m["provenance"] = "UNKNOWN"
    elif change == "measured_prediction":
        m["provenance"] = "MEASURED"
    elif change == "duplicate_scenario":
        data["scenarios"][1]["id"] = "a"
    elif change == "interval":
        m["interval"] = {
            "lower": 1,
            "upper": 2,
            "kind": "prediction",
            "level": 0.95,
            "method": "bootstrap",
        }
    elif change == "duplicate_rank":
        data["rankings"] = [
            {
                "comparison_group": "same-load",
                "metric_id": "latency",
                "order": [["a", "a"]],
                "provenance": "ESTIMATED",
            }
        ]
    else:
        data["private_payload"] = "PRIVATE_secret"
    with pytest.raises(ValidationError) as error:
        validate_artifact(data)
    assert "PRIVATE" not in str(error.value)


@pytest.mark.parametrize(
    "change", ["tamper", "pre_freeze", "link", "configuration", "counts", "estimated"]
)
def test_evaluation_refuses_bad_reference(bundle, change):
    pp, fp, preds, actuals = bundle
    if change == "tamper":
        preds[0].write_bytes(preds[0].read_bytes() + b" ")
    else:
        data = json.loads(actuals[0].read_text())
        if change == "pre_freeze":
            data["started_at"] = "2025-01-01T00:00:00.000000Z"
        elif change == "link":
            data["freeze_sha256"] = "0" * 64
        elif change == "configuration":
            data["scenarios"][0]["configuration"]["workers"] = 99
        elif change == "counts":
            data["counts"]["offered"] = 201
        else:
            data["scenarios"][0]["metrics"][0]["provenance"] = "ESTIMATED"
        actuals[0].write_text(json.dumps(data))
    if change == "estimated":
        result = evaluate(pp, fp, preds, actuals)
        assert result["models"][0]["metric_errors"][0]["reason"] == "reference_is_not_measured"
        assert result["baseline_comparisons"][0]["result"] == "insufficient_evidence"
    else:
        with pytest.raises(ValidationError):
            evaluate(pp, fp, preds, actuals)


def test_all_provenance_and_zero_denominator():
    for category in ("CALIBRATED", "INTERPOLATED", "EXTRAPOLATED", "SIMULATED", "ESTIMATED"):
        row = metric_error(metric(20, category), metric(0, "MEASURED"), 20)
        assert row["predicted_provenance"] == category
        assert row["signed_error"] == row["absolute_error"] == 20
        assert row["relative_error"] is None
        assert row["relative_error_reason"] == "zero_observed_denominator"


def test_interval_and_semantics():
    pred = metric(100)
    pred["interval"] = {
        "lower": 90,
        "upper": 110,
        "level": 0.95,
        "kind": "prediction",
        "method": "empirical",
    }
    assert metric_error(pred, metric(110, "MEASURED"), 20)["interval_contains_observed_point"]
    assert not metric_error(pred, metric(111, "MEASURED"), 20)["interval_contains_observed_point"]
    actual = metric(100, "MEASURED")
    actual["unit"] = "s"
    assert metric_error(pred, actual, 20)["reason"] == "metric_semantics_mismatch"


def test_inconsistent_replications_and_envelope(bundle):
    pp, fp, preds, actuals = bundle
    actual = json.loads(actuals[0].read_text())
    actual["run_id"] = "r1"
    actual["scenarios"][1]["metrics"][0]["value"] = 50
    actual["scenarios"][0]["environment"]["rate"] = 11
    second = actuals[0].parent / "second.json"
    write_new(second, actual)
    result = evaluate(pp, fp, preds, [*actuals, second])
    model = result["models"][0]
    assert model["material_pair_count"] == 0
    assert model["ranking_accuracy"] is None
    assert model["envelope_checks"][2]["undeclared_extrapolations"] == ["rate"]


def test_cli_and_no_simulator_dependency(bundle, capsys):
    pp, fp, preds, actuals = bundle
    args = ["evaluate", "--protocol", str(pp), "--freeze", str(fp)]
    for path in preds:
        args.extend(["--prediction", str(path)])
    args.extend(["--measurement", str(actuals[0])])
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["baseline_comparisons"]
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import workload_lab.validation; import workload_lab.cli; "
            "assert 'workload_lab.simulation' not in sys.modules",
        ],
        check=True,
    )
    with pytest.raises(FileExistsError):
        write_new(fp, {})


def test_json_limits_and_duplicate_keys(tmp_path):
    path = tmp_path / "bad.json"
    for raw in ('{"a":1,"a":2}', '{"a":' + "[" * 65 + "0" + "]" * 65 + "}"):
        path.write_text(raw)
        with pytest.raises(ValidationError):
            load_artifact(path)


def test_frozen_history_preserved():
    root = Path(__file__).parents[1]
    manifest = json.loads((root / "docs/v3/preservation.json").read_text())
    for path, digest in manifest["files"].items():
        assert sha256((root / path).read_bytes()) == digest, path


def test_missing_envelope_is_unknown_and_bottleneck_supported(bundle):
    pp, fp, preds, actuals = bundle
    observed = json.loads(actuals[0].read_text())
    observed["scenarios"][0]["environment"] = {}
    actuals[0].write_text(json.dumps(observed))
    report = evaluate(pp, fp, preds, actuals)
    check = report["models"][0]["envelope_checks"][0]
    assert check["status"] == "UNKNOWN"
    assert check["missing_dimensions"] == ["rate"]
    assert report["models"][0]["bottleneck_agreement"][0]["agreement"] is None


def test_maximize_rankings(bundle):
    pp, fp, preds, actuals = bundle
    protocol = json.loads(pp.read_text())
    protocol["direction"] = "maximize"
    pp.write_text(json.dumps(protocol))
    fp.write_text(json.dumps(freeze_predictions(pp, preds)))
    observed = json.loads(actuals[0].read_text())
    observed["freeze_sha256"] = sha256(fp.read_bytes())
    actuals[0].write_text(json.dumps(observed))
    report = evaluate(pp, fp, preds, actuals)
    assert report["models"][0]["ranking_accuracy"] == 0
    assert report["models"][0]["decisions"][0]["choices"] == ["a"]


def test_comparison_budget_before_loading(bundle):
    with pytest.raises(ValidationError, match="bundle size"):
        evaluate(bundle[0], bundle[1], bundle[2] * 17, bundle[3])
