"""Regenerate the synthetic OTLP fixture; no agent or remote service runs."""

import json
from pathlib import Path

TRACE = "1" * 32
BASE = 1_800_000_000_000_000_000


def attr(key, value):
    if type(value) is bool:
        encoded = {"boolValue": value}
    elif type(value) is int:
        encoded = {"intValue": str(value)}
    elif isinstance(value, list):
        encoded = {"arrayValue": {"values": [{"stringValue": v} for v in value]}}
    else:
        encoded = {"stringValue": value}
    return {"key": key, "value": encoded}


def span(number, start, end, operation, dependencies=(), **extra):
    attrs = [attr("gen_ai.operation.name", operation)]
    if dependencies:
        attrs.append(attr("workload_lab.depends_on", [f"{n:016x}" for n in dependencies]))
    attrs.extend(attr(k, v) for k, v in extra.items())
    result = {
        "traceId": TRACE,
        "spanId": f"{number:016x}",
        "name": "synthetic step",
        "kind": 1,
        "startTimeUnixNano": str(BASE + start * 1_000_000_000),
        "endTimeUnixNano": str(BASE + end * 1_000_000_000),
        "attributes": attrs,
    }
    if number != 1:
        result["parentSpanId"] = f"{1:016x}"
    return result


def fixture():
    groups = [
        (
            "research-workflow",
            [span(1, 0, 12, "invoke_workflow", **{"workload_lab.graph.complete": True})],
        ),
        (
            "model-backend",
            [
                span(
                    2,
                    0,
                    2,
                    "chat",
                    **{"gen_ai.request.model": "synthetic-model", "gen_ai.usage.input_tokens": 100},
                ),
                span(5, 8, 10, "chat", (3, 4)),
            ],
        ),
        (
            "retrieval",
            [
                span(
                    3,
                    2,
                    5,
                    "retrieval",
                    (2,),
                    **{"workload_lab.queue_ns": 0, "workload_lab.service_ns": 3_000_000_000},
                )
            ],
        ),
        (
            "browser-workers",
            [
                span(
                    4,
                    2,
                    8,
                    "execute_tool",
                    (2,),
                    **{
                        "gen_ai.tool.name": "browser",
                        "workload_lab.queue_ns": 1_000_000_000,
                        "workload_lab.service_ns": 5_000_000_000,
                    },
                )
            ],
        ),
        (
            "metadata-db",
            [span(6, 10, 11, "custom", (5,), **{"workload_lab.node.kind": "database"})],
        ),
    ]
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        attr("service.name", name),
                        attr("workload_lab.data.origin", "synthetic"),
                    ]
                },
                "scopeSpans": [
                    {"scope": {"name": "workload-lab-fixture", "version": "1"}, "spans": spans}
                ],
            }
            for name, spans in groups
        ]
    }


if __name__ == "__main__":
    Path(__file__).with_name("research-workflow.otlp.json").write_text(
        json.dumps(fixture(), indent=2) + "\n",
        encoding="utf-8",
    )
