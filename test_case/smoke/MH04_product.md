# MH04 — 🛍️ Trang Sản Phẩm /product (Smoke)

> File test: `tests/smoke/test_smoke_mh04_product.py` · Class: `TestSmokeMH04Product`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_033** | Trang `/product` load đúng | Không 404/500, có heading sản phẩm + ảnh mockup |
| **TC_034** | Image gallery — nhiều view mockup | Ít nhất 1 ảnh hiển thị, click ảnh 2 hoạt động (nếu có) |
| **TC_035** | "Thêm vào giỏ" từ product page | Nút hiển thị, click không crash, có phản hồi |
| **TC_036** | "Mua ngay" từ product page (chưa đăng nhập) | Nút hiển thị, click không crash 500 |

> **Lưu ý selector**: Trang `/product` có bảng size chứa số `38 40 42 44 46 48 50` và SKU `G5000`.
> Dùng `h1:has-text('500')` thay vì `:text('500')` để tránh false positive.

---

### [TC_DAILY_033] Trang /product Load Đúng

- **S1**: Navigate `/product` → chờ load + 2 giây. Chụp `S1_product_page_loaded`.
- **S2**: HTTP status ≠ 404/500 (từ `resp.status`).
- **S3**: Không có `h1:has-text('404')` / `h1:has-text('500')` / `:text('Not Found')`. `.first` để tránh strict mode.
- **S4**: `h1:has-text('Áo')` / `h1:has-text('Tryonic')` hiển thị (8s). Chụp `S2_product_heading_visible`.
- **S5**: `img[src*='tryon']` / `img[src*='product']` hiển thị (8s).

---

### [TC_DAILY_034] Image Gallery — Nhiều View Mockup

- **S1**: Navigate `/product` → chờ load + 2 giây. Chụp `S1_product_gallery_initial`.
- **S2**: `img[src*='view'], img[src*='tryon']...` count ≥ 1.
- **S3**: Ảnh đầu tiên (`first`) hiển thị (5s).
- **S4**: Nếu count ≥ 2: click ảnh thứ 2 → chờ 1s → chụp `S2_product_gallery_view2`.
- **PASS**: Ảnh mockup tồn tại, click gallery không crash.

---

### [TC_DAILY_035] "Thêm vào Giỏ" từ Product Page

- **S1**: Navigate `/product` → chụp `S1_product_page_before_add`.
- **S2**: `button:has-text('Thêm vào giỏ')` hiển thị (8s). Chụp `S2_add_to_cart_btn_visible`.
- **S3**: Click → chờ 2.5 giây. Chụp `S3_after_add_to_cart`.
- **S4**: ASSERT `h1:has-text('404')` / `h1:has-text('500')` / `:text('Not Found')` không hiển thị (tránh false positive với bảng size).
- **S5**: `[PASS]` nếu có toast/modal/redirect cart. `[WARN]` nếu không nhận ra phản hồi rõ ràng.

---

### [TC_DAILY_036] "Mua ngay" từ Product Page — Chưa Đăng nhập

- **S1**: Navigate `/product` → chụp `S1_product_page_before_mua_ngay`.
- **S2**: `button:has-text('Mua ngay')` hiển thị (8s). Chụp `S2_mua_ngay_btn_visible`.
- **S3**: Click → chờ 3 giây. Chụp `S3_after_mua_ngay`.
- **S4**: ASSERT `h1:has-text('500')` / `:text('Internal Server Error')` không hiển thị.
- **S5**: Nếu yêu cầu đăng nhập (URL/dialog): `[PASS]`. Nếu không: `[PASS]` với `[INFO]` — trang không crash là đủ.
