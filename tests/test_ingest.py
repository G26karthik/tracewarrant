import json
from dataclasses import asdict, replace

import pytest
from conftest import make_span

from workload_lab import analyze, compile_workload, ingest
from workload_lab.ir import Dataset, Evidence, Metadata, Provenance, Quantity, ValidationError


def attribute(key, value):
    return {"key": key, "value": value}


def envelope(attrs=None):
    return {
        "resourceSpans": [
            {
                "resource": {"attributes": [attribute("service.name", {"stringValue": "service"})]},
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "traceId": "A" * 32,
                                "spanId": "F" * 16,
                                "startTimeUnixNano": "1800000000000000001",
                                "endTimeUnixNano": "1800000000000000008",
                                "attributes": attrs or [],
                            }
                        ]
                    }
                ],
            }
        ]
    }


def write(tmp_path, data, suffix=".json"):
    target = tmp_path / ("input" + suffix)
    target.write_text(json.dumps(data), encoding="utf-8")
    return target


def raw_span(data):
    return data["resourceSpans"][0]["scopeSpans"][0]["spans"][0]


def test_content_free_import_drops_payloads(tmp_path):
    secret = "DO_NOT_RETAIN-private-secret-credential"
    data = envelope(
        [
            attribute("gen_ai.operation.name", {"stringValue": "chat"}),
            attribute("gen_ai.input.messages", {"stringValue": secret}),
            attribute("url.full", {"stringValue": secret}),
            attribute("gen_ai.tool.call.arguments", {"stringValue": secret}),
        ]
    )
    raw_span(data).update(
        name=secret, events=[{"name": secret}], status={"code": 2, "message": secret}
    )
    dataset = ingest(write(tmp_path, data))
    workflows = compile_workload(dataset)
    serialized = json.dumps([asdict(dataset), asdict(workflows[0]), asdict(analyze(workflows[0]))])
    assert secret not in serialized
    assert dataset.spans[0].status == "ERROR"
    assert dataset.spans[0].span_id == "f" * 16
    assert analyze(workflows[0]).observed_envelope.value == 7


@pytest.mark.parametrize(
    "field,value",
    [
        ("traceId", "0" * 32),
        ("traceId", "short"),
        ("spanId", "z" * 16),
        ("startTimeUnixNano", -1),
        ("startTimeUnixNano", True),
        ("startTimeUnixNano", 1.5),
        ("startTimeUnixNano", "1e9"),
        ("endTimeUnixNano", "1"),
        ("endTimeUnixNano", str(2**64)),
        ("status", {"code": True}),
        ("status", {"code": "STATUS_CODE_OK"}),
        ("kind", 9),
        ("kind", "SPAN_KIND_CLIENT"),
        ("parentSpanId", "bad"),
    ],
)
def test_reject_malformed_wire_fields(tmp_path, field, value):
    data = envelope()
    raw_span(data)[field] = value
    with pytest.raises(ValidationError):
        ingest(write(tmp_path, data))


@pytest.mark.parametrize(
    "attribute_value",
    [
        attribute("gen_ai.usage.input_tokens", {"doubleValue": 2.0}),
        attribute("gen_ai.usage.input_tokens", {"intValue": -1}),
        attribute("gen_ai.request.model", {"stringValue": False}),
        attribute("workload_lab.graph.complete", {"boolValue": "true"}),
        attribute("workload_lab.node.kind", {"stringValue": "invented-kind"}),
        attribute("workload_lab.queue_ns", {"intValue": "8"}),
        attribute("workload_lab.depends_on", {"arrayValue": {"values": [1]}}),
    ],
)
def test_reject_malformed_known_attributes(tmp_path, attribute_value):
    with pytest.raises(ValidationError):
        ingest(write(tmp_path, envelope([attribute_value])))


def test_duplicate_ids_are_rejected(tmp_path):
    data = envelope()
    spans = data["resourceSpans"][0]["scopeSpans"][0]["spans"]
    spans.append(spans[0])
    with pytest.raises(ValidationError, match="duplicate"):
        ingest(write(tmp_path, data))


def test_duplicate_attributes_and_json_keys_rejected(tmp_path):
    item = attribute("gen_ai.operation.name", {"stringValue": "chat"})
    with pytest.raises(ValidationError, match="duplicate"):
        ingest(write(tmp_path, envelope([item, item])))
    path = tmp_path / "duplicate.json"
    path.write_text('{"resourceSpans": [], "resourceSpans": []}')
    with pytest.raises(ValidationError, match="duplicate"):
        ingest(path)


@pytest.mark.parametrize(
    "text",
    [
        "NaN",
        "Infinity",
        '{"resourceSpans":NaN}',
        '{"resourceSpans":[],"extra":1e999}',
        "[]",
        "{}",
        "{",
    ],
)
def test_invalid_json_and_nonfinite_rejected(tmp_path, text):
    path = tmp_path / "input.json"
    path.write_text(text)
    with pytest.raises(ValidationError):
        ingest(path)


def test_jsonl_multiple_traces_and_reused_span_ids(tmp_path):
    first, second = envelope(), envelope()
    raw_span(second)["traceId"] = "b" * 32
    target = tmp_path / "input.jsonl"
    target.write_text(json.dumps(first) + "\n\n" + json.dumps(second) + "\n")
    workflows = compile_workload(ingest(target))
    assert [w.trace_id for w in workflows] == ["a" * 32, "b" * 32]


def test_limits(tmp_path):
    data = envelope()
    target = write(tmp_path, data)
    with pytest.raises(ValidationError, match="byte limit"):
        ingest(target, max_bytes=10)
    second = dict(raw_span(data), spanId="c" * 16)
    data["resourceSpans"][0]["scopeSpans"][0]["spans"].append(second)
    with pytest.raises(ValidationError, match="span limit"):
        ingest(write(tmp_path, data), max_spans=1)


@pytest.mark.parametrize("loss", ["links", "droppedAttributesCount"])
def test_completeness_revoked_for_loss(tmp_path, loss):
    data = envelope([attribute("workload_lab.graph.complete", {"boolValue": True})])
    raw_span(data)[loss] = [{}] if loss == "links" else 1
    assert not compile_workload(ingest(write(tmp_path, data)))[0].graph_complete


def test_library_ir_validation():
    with pytest.raises(ValidationError):
        make_span(1, 2, 1)
    with pytest.raises(ValidationError):
        make_span(1, 0, 7, queue_ns=4, service_ns=4)
    with pytest.raises(ValidationError):
        Metadata(input_tokens=1, cached_input_tokens=2)
    with pytest.raises(ValidationError):
        make_span(1, 0, 1, parent=2, graph_complete=True)
    with pytest.raises(ValidationError):
        Evidence(Provenance.MEASURED, "synthetic", "test", ("fixture",))
    with pytest.raises(ValidationError):
        Quantity(0, "ns", Evidence(Provenance.UNKNOWN, "observed", "test", ("fixture",)))
    with pytest.raises(ValidationError):
        Dataset("b" * 64, "synthetic", ())


def test_origin_and_quantity_cannot_be_overridden_in_workflow():
    workflow = compile_workload(Dataset("b" * 64, "synthetic", (make_span(1, 0, 5),)))[0]
    with pytest.raises(ValidationError):
        replace(workflow, origin="observed")
