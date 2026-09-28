import asyncio
import json
from dataclasses import replace

import pytest

from examples.capture_controlled import capture
from workload_lab import compile_workload, ingest
from workload_lab.calibration import fit_cohort, scenario_for
from workload_lab.ir import ValidationError
from workload_lab.simulation import simulate


def test_narrow_fit_refuses_missing_failed_or_duplicate_sessions(tmp_path):
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(asyncio.run(capture(20, edge_cases=False))))
    workflows = compile_workload(ingest(path))
    cohort = {
        "application_sha256": "a" * 64,
        "hardware": "test",
        "python": "test",
        "pools": {"tool": 1, "stub-model": 2, "database": 1, "retrieval": 2},
        "rate": 2,
        "workload_version": "test",
    }
    model = fit_cohort(workflows, cohort, 20)
    assert model["sessions"] == 20 and all(n["evidence"]["samples"] == 20 for n in model["nodes"])
    assert simulate(scenario_for(model, cohort["pools"], 2, 20, 7))["outcomes"]["completed"] == 20
    with pytest.raises(ValidationError, match="accounting"):
        fit_cohort(workflows[:-1], cohort, 20)
    with pytest.raises(ValidationError, match="duplicate"):
        fit_cohort((workflows[0],) * 20, cohort, 20)
    partial = replace(workflows[0], graph_complete=False)
    with pytest.raises(ValidationError, match="complete observed"):
        fit_cohort((partial, *workflows[1:]), cohort, 20)
    first = workflows[0]
    node = next(n for n in first.nodes if n.role == "work")
    failed_node = replace(
        node, span=replace(node.span, observation=replace(node.span.observation, outcome="failed"))
    )
    failed = replace(first, nodes=tuple(failed_node if n.id == node.id else n for n in first.nodes))
    with pytest.raises(ValidationError, match="failure/censoring"):
        fit_cohort((failed, *workflows[1:]), cohort, 20)
