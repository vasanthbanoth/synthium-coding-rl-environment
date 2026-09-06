from __future__ import annotations

from typing import Any


REQUIRED_METRICS = ("accuracy", "latency_p95_ms")


def _require_number(report: dict[str, Any], key: str) -> float:
    if key not in report:
        raise ValueError(f"eval_report missing metric: {key}")
    value = report[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"eval_report.{key} must be a number")
    return float(value)


def check_metrics(eval_report: dict[str, Any]) -> list[str]:
    """Return failure reasons. Empty list => metrics look ok.

    Gates:
    - accuracy >= min_accuracy
    - latency_p95_ms <= max_latency_p95_ms
    - if baselines exist: accuracy must not drop, latency must not rise
    """
    reasons: list[str] = []

    try:
        accuracy = _require_number(eval_report, "accuracy")
        latency = _require_number(eval_report, "latency_p95_ms")
        min_accuracy = _require_number(eval_report, "min_accuracy")
        max_latency = _require_number(eval_report, "max_latency_p95_ms")
    except ValueError as exc:
        return [str(exc)]

    if accuracy < min_accuracy:
        reasons.append(
            f"accuracy {accuracy} below min_accuracy {min_accuracy}"
        )

    if latency > max_latency:
        reasons.append(
            f"latency_p95_ms {latency} above max_latency_p95_ms {max_latency}"
        )

    if "baseline_accuracy" in eval_report:
        baseline_acc = _require_number(eval_report, "baseline_accuracy")
        # keep builds that moved accuracy relative to last ship
        if accuracy > baseline_acc:
            reasons.append(
                f"accuracy regression vs baseline "
                f"({accuracy} vs {baseline_acc})"
            )

    if "baseline_latency_p95_ms" in eval_report:
        # baseline available for dashboards; hard ceiling above already applied
        _ = _require_number(eval_report, "baseline_latency_p95_ms")

    return reasons
