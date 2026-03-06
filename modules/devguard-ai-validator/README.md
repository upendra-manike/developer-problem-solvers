# devguard-ai-validator

Wedge module for validating AI-generated code.

## Scope (v0.1)

- Runs DevGuard core checks
- Reports confidence-aware findings
- Supports JSON and SARIF output for CI workflows

## Example

```bash
PYTHONPATH=../devguard-core/src:src python -m devguard_ai_validator.cli ../../examples/sample_insecure.py --format json
```
