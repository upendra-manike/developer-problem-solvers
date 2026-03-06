# developer-problem-solvers

Open-source ecosystem for solving high-impact software engineering problems with practical algorithms, developer tooling, and language-specific integrations.

## Vision

Build one coherent platform instead of many disconnected utilities:

`DevGuard` modules that help teams ship safer, faster, and more reliable software.

## Problem Areas We Target

1. AI-generated code reliability
2. Security vulnerabilities
3. Concurrency bugs
4. Dependency conflicts and upgrade risk
5. Microservices debugging and tracing
6. Cloud cost waste
7. Real-time data processing reliability
8. Developer productivity bottlenecks

## Ecosystem Architecture

Core idea: one shared analysis engine plus focused modules.

```text
devguard-core
	|- parser adapters (Python, JS/TS, Java, Go, Rust)
	|- rule engine (security, performance, reliability)
	|- reporting formats (CLI, SARIF, JSON)
	|- plugin API

devguard-ai-validator
devguard-security
devguard-concurrency
devguard-dependency
devguard-microtrace
devguard-cost
```

## Language and Packaging Strategy

1. Python package (`pip`) for fast prototyping and static analysis orchestration
2. JavaScript package (`npm`) for frontend and Node ecosystems
3. Java plugin (`Maven` or `Gradle`) for enterprise adoption
4. .NET package (`NuGet`) for your existing momentum

## Build Order (Recommended)

1. `devguard-core` (shared rule engine + CLI)
2. `devguard-ai-validator` (trust layer for AI-generated code)
3. `devguard-security` (cross-language security checks)
4. `devguard-dependency` (upgrade and conflict intelligence)
5. `devguard-concurrency` (race/deadlock diagnostics)

## MVP Scope (First 6-8 Weeks)

### MVP 1: `devguard-ai-validator`

Goals:

1. Scan generated code files/folders
2. Run baseline checks: insecure patterns, obvious inefficiencies, code smells
3. Produce fix suggestions with confidence score
4. Export SARIF for GitHub code scanning

Initial checks:

1. SQL injection string concatenation patterns
2. Unsafe deserialization usage
3. Hardcoded secret detection
4. N+1 query and repeated allocation heuristics
5. Missing error handling for async/network boundaries

## 30 High-Impact Library Ideas

### AI Reliability

1. `llm-code-diff-risk`: scores risk between human and AI-generated diffs
2. `prompt2test`: generates edge-case tests from prompts and code context
3. `ai-hallucination-linter`: flags likely hallucinated APIs and imports
4. `safe-autofix`: applies only verifiable AI fixes with rollback
5. `context-drift-detector`: detects when generated code ignores project conventions

### Security

6. `polyglot-sec-rules`: shared vulnerability rules across languages
7. `deserialization-guard`: detects unsafe object binding paths
8. `api-auth-auditor`: verifies authz/authn checks across service endpoints
9. `secret-path-scanner`: traces secret usage paths, not just literals
10. `xss-flow-lite`: fast taint tracking for template and DOM sinks

### Concurrency and Reliability

11. `raceguard`: race condition pattern detector for async and thread code
12. `deadlock-scout`: lock-order graph + deadlock risk alerts
13. `async-trace-map`: visualizes async call chains and dropped exceptions
14. `retry-chaos-check`: detects retry storms and missing backoff jitter
15. `state-contention-profiler`: finds high-contention shared state hotspots

### Dependency Intelligence

16. `dep-impact-score`: predicts blast radius of dependency upgrades
17. `semver-reality-check`: compares actual breakage risk vs semantic version
18. `transitive-risk-radar`: highlights risky transitive dependencies
19. `api-break-detector`: static API surface diff for package upgrades
20. `license-compat-engine`: flags license compatibility issues automatically

### Microservices and Distributed Systems

21. `microtrace-lite`: traces request path via logs and headers
22. `service-dependency-graph`: generates live dependency graph from traffic
23. `latency-rootcause`: correlates slow spans with upstream pressure
24. `contract-drift-watch`: detects API contract drift across services
25. `incident-replay-kit`: replays distributed failures from captured events

### Cloud and Performance Cost

26. `k8s-idle-hunter`: identifies underutilized pods/nodes/resources
27. `autoscale-tuner`: recommends HPA/VPA settings from workload shape
28. `storage-waste-lens`: finds stale snapshots, orphan volumes, cold data
29. `cost-anomaly-stream`: real-time cloud spend anomaly detector
30. `queue-cost-optimizer`: balances throughput/latency/cost for queue workers

## What Makes This Repo Stand Out

