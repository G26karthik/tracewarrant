import asyncio
import copy
import hashlib
import json
from pathlib import Path

import pytest

from examples import hotpot_workload as app
from workload_lab.artifacts import canonical_bytes
from workload_lab.graph import compile_workload
from workload_lab.ingest import ingest


@pytest.mark.parametrize(
    "answer,gold,exact,f1",
    [
        ("The, Blue! Sky", "blue sky", True, 1),
        ("A cat and a cat", "cat", False, 0.5),
        ("yes", "yes indeed", False, 0),
        ("no reason", "no", False, 0),
        ("", "", True, 0),
        ("UNKNOWN", "1912", False, 0),
        ("New York", "York", False, 2 / 3),
        ("CAFÉ", "café", True, 1),
    ],
)
def test_official_answer_scoring_semantics(answer, gold, exact, f1):
    assert app.answer_scores(answer, gold) == {"exact": exact, "f1": f1}


def sessions():
    return [
        {"task_id": str(i), "error_type": None, "answer_f1": 1.0, "exact_answer_match": True}
        for i in range(8)
    ]


def test_failures_remain_in_offered_quality_denominator():
    rows = sessions()
    rows[0].update(error_type="application_request_failed", answer_f1=0, exact_answer_match=False)
    gate = app.quality_gate(rows)
    assert gate["offered"] == 8 and gate["completed"] == 7
    assert gate["mean_answer_f1"] == 0.875
    assert gate["passed"] is False
    rows[0]["answer_f1"] = 1
    with pytest.raises(ValueError, match="invalid offered-task"):
        app.quality_gate(rows)


def test_quality_gate_requires_both_exact_and_f1_floor():
    rows = sessions()
    for row in rows[:3]:
        row.update(answer_f1=0.9, exact_answer_match=False)
    assert app.quality_gate(rows)["passed"] is False
    rows = sessions()
    for row in rows[:2]:
        row.update(answer_f1=0, exact_answer_match=False)
    assert app.quality_gate(rows)["passed"] is True  # Exactly at both predeclared floors.


@pytest.mark.parametrize("bad_score", [float("nan"), float("inf"), -1, True])
def test_gate_rejects_invalid_scores(bad_score):
    rows = sessions()
    rows[0]["answer_f1"] = bad_score
    with pytest.raises(ValueError):
        app.quality_gate(rows)


def test_gate_refuses_missing_or_duplicate_tasks():
    with pytest.raises(ValueError):
        app.quality_gate(sessions()[:7])
    rows = sessions()
    rows[0]["task_id"] = rows[1]["task_id"]
    with pytest.raises(ValueError):
        app.quality_gate(rows)


def test_private_answer_output_must_be_ignored_before_any_model_request(tmp_path):
    with pytest.raises(ValueError, match="Git-ignored"):
        asyncio.run(
            app.run(
                tmp_path,
                tmp_path / "selection.json",
                tmp_path / "raw.json",
                tmp_path / "private.json",
            )
        )


def test_bounded_local_input_reader(tmp_path):
    path = tmp_path / "oversized.json"
    path.write_bytes(b"x" * 11)
    with pytest.raises(ValueError, match="byte bound"):
        app.bounded_bytes(path, 10)


def task_rows():
    return [
        {
            "id": f"{i:024x}",
            "question": "PRIVATE_QUESTION",
            "answer": "PRIVATE_GOLD",
            "context": {
                "title": [f"title{j}" for j in range(10)],
                "sentences": [["PRIVATE_DOCUMENT"] for _ in range(10)],
            },
        }
        for i in range(24)
    ]


def test_fixed_samples_are_bound_by_content_and_row_order(tmp_path):
    rows = task_rows()
    task_file = tmp_path / "tasks.json"
    task_file.write_bytes(canonical_bytes(rows))
    selection = {
        "dataset_revision": app.DATASET_REVISION,
        "parquet_sha256": app.PARQUET_SHA,
        "tasks_sha256": hashlib.sha256(task_file.read_bytes()).hexdigest(),
        "samples": {
            phase: [
                {"row": i, "task_id": rows[i]["id"], "task_sha256": app.digest(rows[i])}
                for i in range(offset, offset + 8)
            ]
            for phase, offset in (("feasibility", 0), ("calibration", 8), ("holdout", 16))
        },
    }
    path = tmp_path / "selection.json"
    path.write_bytes(canonical_bytes(selection))
    assert app.load_tasks(tmp_path, path) == rows[:8]
    selection["samples"]["holdout"].reverse()
    path.write_bytes(canonical_bytes(selection))
    with pytest.raises(ValueError, match="sample/order"):
        app.load_tasks(tmp_path, path)
    task_file.write_text("[]")
    with pytest.raises(ValueError, match="byte/digest"):
        app.load_tasks(tmp_path, path)


