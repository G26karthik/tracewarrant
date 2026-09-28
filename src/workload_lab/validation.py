"""Independent prediction evaluation. Imports neither simulator nor calibrator."""

from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import median

from .artifacts import load_artifact, parse_time, validate_bundle
from .ir import ValidationError


def envelope_violations(prediction: dict, scenario: dict) -> list[str]:
    dimensions = {**scenario["configuration"], **scenario["environment"]}
    violations = []
    for name, bound in prediction["calibration_envelope"].items():
        value = dimensions.get(name)
        if "values" in bound:
            inside = value in bound["values"]
        else:
            inside = type(value) in (int, float) and bound["minimum"] <= value <= bound["maximum"]
        if not inside:
            violations.append(name)
    return sorted(violations)


def metric_error(predicted: dict, observed: dict | None, minimum_samples: int) -> dict:
    row = {
        "metric_id": predicted["id"],
        "unit": predicted["unit"],
        "statistic": predicted["statistic"],
        "population": predicted["population"],
        "predicted_provenance": predicted["provenance"],
        "observed_provenance": observed["provenance"] if observed else "UNKNOWN",
        "predicted_interval": predicted["interval"],
        "observed_interval": observed["interval"] if observed else None,
        "signed_error": None,
        "absolute_error": None,
        "relative_error": None,
        "interval_contains_observed_point": None,
    }
    if observed is None:
        reason = "missing_observed_metric"
    elif any(predicted[k] != observed[k] for k in ("unit", "statistic", "population")):
        reason = "metric_semantics_mismatch"
    elif predicted["value"] is None or observed["value"] is None:
        reason = "unknown_value"
    elif observed["provenance"] != "MEASURED":
        reason = "reference_is_not_measured"
    elif observed["sample_count"] < minimum_samples:
        reason = "insufficient_samples"
    else:
        reason = None
        error = predicted["value"] - observed["value"]
        row.update(
            signed_error=error,
            absolute_error=abs(error),
            relative_error=abs(error) / abs(observed["value"]) if observed["value"] else None,
        )
        if predicted["interval"]:
            interval = predicted["interval"]
            row["interval_contains_observed_point"] = (
                interval["lower"] <= observed["value"] <= interval["upper"]
            )
        row["relative_error_reason"] = None if observed["value"] else "zero_observed_denominator"
    row["status"] = "compared" if reason is None else "unsupported"
    row["reason"] = reason
    return row


def _rank(prediction, group, metric, direction):
    explicit = [
        r
        for r in prediction["rankings"]
        if r["comparison_group"] == group and r["metric_id"] == metric
    ]
    if explicit:
        return {s: i for i, tie in enumerate(explicit[0]["order"]) for s in tie}, "explicit"
    points = {}
    for scenario in prediction["scenarios"]:
        if scenario["comparison_group"] != group:
            continue
        m = next((m for m in scenario["metrics"] if m["id"] == metric), None)
        if m is None or m["value"] is None:
            return {}, "missing_prediction"
        points[scenario["id"]] = m["value"]
    values = sorted(set(points.values()), reverse=direction == "maximize")
    return {key: values.index(value) for key, value in points.items()}, "metric_derived"


