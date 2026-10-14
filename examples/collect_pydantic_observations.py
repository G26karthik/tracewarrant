"""Pinned TestModel companion traces with explicitly owned tool leases; no agent-quality claim."""

import argparse
import asyncio
import importlib.metadata
import sqlite3
from pathlib import Path

from workload_lab.artifacts import write_new
from workload_lab.collection import ObservationRecorder, _attribute
from workload_lab.ir import NodeKind, ValidationError
from workload_lab.otel_collection import export_observations


async def collect():
    for name, version in (("pydantic-ai-slim", "2.51.0"), ("opentelemetry-sdk", "1.45.0")):
        if importlib.metadata.version(name) != version:
            raise ValidationError("framework example requires its pinned integration versions")
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from pydantic_ai import Agent, models
    from pydantic_ai.capabilities import Instrumentation
    from pydantic_ai.models.instrumented import InstrumentationSettings
    from pydantic_ai.models.test import TestModel

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    previous = models.ALLOW_MODEL_REQUESTS
    models.ALLOW_MODEL_REQUESTS = False
    recorder = ObservationRecorder()
    pool = recorder.pool(1)
    semaphore = asyncio.Semaphore(1)
    try:
        agent = Agent(
            TestModel(),
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
        with recorder.run() as run:

            @agent.tool_plain
            async def retrieve() -> str:
                """Read one local reference value."""
                with run.operation(NodeKind.RETRIEVAL) as operation:
                    async with operation.lease(pool, semaphore.acquire, semaphore.release):
                        with sqlite3.connect(":memory:") as database:
                            return str(database.execute("select 7").fetchone()[0])

            @agent.tool_plain
            async def database_lookup() -> str:
                """Read one local record."""
                with run.operation(NodeKind.DATABASE) as operation:
                    async with operation.lease(pool, semaphore.acquire, semaphore.release):
                        with sqlite3.connect(":memory:") as database:
                            return str(database.execute("select 11").fetchone()[0])

            await agent.run("PRIVATE_PROMPT_SENTINEL")
        native = exporter.get_finished_spans()
        assert len(native) == 5 and semaphore._value == 1
        export_observations(recorder, exporter)
        # These are companion traces, not a fabricated merged dependency graph.
        # Model requests remain uninstrumented for pool/queue/occupancy claims.
        wire = []
        for span in native:
            operation_name = span.attributes.get("gen_ai.operation.name")
            attrs = []
            if operation_name in ("invoke_agent", "chat", "execute_tool"):
                attrs.append(
                    {"key": "gen_ai.operation.name", "value": {"stringValue": operation_name}}
                )
            if operation_name == "execute_tool":
                # Both known example tools contain a separately recorded owned
                # operation. Treat their outer intervals as containers.
                attrs.append(_attribute("node.role", "container"))
            wire.append(
                {
                    "traceId": f"{span.context.trace_id:032x}",
                    "spanId": f"{span.context.span_id:016x}",
                    **({"parentSpanId": f"{span.parent.span_id:016x}"} if span.parent else {}),
                    "startTimeUnixNano": str(span.start_time),
                    "endTimeUnixNano": str(span.end_time),
                    "attributes": attrs,
                    "status": {"code": span.status.status_code.value},
                }
            )
        result = recorder.envelope()
        result["resourceSpans"].append(
            {
                "resource": {"attributes": []},
                "scopeSpans": [
                    {
                        "scope": {"name": "tracewarrant.pydantic_example", "version": "2.51.0"},
                        "spans": wire,
                    }
                ],
            }
        )
        return result, recorder
    finally:
        models.ALLOW_MODEL_REQUESTS = previous
        provider.shutdown()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result, _ = asyncio.run(collect())
    write_new(args.output, result)


if __name__ == "__main__":
    main()
