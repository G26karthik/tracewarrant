"""Optional explicit SDK exporter bridge; no providers, processors or network setup."""

from .collection import ObservationRecorder
from .ir import ValidationError


def export_observations(recorder: ObservationRecorder, exporter) -> int:
    """Export a closed recorder to a caller-selected OTel SpanExporter, once per call.

    The exporter may send data remotely if the caller configures it to do so.
    No native framework spans are merged, relabeled or inferred by this bridge.
    """
    # Validate bounds before optional imports or invoking the caller's exporter.
    recorder.envelope()
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.sdk.trace.export import SpanExportResult
    from opentelemetry.sdk.util.instrumentation import InstrumentationScope
    from opentelemetry.trace import SpanContext, SpanKind, Status, StatusCode, TraceFlags

    def context(trace_id, identity):
        return SpanContext(int(trace_id, 16), int(identity, 16), False, TraceFlags(1))

    spans = []
    for span in recorder.spans():
        attrs = {
            "workload_lab.node.kind": span.kind.value,
            "workload_lab.node.role": span.role,
            "workload_lab.depends_on": span.depends_on,
            "workload_lab.outcome": span.observation.outcome,
        }
        if span.parent_id is None:
            attrs["workload_lab.graph.complete"] = span.graph_complete
        for name in span.observation.__dataclass_fields__:
            value = getattr(span.observation, name)
            if value is not None and name != "outcome":
                attrs["workload_lab." + name] = value
        spans.append(
            ReadableSpan(
                name="tracewarrant.boundary",
                context=context(span.trace_id, span.span_id),
                parent=context(span.trace_id, span.parent_id) if span.parent_id else None,
                resource=Resource({}),
                attributes=attrs,
                kind=SpanKind.INTERNAL,
                status=Status(StatusCode.ERROR if span.status == "ERROR" else StatusCode.OK),
                start_time=span.start_ns,
                end_time=span.end_ns,
                instrumentation_scope=InstrumentationScope("tracewarrant.collection", "1"),
            )
        )
    if exporter.export(tuple(spans)) != SpanExportResult.SUCCESS:
        raise ValidationError("observation exporter reported failure")
    return len(spans)
