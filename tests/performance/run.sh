#!/usr/bin/env bash
# Chạy perf test (k6) tiện lợi — KHÓA CỨNG môi trường TEST.
#   ./run.sh smoke              # smoke nhẹ (mặc định)
#   ./run.sh load               # load test
#   ./run.sh stress             # stress test
#   BASE_URL=... ./run.sh smoke # override (vẫn phải là *.test.shop.tryonic.ai)
set -euo pipefail

SCENARIO="${1:-smoke}"
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="${BASE_URL:-https://test.shop.tryonic.ai}"

# 🔒 Guard tầng shell: tuyệt đối không trỏ PROD.
if [[ "$BASE_URL" != *"test.shop.tryonic.ai"* ]]; then
  echo "🚫 BASE_URL phải là *.test.shop.tryonic.ai (đang: $BASE_URL)" >&2
  exit 1
fi

SCRIPT="$HERE/${SCENARIO}.js"
if [[ ! -f "$SCRIPT" ]]; then
  echo "Không thấy kịch bản: $SCRIPT (chọn: smoke | load | stress)" >&2
  exit 1
fi

if ! command -v k6 >/dev/null 2>&1; then
  echo "k6 chưa cài. Xem README.md để cài (brew/binary/docker)." >&2
  exit 127
fi

mkdir -p "$HERE/results"
STAMP="$(date +%Y%m%d_%H%M%S)"
echo "▶ k6 $SCENARIO → $BASE_URL"
BASE_URL="$BASE_URL" k6 run \
  --summary-export "$HERE/results/${SCENARIO}_${STAMP}.json" \
  "$SCRIPT"