1. Real developer pain points, not toy examples
2. Shared engine and rules to compound value over time
3. OSS-friendly architecture (plugin API + clear module boundaries)
4. Enterprise-ready outputs (`SARIF`, `JSON`, CI integration)

## Suggested Repository Structure

```text
/docs
	/roadmap
	/architecture
/modules
	/devguard-core
	/devguard-ai-validator
	/devguard-security
	/devguard-dependency
	/devguard-concurrency
/examples
/benchmarks
```

## Contribution Priorities

1. Add first architecture doc for `devguard-core`
2. Define rule format (`id`, `severity`, `match`, `fix`, `references`)
3. Implement 5 high-confidence checks end-to-end
4. Add CI with lint, unit tests, sample scan workflow
5. Publish first package and collect user feedback quickly

## Success Metrics

1. Time saved in code review (measured by reduced manual findings)
2. Precision of checks (low false positives)
3. Number of repos using the tool in CI
4. Community rule contributions
5. Package downloads and GitHub stars

## Current Status

Implemented in this repository:

1. `devguard-core` package scaffold with CLI scanner
2. `devguard-ai-validator` package scaffold with confidence filtering
3. Five initial checks (`DG001` to `DG005`)
4. JSON and SARIF output support
5. Example insecure file and baseline test scaffold
6. AST-backed Python checks for `DG001`-`DG003`
7. Baseline suppression (`--baseline-in`, `--baseline-out`)
8. Production CI with lint, tests, build, SARIF artifact, and Code Scanning upload
9. Changed-files-only scan mode for faster PR checks (`--file-list`)

## Quick Start

Run core scanner:

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan examples/sample_insecure.py --format json
```

Run with production options:

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan examples/sample_insecure.py --min-severity medium --exclude-dir vendor --max-file-size-kb 256 --format sarif --output reports.sarif
```

Generate a baseline (for gradual adoption):

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan examples/sample_insecure.py --baseline-out baseline.json --format json
```

Scan while suppressing known findings in baseline:

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src python -m devguard_core.cli scan examples/sample_insecure.py --baseline-in baseline.json --format json
```

Run AI validator wrapper:

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src:modules/devguard-ai-validator/src python -m devguard_ai_validator.cli examples/sample_insecure.py --format sarif --output reports.sarif
```

## CI

GitHub Actions workflow is included in `.github/workflows/ci.yml`.

Current pipeline:

1. Run `pytest` for `devguard-core`
2. Run scanner against `examples/sample_insecure.py`
3. Run `devguard-ai-validator` and upload `devguard-ai-validator.sarif` as a workflow artifact
4. Upload SARIF to GitHub Code Scanning for Security tab and PR annotations
5. Post/update a sticky PR comment summarizing new high/medium findings from PR gate scan

## Production Gates (Local)

```bash
cd /workspaces/developer-problem-solvers
PYTHONPATH=modules/devguard-core/src pytest -q modules/devguard-core/tests
PYTHONPATH=modules/devguard-core/src:modules/devguard-ai-validator/src pytest -q modules/devguard-ai-validator/tests
ruff check modules/devguard-core/src modules/devguard-core/tests modules/devguard-ai-validator/src modules/devguard-ai-validator/tests
python -m build modules/devguard-core
python -m build modules/devguard-ai-validator
```

## Practical Example

Run a real before-vs-after PR gating demo:

```bash
cd /workspaces/developer-problem-solvers
bash scripts/demo_pr_gate.sh
```

Detailed explanation: `docs/usage/pr-workflow-example.md`.

CI baseline mode details: `docs/usage/ci-baseline-mode.md`.

Advanced feature guide: `docs/usage/advanced-features.md`.

Config template: `.devguard.example.json`.

Package publishing guide: `docs/usage/publish-python-packages.md`.

Release preflight script: `scripts/release_check.sh`.

Automated version/tag/release workflow: `.github/workflows/release-automation.yml`.

Auto publish on every commit: `.github/workflows/auto-publish-python.yml`.

## Public Repo Hardening

Implemented controls:

1. Ownership enforcement via `.github/CODEOWNERS`
2. Security disclosure policy in `SECURITY.md`
3. Automated dependency updates in `.github/dependabot.yml`
4. Auto-publish limited to protected `main` and package-path changes only
5. Serialized publish runs with workflow concurrency guard

Recommended GitHub settings (enable in repository UI):

1. Require pull requests before merging into `main`
2. Require approving review and dismiss stale approvals on new commits
3. Require status checks: `CI / devguard-core-tests`, `CI / devguard-ai-validator`, `CI / devguard-pr-gate`
4. Restrict who can push directly to `main`

## Next Step

Start with `devguard-ai-validator` as the wedge product, then expand into `security` and `dependency` modules using the same engine.