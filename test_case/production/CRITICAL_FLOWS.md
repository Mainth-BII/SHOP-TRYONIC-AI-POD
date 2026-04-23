# Production — 🚨 Critical Path Tests

> File test: `tests/production/test_critical_flows.py` · Class: `TestProductionCriticalFlows`  
> Data prompt: `data/genz_prompts.json` (30 prompts, xoay hàng ngày theo ngày trong năm)  
> Screenshot: `screenshots/production/test_critical_flows/CRITICAL_00X/`  
> Chạy: `pytest tests/production/test_critical_flows.py --env=test -v` hoặc `--env=prod`

> **⚠️ Tất cả test case đều BẮT ĐẦU bằng step S0: Đăng nhập.**  
> Credentials đọc từ `.env` theo môi trường (`DAILY_TEST_*` cho test, `PROD_*` cho prod).

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **CRITICAL_001** | Login → Home → AI Gen → Studio → Order → Checkout → QR | QR code thanh toán xuất hiện cuối luồng |
| **CRITICAL_002** | Login → Verify đăng nhập thành công | Nút "Đăng nhập" biến mất sau login |
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

### [CRITICAL_001] Full luồng Home → QR Thanh toán (đã đăng nhập)

**Mục tiêu:** Đảm bảo toàn bộ luồng mua hàng hoạt động từ đầu đến cuối sau khi đăng nhập.

#### Dữ liệu test
- **Prompt AI:** Tự động chọn từ 30 mẫu GenZ trend trong `data/genz_prompts.json`, xoay theo ngày trong năm
- **Thông tin nhận hàng:** Lấy từ `guest_checkout` trong cùng file JSON
- **Size:** L · **Số lượng:** 2

#### Các bước

| Step | Màn hình | Hành động | Assert | Screenshot |
|:---:|:---|:---|:---|:---|
| S0 | **Home** | *(Đăng nhập — xem step chung)* | Đã login | `S0` |
| S1 | **Home** | Fill prompt GenZ → Click "Tạo ngay" | URL chứa `/studio`, canvas visible | `S1–S3` |
| S1b | **Studio** | Nếu popup Điều khoản sử dụng xuất hiện → Click "Đồng ý" | Popup đóng, canvas accessible | — |
| S2 | **Studio** | Chờ AI tạo artwork (tối đa 120s) | ≥ 3 ảnh xuất hiện + ghi thời gian | `S4` |
| S3 | **Studio** | Chọn màu áo **Trắng** | Màu áo thay đổi (warn nếu không tìm thấy) | `S5` |
| S4 | **Studio** | Click ảnh thứ nhất trong kết quả AI | Artwork áp lên áo | `S6` |
| S5a | **Studio** | Click "Mặt sau" để xoay áo | View chuyển sang mặt sau | `S7` |
| S5b | **Studio** | Mở Thư Viện → Click ảnh bất kỳ | Ảnh áp lên mặt sau | `S8` |
| S6 | **Studio** | Click "Hoàn tất thiết kế" | Navigate sang trang `/review` | `S9` |
| S7a | **Review** | Click "Đặt hàng" | Màn hình đặt hàng mở | `S10` |
| S7b | **Order** | Chọn size **L**, số lượng **2** | Size L active, qty = 2 | `S11` |
| S7c | **Order** | Click "Mua ngay" | Navigate sang checkout | `S12` |
| S8a | **Checkout** | Điền: Họ tên · SĐT · Địa chỉ | Các field được điền đủ | `S13` |
| S8b | **Checkout** | Click "Thanh toán" | — | `S14` |
| S8c | **QR** | Kiểm tra QR code xuất hiện | QR code visible (timeout 15s) | `S15` |

#### Điều kiện SKIP tự động
- S0: Thiếu credentials → **SKIP** toàn bộ
- S2: AI gen chỉ tạo được < 3 ảnh sau 120s → **SKIP** với thông báo rõ lý do
- S5: Nút "Mặt sau" không hiển thị → bỏ qua bước S5, vẫn tiếp tục

---

### [CRITICAL_002] Thêm vào giỏ hàng → Hủy thanh toán → Thanh toán lại

**Mục tiêu:** Xác nhận luồng Add to Cart → Login tại Checkout → Thanh toán → Hủy → Xem đơn hàng → Thanh toán lại.

| Step | Trang | Hành động | Expected Result | Screenshot |
|------|-------|-----------|-----------------|------------|
| S1 | **Home** | Nhập prompt → Click "Tạo ngay" | Navigate Studio | `S1` |
| S2 | **Studio** | Chờ AI gen ≥ 3 artwork | ≥ 3 ảnh hiển thị | `S2` |
| S3 | **Studio** | Click Variant 2 → Apply mặt trước | Artwork trên áo | `S3` |
| S4 | **Studio** | Xoay áo → Click Variant 1 cho mặt sau | Artwork mặt sau | `S4` |
| S5 | **Studio** | Click "Hoàn tất thiết kế" | Review page | `S5` |
| S6 | **Review** | Click "Đặt hàng" | Order screen | `S6` |
| S7 | **Order** | Chọn size 4XL | Size active | `S7` |
| S8 | **Order** | Click "Thêm vào giỏ" | Toast/badge cập nhật | `S8` |
| S9 | **Cart** | Mở giỏ hàng → "Thanh toán ngay" | Checkout page | `S9` |
| S10 | **Checkout** | Click "Đăng nhập" → Nhập email/pass | Login thành công | `S10` |
| S11 | **Checkout** | Nhập MST → Click "Thanh toán" | Navigate payOS | `S11` |
| S12 | **payOS** | Click "Huỷ" → "Xác nhận hủy" | Quay lại site | `S12` |
| S13 | **Site** | Click "Xem đơn hàng" | Trang đơn hàng | `S13` |
| S14 | **Orders** | Click "Đơn hàng của tôi" | Tab đơn hàng | `S14` |
| S15 | **Orders** | Click đơn hàng đầu tiên | Chi tiết đơn | `S15` |
| S16 | **Detail** | Click "Thanh toán ngay" | Navigate payOS | `S16` |

> Credentials đọc từ `.env` — login xảy ra tại Checkout (không login trước).

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
│   ├── S11_size_L_qty_2_selected_HHMMSS.png
│   ├── S12_after_mua_ngay_HHMMSS.png
│   ├── S13_shipping_info_filled_HHMMSS.png
│   ├── S14_after_payment_click_HHMMSS.png
│   └── S15_qr_code_displayed_HHMMSS.png
├── CRITICAL_002/
│   └── S1_after_login_attempt_HHMMSS.png
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
| AI gen < 3 ảnh sau 120s | CRITICAL_001 → **SKIP** |
| Nút "Mặt sau" ẩn | S5 bỏ qua, test tiếp tục |
| Footer thiếu link pháp lý | CRITICAL_003 → **FAIL** |
| Luồng bình thường | 3 PASSED |
