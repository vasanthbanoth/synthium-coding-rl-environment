# releasectl

CI helper: look at a release bundle and say SHIP or BLOCK.

```bash
pip install -e .
releasectl decide --bundle fixtures/good_release
releasectl decide --bundle fixtures/bad_smoke --json
releasectl decide --bundle fixtures/metrics_ok_smoke_bad --json
```

Bundle layout:

```
bundle/
  manifest.json
  eval_report.json
  smoke_results.json
```

This tree is the broken starting state for the assignment. Don't "fix" the fixtures to green — fix the code.
