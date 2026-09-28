"""PydanticAI 2.51.0 TestModel -> local, content-free OTLP JSON. No remote exporter."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from examples.capture_controlled import attribute
from workload_lab.ingest import _INT_KEYS, _STRING_KEYS


async def capture():
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from pydantic_ai import Agent, models
    from pydantic_ai.capabilities import Instrumentation
    from pydantic_ai.models.instrumented import InstrumentationSettings
    from pydantic_ai.models.test import TestModel

    models.ALLOW_MODEL_REQUESTS = False
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource({"service.name": "pydantic-reference-v1"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    agent = Agent(
        TestModel(),
        name="research",
        capabilities=[
            Instrumentation(
                InstrumentationSettings(
                    tracer_provider=provider,
                    include_content=False,
                    include_binary_content=False,
                    include_model_request_parameters=False,
                    version=5,
                )
            )
        ],
    )

    @agent.tool_plain
    async def retrieve() -> str:
        """Find controlled local reference information."""
        await asyncio.sleep(0.004)
        return "PRIVATE_TOOL_RESULT_SENTINEL"

    @agent.tool_plain
    async def database() -> str:
        """Read a controlled local reference record."""
        import sqlite3

        with sqlite3.connect(":memory:") as db:
            result = db.execute("select 7").fetchone()[0]
        return str(result)

    await agent.run("PRIVATE_PROMPT_SENTINEL")
    captured = exporter.get_finished_spans()
    groups = []
    for span in captured:
        # Never persist names, events, arguments, results, URLs, raw resource maps.
        safe = {k: v for k, v in span.attributes.items() if k in _STRING_KEYS | _INT_KEYS}
        item = {
            "traceId": f"{span.context.trace_id:032x}",
            "spanId": f"{span.context.span_id:016x}",
            "startTimeUnixNano": str(span.start_time),
            "endTimeUnixNano": str(span.end_time),
            "attributes": [attribute(k, v) for k, v in safe.items()],
            "status": {"code": span.status.status_code.value},
        }
        if span.parent:
            item["parentSpanId"] = f"{span.parent.span_id:016x}"
        groups.append(
            {
                "scope": {
                    "name": span.instrumentation_scope.name,
                    "version": span.instrumentation_scope.version,
                },
                "schemaUrl": span.instrumentation_scope.schema_url or "",
                "spans": [item],
            }
        )
    result = {
        "resourceSpans": [
            {
                "resource": {"attributes": [attribute("service.name", "pydantic-reference-v1")]},
                "scopeSpans": groups,
            }
        ]
    }
    provider.shutdown()
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = asyncio.run(capture())
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
