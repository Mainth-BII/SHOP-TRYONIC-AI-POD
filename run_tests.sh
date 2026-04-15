#!/usr/bin/env bash
# run_tests.sh — Local test runner for Tryonic AI QA
# Usage:
#   ./run_tests.sh              # Run all tests (headed)
#   ./run_tests.sh smoke        # Smoke tests only (P0)
#   ./run_tests.sh artwork      # Artwork generation tests
#   ./run_tests.sh headless     # All tests, headless
#   GOOGLE_CHAT_WEBHOOK_URL=https://... ./run_tests.sh  # With chat notification

set -euo pipefail

SUITE="${1:-all}"
BASE_URL="${BASE_URL:-https://pre-launch.tryonic.ai}"

echo "======================================================"
echo "  Tryonic AI — Playwright Test Runner"
echo "  Suite:    $SUITE"
echo "  URL:      $BASE_URL"
echo "  Date:     $(date '+%Y-%m-%d %H:%M')"
echo "======================================================"

# ── Setup ──────────────────────────────────────────────────────────────────
pip install -r requirements.txt -q
python -m playwright install chromium --with-deps -q

cd tests
mkdir -p screenshots test_reports

# ── Build pytest args ───────────────────────────────────────────────────────
ARGS="--browser chromium -v --tb=short --timeout=150000"

case "$SUITE" in
  smoke)    ARGS="$ARGS -m smoke" ;;
  artwork)  ARGS="$ARGS -m artwork" ;;
  validation) ARGS="$ARGS -m validation" ;;
  mobile)   ARGS="$ARGS -m mobile" ;;
  headless) ARGS="$ARGS --headless" ;;
  all)      ARGS="$ARGS --headed" ;;
  *)        echo "Unknown suite: $SUITE"; exit 1 ;;
esac

# ── Run ─────────────────────────────────────────────────────────────────────
EXIT_CODE=0
python -m pytest $ARGS \
  --junit-xml=test_reports/junit.xml \
  2>&1 | tee test_reports/test_output.txt || EXIT_CODE=$?

# ── Report ──────────────────────────────────────────────────────────────────
echo ""
echo "======================================================"
if [ $EXIT_CODE -eq 0 ]; then
  echo "  ✅ All tests PASSED"
else
  echo "  ❌ Some tests FAILED (exit code: $EXIT_CODE)"
fi
echo "  Reports: tests/test_reports/"
echo "  Screenshots: tests/screenshots/"
echo "======================================================"

# ── Google Chat notification (optional) ─────────────────────────────────────
if [ -n "${GOOGLE_CHAT_WEBHOOK_URL:-}" ]; then
  cd ..
  TOTAL=$(grep -oP 'tests="\K[0-9]+' tests/test_reports/junit.xml 2>/dev/null | head -1 || echo "0")
  FAILED=$(grep -oP 'failures="\K[0-9]+' tests/test_reports/junit.xml 2>/dev/null | head -1 || echo "0")
  PASSED=$((TOTAL - FAILED))
  STATUS="PASS"
  [ "$FAILED" -gt 0 ] && STATUS="FAIL"

  STATUS=$STATUS TOTAL=$TOTAL PASSED=$PASSED FAILED=$FAILED \
    RUN_URL="local" RUN_NUMBER="local" BASE_URL=$BASE_URL \
    python .github/scripts/notify_google_chat.py
fi

exit $EXIT_CODE
