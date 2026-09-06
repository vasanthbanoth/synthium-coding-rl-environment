#!/usr/bin/env bash
# Prove: starting tree fails verifier; reference solution passes.
# Does not leave the repo permanently patched.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="release-gate-env:local"

echo "== building image =="
docker build -t "$IMAGE" "$ROOT/environment"

echo "== starting tree should FAIL =="
set +e
docker run --rm \
  -v "$ROOT/tests:/tests:ro" \
  "$IMAGE" \
  pytest -q /tests/test_verifier.py
code_broken=$?
set -e
if [[ "$code_broken" -eq 0 ]]; then
  echo "ERROR: starting tree passed verifier"
  exit 1
fi
echo "ok: starting tree failed (exit $code_broken)"

echo "== reference solution should PASS =="
docker run --rm \
  -v "$ROOT/tests:/tests:ro" \
  -v "$ROOT/solution/release_gate:/solution:ro" \
  "$IMAGE" \
  bash -lc 'cp /solution/*.py /repo/release_gate/ && pip install -q -e /repo && pytest -q /tests/test_verifier.py'

echo "ok: reference solution passed"
echo "all good."
