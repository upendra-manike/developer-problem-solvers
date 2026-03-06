#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR/modules/devguard-core/src"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

cp "$ROOT_DIR/examples/sample_insecure.py" "$WORK_DIR/sample_insecure.py"

echo "[1/4] Create baseline from existing known findings"
python -m devguard_core.cli scan "$WORK_DIR" --baseline-out "$WORK_DIR/baseline.json" --format json >/dev/null || true

echo "[2/4] Baseline scan on unchanged code (expected exit 0)"
set +e
python -m devguard_core.cli scan "$WORK_DIR" --baseline-in "$WORK_DIR/baseline.json" --format json >/dev/null
clean_exit=$?
set -e
echo "baseline_scan_exit_code=$clean_exit"

echo "[3/4] Simulate new PR change introducing a high-severity issue"
cat > "$WORK_DIR/pr_change.py" <<'PY'
API_KEY = "new-super-secret-token"
PY

echo "[4/4] Scan with same baseline after PR change (expected exit 1)"
set +e
output="$(python -m devguard_core.cli scan "$WORK_DIR" --baseline-in "$WORK_DIR/baseline.json" --format json)"
pr_exit=$?
set -e
echo "pr_scan_exit_code=$pr_exit"
echo "$output"

if [[ "$clean_exit" -eq 0 && "$pr_exit" -eq 1 ]]; then
  echo "demo_result=PASS"
else
  echo "demo_result=FAIL"
  exit 1
fi
