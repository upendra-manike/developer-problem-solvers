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
3. `auth_mode`: `token` or `trusted`

Auth mode guidance:

1. `token`: use repository secrets (`TEST_PYPI_API_TOKEN`, `PYPI_API_TOKEN`)
2. `trusted`: use PyPI/TestPyPI Trusted Publisher setup (no API token password)

## Auto Publish On Every Commit

Use workflow: `.github/workflows/auto-publish-python.yml`

Behavior:

1. Runs automatically on every push to `main`.
2. Publishes both packages to PyPI.
3. Generates unique post-release versions from the base package version:
   - `devguard-core`: `<base>.post<GITHUB_RUN_NUMBER>`
   - `devguard-ai-validator`: `<base>.post<GITHUB_RUN_NUMBER>`
4. Updates ai-validator dependency to the generated core version during build.

Requirement:

1. `PYPI_API_TOKEN` secret must be configured.

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

## Troubleshooting

### Trusted publishing exchange failure

Error example:

`OpenID Connect token retrieval failed ... ACTIONS_ID_TOKEN_REQUEST_TOKEN environment variable was unset`

Fix:

1. Ensure workflow permissions include `id-token: write`.
2. Ensure each publish job also has job-level `permissions: id-token: write`.
3. Ensure required secrets are present:
   - `TEST_PYPI_API_TOKEN` for TestPyPI runs
   - `PYPI_API_TOKEN` for PyPI runs
4. If using Trusted Publishing, run workflow with `auth_mode=trusted` and configure project trusted publisher in PyPI/TestPyPI.
