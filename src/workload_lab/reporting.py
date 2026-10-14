"""Standalone escaped reports; no executable content or remote resources."""

import html
import json


def job_html(report: dict) -> str:
    def escape(value):
        return html.escape(str(value), quote=True)

    def table(headers, rows):
        head = "".join(f"<th>{escape(h)}</th>" for h in headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{escape(v)}</td>" for v in row) + "</tr>" for row in rows
        )
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    gates = table(
        ["Gate", "Status", "Observed", "Required", "Reason"],
        [
            [g["id"], g["status"], g["observed"], g["required"], g["reason"] or ""]
            for g in report["gates"]
        ],
    )
    comparisons = table(
        ["Model", "Baseline", "Group", "Outcome"],
        [
            [r["model_id"], r["baseline_id"], r["comparison_group"], r["result"]]
            for r in report["evaluation"]["baseline_comparisons"]
        ],
    )
    quality = table(
        ["Scenario", "Replication", "Measured quality", "Reason"],
        [
            [r["scenario_id"], r["run_id"], r["value"], r["reason"] or ""]
            for r in report["quality_rows"][:100]
        ],
    )
    quality_note = (
        "Quality was not assessed. A policy pass does not establish a useful agent."
        if report["policy"]["quality"] is None
        else "Quality requires matching measured evidence in every scenario and replication."
    )
    if len(report["quality_rows"]) > 100:
        quality_note += " First 100 quality rows shown; the JSON report contains every row."
    limits = "".join(f"<li>{escape(item)}</li>" for item in report["limitations"])
    policy = escape(json.dumps(report["policy"], indent=2, sort_keys=True))
    selected = next(
        m for m in report["evaluation"]["models"] if m["model"]["id"] == report["model_id"]
    )
    envelopes = table(
        ["Scenario", "Replication", "Envelope status", "Violations"],
        [
            [r["scenario_id"], r["run_id"], r["status"], ", ".join(r["violations"])]
            for r in selected["envelope_checks"]
        ],
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<meta http-equiv="Content-Security-Policy" content="default-src 'none';
style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>TraceWarrant validation job: {escape(report["result"])}</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:2rem auto;
padding:0 1rem;color:#182733;background:#f7f9fb}}
table{{border-collapse:collapse;width:100%;background:white;margin:1rem 0;overflow-wrap:anywhere}}
th,td{{border:1px solid #ccd5de;padding:.5rem;text-align:left}}th{{background:#e7eef4}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:1rem}}
h1,h2{{line-height:1.2}}code{{overflow-wrap:anywhere}}</style></head><body>
<h1>Validation policy: {escape(report["result"])}</h1>
<p>Model: <strong>{escape(report["model_id"])}</strong>. Scope: {escape(report["claim_scope"])}.</p>
<p>{escape(quality_note)}</p>
<p>This report checks an explicit policy; it is not production certification.</p>
<h2>Acceptance gates</h2>{gates}<h2>Baseline comparisons</h2>{comparisons}
<h2>Quality evidence</h2>{quality}<h2>Policy</h2><pre>{policy}</pre>
<h2>Calibration envelope</h2>{envelopes}
<h2>Evidence and limits</h2>
<p>Job SHA-256: <code>{escape(report["job_manifest_sha256"])}</code>.</p>
<p>Predictions retain their original freeze.
This policy is not bound by that freeze and may be retrospective.</p>
<ul>{limits}</ul><p><a href="report.json">Full machine-readable report</a>;
verify report files against SHA256SUMS.</p>
</body></html>
"""
