# Production — 🚨 Critical Path Tests

> File test: `tests/production/test_critical_flows.py` · Class: `TestProductionCriticalFlows`  
> Data prompt: `data/genz_prompts.json` (30 prompts, xoay hàng ngày theo ngày trong năm)  
> Screenshot: `screenshots/production/test_critical_flows/CRITICAL_00X/`  
> Chạy: `pytest tests/production/test_critical_flows.py --env=test -v` hoặc `--env=prod`

> **⚠️ Tất cả test case đều BẮT ĐẦU bằng step S0: Đăng nhập.**  
> Credentials đọc từ `.env` theo môi trường (`DAILY_TEST_*` cho test, `PROD_*` cho prod).

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **CRITICAL_001** | Login → Home → AI Gen → Studio → Order → Checkout → QR → Hủy → Xem đơn → Verify | Chi tiết đơn hàng khớp dữ liệu đã capture trong luồng |
| **CRITICAL_002** | Home → AI Gen → Studio → Add to Cart → Login tại Checkout → Pay → Hủy → Xem đơn → Verify → Thanh toán lại | Thanh toán lại thành công trên payOS |
| **CRITICAL_003** | Login → Kiểm tra link pháp lý & liên hệ ở Footer | Đủ 3 link: bảo mật · đổi trả · CSKH |

---

## [Chung] Step S0 — Đăng nhập (áp dụng cho TẤT CẢ test case)

| Step | Hành động | Assert |
|:---:|:---|:---|
| S0a | Navigate home → Click "Đăng nhập" | Modal đăng nhập mở |
| S0b | Điền email + password từ `env.login_email` / `env.login_password` → Submit | — |
| S0c | Chờ 3s → Kiểm tra trạng thái | Nút "Đăng nhập" **KHÔNG** còn visible (đã login) |

> **SKIP** toàn bộ test nếu thiếu credentials trong `.env`.

---

### [CRITICAL_001] Full luồng Home → QR Thanh toán → Hủy → Verify đơn hàng

**Mục tiêu:** Đảm bảo toàn bộ luồng mua hàng hoạt động từ đầu đến cuối và dữ liệu đơn hàng tạo ra khớp với những gì người dùng đã chọn.

#### Dữ liệu test
- **Prompt AI:** Tự động chọn từ 30 mẫu GenZ trend trong `data/genz_prompts.json`, xoay theo ngày trong năm
- **Màu áo:** Trắng
- **Size:** M
- **order_data** (capture xuyên suốt luồng): `color`, `size`, `artwork_front_src`, `artwork_back_src`, `product_type`, `unit_price`, `total_price`, `address`, `order_code`

#### Các bước

| Step | Màn hình | Hành động | Assert / Capture | Screenshot |
|:---:|:---|:---|:---|:---|
| S0 | **Home** | *(Đăng nhập — xem step chung)* | Đã login | `S0` |
| S1 | **Home** | Fill prompt GenZ → Click "Tạo ngay" | URL chứa `/studio`, canvas visible | `S1–S3` |
| S1b | **Studio** | Nếu popup Điều khoản xuất hiện → Click "Đồng ý" | Popup đóng | — |
| S2 | **Studio** | Chờ AI tạo artwork (tối đa 120s) | ≥ 3 ảnh + ghi thời gian | `S4` |
| S3 | **Studio** | Chọn màu áo **Trắng** | Màu áo thay đổi (warn nếu không tìm thấy) | `S5` |
| S4 | **Studio** | Click ảnh đầu tiên trong kết quả AI (index 0) | Artwork áp lên áo · 📊 capture `artwork_front_src` | `S6` |
| S5a | **Studio** | Click "Xoay áo" sang mặt sau | View chuyển mặt sau | `S7` |
| S5b | **Studio** | Click ảnh thứ 3 trong Thư Viện (index 2) | Ảnh áp lên mặt sau · 📊 capture `artwork_back_src` | `S8` |
| S6 | **Studio** | Click "Hoàn tất thiết kế" | Navigate sang `/review` | `S9` |
| S7a | **Order** | Click "Đặt hàng" | URL chứa `/order` · 📊 capture `product_type`, `unit_price` | `S10` |
| S7b | **Order** | Chọn size **M** | Size M active | `S11` |
| S7c | **Order** | Click "Mua ngay" | Navigate sang `/checkout` · 📊 capture `total_price`, `address` | `S12` |
| S8a | **Checkout** | Điền MST `012345` vào ô Mã số thuế | Field được điền (địa chỉ auto-fill do đã đăng nhập) | `S13` |
| S8b | **Checkout** | Click "Thanh toán" | — | `S14` |
| S8c | **QR** | Kiểm tra QR code xuất hiện | QR visible (timeout 15s) | `S15` |
| S9 | **QR** | Click "Hủy" | Nút Hủy visible và click được | — |
| S10 | **QR** | Click "Xác nhận hủy" → chờ redirect | URL thoát khỏi payOS · 📊 capture `order_code` từ URL | `S16` |
| S11 | **Site** | Click "Xem đơn hàng" (fallback: navigate `/profile`) | Trang đơn hàng / profile hiển thị | `S17` |
| S12 | **Profile** | Click tab "Đơn hàng của tôi" | Tab active, danh sách đơn hiển thị | `S18` |
| S13 | **Orders** | Click đơn hàng đầu tiên | Chi tiết đơn hiển thị · ✅ `verify_order_data` (order_code + size) | `S19` |

