import json
from dataclasses import replace
from pathlib import Path

from examples.adapt_frames_trace import adapt
from workload_lab.artifacts import write_new
from workload_lab.conformance import inspect_observations
from workload_lab.ingest import ingest
from workload_lab.ir import Dataset, Observation, Span

ROOT = Path(__file__).parents[1]


def test_two_real_trace_sources_and_refusal():
    controlled = inspect_observations(ingest(ROOT / "examples/traces/controlled-v1.otlp.json"))
    framework = inspect_observations(ingest(ROOT / "examples/traces/pydantic-ai-2.51.0.otlp.json"))
    assert controlled["claims"]["dependency_graph"]["support"] == "supported"
    assert framework["claims"]["dependency_graph"]["support"] == "unsupported"
    assert framework["claims"]["queue_wait"]["missing_fields"]["acquired_ns"] > 0
    for result in (controlled, framework):
        assert result["claims"]["inference_service_demand"]["classification"] == "not_identifiable"
        assert result["claims"]["prediction_suitability"]["support"] == "unsupported"


def test_capacity_contradiction_content_exclusion_and_missingness():
    obs = Observation(
        pool="PRIVATE_secret", capacity=1, enqueued_ns=0, acquired_ns=1, released_ns=10
    )
    a = Span(
        "a" * 32, "1" * 16, None, 0, 20, role="work", service="PRIVATE_service", observation=obs
    )
    b = replace(a, trace_id="b" * 32)
    report = inspect_observations(Dataset("a" * 64, "observed", (a, b)))
    assert report["violations"]["observed_occupancy_exceeds_declared_capacity"] == 1
    assert report["claims"]["finite_pool_capacity"]["support"] == "unsupported"
    assert "PRIVATE" not in json.dumps(report)
    b = replace(b, observation=Observation())
    report = inspect_observations(Dataset("a" * 64, "observed", (a, b)))
    assert report["claims"]["queue_wait"]["support"] == "partial"
    assert report["claims"]["queue_wait"]["eligible"] == 2


def test_synthetic_never_certifies_prediction():
    report = inspect_observations(
        ingest(ROOT / "examples/research-workflow.otlp.json", origin="synthetic")
    )
    assert report["origin"] == "synthetic"
    assert report["claims"]["prediction_suitability"]["classification"] == "unsupported"


def test_external_trace_detects_binding_error_and_explicit_adapter(tmp_path):
    original = ROOT / "examples/v3/frames-heldout-base.otlp.json"
    before = inspect_observations(ingest(original))
    assert before["claims"]["dependency_graph"]["support"] == "unsupported"
    raw = json.loads(original.read_text())
    transformed, count = adapt(raw)
    assert count == 8 and raw != transformed
    path = tmp_path / "adapted.json"
    write_new(path, transformed)
    after = inspect_observations(ingest(path))
    assert after["claims"]["dependency_graph"]["support"] == "supported"
    assert after["claims"]["prediction_suitability"]["support"] == "unsupported"
    assert after["claims"]["inference_service_demand"]["provenance"] == "UNKNOWN"
