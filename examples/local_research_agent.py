"""Bounded real-model non-coding probe using cached local Ollama and PydanticAI.

No remote provider, model pull, arbitrary endpoint, prompts or reports in artifacts.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
import subprocess
import time
import urllib.request
from pathlib import Path

from benchmarks.provenance import metadata
from examples.capture_controlled import Pool, Recorder, envelope
from workload_lab.simulation import percentile

MODEL = "qwen3-vl:4b"
OPTIONS = {"temperature": 0, "seed": 27, "num_predict": 160, "num_ctx": 4096}
SCHEMA = {
    "type": "object",
    "properties": {
        "site_id": {"type": "string"},
        "supplier_share": {"type": "integer"},
        "stock_days": {"type": "integer"},
        "risk": {"type": "string"},
    },
    "required": ["site_id", "supplier_share", "stock_days", "risk"],
}


def local_request(route, body=None):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/" + route,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with opener.open(request, timeout=120) as response:
        raw = response.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("local model response exceeds limit")
    return json.loads(raw)


async def batch(tool_count, client_count, number=8):
    from pydantic_ai import Agent, models
    from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
    from pydantic_ai.models.function import FunctionModel

    models.ALLOW_MODEL_REQUESTS = False  # Only our explicit loopback bridge makes model requests.
    tools, clients = Pool("evidence-tool", tool_count), Pool("inference-client", client_count)
    clock = (time.time_ns(), time.perf_counter_ns())

    async def session(index):
        recorder = Recorder(index + 1, clock)
        root, start = recorder.new_id(), recorder.now()
        expected = {
            "site_id": f"facility-{index % 4}",
            "supplier_share": 65 + index % 4,
            "stock_days": 8 + index % 4,
        }
        plan = recorder.new_id()
        planning_start = recorder.now()
        recorder.record(
            plan,
            root,
            planning_start,
            recorder.now(),
            "compute",
            **{"workload_lab.outcome": "completed"},
        )
        dependencies = []
        provider_metrics = {}

        async def observed(kind, pool, parents, operation):
            sid, begin = recorder.new_id(), recorder.now()
            enqueue = recorder.now()
            await pool.semaphore.acquire()
            acquired = recorder.now()
            outcome = "completed"
            try:
                return sid, await operation()
            except Exception:
                outcome = "failed"
                raise
            finally:
                released = recorder.now()
                pool.semaphore.release()
                recorder.record(
                    sid,
                    root,
                    begin,
                    recorder.now(),
                    kind,
                    **{
                        "workload_lab.node.role": "work",
                        "workload_lab.depends_on": parents,
                        "workload_lab.pool": pool.name,
                        "workload_lab.queue": pool.name,
                        "workload_lab.capacity": pool.capacity,
                        "workload_lab.enqueued_ns": enqueue,
                        "workload_lab.acquired_ns": acquired,
                        "workload_lab.service_start_ns": acquired,
                        "workload_lab.service_end_ns": released,
                        "workload_lab.released_ns": released,
                        "workload_lab.outcome": outcome,
                    },
                )

        async def bridge(messages, info):
            returns = [
                p for message in messages for p in message.parts if isinstance(p, ToolReturnPart)
            ]
            if not returns:
                return ModelResponse([ToolCallPart("retrieve", {}), ToolCallPart("lookup", {})])
            context = "\n".join(str(p.content) for p in returns)

            async def infer():
                response = await asyncio.to_thread(
                    local_request,
                    "chat",
                    {
                        "model": MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": (
                                    "Use only these fictional facility records. Return JSON with "
                                    "site_id, supplier_share, stock_days and one short risk sentence. "
                                    "Preserve exact facts.\n" + context
                                ),
                            }
                        ],
                        "stream": False,
                        "think": False,
                        "format": SCHEMA,
                        "options": OPTIONS,
                        "keep_alive": "2m",
                    },
                )
                provider_metrics.update(
                    {
                        k: response.get(k)
                        for k in (
                            "total_duration",
                            "load_duration",
                            "prompt_eval_count",
                            "prompt_eval_duration",
                            "prompt_eval_cached_count",
                            "eval_count",
                            "eval_duration",
                            "done_reason",
                        )
                    }
                )
                return response["message"]["content"]

            _, content = await observed("llm", clients, tuple(sorted(dependencies)), infer)
            return ModelResponse(
                [TextPart(content)], model_name=MODEL, provider_name="ollama-local"
            )

        agent = Agent(
            FunctionModel(bridge, model_name="loopback-ollama-bridge"), name="facility_research"
        )

        @agent.tool_plain
        async def retrieve() -> str:
            """Retrieve the relevant fictional facility supplier record."""

            def search():
                corpus = [
                    {
                        "site_id": f"facility-{n}",
                        "supplier_share": 65 + n % 4,
                        "source": "fictional supplier register",
                    }
                    for n in range(600)
                ]
                return json.dumps(
                    next(row for row in corpus if row["site_id"] == expected["site_id"])
                )

            sid, result = await observed(
                "retrieval", tools, (plan,), lambda: asyncio.to_thread(search)
            )
            dependencies.append(sid)
            return result

        @agent.tool_plain
        async def lookup() -> str:
            """Read the fictional facility's current stock-cover record."""

            def query():
                with sqlite3.connect(":memory:") as db:
                    db.execute("create table stock (site text, days integer)")
                    db.executemany(
                        "insert into stock values (?,?)",
                        [(f"facility-{n}", 8 + n) for n in range(4)],
                    )
                    value = db.execute(
                        "select days from stock where site=?", (expected["site_id"],)
                    ).fetchone()[0]
                return json.dumps({"site_id": expected["site_id"], "stock_days": value})

            sid, result = await observed(
                "database", tools, (plan,), lambda: asyncio.to_thread(query)
            )
            dependencies.append(sid)
            return result

        error = None
        facts_correct = False
        try:
            result = await agent.run("Assess the fictional facility's supplier disruption risk.")
            parsed = json.loads(result.output)
            facts_correct = all(parsed.get(k) == v for k, v in expected.items()) and bool(
                parsed.get("risk")
            )
        except Exception as exc:
            error = type(exc).__name__  # Never persist exception payload/provider body.
        recorder.record(
            root,
            None,
            start,
            recorder.now(),
            "workflow",
            **{"workload_lab.graph.complete": error is None},
        )
        return {
            "trace": envelope(recorder.spans, "local-facility-agent-v1"),
            "latency_ns": recorder.now() - start,
            "facts_correct": facts_correct,
            "error_type": error,
            "provider_metrics": provider_metrics,
        }

    return await asyncio.gather(*(session(i) for i in range(number)))


