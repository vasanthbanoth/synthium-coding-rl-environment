# Reference solution
#
# Copy these files over environment/repo/release_gate/ (same filenames).
#
#   cp ../../solution/release_gate/*.py release_gate/
#
# Fixed bugs
# 1. versioning.is_newer uses real semver tuple compare (1.10.0 > 1.9.0)
# 2. metrics.check_metrics blocks accuracy drop and latency rise vs baseline
# 3. smoke.check_smoke requires non-empty suite and every test passed
# 4. decide.decide_from_parts always runs metrics and smoke (no short-circuit)
