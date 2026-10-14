"""Qualify optional SDK export and pinned framework coverage without a model service."""

import argparse
import asyncio
import importlib.metadata
import tempfile
from pathlib import Path

from benchmarks.provenance import metadata
from workload_lab.artifacts import canonical_bytes, write_new
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import ingest
from workload_lab.ir import ValidationError
from workload_lab.otel_collection import export_observations


def qualify():
    from opentelemetry.sdk.trace.export import SpanExportResult
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from opentelemetry.trace import get_tracer_provider
    from pydantic_ai import models

    from examples.collect_observations import collect as plain_collect
    from examples.collect_pydantic_observations import collect as framework_collect

    global_provider = get_tracer_provider()
    recorder = asyncio.run(plain_collect())
    exporter = InMemorySpanExporter()
    assert export_observations(recorder, exporter) == 3
    for observed, exported in zip(recorder.spans(), exporter.get_finished_spans(), strict=True):
        assert observed.trace_id == f"{exported.context.trace_id:032x}"
        assert observed.span_id == f"{exported.context.span_id:016x}"
        assert observed.start_ns == exported.start_time and observed.end_ns == exported.end_time
        assert exported.attributes["workload_lab.depends_on"] == observed.depends_on
        assert exported.attributes["workload_lab.node.role"] == observed.role
        assert exported.attributes["workload_lab.outcome"] == observed.observation.outcome

    class RefusingExporter:
        def export(self, spans):
            return SpanExportResult.FAILURE

    try:
        export_observations(recorder, RefusingExporter())
    except ValidationError:
        pass
    else:
        raise AssertionError("exporter failure accepted")
    original_requests = models.ALLOW_MODEL_REQUESTS
    combined, framework_recorder = asyncio.run(framework_collect())
    assert models.ALLOW_MODEL_REQUESTS is original_requests
    assert get_tracer_provider() is global_provider
    with tempfile.TemporaryDirectory(prefix="tracewarrant-collection-check-") as folder:
        root = Path(folder)
        recorder.write(root / "plain.json")
        plain = inspect_observations(ingest(root / "plain.json"))
        (root / "framework.json").write_bytes(canonical_bytes(combined))
        framework = inspect_observations(ingest(root / "framework.json"))
    assert plain["claims"]["dependency_graph"]["support"] == "supported"
    assert plain["claims"]["queue_wait"]["observed"] == 2
    assert not plain["violations"] and not framework["violations"]
    assert framework["atomic_spans"] == 4 and framework["trace_count"] == 2
    for claim in ("queue_wait", "resource_occupancy", "finite_pool_capacity"):
        assert framework["claims"][claim]["support"] == "partial"
        assert framework["claims"][claim]["observed"] == 2
        assert framework["claims"][claim]["eligible"] == 4
    assert framework["claims"]["dependency_graph"]["support"] == "unsupported"
    assert framework["claims"]["inference_service_demand"]["value"] is None
    assert framework["claims"]["prediction_suitability"]["support"] == "unsupported"
    assert "PRIVATE" not in str(combined) and "select " not in str(combined)
    return {
        "artifact_type": "collection_integration_qualification",
        "metadata": metadata(__file__, {"network": False, "model_execution": False}, 0),
        "versions": {
            name: importlib.metadata.version(name)
            for name in ("pydantic-ai-slim", "opentelemetry-sdk", "anyio")
        },
        "sdk_span_ids_timestamps_roles_edges_preserved": True,
        "exporter_failure_refused": True,
        "global_provider_and_model_permissions_unchanged": True,
        "plain_conformance": plain,
        "framework_conformance": framework,
        "framework_owned_operations": len(framework_recorder.spans()) - 1,
        "limits": [
            "testmodel_not_real_task_quality",
            "companion_traces_not_combined_causal_graph",
            "caller_declared_boundaries_not_authenticated",
            "not_external_adoption",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_new(args.output, qualify())
    print('{"collection_integration_qualified":true}')


if __name__ == "__main__":
    main()
