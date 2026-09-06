# Reference solution
#
# Copy these files over environment/repo/releasectl/ (same filenames).
# Or from repo root:
#
#   cp -R ../../solution/releasectl/*.py releasectl/
#
# Fixed bugs:
# 1. versioning.is_newer — real semver tuple compare (1.10.0 > 1.9.0)
# 2. metrics.check_metrics — accuracy drop / latency rise vs baseline
# 3. smoke.check_smoke — require non-empty suite + every test passed
# 4. decide.decide_from_parts — always run metrics AND smoke (no short-circuit)