def test_bad_candidate_rows_are_refused_without_replacement():
    rows = task_rows()
    rows[3]["context"]["sentences"].pop()
    with pytest.raises(ValueError, match="ten complete"):
        app.validate_rows(rows)
    rows = task_rows()
    rows[4]["id"] = rows[3]["id"]
    with pytest.raises(ValueError, match="repeated"):
        app.validate_rows(rows)


def test_application_database_and_pack_do_not_accept_gold():
    context = copy.deepcopy(task_rows()[0]["context"])
    context["title"][0] = "'); DROP TABLE evidence;--"
    docs = app.read_evidence(context)
    assert len(docs) == 10
    evidence, packing = app.pack_evidence(docs)
    assert "PRIVATE_GOLD" not in evidence
    assert packing["candidate_count"] == 10
    docs[0] = ("title", "a" * (app.EVIDENCE_LIMIT + 1))
    evidence, packing = app.pack_evidence(docs)
    assert len(evidence) == app.EVIDENCE_LIMIT and packing["truncated"] is True


def test_collector_measures_real_stages_and_omits_content(monkeypatch, tmp_path):
    def infer(question, evidence):
        assert "PRIVATE_GOLD" not in evidence
        return "PRIVATE_ANSWER", {"prompt_eval_count": 1}

    monkeypatch.setattr(app, "infer", infer)
    cell, private = asyncio.run(app.collect(task_rows()[:8]))
    raw = json.dumps(cell)
    for payload in ("PRIVATE_QUESTION", "PRIVATE_GOLD", "PRIVATE_DOCUMENT", "PRIVATE_ANSWER"):
        assert payload not in raw
    assert private[0]["answer"] == "PRIVATE_ANSWER"
    assert app.quality_gate(cell["sessions"])["passed"] is False
    for row in cell["sessions"]:
        assert row["latency_ns"] > 0 and row["error_type"] is None
        assert {s["stage"] for s in row["stages"]} == {"database", "context", "inference-client"}
        path = tmp_path / "trace.json"
        path.write_bytes(canonical_bytes(row["trace"]))
        assert compile_workload(ingest(path))[0].graph_complete


def test_failed_requests_are_recorded_without_exception_payload(monkeypatch):
    def fail(question, evidence):
        raise RuntimeError("PRIVATE_EXCEPTION_PAYLOAD")

    monkeypatch.setattr(app, "infer", fail)
    cell, _ = asyncio.run(app.collect(task_rows()[:8]))
    assert "PRIVATE_EXCEPTION_PAYLOAD" not in json.dumps(cell)
    assert app.quality_gate(cell["sessions"])["completed"] == 0
    assert all(s["answer_f1"] == 0 and not s["exact_answer_match"] for s in cell["sessions"])


def test_collector_uses_fixed_loopback_model_and_structured_prompt(monkeypatch):
    captured = []

    def request(route, body):
        captured.append((route, body))
        return {"done": True, "message": {"content": '{"answer":"yes"}'}}

    monkeypatch.setattr(app, "local_request", request)
    assert app.infer("question", "evidence")[0] == "yes"
    route, body = captured[0]
    assert route == "chat" and body["model"] == "llama3.1:8b"
    assert body["options"] == app.OPTIONS
    assert body["messages"][0]["content"] == app.SYSTEM
    monkeypatch.setattr(
        app, "local_request", lambda *a: {"done": False, "message": {"content": '{"answer":"yes"}'}}
    )
    with pytest.raises(ValueError, match="incomplete"):
        app.infer("q", "e")


def test_core_does_not_import_application_or_optional_dataset_dependency():
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import workload_lab.jobs; "
            "assert 'pyarrow' not in sys.modules; "
            "assert 'examples.hotpot_workload' not in sys.modules",
        ],
        cwd=Path(__file__).parents[1],
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
