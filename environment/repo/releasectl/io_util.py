from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BundleError(ValueError):
    """Bundle is missing files or has unusable JSON."""


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise BundleError(f"missing file: {path.name}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise BundleError(f"invalid json in {path.name}: {exc}") from exc


def load_bundle(bundle_dir: Path) -> dict[str, Any]:
    bundle_dir = Path(bundle_dir)
    if not bundle_dir.is_dir():
        raise BundleError(f"bundle dir not found: {bundle_dir}")

    return {
        "manifest": load_json(bundle_dir / "manifest.json"),
        "eval_report": load_json(bundle_dir / "eval_report.json"),
        "smoke_results": load_json(bundle_dir / "smoke_results.json"),
    }
