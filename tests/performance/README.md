# Performance Tests (k6) — CHỈ môi trường TEST

Bộ test hiệu năng **tách riêng** khỏi functional/E2E (Playwright/pytest).
Dùng [k6](https://k6.io) (xu hướng load-testing hiện đại: kịch bản code, nhẹ,
Git/CI-friendly, có thresholds/SLO built-in).

> 🔒 **An toàn:** mọi kịch bản **khóa cứng `*.test.shop.tryonic.ai`** (guard ở
> `config.js` + `run.sh`). **TUYỆT ĐỐI không** load/stress PROD. Chỉ GET trang
> công khai → không tạo đơn / không ghi dữ liệu.

## Loại test

| File | Mục đích | Tải |
|---|---|---|
| `smoke.js` | Sanity + baseline latency | 2 VUs / 30s (rất nhẹ) |
| `load.js`  | Tải kỳ vọng giờ cao điểm (sustained) | ramp → 50 VUs, giữ 3' |
| `stress.js`| Tìm "điểm gãy" (breaking point) | bậc thang tới ~300 VUs |

VU = Virtual User (người dùng ảo).

## Cài k6

- macOS (Homebrew): `brew install k6`
- macOS/Linux (binary): tải từ https://github.com/grafana/k6/releases
- Docker: `docker run --rm -i grafana/k6 run - <smoke.js`

## Chạy

```bash
cd tests/performance
./run.sh smoke      # nhẹ, an toàn
./run.sh load       # tải thật (có thể làm chậm TEST tạm thời)
./run.sh stress     # nặng — canh giờ thấp điểm, báo team trước

# hoặc trực tiếp:
k6 run smoke.js
PEAK_VUS=100 HOLD=5m k6 run load.js
MAX_VUS=400 k6 run stress.js
```

Kết quả JSON lưu ở `results/`. Override path đo qua `-e PATHS=/,/products`.

## Chỉ số quan trọng (đọc kết quả k6)

- `http_req_duration` **p(95)** — 95% request nhanh hơn mốc này (mục tiêu < 2s).
- `http_req_failed` — tỉ lệ request lỗi (mục tiêu < 1%).
- `http_reqs` / `iterations` — throughput (RPS).
- `page_duration{path=...}` — latency theo từng trang.

## CI

`.github/workflows/perf-test.yml` — chạy tay (workflow_dispatch), chọn scenario.
Mặc định `smoke`. Không bật cron (tránh tải định kỳ ngoài ý muốn).

## Mở rộng

- Thêm trang đo: sửa `PATHS` trong `config.js`.
- Thêm kịch bản API: tạo file mới import `lib/scenario.js` hoặc viết flow riêng.
- Đổi ngưỡng SLO: sửa `THRESHOLDS` trong `config.js`.
