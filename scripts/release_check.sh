#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python -m pip install --upgrade pip >/dev/null
python -m pip install pytest ruff build twine >/dev/null

echo "[1/4] Run core tests"
PYTHONPATH=modules/devguard-core/src pytest -q modules/devguard-core/tests

echo "[2/4] Run ai-validator tests"
PYTHONPATH=modules/devguard-core/src:modules/devguard-ai-validator/src pytest -q modules/devguard-ai-validator/tests

echo "[3/4] Run lint"
ruff check modules/devguard-core/src modules/devguard-core/tests modules/devguard-ai-validator/src modules/devguard-ai-validator/tests

echo "[4/4] Build and validate distributions"
python -m build modules/devguard-core --outdir dist/devguard-core
python -m build modules/devguard-ai-validator --outdir dist/devguard-ai-validator
python -m twine check dist/devguard-core/* dist/devguard-ai-validator/*

echo "release_check=PASS"
