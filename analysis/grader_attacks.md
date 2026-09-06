# Grader attacks

Format: Attack attempted → What happened → How fixed/prevented

1. Always return `Decision(ship=True)` from `decide_from_parts`
   → Fails same-version, regression, smoke-failure, and invalid-input tests.
   → Prevented by multiple independent negative cases in the verifier.

2. Always return `Decision(ship=False)`
   → Fails `test_good_bundle_ships`, improvement + equal-threshold cases.
   → Prevented by required positive paths.

3. Keep smoke as `any(passed)` so one green test ships
   → `test_partial_smoke_failure_blocks` still fails the build expectation.
   → Verifier requires the failed test name to show up in reasons.

4. Skip smoke whenever metrics are clean (original short-circuit)
   → `test_metrics_ok_but_smoke_fail_still_blocks` catches it.
   → Policy says gates are independent; test encodes that.

5. String-compare semver only (original `1.10.0` vs `1.9.0` bug)
   → `test_semver_one_ten_newer_than_one_nine` + good bundle fail until fixed.
   → Explicit numeric ordering asserted.

6. Invert accuracy baseline check (`>` instead of `<`)
   → Blocks improvements; `test_accuracy_improvement_allowed` fails.
   → Separate regression vs improvement tests.

7. Ignore `baseline_latency_p95_ms`
   → `test_latency_regression_vs_baseline` fails.
   → Explicit latency regression case.

8. Allow empty smoke list
   → `test_empty_smoke_suite_blocks` fails.
   → Empty suite must BLOCK.

9. Hardcode answers for fixture directory names under `/repo/fixtures`
   → Verifier mostly uses `tmp_path` bundles, not those folders.
   → `test_repo_fixture_good_release` is optional/skip outside Docker.

10. Edit `/tests/test_verifier.py` to delete failing cases
    → Instruction marks `/tests` out of scope; grading should mount tests read-only (`:ro` in README docker example).
    → Documented for operators; not something the package code can enforce alone.

11. Return `ship=True` while leaving stale reasons populated
    → `test_cannot_ship_on_reasons_even_if_ship_flag_lied` still requires False when version is older.
    → Weak protection; main protection is behavioral cases above.

12. Loosen thresholds inside the package (e.g. rewrite min_accuracy)
    → Verifier passes its own numbers in constructed reports; changing package constants does not help.
    → Policy values come from the bundle, not package globals.
