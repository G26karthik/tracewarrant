"""Explicit binding migration for the frozen FRAMES collector's misspelled root key.

Never infer completeness. Rename only an existing boolean assertion on a root.
"""

import argparse
import copy
from pathlib import Path

from workload_lab.artifacts import write_new
from workload_lab.ingest import DEFAULT_MAX_BYTES, _decode
from workload_lab.ir import ValidationError


def adapt(data):
    result = copy.deepcopy(data)
    renamed = 0
    for resource in result["resourceSpans"]:
        for scope in resource["scopeSpans"]:
            for span in scope["spans"]:
                attributes = span.get("attributes", [])
                legacy = [a for a in attributes if a["key"] == "workload_lab.graph_complete"]
                current = [a for a in attributes if a["key"] == "workload_lab.graph.complete"]
                if legacy:
                    if len(legacy) != 1 or current or span.get("parentSpanId"):
                        raise ValidationError("ambiguous completeness binding")
                    if (
                        set(legacy[0]["value"]) != {"boolValue"}
                        or type(legacy[0]["value"]["boolValue"]) is not bool
                    ):
                        raise ValidationError("completeness assertion must be boolean")
                    legacy[0]["key"] = "workload_lab.graph.complete"
                    renamed += 1
    return result, renamed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open("rb") as stream:
        raw = stream.read(DEFAULT_MAX_BYTES + 1)
    if len(raw) > DEFAULT_MAX_BYTES:
        raise ValidationError("trace exceeds byte limit")
    data, count = adapt(_decode(raw.decode("utf-8")))
    write_new(args.output, data)
    print(f"Renamed {count} existing root assertions; source remains unchanged.")
