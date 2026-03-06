# Publish Python Packages

This repository publishes two Python packages:

1. `devguard-core`
2. `devguard-ai-validator`

## One-Time Setup

Create repository secrets in GitHub:

1. `TEST_PYPI_API_TOKEN`
2. `PYPI_API_TOKEN`

Generate tokens in TestPyPI/PyPI with scope limited to the specific project(s).

## Publish Workflow

Use workflow: `.github/workflows/publish-python.yml`

Inputs:

1. `package`: `devguard-core`, `devguard-ai-validator`, or `both`
2. `repository`: `testpypi` or `pypi`

## Automated Version + Tag + Release

Use workflow: `.github/workflows/release-automation.yml`

Inputs:

1. `part`: `patch`, `minor`, `major`
2. `package`: `devguard-core`, `devguard-ai-validator`, or `both`

This workflow will:

1. bump versions in `pyproject.toml`
2. sync `devguard-ai-validator` minimum dependency when core changes
3. update `CHANGELOG.md`
4. run release preflight checks
5. commit changes
6. create and push git tag
7. create GitHub Release notes automatically

## Recommended Release Flow

1. Bump package versions in both `pyproject.toml` files.
2. Run local gates:
   - tests
   - lint
   - package builds
3. Publish to TestPyPI first.
4. Verify install from TestPyPI.
5. Publish to PyPI.

## Install Verification

TestPyPI examples:

```bash
python -m pip install -i https://test.pypi.org/simple/ devguard-core
python -m pip install -i https://test.pypi.org/simple/ devguard-ai-validator
```

PyPI examples:

```bash
python -m pip install devguard-core
python -m pip install devguard-ai-validator
```

## Notes

1. `devguard-ai-validator` depends on `devguard-core>=0.1.0`.
2. If publishing both, publish `devguard-core` first.
3. If package version already exists, publish will fail by design.
