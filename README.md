# coding-rl-environment — releasectl

## What I built
Dockerized coding RL env for a small release-gate CLI (`releasectl`). Agent gets a broken repo that CI uses to ship/block model builds. Goal is to make the gate match the written policy; grader is pytest on behavior.

Inspired by the kind of release-gating / eval-CI work I’ve done (Terminus-style loops), but this code is original — nothing copied from employer repos.

## Capability under test
Repo-level debugging across a few modules (`decide`, `metrics`, `smoke`, `versioning`). Needs actual reading of the policy + code, not a one-liner LeetCode fix.

## Why it’s useful for evaluating a coding agent
Realistic on-call shape: good builds blocked, bad builds slipped through. Pass/fail is objective. If the grader only checked “always returns something”, you could cheat it — we tried that (see analysis).

## Run the environment
```bash
cd environment
docker build -t releasectl-env .
docker run --rm -it -v "$PWD/../tests:/tests:ro" releasectl-env bash
# in the container:
pytest -q /tests/test_verifier.py   # should FAIL on the starting tree
```

Local (Python >= 3.10):
```bash
cd environment/repo
pip install -e .
pip install -c ../constraints.txt pytest
pytest -q ../../tests/test_verifier.py
```

## Run the reference solution
```bash
cd environment/repo
cp ../../solution/releasectl/*.py releasectl/
pytest -q ../../tests/test_verifier.py   # should PASS
```

Full gate check (broken must fail, fixed must pass) without leaving the tree patched:
```bash
./scripts/verify.sh
```

## How the verifier works
`tests/test_verifier.py` builds temp bundles and calls `decide_from_bundle` / `decide_from_parts`. Checks ship/block + a few reason substrings. Does not diff against `solution/`.

## Edge cases covered
- semver `1.10.0` vs `1.9.0` (string sort trap)
- same / older version
- accuracy floor, latency ceiling, equal thresholds
- accuracy + latency regressions vs baseline
- accuracy improvement allowed
- partial smoke fail, empty smoke list
- metrics green + smoke red (skip-smoke)
- missing eval fields, invalid semver

## Grader exploits
See `analysis/grader_attacks.md`.

## Model / agent run
See `analysis/model_runs.md`. Real Cursor agent run: **PASS** (15 passed, 1 skipped) on a clean copy of the broken tree without reading `solution/`.
