# Contributing

## Local Setup

```bash
python -m pip install -U pip
python -m pip install pytest ruff build
```

## Run Quality Gates

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src pytest -q modules/devguard-core/tests
PYTHONPATH=modules/devguard-core/src:modules/devguard-ai-validator/src pytest -q modules/devguard-ai-validator/tests
ruff check modules/devguard-core/src modules/devguard-core/tests modules/devguard-ai-validator/src modules/devguard-ai-validator/tests
python -m build modules/devguard-core
python -m build modules/devguard-ai-validator
```

## Coding Standards

1. Keep findings deterministic and sorted.
2. Add tests for every new rule and CLI option.
3. Preserve SARIF compatibility when changing output format.
4. Favor AST-backed checks when language parsers are available.

## Pull Request Checklist

1. Tests pass locally.
2. Lint passes locally.
3. New behavior is documented in `README.md` or module docs.
4. CI workflow remains green on push and pull request events.

## Publishing

1. Run `bash scripts/release_check.sh` before publishing.
2. Follow `docs/usage/publish-python-packages.md`.
3. Use GitHub workflow `.github/workflows/publish-python.yml` and publish to TestPyPI before PyPI.
