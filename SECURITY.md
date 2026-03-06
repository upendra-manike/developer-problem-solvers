# Security Policy

## Supported Versions

Only the latest release of each package is supported for security fixes.

## Reporting a Vulnerability

Please do not open public issues for potential vulnerabilities.

1. Email the maintainer directly with details and reproduction steps.
2. Include affected package and version (`devguard-core` or `devguard-ai-validator`).
3. Allow reasonable time for triage before public disclosure.

You should receive an acknowledgement within 72 hours.

## Disclosure Guidelines

1. Provide a clear impact statement and proof of concept.
2. Share minimal exploit details needed for triage.
3. Coordinate disclosure timing after a fix is available.

## Supply Chain Controls

The repository uses the following controls:

- Restricted ownership via `CODEOWNERS`.
- CI and PR gate scanning with SARIF uploads.
- Controlled PyPI publishing workflows.
- Versioned release automation with changelog updates.
