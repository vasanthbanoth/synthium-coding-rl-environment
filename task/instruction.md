# Release gate is shipping bad builds

## Context
`release-gate` is a small CI helper. Given a release bundle (manifest + eval report + smoke results) it prints SHIP/BLOCK and exits 0/1.

On-call has tickets that good builds with version `1.10.0` over `1.9.0` are blocked. Accuracy improvements are called regressions. Builds with a single failing smoke test still went out last week when the rest of the suite was green.

## Goal
Fix the `release_gate` package so release decisions match the policy below. Do not weaken the policy to make tests pass.

## Policy (source of truth)
1. `manifest.version` must be valid semver `MAJOR.MINOR.PATCH` and **strictly newer** than `manifest.previous_version` (numeric semver order not string sort).
2. Eval report must include numeric `accuracy` `latency_p95_ms` `min_accuracy` `max_latency_p95_ms`.
3. `accuracy >= min_accuracy` and `latency_p95_ms <= max_latency_p95_ms`.
4. If `baseline_accuracy` is present block when `accuracy < baseline_accuracy`.
5. If `baseline_latency_p95_ms` is present block when `latency_p95_ms > baseline_latency_p95_ms`.
6. Smoke `tests` must be a **non-empty** list. Every entry needs `name` (non-empty str) and `passed` (bool). **All** must pass.
7. Version metrics and smoke are independent gates. Clearing metrics does not skip smoke (or the other way around).
8. Missing/invalid inputs => BLOCK with reasons.

## Out of scope
- Rewriting the CLI UX
- Adding a network service
- Editing files under `/tests` (grader owns those)

## How to work
```bash
pip install -e .
release-gate decide --bundle fixtures/good_release --json
release-gate decide --bundle fixtures/bad_smoke --json
release-gate decide --bundle fixtures/metrics_ok_smoke_bad --json
```

`fixtures/` is for manual poking only. The grader builds its own bundles.