async def run(output):
    tags = local_request("tags")
    model = next((m for m in tags["models"] if m["name"] == MODEL), None)
    if model is None:
        raise ValueError("required local model absent; no automatic download")
    gpu = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
        text=True,
        capture_output=True,
        check=False,
    )
    meta = metadata(
        __file__,
        {"model": MODEL, "options": OPTIONS, "sessions_per_batch": 8, "repetitions": 2},
        27,
    )
    meta.update(
        gpu=gpu.stdout.strip(),
        driver="included in GPU query",
        cuda="not directly used; Ollama backend",
    )
    result = {
        "artifact_type": "real_model_applicability_probe",
        "metadata": meta,
        "ollama_version": local_request("version"),
        "model_identity": model,
        "design": "docs/experiments/real-model-probe-design.md",
        "cells": [],
        "limitations": [
            "exploratory small sample; no p95/p99 or causal accuracy claims",
            "client slots are not GPU workers; backend queueing UNKNOWN",
            "exact fact extraction is a narrow quality proxy",
        ],
    }
    result["warmup"] = await batch(1, 1, 1)
    if result["warmup"][0]["error_type"]:
        output.write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
        raise RuntimeError("local warmup failed; preserved content-free evidence")
    result["backend_residency_after_warmup"] = local_request("ps")
    configurations = [("BASELINE", 1, 1), ("TOOL+", 2, 1), ("CLIENT+", 1, 2)]
    for repetition in range(2):
        for name, tools, clients in configurations if repetition == 0 else reversed(configurations):
            rows = await batch(tools, clients)
            result["cells"].append(
                {
                    "configuration": name,
                    "tool_workers": tools,
                    "client_slots": clients,
                    "repetition": repetition,
                    "sessions": rows,
                    "median_latency_ns": percentile([r["latency_ns"] for r in rows], 0.5),
                    "fact_successes": sum(r["facts_correct"] for r in rows),
                    "errors": sum(r["error_type"] is not None for r in rows),
                }
            )
            output.write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
            print(f"Measured real model: {name}, repetition {repetition}", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("use a new output file; previous evidence must be preserved")
    asyncio.run(run(args.output))
