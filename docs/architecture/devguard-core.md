# DevGuard Core Architecture

## Design Goals

1. Fast static checks with low setup overhead
2. Shared rule schema across modules
3. CI-friendly outputs (`json`, `sarif`)
4. Extensible plugin model for future rule packs

## Layers

1. `checks.py`: detection heuristics and language mapping
2. `scanner.py`: file traversal and check orchestration
3. `formatters.py`: output rendering for CI and tooling
4. `cli.py`: command interface for local and CI use

## Rule Schema (v0.1)

Each rule carries:

- `id`: stable identifier (example: `DG001`)
- `severity`: `low|medium|high`
- `description`: human-readable issue statement
- `fix`: concise remediation action
- `match_type`: detection strategy (`regex` for MVP)

## Near-Term Evolution

1. Add AST-backed checks for better precision
2. Add plugin entrypoints for external modules
3. Add suppression mechanism and baseline snapshots
4. Add confidence calibration via benchmark corpus
