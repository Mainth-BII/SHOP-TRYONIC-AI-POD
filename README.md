# Tryonic Shop — Daily Monitoring Suite

Dự án kiểm thử tự động hàng ngày cho hệ thống [shop.tryonic.ai](https://shop.tryonic.ai/).

## 🚀 Cấu trúc dự án
- `.agent/`: Cấu hình AI Agent hỗ trợ viết và debug test.
- `tests/`: Chứa các script test Playwright (Python).
  - `test_daily_smoke.py`: Kiểm tra tính sẵn sàng của các trang chính.
  - `test_daily_auth.py`: Kiểm tra luồng đăng nhập.
  - `test_daily_order.py`: Kiểm tra luồng đặt hàng.
- `test_case/`: Tài liệu các bước thực hiện (Test Steps).
- `screenshots/`: Lưu trữ ảnh minh chứng kết quả test.

## 🛠 Cài đặt
1. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Chạy test:
   ```bash
   # Chạy toàn bộ suite Daily
   pytest -m daily
   
   # Chạy riêng Smoke test
   pytest -m smoke
   ```

## 📊 Báo cáo
Kết quả test được lưu tại `tests/test_reports/` và ảnh minh chứng tại `screenshots/daily/`.
