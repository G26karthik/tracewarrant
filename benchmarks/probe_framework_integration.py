"""Offline framework interface probe; TestModel is not real application quality."""

from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import json
import tempfile
from collections import Counter
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.artifacts import write_new
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import _INT_KEYS, _STRING_KEYS, ingest


def summarize(path):
    dataset = ingest(path)
    report = inspect_observations(dataset)
    return {
        "source_sha256": dataset.source_sha256,
        "span_count": len(dataset.spans),
        "node_kinds": dict(Counter(span.kind.value for span in dataset.spans)),
        "claims": {
            key: {k: value[k] for k in ("support", "observed", "eligible") if k in value}
            for key, value in report["claims"].items()
        },
    }


async def probe():
    # Optional, locked integration dependencies; never imported by the core CLI.
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from pydantic_ai.concurrency import ConcurrencyLimiter

    from examples.capture_pydantic_ai import capture

    # The existing collector disables remote model requests and uses TestModel.
    with tempfile.TemporaryDirectory(prefix="tracewarrant-framework-probe-") as folder:
        path = Path(folder) / "trace.json"
        path.write_text(json.dumps(await capture()), encoding="utf-8")
        framework = summarize(path)
    assert framework["span_count"] == 5
    assert framework["claims"]["dependency_graph"]["observed"] == 0
    assert framework["claims"]["queue_wait"]["observed"] == 0
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("tracewarrant-interface-research")
    limiter = ConcurrencyLimiter(1, name="opaque-pool", tracer=tracer)
    try:
        with tracer.start_as_current_span("local-probe"):
            await limiter.acquire("opaque-operation")

            async def waiting_operation():
                await limiter.acquire("opaque-operation")
                # 2.51.0 has task-owned tokens; release on the acquiring task.
                limiter.release()

            waiter = asyncio.create_task(waiting_operation())
            try:
                # Yield for synchronization, not fabricated benchmark latency.
                for _ in range(1000):
                    if limiter.waiting_count:
                        break
                    await asyncio.sleep(0)
                assert limiter.waiting_count == 1
            finally:
                limiter.release()
            await asyncio.wait_for(waiter, timeout=5)
        spans = exporter.get_finished_spans()
        waiting = [span for span in spans if "max_running" in span.attributes]
        assert len(waiting) == 1 and limiter.running_count == 0 and limiter.waiting_count == 0
        keys = set(waiting[0].attributes)
    finally:
        provider.shutdown()
    return {
        "artifact_type": "framework_integration_research_probe",
        "schema_version": "1.0",
        "metadata": metadata(__file__, {"model_execution": False, "network": False}, 0),
        "locked_integration_versions": {
            name: importlib.metadata.version(name)
            for name in ("pydantic-ai-slim", "opentelemetry-sdk", "anyio")
        },
        "fresh_pydantic": framework,
        "native_concurrency": {
            "wait_spans": len(waiting),
            "attribute_keys": sorted(keys),
            "keys_current_importer_retains": sorted(keys & (_STRING_KEYS | _INT_KEYS)),
            "max_running": waiting[0].attributes["max_running"],
            "final_running": limiter.running_count,
            "final_waiting": limiter.waiting_count,
        },
        "limitations": [
            "probe_not_implemented_adapter",
            "testmodel_not_real_task_quality",
            "controlled_tools_not_independent_deployed_application",
            "synchronization_probe_not_performance_benchmark",
            "no_upstream_adoption_or_uniqueness_claim",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(probe())
    write_new(args.output, result)
    print(json.dumps({"spans": result["fresh_pydantic"]["span_count"], "probe_complete": True}))


if __name__ == "__main__":
    main()