#### Điều kiện SKIP tự động
- S0: Thiếu credentials → **SKIP** toàn bộ
- S2: AI gen chỉ tạo được < 3 ảnh sau 120s → **SKIP** với thông báo rõ lý do
- S5a: Nút "Xoay áo" không hiển thị → bỏ qua S5a + S5b, vẫn tiếp tục

#### Logic `verify_order_data` tại S13
- `order_code`: **ASSERT** — phải tìm thấy trong trang chi tiết đơn
- `size`: **ASSERT** — phải tìm thấy trong trang chi tiết đơn
- `unit_price`, `total_price`: **WARN** only — log nếu không khớp, không fail test
- `artwork_front_src`, `artwork_back_src`, `address`, `product_type`: **INFO** log only

---

### [CRITICAL_002] Thêm vào giỏ hàng → Hủy thanh toán → Thanh toán lại

**Mục tiêu:** Xác nhận luồng Add to Cart → Login tại Checkout → Thanh toán → Hủy → Xem đơn hàng → Verify → Thanh toán lại.

> **Lưu ý:** CRITICAL_002 **KHÔNG** login trước (S0). Login xảy ra tại bước S10 (tại trang Checkout).  
> Credentials vẫn đọc từ `.env` — thiếu credentials → **SKIP**.

| Step | Trang | Hành động | Expected Result / Capture | Screenshot |
|------|-------|-----------|--------------------------|------------|
| S1 | **Home** | Nhập prompt → Click "Tạo ngay" | Navigate Studio | `S1` |
| S2 | **Studio** | Chờ AI gen ≥ 3 artwork (120s) | ≥ 3 ảnh hiển thị | `S2` |
| S3 | **Studio** | Click Variant 2 (index 1) → Apply mặt trước | Artwork trên áo · 📊 capture `artwork_front_src` | `S3` |
| S4 | **Studio** | Xoay áo → Click Variant 1 (index 0) cho mặt sau | Artwork mặt sau · 📊 capture `artwork_back_src` | `S4` |
| S5 | **Studio** | Click "Hoàn tất thiết kế" | Navigate `/review` | `S5` |
| S6 | **Review** | Click "Đặt hàng" | Navigate `/order` · 📊 capture `product_type`, `unit_price` | `S6` |
| S7 | **Order** | Chọn size **4XL** | Size 4XL active | `S7` |
| S8 | **Order** | Click "Thêm vào giỏ" | Toast/badge giỏ hàng cập nhật | `S8` |
| S9 | **Cart** | Mở giỏ hàng → Click "Thanh toán ngay" | Navigate `/checkout` · 📊 capture `total_price`, `address` | `S9` |
| S10 | **Checkout** | Click "Đăng nhập" → Điền email/pass → Submit | Login thành công — nút "Đăng nhập" biến mất | `S10` |
| S11 | **Checkout** | Điền MST `123456` → Click "Thanh toán" | Navigate payOS | `S11` |
| S12 | **payOS** | Click "Huỷ" → Click "Xác nhận hủy" | Quay lại site, URL thoát khỏi payOS | `S12` |
| S13 | **Site** | Click "Xem đơn hàng" | Trang đơn hàng / profile · 📊 capture `order_code` từ URL | `S13` |
| S14 | **Profile** | Click tab "Đơn hàng của tôi" | Tab active, danh sách đơn hiển thị | `S14` |
| S15 | **Orders** | Click đơn hàng đầu tiên | Chi tiết đơn · ✅ `verify_order_data` (order_code + size) | `S15` |
| S16 | **Detail** | Click "Thanh toán ngay" | Navigate payOS — thanh toán lại thành công | `S16` |

#### Điều kiện SKIP tự động
- Thiếu credentials → **SKIP** toàn bộ
- S2: AI gen < 3 ảnh → **SKIP**
- S4: Nút "Xoay áo" không hiển thị → bỏ qua, tiếp tục
- S16: Nút "Thanh toán ngay" không tìm thấy → **INFO** log, không fail

---

### [CRITICAL_003] Footer — Link pháp lý & liên hệ

**Mục tiêu:** Đảm bảo 3 link bắt buộc về pháp lý luôn tồn tại ở Footer.

