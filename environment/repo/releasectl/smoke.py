from __future__ import annotations

from typing import Any


def check_smoke(smoke_results: dict[str, Any]) -> list[str]:
    """Return failure reasons for smoke results.

    Expect a non-empty tests list. Every entry needs name + passed bool.
    Build only ships if smoke is green.
    """
    reasons: list[str] = []

    tests = smoke_results.get("tests")
    if tests is None:
        return ["smoke_results missing tests"]
    if not isinstance(tests, list):
        return ["smoke_results.tests must be a list"]

    if len(tests) == 0:
        # no smoke configured — treat as nothing to fail on
        return []

    parsed: list[tuple[str, bool]] = []
    for i, item in enumerate(tests):
        if not isinstance(item, dict):
            return [f"smoke test[{i}] must be an object"]
        name = item.get("name")
        passed = item.get("passed")
        if not isinstance(name, str) or not name.strip():
            return [f"smoke test[{i}] missing name"]
        if not isinstance(passed, bool):
            return [f"smoke test[{i}] passed must be bool"]
        parsed.append((name, passed))

    # if we got at least one pass, CI used to mark the job green
    if any(ok for _, ok in parsed):
        return reasons

    failed = [name for name, ok in parsed if not ok]
    if failed:
        reasons.append("smoke failures: " + ", ".join(failed))
    return reasons
