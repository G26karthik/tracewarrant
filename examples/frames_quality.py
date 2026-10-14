"""Expose original FRAMES exact-match labels as neutral measured quality metrics.

This adapter reads retained evidence only. It does not run a model, reassess an
answer, alter a freeze or replace the original measurements.
"""

import argparse
import hashlib
from pathlib import Path

from workload_lab.artifacts import load_artifact, validate_artifact, write_new
from workload_lab.ingest import DEFAULT_MAX_BYTES, _decode
from workload_lab.ir import ValidationError


def attach_quality(measurement_path: Path, raw_path: Path) -> dict:
    measurement = load_artifact(measurement_path, "measurement")[0]
    with raw_path.open("rb") as stream:
        raw = stream.read(DEFAULT_MAX_BYTES + 1)
    if len(raw) > DEFAULT_MAX_BYTES:
        raise ValidationError("quality source exceeds byte limit")
    digest = hashlib.sha256(raw).hexdigest()
    if not any(
        r["role"] == "raw_observations" and r["sha256"] == digest for r in measurement["lineage"]
    ):
        raise ValidationError("quality source does not match measurement lineage")
    try:
        data = _decode(raw.decode("utf-8"))
    except UnicodeError:
        raise ValidationError("quality source must be UTF-8") from None
    if (
        not isinstance(data, dict)
        or data.get("phase") != "holdout"
        or data.get("freeze_sha256") != measurement["freeze_sha256"]
        or not isinstance(data.get("cells"), list)
    ):
        raise ValidationError("quality source identity mismatch")
    cells = {}
    for cell in data["cells"]:
        if not isinstance(cell, dict) or type(cell.get("repetition")) is not int:
            raise ValidationError("invalid quality source cell")
        if f"repetition-{cell['repetition']}" != measurement["run_id"]:
            continue
        identity = cell.get("configuration")
        if not isinstance(identity, str) or identity in cells:
            raise ValidationError("duplicate or invalid quality scenario")
        sessions = cell.get("sessions")
        if not isinstance(sessions, list) or not sessions:
            raise ValidationError("quality source has no offered sessions")
        if any(
            not isinstance(s, dict) or type(s.get("exact_answer_match")) is not bool
            for s in sessions
        ):
            raise ValidationError("quality labels missing or incomplete")
        cells[identity] = sessions
    if (
        set(cells) != {s["id"] for s in measurement["scenarios"]}
        or sum(len(s) for s in cells.values()) != measurement["counts"]["offered"]
    ):
        raise ValidationError("quality scenario or offered-count mismatch")
    for scenario in measurement["scenarios"]:
        if any(m["id"] == "answer.exact" for m in scenario["metrics"]):
            raise ValidationError("quality metric already present")
        sessions = cells[scenario["id"]]
        scenario["metrics"].append(
            {
                "id": "answer.exact",
                "unit": "ratio",
                "statistic": "fraction",
                "population": "offered",
                "value": sum(s["exact_answer_match"] for s in sessions) / len(sessions),
                "provenance": "MEASURED",
                "sample_count": len(sessions),
                "interval": None,
            }
        )
    measurement["lineage"].append(
        {
            "role": "quality_adapter_source",
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
    )
    measurement["limitations"].append("exact_match_is_not_semantic_quality")
    return validate_artifact(measurement, "measurement")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_new(args.output, attach_quality(args.measurement, args.raw))