- **S0:** Đăng nhập (step chung) — thiếu credentials → **SKIP**
- **S1:** Navigate home → `scroll_to_bottom()`. Chụp `S1_footer_check`
- **S2:** ASSERT lần lượt 3 link trong `footer a[href*='...']`:
  - `chinh-sach-bao-mat` — Chính sách bảo mật
  - `chinh-sach-doi-tra` — Chính sách đổi trả
  - `lien-he-cskh` — Liên hệ CSKH
- **FAIL:** Bất kỳ link nào thiếu hoặc không visible

---

## Cấu trúc Screenshot

```
screenshots/production/test_critical_flows/
├── CRITICAL_001/
│   ├── S0_after_login_HHMMSS.png
│   ├── S1_home_loaded_HHMMSS.png
│   ├── S2_prompt_filled_HHMMSS.png
│   ├── S3_studio_navigated_HHMMSS.png
│   ├── S4_artworks_generated_Nimgs_Xs_HHMMSS.png   ← N ảnh, X giây
│   ├── S5_color_white_selected_HHMMSS.png
│   ├── S6_artwork_applied_to_shirt_HHMMSS.png
│   ├── S7_shirt_back_view_HHMMSS.png
│   ├── S8_library_image_on_back_HHMMSS.png
│   ├── S9_review_page_HHMMSS.png
│   ├── S10_order_screen_HHMMSS.png
│   ├── S11_size_M_selected_HHMMSS.png
│   ├── S12_after_mua_ngay_HHMMSS.png
│   ├── S13_tax_code_filled_HHMMSS.png
│   ├── S14_after_payment_click_HHMMSS.png
│   ├── S15_qr_code_displayed_HHMMSS.png
│   ├── S16_after_cancel_HHMMSS.png                 ← Sau khi hủy QR
│   ├── S17_view_orders_HHMMSS.png                  ← Trang đơn hàng
│   ├── S18_my_orders_HHMMSS.png                    ← Tab Đơn hàng của tôi
│   └── S19_order_detail_HHMMSS.png                 ← Chi tiết đơn (verify tại đây)
├── CRITICAL_002/
│   ├── S1_studio_navigated_HHMMSS.png
│   ├── S2_artworks_Nimgs_Xs_HHMMSS.png
│   ├── S3_artwork_front_HHMMSS.png
│   ├── S4_artwork_back_HHMMSS.png
│   ├── S5_review_page_HHMMSS.png
│   ├── S6_order_screen_HHMMSS.png
│   ├── S7_size_4xl_HHMMSS.png
│   ├── S8_added_to_cart_HHMMSS.png
│   ├── S9_checkout_page_HHMMSS.png
│   ├── S10_logged_in_HHMMSS.png
│   ├── S11_payos_page_HHMMSS.png
│   ├── S12_cancelled_HHMMSS.png
│   ├── S13_view_orders_HHMMSS.png
│   ├── S14_my_orders_HHMMSS.png
│   ├── S15_order_detail_HHMMSS.png                 ← verify tại đây
│   └── S16_repay_payos_HHMMSS.png
└── CRITICAL_003/
    └── S1_footer_check_HHMMSS.png
```

---

## Data GenZ Prompts (`data/genz_prompts.json`)

30 mẫu prompt xoay theo ngày trong năm (`day_of_year % 30`):

| # | Chủ đề |
|:---:|:---|
| 1–5 | Cyberpunk, Pixel art, Ukiyo-e, Dark academia, Kawaii cottagecore |
| 6–10 | Watercolor wolf, Robot android, Thủy mặc, Pop art koi, Psychedelic skull |
| 11–15 | Y2K panda DJ, Vaporwave city, Samurai sumi-e, Matrix cat, Minimalist eagle |
| 16–20 | Fine line snake, Harajuku chibi, Electric piranha, White tiger, Gothic doll |
| 21–25 | Traditional dragon boat, Streetwear cat, Nine-tail fox, Vintage Kraken, Dark academia owl |
| 26–30 | Neon jellyfish, Ninja rabbit, Neo-traditional rose, Hypebeast polar bear, Dark romanticism angel |

---

## Ghi chú vận hành

| Điều kiện | Kết quả dự kiến |
|:---|:---|
| Thiếu `.env` credentials | TẤT CẢ test → **SKIP** |
| AI gen < 3 ảnh sau 120s | CRITICAL_001 / CRITICAL_002 → **SKIP** |
| Nút "Xoay áo" ẩn | S5 bỏ qua, test tiếp tục |
| Tài khoản không có địa chỉ lưu sẵn | `address` capture = `None` — INFO log, không fail |
| Footer thiếu link pháp lý | CRITICAL_003 → **FAIL** |
| Luồng bình thường | 3 PASSED |
