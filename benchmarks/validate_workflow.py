"""Offline V4 workflow qualification over unchanged FRAMES evidence."""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.artifacts import canonical_bytes, write_new
from workload_lab.jobs import bundle_job, run_job, verify_bundle
from workload_lab.qualification import qualify_application

ROOT = Path(__file__).parents[1]


def qualify():
    quality_root = ROOT / "examples/qualification/hotpot"
    quality = qualify_application(quality_root / "sample.json", quality_root / "policy.json")
    assert quality["result"] == "failed"
    assert [g["status"] for g in quality["gates"]] == ["passed", "passed", "failed", "failed"]
    example = ROOT / "examples/validation/frames"
    strict = run_job(example / "job.json")
    performance = run_job(example / "performance-job.json")
    missing_quality = run_job(example / "missing-quality-job.json")
    assert strict["result"] == "failed"
    assert performance["result"] == "passed"
    assert performance["claim_scope"] == "performance_only_policy"
    assert strict["evaluation"]["models"] == performance["evaluation"]["models"]
    assert (
        canonical_bytes(performance["evaluation"])
        == (ROOT / "docs/v3/frames-evaluation/validation.json").read_bytes()
    )
    statuses = {g["id"]: g["status"] for g in strict["gates"]}
    assert statuses["measured_quality"] == "failed"
    assert all(row["value"] == 0 for row in strict["quality_rows"])
    assert (
        next(g for g in missing_quality["gates"] if g["id"] == "measured_quality")["status"]
        == "unsupported"
    )
    assert statuses["calibration_envelope"] == "failed"
    assert statuses["added_decision_value"] != "passed"
    with tempfile.TemporaryDirectory(prefix="tracewarrant-workflow-qualification-") as folder:
        path = Path(folder) / "bundle"
        bundled = bundle_job(example / "performance-job.json", path)
        replay = verify_bundle(path)
        assert replay["gates"] == bundled["gates"]
        assert replay["evaluation"] == bundled["evaluation"]
        for original, copy in (
            ("freeze.json", "freeze-000.json"),
            ("simpy.json", "predictions-000.json"),
        ):
            assert (example / original).read_bytes() == (path / copy).read_bytes()
        checksums = hashlib.sha256((path / "SHA256SUMS").read_bytes()).hexdigest()
    return {
        "artifact_type": "offline_workflow_qualification",
        "metadata": metadata(__file__, {"network": False, "model_execution": False}, 0),
        "performance_policy": performance["result"],
        "strict_policy": strict["result"],
        "strict_gate_statuses": statuses,
        "measured_exact_quality": 0,
        "missing_quality_refused": True,
        "frozen_evaluation_byte_exact": True,
        "portable_replay_verified": True,
        "application_quality_qualification": {
            "result": quality["result"],
            "counts": quality["counts"],
            "gates": quality["gates"],
            "sample_sha256": quality["sample_sha256"],
            "policy_sha256": quality["policy_sha256"],
        },
        "portable_checksums_sha256": checksums,
        "note": "Retrospective workflow qualification; no new task quality or added-value result.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = qualify()
    write_new(args.output, result)
    print(
        json.dumps(
            {
                "performance_policy": result["performance_policy"],
                "strict_policy": result["strict_policy"],
                "portable_replay_verified": True,
            }
        )
    )
