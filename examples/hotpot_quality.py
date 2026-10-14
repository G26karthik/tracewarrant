"""Export unchanged V5 offered-task scores into the standalone qualification format."""

import argparse
import json
from pathlib import Path

from benchmarks.hotpot_validation import audit
from benchmarks.provenance import sha
from workload_lab.artifacts import write_new


def convert(raw, selection):
    checked = audit(raw, selection)
    data = json.loads(raw.read_bytes())
    if data["phase"] != "feasibility":
        raise ValueError("only the retained feasibility sample is supported")
    sample = {
        "schema_version": "1.0",
        "artifact_type": "application_sample",
        "workload_id": "hotpot-distractor-local-v5",
        "sample_id": "feasibility-eight",
        "provenance": "MEASURED",
        "lineage": [
            {"role": "raw_observations", "sha256": checked["raw_sha256"]},
            {"role": "selection", "sha256": checked["selection_sha256"]},
            {"role": "score_adapter", "sha256": sha(__file__)},
        ],
        "rows": [
            {
                "id": row["task_id"],
                "outcome": "completed" if row["error_type"] is None else "failed",
                "metrics": [
                    {"id": "answer.exact", "value": int(row["exact_answer_match"])},
                    {"id": "answer.f1", "value": row["answer_f1"]},
                ],
            }
            for row in data["cells"][0]["sessions"]
        ],
        "limitations": [
            "exact_and_token_overlap_are_not_semantic_quality",
            "retained_scalar_scores_not_rescored_by_adapter",
            "small_development_sample",
        ],
    }
    gate = checked["quality_gate"]["policy"]
    policy = {
        "schema_version": "1.0",
        "artifact_type": "application_quality_policy",
        "minimum_samples": gate["minimum_completed"],
        "minimum_completion_fraction": 1,
        "metrics": [
            {
                "id": "answer.exact",
                "statistic": "fraction",
                "minimum_value": gate["minimum_exact_matches"] / checked["quality_gate"]["offered"],
            },
            {"id": "answer.f1", "statistic": "mean", "minimum_value": gate["minimum_mean_f1"]},
        ],
    }
    return sample, policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sample, policy = convert(args.raw, args.selection)
    args.output.mkdir(parents=True, exist_ok=False)
    write_new(args.output / "sample.json", sample)
    write_new(args.output / "policy.json", policy)
