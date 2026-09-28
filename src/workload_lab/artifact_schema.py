"""Open JSON Schema 2020-12, independent of a simulator or framework."""

VERSION = "1.0"
PROVENANCE = [
    "MEASURED",
    "CALIBRATED",
    "INTERPOLATED",
    "EXTRAPOLATED",
    "SIMULATED",
    "ESTIMATED",
    "UNKNOWN",
]
TOKEN = {
    "type": "string",
    "minLength": 1,
    "maxLength": 128,
    "pattern": r"^[A-Za-z0-9][A-Za-z0-9_.:/-]*$",
}
NUMBER = {"type": "number", "minimum": 0, "maximum": 1e30}
COUNT = {"type": "integer", "minimum": 0, "maximum": 1_000_000_000}
SHA = {"type": "string", "pattern": "^[0-9a-f]{64}$", "maxLength": 64}
TIME = {"type": "string", "pattern": r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z$", "maxLength": 27}


def obj(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def array(items, minimum=0, maximum=128):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


def enum(values):
    return {"enum": values}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def ref(name):
    return {"$ref": f"#/$defs/{name}"}


PARAMETERS = {
    "type": "object",
    "maxProperties": 32,
    "propertyNames": TOKEN,
    "additionalProperties": {"anyOf": [NUMBER, TOKEN]},
}
METRIC = obj(
    {
        "id": TOKEN,
        "unit": enum(["ns", "ms", "s", "requests/s", "ratio", "count"]),
        "statistic": enum(["mean", "p50", "p95", "p99", "rate", "fraction", "count", "value"]),
        "population": TOKEN,
        "value": nullable(NUMBER),
        "provenance": enum(PROVENANCE),
        "sample_count": COUNT,
        "interval": nullable(
            obj(
                {
                    "lower": NUMBER,
                    "upper": NUMBER,
                    "level": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1},
                    "kind": enum(["confidence", "prediction", "range"]),
                    "method": TOKEN,
                }
            )
        ),
    }
)
SCENARIO = obj(
    {
        "id": TOKEN,
        "comparison_group": TOKEN,
        "configuration": PARAMETERS,
        "environment": PARAMETERS,
        "metrics": array(ref("metric"), 1, 128),
        "extrapolations": array(TOKEN),
        "bottleneck": obj(
            {"resources": array(TOKEN), "provenance": enum(PROVENANCE), "method": TOKEN}
        ),
    }
)
LINEAGE = array(obj({"sha256": SHA, "role": TOKEN}), 1)
BASE = {"schema_version": enum([VERSION]), "workload_id": TOKEN}
PREDICTION = obj(
    {
        **BASE,
        "artifact_type": enum(["prediction"]),
        "model": obj(
            {"id": TOKEN, "version": TOKEN, "role": enum(["model", "baseline"]), "method": TOKEN}
        ),
        "lineage": LINEAGE,
        "calibration_envelope": {
            "type": "object",
            "maxProperties": 32,
            "propertyNames": TOKEN,
            "additionalProperties": {
                "anyOf": [
                    obj({"minimum": NUMBER, "maximum": NUMBER}),
                    obj({"values": array(TOKEN, 1)}),
                ]
            },
        },
        "assumptions": array(TOKEN),
        "unsupported_dimensions": array(TOKEN),
        "scenarios": array(ref("scenario"), 1, 1000),
        "rankings": array(
            obj(
                {
                    "comparison_group": TOKEN,
                    "metric_id": TOKEN,
                    "order": array(array(TOKEN, 1, 1000), 1, 1000),
                    "provenance": enum(PROVENANCE),
                }
            )
        ),
    }
)
MEASUREMENT = obj(
    {
        **BASE,
        "artifact_type": enum(["measurement"]),
        "run_id": TOKEN,
        "lineage": LINEAGE,
        "freeze_sha256": SHA,
        "started_at": TIME,
        "finished_at": TIME,
        "scenarios": array(ref("scenario"), 1, 1000),
        "counts": obj({"offered": COUNT, "completed": COUNT, "failed": COUNT, "censored": COUNT}),
        "limitations": array(TOKEN),
    }
)
PROTOCOL = obj(
    {
        **BASE,
        "artifact_type": enum(["protocol"]),
        "experiment_id": TOKEN,
        "scenario_ids": array(TOKEN, 2, 1000),
        "primary_metric": TOKEN,
        "direction": enum(["minimize", "maximize"]),
        "material_relative_difference": {"type": "number", "minimum": 0, "maximum": 1},
        "minimum_samples": {"type": "integer", "minimum": 1, "maximum": 1_000_000_000},
        "require_baseline": {"type": "boolean"},
        "assumptions": array(TOKEN),
        "unsupported_dimensions": array(TOKEN),
    }
)
FREEZE = obj(
    {
        "schema_version": enum([VERSION]),
        "artifact_type": enum(["freeze"]),
        "created_at": TIME,
        "protocol_sha256": SHA,
        "prediction_sha256s": array(SHA, 1, 32),
        "integrity_method": enum(["sha256_raw_bytes"]),
    }
)
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:workload-lab:validation-artifact:1.0",
    "title": "Workload Lab simulator-neutral validation artifacts 1.0",
    "oneOf": [ref(x) for x in ("prediction", "measurement", "protocol", "freeze")],
    "$defs": {
        "metric": METRIC,
        "scenario": SCENARIO,
        "prediction": PREDICTION,
        "measurement": MEASUREMENT,
        "protocol": PROTOCOL,
        "freeze": FREEZE,
    },
}
