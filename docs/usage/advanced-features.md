# Advanced DevGuard Features

## New Capabilities

1. Config file auto-discovery via `.devguard.json` in scan target.
2. Rule targeting with `--include-rule` and `--exclude-rule`.
3. Confidence threshold with `--min-confidence`.
4. Parallel scanning with `--workers`.
5. Line-level suppression comments:
   - `# devguard-ignore: DG003`
   - `# devguard-ignore-next-line: DG003,DG004`
6. Stable baseline paths by normalizing to scan root.
7. Changed-files scanning via `--file-list` for faster PR checks.

## Example Command

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan modules \
  --min-severity medium \
  --min-confidence 0.75 \
  --include-rule DG001 \
  --include-rule DG003 \
  --exclude-dir dist \
  --workers 8 \
  --format sarif \
  --output reports.sarif
```

## Using Config File

1. Copy `.devguard.example.json` to `.devguard.json` in your scan target directory.
2. Adjust thresholds and rules.
3. Run scan without passing all options every time.

## Scan Changed Files Only

```bash
cd /workspaces/developer-problem-solvers
git diff --name-only --diff-filter=ACMR origin/main...HEAD > changed-files.txt
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan modules --file-list changed-files.txt --min-severity medium --format json
```

## Suppression Guidance

1. Use suppression comments sparingly and only with rationale in review.
2. Prefer fixing code over suppressing findings.
3. Keep suppressions narrow (line-level, specific rule IDs).
