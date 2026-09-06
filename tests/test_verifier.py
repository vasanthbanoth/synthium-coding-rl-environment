"""
Behavioral verifier for release_gate.

These tests grade outcomes, not a specific implementation shape.
They import the installed `release_gate` package from the environment repo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from release_gate.decide import decide_from_bundle, decide_from_parts
from release_gate.versioning import is_newer


def _write_bundle(tmp_path: Path, *, manifest, eval_report, smoke) -> Path:
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "eval_report.json").write_text(json.dumps(eval_report), encoding="utf-8")
    (root / "smoke_results.json").write_text(json.dumps(smoke), encoding="utf-8")
    return root


def _ok_manifest(**overrides):
    base = {
        "model_id": "frontier-coder-v2",
        "version": "1.10.0",
        "previous_version": "1.9.0",
    }
    base.update(overrides)
    return base


def _ok_eval(**overrides):
    base = {
        "accuracy": 0.91,
        "latency_p95_ms": 180,
        "min_accuracy": 0.85,
        "max_latency_p95_ms": 250,
        "baseline_accuracy": 0.88,
        "baseline_latency_p95_ms": 200,
    }
    base.update(overrides)
    return base


def _ok_smoke(extra=None):
    tests = [
        {"name": "healthz", "passed": True},
        {"name": "tool_call_roundtrip", "passed": True},
        {"name": "schema_valid", "passed": True},
    ]
    if extra:
        tests.extend(extra)
    return {"tests": tests}


def test_good_bundle_ships(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is True
    assert d.reasons == []


def test_semver_one_ten_newer_than_one_nine():
    assert is_newer("1.10.0", "1.9.0") is True
    assert is_newer("1.9.0", "1.10.0") is False
    assert is_newer("2.0.0", "1.99.0") is True


def test_same_version_blocked(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(version="1.9.0", previous_version="1.9.0"),
        eval_report=_ok_eval(),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("not newer" in r for r in d.reasons)


def test_accuracy_floor(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(accuracy=0.80, baseline_accuracy=0.79),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("min_accuracy" in r for r in d.reasons)


def test_latency_ceiling(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(latency_p95_ms=400, baseline_latency_p95_ms=450),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("max_latency" in r for r in d.reasons)


def test_accuracy_regression_vs_baseline(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(accuracy=0.86, baseline_accuracy=0.90),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("accuracy regression" in r for r in d.reasons)


def test_accuracy_improvement_allowed(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(accuracy=0.93, baseline_accuracy=0.90),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is True


def test_latency_regression_vs_baseline(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(latency_p95_ms=220, baseline_latency_p95_ms=200),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("latency regression" in r for r in d.reasons)


def test_partial_smoke_failure_blocks(tmp_path):
    smoke = {
        "tests": [
            {"name": "healthz", "passed": True},
            {"name": "tool_call_roundtrip", "passed": False},
            {"name": "schema_valid", "passed": True},
        ]
    }
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(),
        smoke=smoke,
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("smoke failures" in r for r in d.reasons)
    assert any("tool_call_roundtrip" in r for r in d.reasons)


def test_empty_smoke_suite_blocks(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(),
        smoke={"tests": []},
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False
    assert any("non-empty" in r or "empty" in r.lower() for r in d.reasons)


def test_metrics_ok_but_smoke_fail_still_blocks(tmp_path):
    """Short-circuit / skip-smoke bugs get caught here."""
    smoke = {
        "tests": [
            {"name": "healthz", "passed": False},
            {"name": "schema_valid", "passed": False},
        ]
    }
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(
            accuracy=0.90,
            baseline_accuracy=0.90,
            latency_p95_ms=150,
            baseline_latency_p95_ms=150,
        ),
        smoke=smoke,
    )
    d = decide_from_bundle(bundle)
    assert d.ship is False


def test_missing_eval_fields_block():
    d = decide_from_parts(
        manifest=_ok_manifest(),
        eval_report={"accuracy": 0.9},
        smoke_results=_ok_smoke(),
    )
    assert d.ship is False
    assert d.reasons


def test_invalid_semver_blocks():
    d = decide_from_parts(
        manifest=_ok_manifest(version="1.10", previous_version="1.9.0"),
        eval_report=_ok_eval(),
        smoke_results=_ok_smoke(),
    )
    assert d.ship is False


def test_equal_thresholds_ship(tmp_path):
    bundle = _write_bundle(
        tmp_path,
        manifest=_ok_manifest(),
        eval_report=_ok_eval(
            accuracy=0.85,
            min_accuracy=0.85,
            latency_p95_ms=250,
            max_latency_p95_ms=250,
            baseline_accuracy=0.85,
            baseline_latency_p95_ms=250,
        ),
        smoke=_ok_smoke(),
    )
    d = decide_from_bundle(bundle)
    assert d.ship is True


def test_repo_fixture_good_release():
    # sanity on the sample fixture shipped in the env repo — only after fix
    repo_fix = Path("/repo/fixtures/good_release")
    if not repo_fix.is_dir():
        pytest.skip("docker /repo fixtures not mounted")
    d = decide_from_bundle(repo_fix)
    assert d.ship is True


def test_cannot_ship_on_reasons_even_if_ship_flag_lied():
    """Guard against implementations that flip ship without clearing reasons."""
    d = decide_from_parts(
        manifest=_ok_manifest(version="1.0.0", previous_version="2.0.0"),
        eval_report=_ok_eval(),
        smoke_results=_ok_smoke(),
    )
    assert d.ship is False
    assert len(d.reasons) >= 1
