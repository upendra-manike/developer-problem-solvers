# devguard-core

Shared scanning engine and rule framework for DevGuard modules.

## Features

- Rule metadata model (`id`, `severity`, `match_type`, `description`, `fix`)
- File walker with language detection
- Built-in checks for common AI-code risks
- AST-backed Python checks for SQL injection, unsafe deserialization, and hardcoded secrets
- JSON and SARIF output
- Baseline input/output for incremental CI rollout

## Quick Run

```bash
PYTHONPATH=src python -m devguard_core.cli scan ../../examples/sample_insecure.py --format json
```
