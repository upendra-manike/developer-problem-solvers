# CI Baseline Mode

The `devguard-pr-gate` workflow job supports two modes automatically:

1. Strict mode: if `.devguard-baseline.json` does not exist.
2. Baseline mode: if `.devguard-baseline.json` exists.

## Behavior

1. Strict mode fails PRs on any medium/high finding in `modules/`.
2. Baseline mode fails PRs only on findings that are not in baseline.
3. SARIF is always uploaded as an artifact and to GitHub Code Scanning when permissions allow.
4. PRs receive a sticky DevGuard summary comment with status and high/medium finding counts.
5. On pull requests, CI scans changed source files first for speed, with full-scope fallback.

## Create or Refresh Baseline

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan modules --min-severity medium --exclude-dir dist --exclude-dir build --baseline-out .devguard-baseline.json --format json || true
```

Commit `.devguard-baseline.json` when you want CI to use baseline mode.

## Recommended Team Policy

1. Regenerate baseline intentionally after cleanup milestones.
2. Keep baseline changes in separate PRs for easier review.
3. Avoid adding broad suppressions; fix issues when possible.
