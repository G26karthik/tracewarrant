import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from workload_lab.artifacts import canonical_bytes
from workload_lab.cli import main
from workload_lab.ir import ValidationError
from workload_lab.qualification import (
    FREEZE_SCHEMA,
    PLAN_SCHEMA,
    freeze_application_quality,
    qualification_html,
    qualify_application,
)

ROOT = Path(__file__).parents[1]


@pytest.fixture
def frozen(tmp_path):
    sample = json.loads((ROOT / "examples/qualification/hotpot/sample.json").read_bytes())
    policy = json.loads((ROOT / "examples/qualification/hotpot/policy.json").read_bytes())
    plan = {
        "schema_version": "1.0",
        "artifact_type": "application_quality_plan",
        "workload_id": sample["workload_id"],
        "sample_id": sample["sample_id"],
        "row_ids": [r["id"] for r in sample["rows"]],
    }
    for name, data in (("sample", sample), ("policy", policy), ("plan", plan)):
        (tmp_path / f"{name}.json").write_bytes(canonical_bytes(data))
    receipt = freeze_application_quality(tmp_path / "plan.json", tmp_path / "policy.json")
    (tmp_path / "freeze.json").write_bytes(canonical_bytes(receipt))
    return tmp_path


def evaluate(root):
    return qualify_application(
        root / "sample.json",
        root / "policy.json",
        plan_path=root / "plan.json",
        freeze_path=root / "freeze.json",
    )


def edit(root, name, change):
    path = root / f"{name}.json"
    data = json.loads(path.read_bytes())
    change(data)
    path.write_bytes(canonical_bytes(data))


def test_exact_binding_keeps_actual_failed_scores_and_unbound_shape(frozen):
    unbound = qualify_application(frozen / "sample.json", frozen / "policy.json")
    bound = evaluate(frozen)
    binding = bound.pop("binding")
    assert bound == unbound
    assert binding["status"] == "verified" and binding["expected_offered"] == 8
    assert binding["chronology"] == "not_authenticated"
    assert bound["result"] == "failed" and [g["observed"] for g in bound["gates"]][2:] == [
        0.5,
        13 / 24,
    ]
    assert "policy_chronology_not_proven" in bound["limitations"]
    assert "do not prove registration" in qualification_html(evaluate(frozen))


@pytest.mark.parametrize("role", ["plan", "policy"])
def test_byte_changes_are_refused_even_if_json_is_semantically_identical(frozen, role):
    path = frozen / f"{role}.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValidationError, match="exact plan/policy"):
        evaluate(frozen)


@pytest.mark.parametrize("population", ["missing", "extra", "replaced", "duplicate"])
def test_missing_or_substituted_tasks_cannot_hide_behind_sample_count(frozen, population):
    def alter(sample):
        if population == "missing":
            sample["rows"].pop()
        elif population == "extra":
            row = copy.deepcopy(sample["rows"][0])
            row["id"] = "unexpected-task"
            sample["rows"].append(row)
        elif population == "replaced":
            sample["rows"][0]["id"] = "unexpected-task"
        else:
            sample["rows"][0]["id"] = sample["rows"][1]["id"]

    edit(frozen, "sample", alter)
    with pytest.raises(ValidationError):
        evaluate(frozen)


@pytest.mark.parametrize("field", ["sample_id", "workload_id"])
def test_identity_binding_refuses_cross_application_samples(frozen, field):
    edit(frozen, "sample", lambda d: d.update({field: "different"}))
    with pytest.raises(ValidationError, match="sample identity"):
        evaluate(frozen)


def test_observed_row_order_can_change_without_changing_declared_membership(frozen):
    before = evaluate(frozen)
    edit(frozen, "sample", lambda d: d["rows"].reverse())
    after = evaluate(frozen)
    assert after["binding"] == before["binding"] and after["gates"] == before["gates"]
    assert after["sample_sha256"] != before["sample_sha256"]


def test_plan_rejects_duplicates_and_impossible_sample_floor(frozen):
    edit(frozen, "plan", lambda d: d["row_ids"].append(d["row_ids"][0]))
    with pytest.raises(ValidationError, match="duplicate planned"):
        freeze_application_quality(frozen / "plan.json", frozen / "policy.json")
    edit(frozen, "plan", lambda d: d["row_ids"].pop())
    edit(frozen, "policy", lambda d: d.update(minimum_samples=9))
    with pytest.raises(ValidationError, match="more samples"):
        freeze_application_quality(frozen / "plan.json", frozen / "policy.json")


@pytest.mark.parametrize("missing", ["plan", "freeze"])
def test_half_binding_is_refused(frozen, missing):
    arguments = {"plan_path": frozen / "plan.json", "freeze_path": frozen / "freeze.json"}
    arguments[missing + "_path"] = None
    with pytest.raises(ValidationError, match="both plan and freeze"):
        qualify_application(frozen / "sample.json", frozen / "policy.json", **arguments)


def test_schema_and_actual_calendar_validation(frozen):
    for name, schema, filename in (
        ("plan", PLAN_SCHEMA, "application-quality-plan-v1.schema.json"),
        ("freeze", FREEZE_SCHEMA, "application-quality-freeze-v1.schema.json"),
    ):
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads((frozen / f"{name}.json").read_bytes()))
        assert schema == json.loads((ROOT / "schemas" / filename).read_bytes())
    edit(frozen, "freeze", lambda d: d.update(created_at="2026-02-30T12:00:00.000000Z"))
    with pytest.raises(ValidationError, match="UTC timestamp"):
        evaluate(frozen)


def test_cli_freeze_no_overwrite_and_invalid_binding_no_reports(frozen, capsys):
    fresh = frozen / "new-freeze.json"
    freeze = [
        "freeze-quality",
        "--plan",
        str(frozen / "plan.json"),
        "--policy",
        str(frozen / "policy.json"),
        "--output",
        str(fresh),
    ]
    assert main(freeze) == 0
    original = fresh.read_bytes()
    assert main(freeze) == 2 and fresh.read_bytes() == original
    args = [
        "qualify-application",
        str(frozen / "sample.json"),
        "--policy",
        str(frozen / "policy.json"),
        "--plan",
        str(frozen / "plan.json"),
        "--freeze",
        str(fresh),
        "--output",
        str(frozen / "reports"),
    ]
    assert main(args) == 1
    edit(frozen, "policy", lambda d: d.update(minimum_completion_fraction=0.5))
    args[-1] = str(frozen / "must-not-exist")
    assert main(args) == 2 and not (frozen / "must-not-exist").exists()
    assert str(frozen) not in capsys.readouterr().err


def test_binding_does_not_authenticate_a_rewritten_receipt(frozen):
    # A caller can create a new receipt after seeing data. Binding is integrity,
    # not an authenticated chronology or an assurance that a design was honest.
    edit(frozen, "policy", lambda d: d["metrics"][0].update(minimum_value=0.5))
    receipt = freeze_application_quality(frozen / "plan.json", frozen / "policy.json")
    (frozen / "freeze.json").write_bytes(canonical_bytes(receipt))
    report = evaluate(frozen)
    assert report["binding"]["chronology"] == "not_authenticated"
    assert report["gates"][2]["status"] == "passed" and report["gates"][3]["status"] == "failed"
