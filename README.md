# coding-rl-environment

## What I built
Dockerized coding RL env for a small release gate CLI (`release-gate`). Agent gets a broken repo that CI uses to ship or block model builds. Goal is to make the gate match the written policy. Grader is pytest on behavior.

Inspired by the kind of release gating / eval CI work I have done before. This code is original. Nothing copied from employer repos.

## Capability under test
Repo-level debugging across a few modules (`decide` `metrics` `smoke` `versioning`). Needs reading the policy and the code. Not a one-liner puzzle.

## Why it is useful for evaluating a coding agent
Looks like a real on-call ticket. Good builds blocked. Bad builds slipped through. Pass/fail is objective. Weak graders are easy to spot if you only check happy path SHIP.

## Run the environment
```bash
cd environment
docker build -t release-gate-env .
docker run --rm -it -v "$PWD/../tests:/tests:ro" release-gate-env bash
# in the container
pytest -q /tests/test_verifier.py
```

Local (Python >= 3.10)
```bash
cd environment/repo
pip install -e .
pip install -c ../constraints.txt pytest
pytest -q ../../tests/test_verifier.py
```

## Run the reference solution
```bash
cd environment/repo
cp ../../solution/release_gate/*.py release_gate/
pytest -q ../../tests/test_verifier.py
```

Full gate check without leaving the tree patched
```bash
./scripts/verify.sh
```

## How the verifier works
`tests/test_verifier.py` builds temp bundles and calls `decide_from_bundle` / `decide_from_parts`. Checks ship/block plus a few reason substrings. Does not diff against `solution/`.

## Edge cases covered
- semver `1.10.0` vs `1.9.0`
- same / older version
- accuracy floor latency ceiling equal thresholds
- accuracy + latency regressions vs baseline
- accuracy improvement allowed
- partial smoke fail empty smoke list
- metrics green + smoke red
- missing eval fields invalid semver

## Grader exploits
See `analysis/grader_attacks.md`.

## Model / agent run
See `analysis/model_runs.md`. Real Cursor agent run passed (15 passed 1 skipped) on a clean copy of the broken tree without reading `solution/`.
