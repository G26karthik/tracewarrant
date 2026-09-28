"""Reproduce V3 preservation, conformance and evaluation without network/model access."""

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from benchmarks.provenance import metadata, sha
from examples.adapt_frames_trace import adapt
from workload_lab.artifacts import canonical_bytes, write_new
from workload_lab.conformance import inspect_observations
from workload_lab.graph import compile_workload
from workload_lab.ingest import ingest
from workload_lab.validation import evaluate

ROOT = Path(__file__).parents[1]


def audit():
    preservation = json.loads((ROOT / "docs/v3/preservation.json").read_text())
    byte_exact = 0
    for name, digest in preservation["files"].items():
        current = sha(ROOT / name)
        assert current in {digest, preservation["git_blob_sha256"][name]}, "preserved file changed"
        byte_exact += current == digest
    resolved = subprocess.check_output(
        ["git", "rev-parse", "research-pilot-1^{}"], cwd=ROOT, text=True
    ).strip()
    assert resolved == preservation["baseline_commit"]
    reports = {}
    for label, path in (
        ("controlled", "examples/traces/controlled-v1.otlp.json"),
        ("pydantic-ai", "examples/traces/pydantic-ai-2.51.0.otlp.json"),
        ("frames-original", "examples/v3/frames-heldout-base.otlp.json"),
    ):
        reports[label] = inspect_observations(ingest(ROOT / path))
    total = complete = originally_complete = 0
    with tempfile.TemporaryDirectory(prefix="workload-v3-audit-") as folder:
        path = Path(folder) / "trace.json"
        for phase in ("feasibility", "calibration", "holdout"):
            raw = json.loads((ROOT / f"docs/v3/frames-{phase}.json").read_text())
            for cell in raw["cells"]:
                for session in cell["sessions"]:
                    assert session["error_type"] is None
                    path.write_bytes(canonical_bytes(session["trace"]))
                    originally_complete += compile_workload(ingest(path))[0].graph_complete
                    mapped, renamed = adapt(session["trace"])
                    assert renamed == 1
                    path.write_bytes(canonical_bytes(mapped))
                    complete += compile_workload(ingest(path))[0].graph_complete
                    total += 1
        original = json.loads((ROOT / "examples/v3/frames-heldout-base.otlp.json").read_text())
        mapped, renamed = adapt(original)
        assert renamed == 8
        path.write_bytes(canonical_bytes(mapped))
        reports["frames-adapted"] = inspect_observations(ingest(path))
    frozen = ROOT / "docs/v3/frames-frozen"
    measured = ROOT / "docs/v3/frames-evaluation"
    result = evaluate(
        frozen / "protocol.json",
        frozen / "freeze.json",
        [frozen / f"{n}.json" for n in ("simpy", "fixed", "utilization")],
        [measured / f"measured-r{r}.json" for r in range(2)],
    )
    assert canonical_bytes(result) == (measured / "validation.json").read_bytes()
    return {
        "artifact_type": "v3_offline_audit",
        "metadata": metadata(__file__, {"network": False, "model_execution": False}, 0),
        "preserved_file_count": len(preservation["files"]),
        "original_working_bytes_exact": byte_exact,
        "pilot_tag_unchanged": True,
        "original_frames_complete_graphs": originally_complete,
        "adapted_frames_complete_graphs": complete,
        "frames_sessions": total,
        "evaluation_byte_exact": True,
        "conformance": reports,
        "note": "Adapter renames an existing root assertion; no dependencies or timings inferred.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    write_new(args.output, result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "preserved_file_count",
                    "frames_sessions",
                    "adapted_frames_complete_graphs",
                    "evaluation_byte_exact",
                )
            }
        )
    )
