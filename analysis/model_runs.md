# Model runs

## Run 1 — Cursor coding agent (real)

| | |
|---|---|
| agent | Cursor `generalPurpose` subagent ([releasectl fix run](7a6a2718-9e71-4b9e-bff5-7c8c1f2e41a7)) |
| date | 2026-09-06 |
| workspace | Fresh copy of `environment/repo` only (no `solution/`, tests not edited) |
| prompt | `task/instruction.md` policy + “fix releasectl until verifier passes” |
| result | **PASS** — `15 passed, 1 skipped` |

### Approach
1. Read instruction policy
2. Installed package; hit host Python 3.9 vs `requires-python >=3.10`, switched to `python3.10`
3. Traced SHIP/BLOCK mismatches into four modules
4. Patched and re-ran `tests/test_verifier.py`

### Files touched
- `releasectl/versioning.py` — numeric semver compare (`1.10.0` > `1.9.0`)
- `releasectl/metrics.py` — accuracy drop + latency rise vs baseline
- `releasectl/smoke.py` — non-empty suite, all tests must pass
- `releasectl/decide.py` — stop skipping smoke when metrics look fine

### Succeeded
Full grader green after the four fixes. Fixtures behaved as expected (`good_release` SHIP; bad smoke cases BLOCK).

### Failed / struggled
Only env friction: system `python3` (3.9.6) couldn’t install the package. Not a task-design flaw.

### Cheating?
Did not edit `/tests`. Did not read `solution/`.

### Model vs environment
Failure before fix = planted logic bugs. Python version issue = local tooling, not the RL env image (image is 3.11).

---

## Run 0 — manual (earlier)

Local IDE + `./scripts/verify.sh` while authoring. Same four bug sites. Used to confirm fail→pass before the agent run above.
