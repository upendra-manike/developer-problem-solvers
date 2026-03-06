# devguard-ai-validator

`devguard-ai-validator` validates AI-generated code using confidence-aware checks built on `devguard-core`.

It is optimized for teams using LLM-generated code in pull requests and CI pipelines.

## Install

```bash
python -m pip install devguard-ai-validator
```

## Scope (v0.1)

- Runs DevGuard core checks
- Reports confidence-aware findings
- Supports JSON and SARIF output for CI workflows

## Example

```bash
devguard-ai-validator ./src --format json
```

Use stricter confidence threshold:

```bash
devguard-ai-validator ./src --min-confidence 0.85 --format json
```

Generate SARIF for security tooling:

```bash
devguard-ai-validator ./src --format sarif --output devguard-ai-validator.sarif
```