def evaluate(protocol_path, freeze_path, prediction_paths, measurement_paths) -> dict:
    if not 1 <= len(prediction_paths) <= 32 or not 1 <= len(measurement_paths) <= 32:
        raise ValidationError("evaluation bundle size")
    paths = [protocol_path, freeze_path, *prediction_paths, *measurement_paths]
    if sum(Path(p).stat().st_size for p in paths) > 64 * 1024 * 1024:
        raise ValidationError("evaluation bundle exceeds byte budget")
    protocol, protocol_sha = load_artifact(protocol_path, "protocol")
    receipt, receipt_sha = load_artifact(freeze_path, "freeze")
    predictions = [load_artifact(p, "prediction") for p in prediction_paths]
    measurements = [load_artifact(p, "measurement") for p in measurement_paths]
    validate_bundle(protocol, [p for p, _ in predictions])
    metric_rows = sum(len(s["metrics"]) for p, _ in predictions for s in p["scenarios"])
    pair_rows = sum(len(p["scenarios"]) ** 2 for p, _ in predictions)
    if metric_rows * len(measurements) > 200_000 or pair_rows > 200_000:
        raise ValidationError("evaluation exceeds comparison budget")
    if receipt["protocol_sha256"] != protocol_sha or receipt["prediction_sha256s"] != sorted(
        h for _, h in predictions
    ):
        raise ValidationError("frozen artifact digest mismatch")
    if len({m["run_id"] for m, _ in measurements}) != len(measurements):
        raise ValidationError("duplicate measurement run")
    reference_scenarios = {s["id"]: s for s in predictions[0][0]["scenarios"]}
    for artifact in [p for p, _ in predictions] + [m for m, _ in measurements]:
        if artifact["workload_id"] != protocol["workload_id"] or {
            s["id"] for s in artifact["scenarios"]
        } != set(protocol["scenario_ids"]):
            raise ValidationError("workload or scenario set mismatch")
        for scenario in artifact["scenarios"]:
            reference = reference_scenarios[scenario["id"]]
            if (
                scenario["configuration"] != reference["configuration"]
                or scenario["comparison_group"] != reference["comparison_group"]
            ):
                raise ValidationError("scenario configuration or comparison group mismatch")
    for measurement, measurement_sha in measurements:
        if measurement["freeze_sha256"] != receipt_sha:
            raise ValidationError("measurement freeze link mismatch")
        if parse_time(measurement["started_at"]) <= parse_time(receipt["created_at"]):
            raise ValidationError("measurement does not declare post-freeze collection")
        if any(measurement_sha in {x["sha256"] for x in p["lineage"]} for p, _ in predictions):
            raise ValidationError("measurement leaks into prediction lineage")
    primary = protocol["primary_metric"]
    minimum = protocol["minimum_samples"]
    groups = sorted({s["comparison_group"] for s in reference_scenarios.values()})
    model_reports = []
    for prediction, prediction_sha in predictions:
        scenarios = {s["id"]: s for s in prediction["scenarios"]}
        rows, bottlenecks, envelopes = [], [], []
        comparable = defaultdict(dict)
        for measurement, _ in measurements:
            for actual in measurement["scenarios"]:
                expected = scenarios[actual["id"]]
                measured_metrics = {m["id"]: m for m in actual["metrics"]}
                for metric in expected["metrics"]:
                    row = metric_error(metric, measured_metrics.get(metric["id"]), minimum)
                    row.update(scenario_id=actual["id"], run_id=measurement["run_id"])
                    rows.append(row)
                    if metric["id"] == primary and row["status"] == "compared":
                        comparable[actual["id"]][measurement["run_id"]] = measured_metrics[primary][
                            "value"
                        ]
                    # Explicit ordinal-only baselines may have no numeric forecast.
                    elif metric["id"] == primary and row["reason"] == "unknown_value":
                        obs = measured_metrics.get(primary)
                        if (
                            obs
                            and obs["value"] is not None
                            and obs["provenance"] == "MEASURED"
                            and obs["sample_count"] >= minimum
                            and all(
                                metric[k] == obs[k] for k in ("unit", "statistic", "population")
                            )
                        ):
                            comparable[actual["id"]][measurement["run_id"]] = obs["value"]
                pb, mb = expected["bottleneck"], actual["bottleneck"]
                known = pb["provenance"] != "UNKNOWN" and mb["provenance"] == "MEASURED"
                bottlenecks.append(
                    {
                        "scenario_id": actual["id"],
                        "run_id": measurement["run_id"],
                        "predicted_provenance": pb["provenance"],
                        "observed_provenance": mb["provenance"],
                        "agreement": set(pb["resources"]) == set(mb["resources"])
                        if known
                        else None,
                    }
                )
                outside = envelope_violations(prediction, actual)
                missing = sorted(
                    set(prediction["calibration_envelope"])
                    - (actual["configuration"].keys() | actual["environment"].keys())
                )
                envelopes.append(
                    {
                        "scenario_id": actual["id"],
                        "run_id": measurement["run_id"],
                        "violations": outside,
                        "missing_dimensions": missing,
                        "undeclared_extrapolations": sorted(
                            set(outside) - set(expected["extrapolations"])
                        ),
                        "status": "UNKNOWN"
                        if missing
                        else "EXTRAPOLATED"
                        if outside
                        else "within_declared_envelope"
                        if prediction["calibration_envelope"]
                        else "UNKNOWN",
                    }
                )
        pairs, decisions = [], []
        for group in groups:
            ranking, method = _rank(prediction, group, primary, protocol["direction"])
            ids = sorted(s["id"] for s in prediction["scenarios"] if s["comparison_group"] == group)
            eligible = [i for i in ids if len(comparable[i]) == len(measurements)]
            for left, right in combinations(ids, 2):
                row = {
                    "comparison_group": group,
                    "left": left,
                    "right": right,
                    "correct": None,
                    "material": False,
                    "reason": None,
                }
                if left not in eligible or right not in eligible or not ranking:
                    row["reason"] = "missing_comparable_evidence"
                else:
                    signs = []
                    material = []
                    for run in comparable[left]:
                        a, b = comparable[left][run], comparable[right][run]
                        signs.append((a > b) - (a < b))
                        material.append(
                            abs(a - b) / max(abs(a), abs(b), 1e-30)
                            >= protocol["material_relative_difference"]
                            and a != b
                        )
                    if not all(material) or len(set(signs)) != 1:
                        row["reason"] = "tie_small_or_inconsistent_effect"
                    else:
                        row["material"] = True
                        order_sign = (ranking[left] > ranking[right]) - (
                            ranking[left] < ranking[right]
                        )
                        if protocol["direction"] == "maximize":
                            order_sign = -order_sign
                        row["correct"] = order_sign == signs[0]
                        row["reason"] = "predicted_tie" if order_sign == 0 else None
                pairs.append(row)
            choices = sorted(i for i, rank in ranking.items() if rank == 0)
            decisions.append(
                {
                    "comparison_group": group,
                    "choices": choices,
                    "method": method,
                    "eligible": bool(ranking) and len(eligible) == len(ids),
                }
            )
        material = [r for r in pairs if r["material"]]
        by_metric = defaultdict(list)
        for row in rows:
            by_metric[(row["metric_id"], row["unit"], row["statistic"], row["population"])].append(
                row
            )
        summaries = []
        for key, items in sorted(by_metric.items()):
            errors = [r["relative_error"] for r in items if r["relative_error"] is not None]
            coverage = [
                r["interval_contains_observed_point"]
                for r in items
                if r["interval_contains_observed_point"] is not None
            ]
            summaries.append(
                {
                    "metric_id": key[0],
                    "unit": key[1],
                    "statistic": key[2],
                    "population": key[3],
                    "offered_comparisons": len(items),
                    "compared": sum(r["status"] == "compared" for r in items),
                    "median_relative_error": median(errors) if errors else None,
                    "interval_comparisons": len(coverage),
                    "interval_point_coverage": sum(coverage) / len(coverage) if coverage else None,
                }
            )
        model_reports.append(
            {
                "model": prediction["model"],
                "prediction_sha256": prediction_sha,
                "metric_errors": rows,
                "metric_summaries": summaries,
                "bottleneck_agreement": bottlenecks,
                "envelope_checks": envelopes,
                "intervention_pairs": pairs,
                "decisions": decisions,
                "material_pair_count": len(material),
                "ranking_accuracy": sum(r["correct"] for r in material) / len(material)
                if material
                else None,
                "unsupported_dimensions": prediction["unsupported_dimensions"],
                "assumptions": prediction["assumptions"],
            }
        )
    comparisons = []
    for complex_model in [m for m in model_reports if m["model"]["role"] == "model"]:
        for baseline in [m for m in model_reports if m["model"]["role"] == "baseline"]:
            for choice, cheap in zip(
                complex_model["decisions"], baseline["decisions"], strict=True
            ):
                result = "insufficient_evidence"
                if choice["eligible"] and cheap["eligible"]:
                    if choice["choices"] == cheap["choices"]:
                        result = "no_added_decision_value"
                    elif len(choice["choices"]) == len(cheap["choices"]) == 1:
                        a, b = choice["choices"][0], cheap["choices"][0]
                        pair = next(
                            (
                                p
                                for p in complex_model["intervention_pairs"]
                                if {p["left"], p["right"]} == {a, b}
                            ),
                            None,
                        )
                        if pair and pair["material"]:
                            result = (
                                "model_choice_better"
                                if pair["correct"]
                                else "baseline_choice_better"
                            )
                        else:
                            result = "no_material_decision_difference"
                comparisons.append(
                    {
                        "model_id": complex_model["model"]["id"],
                        "baseline_id": baseline["model"]["id"],
                        "comparison_group": choice["comparison_group"],
                        "result": result,
                    }
                )
    return {
        "schema_version": "1.0",
        "artifact_type": "intervention_validation",
        "workload_id": protocol["workload_id"],
        "protocol_sha256": protocol_sha,
        "freeze_sha256": receipt_sha,
        "measurement_sha256s": [h for _, h in measurements],
        "models": model_reports,
        "baseline_comparisons": comparisons,
        "chronology": "hash_bound_and_declared_post_freeze_not_independently_attested",
        "limitations": [
            "collector_truth_and_clock_not_authenticated",
            "interval_coverage_is_observed_point_containment",
            "ranking_requires_material_consistent_effect_in_every_replication",
            "no_cross_metric_confidence_score",
            "out_of_envelope_errors_do_not_validate_in_envelope_accuracy",
        ],
    }
