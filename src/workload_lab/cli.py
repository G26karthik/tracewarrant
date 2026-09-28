"""File interface for the experimental library."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .analysis import AnalysisReport, analyze
from .graph import compile_workload
from .ingest import DEFAULT_MAX_BYTES, DEFAULT_MAX_SPANS, _decode, ingest
from .ir import SCHEMA_VERSION, ValidationError
from .simulation import scenario_from_dict, simulate


def _text(report: AnalysisReport) -> str:
    provenance = report.critical_path_elapsed.evidence.provenance.value
    path_time = (
        f"{report.critical_path_elapsed.value} ns"
        if report.critical_path_elapsed.value is not None
        else "UNKNOWN"
    )
    lines = [
        f"Trace: {report.trace_id}",
        f"Origin: {report.origin} | timing provenance: {provenance}",
        f"Atomic work nodes: {report.work_node_count} / spans: {report.span_count}",
        f"Dependency graph: {'asserted complete' if report.graph_complete else 'INCOMPLETE'}",
        f"Observed span envelope: {report.observed_envelope.value} ns",
        f"Declared-DAG critical path: {path_time}",
        "Path: " + (" -> ".join(report.critical_path_nodes) or "(no work nodes)"),
        f"Total elapsed work (overlap additive): {report.total_elapsed_work.value} ns",
        f"Unattributed wall time (not queue): {report.unattributed_wall_time.value} ns",
        "Contributions (kind / service: total work, chosen path):",
    ]
    for item in report.contributions:
        service_label = json.dumps(item.service, ensure_ascii=True)
        lines.append(
            f"  {item.kind} / {service_label}: {item.elapsed_work.value} ns, "
            f"{item.chosen_path_elapsed.value} ns"
        )
    lines.extend(
        [
            f"Unknown queue / service components: {report.unknown_queue_nodes} / "
            f"{report.unknown_service_nodes} nodes",
            "Model: fixed elapsed weights, zero gaps, one deterministic tied path.",
            "Elapsed contribution is not utilization or a proven capacity bottleneck.",
            "GPU utilization: UNKNOWN | Capacity recommendation: unavailable in M1",
            "Diagnostics: " + ", ".join(report.diagnostics),
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="workload-lab", description=__doc__)
    parser.add_argument("--version", action="version", version="workload-lab 0.1.0 (internal)")
    commands = parser.add_subparsers(dest="command", required=True)
    simulation = commands.add_parser("simulate", help="run an explicit offline scenario")
    simulation.add_argument("input", type=Path)
    simulation.add_argument("--output", type=Path)
    for command in ("ingest", "analyze"):
        sub = commands.add_parser(command)
        sub.add_argument("input", type=Path, help="local OTLP JSON or JSONL envelopes")
        sub.add_argument("--origin", choices=("observed", "synthetic"), default="observed")
        sub.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
        sub.add_argument("--max-spans", type=int, default=DEFAULT_MAX_SPANS)
        sub.add_argument(
            "--output", type=Path, help="create a new output file; never overwrite input"
        )
        if command == "analyze":
            sub.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        if args.command == "simulate":
            with args.input.open("rb") as stream:
                chunks, remaining = [], DEFAULT_MAX_BYTES + 1
                while remaining:
                    chunk = stream.read(min(65536, remaining))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
            raw = b"".join(chunks)
            if len(raw) > DEFAULT_MAX_BYTES:
                raise ValidationError("scenario exceeds byte limit")
            try:
                data = _decode(raw.decode("utf-8-sig"))
            except UnicodeError:
                raise ValidationError("scenario must be UTF-8") from None
            result = simulate(scenario_from_dict(data))
            result["scenario"] = data
            output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
            if args.output:
                with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(output + "\n")
            else:
                print(output)
            return 0
        dataset = ingest(
            args.input, origin=args.origin, max_bytes=args.max_bytes, max_spans=args.max_spans
        )
        workflows = compile_workload(dataset)
        if args.command == "ingest":
            result = {
                "schema_version": SCHEMA_VERSION,
                "artifact_type": "execution_ir",
                "workflows": [asdict(w) for w in workflows],
            }
            output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
        else:
            reports = [analyze(w) for w in workflows]
            if args.format == "json":
                output = json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "artifact_type": "analysis",
                        "reports": [asdict(r) for r in reports],
                    },
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
            else:
                output = "\n\n".join(_text(r) for r in reports)
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(output + "\n")
        else:
            print(output)
        return 0
    except (ValidationError, OSError, RecursionError) as exc:
        # Do not echo filenames, raw JSON, user span names or unknown attributes.
        message = str(exc) if isinstance(exc, ValidationError) else type(exc).__name__
        print(f"workload-lab: {message}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
