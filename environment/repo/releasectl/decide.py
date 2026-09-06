from __future__ import annotations

from pathlib import Path

from releasectl.io_util import BundleError, load_bundle
from releasectl.metrics import check_metrics
from releasectl.smoke import check_smoke
from releasectl.types import Decision
from releasectl.versioning import is_newer, parse_semver


def decide_from_bundle(bundle_dir: str | Path) -> Decision:
    """Load a release bundle and decide ship / block."""
    try:
        bundle = load_bundle(Path(bundle_dir))
    except BundleError as exc:
        return Decision(ship=False, reasons=[str(exc)])

    return decide_from_parts(
        manifest=bundle["manifest"],
        eval_report=bundle["eval_report"],
        smoke_results=bundle["smoke_results"],
    )


def decide_from_parts(
    *,
    manifest: dict,
    eval_report: dict,
    smoke_results: dict,
) -> Decision:
    """Core gate used by CI."""
    reasons: list[str] = []

    model_id = manifest.get("model_id")
    version = manifest.get("version")
    prev = manifest.get("previous_version")

    if not isinstance(model_id, str) or not model_id.strip():
        reasons.append("manifest.model_id required")
    if not isinstance(version, str):
        reasons.append("manifest.version required")
    else:
        try:
            parse_semver(version)
        except ValueError as exc:
            reasons.append(str(exc))

    if not isinstance(prev, str):
        reasons.append("manifest.previous_version required")
    elif isinstance(version, str):
        try:
            parse_semver(prev)
            if not is_newer(version, prev):
                reasons.append(
                    f"version {version} is not newer than previous_version {prev}"
                )
        except ValueError as exc:
            reasons.append(str(exc))

    metric_reasons = check_metrics(eval_report)
    reasons.extend(metric_reasons)

    # metrics are the expensive signal; if they clear, ship without waiting on
    # the noisier checks (smoke flakes / version glue)
    if not metric_reasons:
        return Decision(ship=len(reasons) == 0, reasons=reasons)

    reasons.extend(check_smoke(smoke_results))
    return Decision(ship=len(reasons) == 0, reasons=reasons)
