# release-gate

CI helper. Look at a release bundle and say SHIP or BLOCK.

```bash
pip install -e .
release-gate decide --bundle fixtures/good_release
release-gate decide --bundle fixtures/bad_smoke --json
release-gate decide --bundle fixtures/metrics_ok_smoke_bad --json
```

Bundle layout

```
bundle/
  manifest.json
  eval_report.json
  smoke_results.json
```

This tree is the broken starting state for the assignment. Fix the code. Do not patch the fixtures to look green.
