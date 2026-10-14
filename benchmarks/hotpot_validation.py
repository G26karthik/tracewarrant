"""Offline structural replay and optional official-scorer parity for V5 evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import statistics
import string
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from examples.hotpot_workload import (
    DATASET_REVISION,
    PARQUET_SHA,
    ROOT,
    SCORER_SHA,
    answer_scores,
    bounded_bytes,
    quality_gate,
)
from workload_lab.artifacts import canonical_bytes, write_new
from workload_lab.graph import compile_workload
from workload_lab.ingest import ingest


def official_functions(path):
    raw = bounded_bytes(path, 100_000)
    if hashlib.sha256(raw).hexdigest() != SCORER_SHA:
        raise ValueError("official evaluator digest mismatch")
    tree = ast.parse(raw)
    names = {"normalize_answer", "f1_score", "exact_match_score"}
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in functions} != names:
        raise ValueError("official evaluator functions missing")
    # Only the exact hash-pinned three scorer functions execute. No module I/O,
    # ujson dependency, CLI body, network call or arbitrary user code is loaded.
    namespace = {"re": re, "string": string, "Counter": Counter}
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, "pinned_hotpot_scorer", "exec"), namespace)
    return namespace


def check_parity(private, official_path, sessions=None):
    reference = official_functions(official_path)
    if sessions is not None:
        if len(private) != len(sessions) or [p["task_id"] for p in private] != [
            s["task_id"] for s in sessions
        ]:
            raise ValueError("private answer population/order mismatch")
    for index, pair in enumerate(private):
        answer = pair["answer"] or ""
        expected_f1 = reference["f1_score"](answer, pair["gold"])[0]
        expected_exact = reference["exact_match_score"](answer, pair["gold"])
        score = answer_scores(answer, pair["gold"])
        if (
            not math.isclose(score["f1"], expected_f1, abs_tol=1e-14)
            or score["exact"] != expected_exact
        ):
            raise ValueError("score differs from official evaluator")
        if sessions is not None:
            saved = sessions[index]
            answer_sha = (
                hashlib.sha256(pair["answer"].encode()).hexdigest()
                if pair["answer"] is not None
                else None
            )
            if saved["answer_sha256"] != answer_sha:
                raise ValueError("private answer digest mismatch")
            observed = score if saved["error_type"] is None else {"f1": 0.0, "exact": False}
            if saved["exact_answer_match"] != observed["exact"] or not math.isclose(
                saved["answer_f1"], observed["f1"], abs_tol=1e-14
            ):
                raise ValueError("recorded score mismatch")
    return {"pairs_checked": len(private), "official_scorer_sha256": SCORER_SHA, "parity": True}


def source_bytes(commit, name):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("invalid measured source commit")
    return subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)


def audit(raw_path, selection_path):
    raw_bytes = bounded_bytes(raw_path, 2_000_000)
    selection_bytes = bounded_bytes(selection_path, 100_000)
    data, selection = json.loads(raw_bytes), json.loads(selection_bytes)
    if (
        data["phase"] != "feasibility"
        or data["artifact_type"] != "hotpot_raw_observations"
        or data["dataset_revision"] != DATASET_REVISION
        or data["dataset_sha256"] != PARQUET_SHA
        or data["selection_sha256"] != hashlib.sha256(selection_bytes).hexdigest()
        or data["metadata"]["git_dirty"] is not False
        or len(data["cells"]) != 1
    ):
        raise ValueError("raw evidence identity mismatch")
    for name, key in (
        ("examples/hotpot_workload.py", "application_sha256"),
        ("docs/v5/preregistration.md", "preregistration_sha256"),
    ):
        if (
            hashlib.sha256(source_bytes(data["metadata"]["git_commit"], name)).hexdigest()
            != data[key]
        ):
            raise ValueError("measured committed source digest mismatch")
    names = {
        "examples/capture_controlled.py",
        "examples/frames_workload.py",
        "benchmarks/provenance.py",
        "benchmarks/analysis_benchmark.py",
    }
    if set(data["collector_dependencies"]) != names:
        raise ValueError("missing collector dependency provenance")
    for name in names:
        actual = hashlib.sha256(source_bytes(data["metadata"]["git_commit"], name)).hexdigest()
        if actual != data["collector_dependencies"][name]:
            raise ValueError("collector dependency source mismatch")
    cell = data["cells"][0]
    if cell["configuration"] != "BASE":
        raise ValueError("unexpected feasibility configuration")
    sessions = cell["sessions"]
    if [(s["task_id"], s["task_sha256"]) for s in sessions] != [
        (s["task_id"], s["task_sha256"]) for s in selection["samples"]["feasibility"]
    ]:
        raise ValueError("observed population does not match fixed selection")
    gate = quality_gate(sessions)
    disposition = "qualified_for_calibration" if gate["passed"] else "stop_quality_gate_failed"
    if data["quality_gate"] != gate or data["disposition"] != disposition:
        raise ValueError("recorded quality decision mismatch")
    complete_graphs = 0
    with tempfile.TemporaryDirectory(prefix="hotpot-audit-") as folder:
        trace = Path(folder) / "trace.json"
        for session in sessions:
            if not (cell["start_ns"] <= session["start_ns"] <= session["end_ns"] <= cell["end_ns"]):
                raise ValueError("session clock lies outside observed cell")
            if session["latency_ns"] != session["end_ns"] - session["start_ns"]:
                raise ValueError("session latency mismatch")
            if any(s["queue_ns"] < 0 or s["occupied_ns"] < 0 for s in session["stages"]):
                raise ValueError("negative owned clock measurement")
            trace.write_bytes(canonical_bytes(session["trace"]))
            workflows = compile_workload(ingest(trace))
            if len(workflows) != 1 or not workflows[0].graph_complete:
                raise ValueError("recorded dependency graph is incomplete")
            complete_graphs += 1
    latencies = [s["latency_ns"] / 1e9 for s in sessions if s["error_type"] is None]
    window = cell["end_ns"] - cell["start_ns"]
    return {
        "artifact_type": "hotpot_offline_audit",
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "selection_sha256": hashlib.sha256(selection_bytes).hexdigest(),
        "measured_source_commit": data["metadata"]["git_commit"],
        "quality_gate": gate,
        "disposition": disposition,
        "complete_graphs": complete_graphs,
        "observed_mean_completed_latency_seconds": statistics.mean(latencies)
        if latencies
        else None,
        "owned_pool_occupied_fraction": {
            pool: sum(
                s["occupied_ns"] for row in sessions for s in row["stages"] if s["pool"] == pool
            )
            / window
            for pool in ("database", "context", "inference-client")
        },
        "limits": [
            "scores_not_rescored_without_private_answers",
            "no_heldout_predictions",
            "no_semantic_quality_claim",
            "no_external_adoption",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--private", type=Path)
    parser.add_argument("--official-scorer", type=Path)
    args = parser.parse_args()
    if bool(args.private) != bool(args.official_scorer):
        parser.error("supply both private answers and official scorer, or neither")
    result = audit(args.raw, args.selection)
    if args.private:
        result["scorer_parity"] = check_parity(
            json.loads(args.private.read_bytes()),
            args.official_scorer,
            json.loads(args.raw.read_bytes())["cells"][0]["sessions"],
        )
    write_new(args.output, result)
    print(json.dumps(result))
