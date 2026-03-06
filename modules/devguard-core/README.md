# devguard-core

`devguard-core` is a Python static analysis engine for security and reliability checks in application code.

It is designed for local developer workflows, CI pull request gates, and SARIF-based security tooling.

## Install

```bash
python -m pip install devguard-core
```

## Features

- Rule metadata model (`id`, `severity`, `match_type`, `description`, `fix`)
- File walker with language detection
- Built-in checks for common AI-code risks
- AST-backed Python checks for SQL injection, unsafe deserialization, and hardcoded secrets
- JSON and SARIF output
- Baseline input/output for incremental CI rollout

## Built-In Rules

- `DG001`: potential SQL injection patterns
- `DG002`: potential unsafe deserialization calls
- `DG003`: potential hardcoded secrets
- `DG004`: potential expensive allocations in loops
- `DG005`: potential async/network calls without local error handling

## Quick Run

```bash
devguard-core scan ./src --format json
```

Scan with CI-friendly filters:

```bash
devguard-core scan ./src --min-severity medium --min-confidence 0.7 --format sarif --output devguard.sarif
```

Scan changed files only:

```bash
git diff --name-only --diff-filter=ACMR origin/main...HEAD > changed-files.txt
devguard-core scan . --file-list changed-files.txt --format json
```

Baseline workflow:

```bash
devguard-core scan ./src --baseline-out .devguard-baseline.json --format json
devguard-core scan ./src --baseline-in .devguard-baseline.json --format json
```

## Output Formats

- `json`: machine and script friendly output
- `sarif`: GitHub Code Scanning and security platform integration
