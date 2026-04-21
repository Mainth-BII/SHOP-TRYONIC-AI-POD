# MH01 — 🏠 Trang Chủ (Smoke)

> File test: `tests/smoke/test_smoke_mh01_home.py` · Class: `TestSmokeMH01Home`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_001** | Home page load | Load được, `<title>` không rỗng, không 404/500, có nội dung chính |
| **TC_017** | AI Generate khởi động | Navigate sang `/studio/` hoặc loading bắt đầu |
| **TC_029** | SEO meta tags | `<title>`, `description`, `og:title`, `og:image` không rỗng |

---

### [TC_DAILY_001] Home page load thành công

- **S1**: Truy cập `/` (`wait_until="domcontentloaded"`, timeout 30s).
- **S2**: Chờ `load` state.
- **S3**: Xác nhận `<title>` không rỗng.
- **S4**: Không có `"404"` / `"Not Found"` / `"500"` / `"Internal Server Error"`.
- **S5**: Ít nhất một trong: `h1`, `"Tạo ngay"`, AI input, `textarea` hiển thị (10s).
- **S6**: Chụp ảnh `S1_home_page_loaded`.

---

### [TC_DAILY_017] AI Generate — Luồng sinh ảnh khởi động được

- **S1**: Nhập prompt vào AI input trên Home. Chụp ảnh `S1_prompt_filled`.
- **S2**: Xác nhận nút **"Tạo ngay"** hiển thị và không disabled. Chụp ảnh `S2_before_generate`.
- **S3**: Click **"Tạo ngay"** → Chờ 3 giây. Chụp ảnh `S3_after_generate_click`.
- **S4**: PASS nếu: URL chứa `/studio/` **HOẶC** loading/spinner **HOẶC** email gate.

> Thực tế: Navigate sang `/studio/<uuid>`, AI hiển thị "Đang phân tích..."

---

### [TC_DAILY_029] SEO Meta Tags — Không rỗng trên Home

- **S1**: Truy cập Home. Chụp ảnh `S1_home_for_seo_check`.
- **S2**: Dùng `page.evaluate()` đọc DOM: `title`, `description`, `og:title`, `og:image`, `og:description`, `og:url`.
- **S3**: FAIL nếu bất kỳ tag **bắt buộc** nào rỗng: `<title>`, `description`, `og:title`, `og:image`.
- **S4**: Log `[WARN]` nếu `og:description` hoặc `og:url` thiếu (không FAIL).

> Tại sao: Sau deploy CMS, meta tag hay bị xóa vô tình → ảnh hưởng SEO + share Zalo/Facebook.
