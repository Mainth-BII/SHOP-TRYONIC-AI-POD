# MH06 — 🎨 Studio Canvas (Smoke)

> File test: `tests/smoke/test_smoke_mh06_studio_canvas.py` · Class: `TestSmokeMH06StudioCanvas`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_002** | Studio load | `/studio?category=t-shirts` load được, có canvas/main |
| **TC_006** | Product page | `/studio?view=product` load được, có product grid/cards |
| **TC_025** | Studio Hoodie | Thử 3 URL hoodie, URL đầu tiên hợp lệ có canvas/main |
| **TC_027** | Mockup image | Ảnh product/mockup trong canvas area không bị broken |
| **TC_028** | Mobile viewport | Home + Studio không crash trên viewport 390×844 |
| **TC_031** | Performance | Home ≤8s · Studio ≤12s · Policy ≤6s (ngưỡng FAIL) |

---

### [TC_DAILY_002] Studio Canvas — Load thành công

- **S1**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây.
- **S2**: URL chứa `/studio`, không có `404`/`Not Found`.
- **S3**: Ít nhất một trong `.canvas-container` / `canvas` / `main` hiển thị (8s). Chụp `S1_studio_page_loaded`.

---

### [TC_DAILY_006] Product Page — Load thành công

- **S1**: Navigate `/studio?view=product` → chờ load + 2 giây.
- **S2**: URL chứa `/studio`, không có `404`/`Not Found`.
- **S3**: `[class*='product']` / `[class*='grid']` / `[class*='card']` / `main` hiển thị (8s). Chụp `S1_product_page_loaded`.

---

### [TC_DAILY_025] Studio Hoodie — URL hợp lệ load được

- **S1**: Thử lần lượt: `/studio?category=hoodies` → `hoodie` → `ao-hoodie`. Lấy URL đầu tiên HTTP ≠ 404/500.
- **S2**: URL chứa `/studio`, không có `404`/`Not Found`.
- **S3**: Canvas/main hiển thị. Chụp `S1_studio_hoodie_loaded`.

---

### [TC_DAILY_027] Mockup Image — Không broken

- **S1**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây. Chụp `S1_studio_before_check`.
- **S2**: Có ít nhất 1 thẻ `<img>`.
- **S3**: Dùng `page.evaluate()` lọc ảnh `complete && naturalWidth === 0` → log `[WARN]` nếu có broken (không FAIL toàn bộ).
- **S4**: Lọc riêng ảnh trong vùng canvas/mockup/preview → FAIL nếu bất kỳ ảnh nào broken. Chụp `S2_product_image_state`.

---

### [TC_DAILY_028] Mobile Viewport — Home + Studio không crash

> Dùng fixture `mobile_page` (viewport 390×844)

- **S1**: Navigate Home → chờ load + 2 giây → chụp `S1_mobile_home`.
- **S2**: Không có `500`/`Internal Server Error`/`Application error`.
- **S3**: `h1` / `main` / `:text('Tạo ngay')` hiển thị (8s).
- **S4**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây → chụp `S2_mobile_studio`.
- **S5**: URL chứa `/studio`, không có `500`/crash.
- **S6**: `.canvas-container` / `canvas` / `main` hiển thị (8s). Chụp `S3_mobile_studio_canvas`.

---

### [TC_DAILY_031] Page Load Performance — Trong ngưỡng cho phép

| Trang | Ngưỡng WARN | Ngưỡng FAIL |
|:---|---:|---:|
| Home `/` | 4s | 8s |
| Studio `/studio?category=t-shirts` | 6s | 12s |
| Chính sách thanh toán | 3s | 6s |

- **S1**: Lần lượt navigate + đo `domcontentloaded` cho từng trang.
- **S2**: Log `[WARN]` nếu vượt ngưỡng cảnh báo, `[FAIL]` nếu vượt ngưỡng FAIL. Chụp `S1_last_page_timing`.
- **S3**: FAIL tổng hợp nếu bất kỳ trang nào vượt ngưỡng FAIL.
