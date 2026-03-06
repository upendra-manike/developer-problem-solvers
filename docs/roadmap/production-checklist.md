# Production Readiness Checklist

## Core Quality

1. Deterministic finding order.
2. Stable rule IDs and severities.
3. Clear CLI exit-code contract (`0` clean, `1` findings, `2` usage error).
4. Baseline support for incremental rollout.

## Security and Reliability

1. SARIF output validated in GitHub Code Scanning.
2. Excluded directory scanning controls.
3. Max file size limits for bounded resource use.
4. Safe handling for malformed baseline files.

## Delivery

1. Package builds succeed for `devguard-core` and `devguard-ai-validator`.
2. License metadata is SPDX compliant.
3. CI runs lint, tests, build, SARIF generation, and code scanning upload.
4. Contribution guide reflects local production gates.

## Next Hardening Steps

1. Add benchmark corpus with expected findings snapshots.
2. Add changelog and semantic versioning policy.
3. Add signed release workflow and package publishing automation.
4. Add rule suppression comments for line-level waivers.
