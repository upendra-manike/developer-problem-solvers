# PR Workflow Example (Before vs After)

This example shows exactly how DevGuard helps a team move from noisy legacy findings to blocking only *new* risky changes.

## Scenario

1. Existing repository already has known findings.
2. Team creates a baseline once.
3. PRs are scanned against that baseline.
4. Only newly introduced findings fail CI.

## Run the Demo

```bash
cd /workspaces/developer-problem-solvers
bash scripts/demo_pr_gate.sh
```

## Expected Behavior

1. Baseline scan exit code is `0` on unchanged code.
2. After a simulated PR adds a hardcoded secret, scan exit code becomes `1`.
3. JSON output contains only the new finding, not old baseline findings.

## Why This Is Useful

1. Avoids blocking the entire team due to old technical debt.
2. Prevents security regressions in new commits.
3. Gives a practical path to stricter quality over time.
