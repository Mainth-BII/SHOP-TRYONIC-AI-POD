# MH08 — 🛒 Đặt hàng & Giỏ hàng (Smoke)

> File test: `tests/smoke/test_smoke_mh08_checkout.py` · Class: `TestSmokeMH08Checkout`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_007** | Không có thiết kế → nút disabled | Nút "Hoàn tất thiết kế" **PHẢI** bị disable khi chưa có artwork |
| **TC_010** | Nhập prompt → AI gen → nút enabled → xác nhận | Sau AI gen, nút ENABLED → click → màn hình xác nhận có nút "Đặt hàng" |
| **TC_011** | Màn hình xác nhận → Đặt hàng → 2 nút | "Đặt hàng" → modal có đủ "Thêm vào giỏ" + "Mua ngay" |
| **TC_021** | Trang giỏ hàng | `/checkout` hoặc `/cart` load được, không 404/500 |
| **TC_026** | Thêm vào giỏ → toast | Click "Thêm vào giỏ" → hiển thị toast "Đã thêm vào giỏ" |
| **TC_030** | Mua ngay (chưa đăng nhập) → login | Click "Mua ngay" khi chưa đăng nhập → yêu cầu đăng nhập |

---

### [TC_DAILY_007] Không có thiết kế — Nút PHẢI bị disabled

- **S0**: Nếu dialog Điều khoản hiện → chụp `S0_terms_dialog` → click "Đồng ý".
- **S1**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây. Chụp `S1_studio_no_design`.
- **S2**: `button:has-text('Hoàn tất thiết kế')` hiển thị (10s).
- **S3**: `get_attribute("disabled") is not None` → **PASS** (disabled là đúng, chưa có artwork). Chụp `S2_finish_btn_state`.
- **FAIL**: Nếu nút **KHÔNG** bị disabled khi chưa có thiết kế → bug.

---

### [TC_DAILY_010] Nhập Prompt → AI Gen → Xác Nhận

- **S0**: Nếu dialog Điều khoản hiện → click "Đồng ý".
- **S1**: Navigate Studio → chụp `S1_studio_before_prompt`.
- **gen1**: Nhập `_AI_PROMPT` vào `textarea[placeholder*='Mô tả ý tưởng thiết kế']`. Chụp `gen1_prompt_entered`.
- **gen2**: Click nút "Tạo" / "Generate" (nếu có), fallback: Enter. Poll 60s cho nút ENABLED. Chụp `gen2_generation_complete` hoặc `gen2_generation_timeout`.
- **FAIL nếu timeout**: Nút "Hoàn tất thiết kế" vẫn DISABLED sau 60s.
- **S2**: Chụp `S2_ai_gen_done_btn_enabled`.
- **S3**: Click "Hoàn tất thiết kế" → chờ 3 giây. Chụp `S3_confirmation_screen`.
- **S4**: `button:has-text('Đặt hàng')` hiển thị (10s) trên màn hình xác nhận. Chụp `S4_dat_hang_btn_visible`.

---

### [TC_DAILY_011] Màn Hình Xác Nhận → Đặt Hàng → 2 Nút

- **S0**: Nếu dialog Điều khoản hiện → click "Đồng ý".
- **gen**: Nhập prompt → AI gen (poll 60s) → FAIL nếu nút vẫn disabled.
- **S1**: Chụp `S1_after_ai_gen`.
- **S2**: Click "Hoàn tất thiết kế" → chờ 3 giây. Chụp `S2_confirmation_screen`.
- **S3**: Click "Đặt hàng" → chờ 2 giây. Chụp `S3_order_screen_after_dat_hang`.
- **S4**: ASSERT cả 2 nút hiển thị: `button:has-text('Thêm vào giỏ')` (8s) **VÀ** `button:has-text('Mua ngay')` (5s). Chụp `S4_both_buttons_visible`.

---

### [TC_DAILY_021] Trang Giỏ Hàng — Truy cập được

- **S1**: Thử `/checkout` → `/cart` → `/gio-hang`. Lấy URL đầu tiên HTTP ≠ 404/500.
- **S2**: Không có text lỗi 404/500. Chụp `S1_cart_page`.
- **S3**: PASS nếu: text "Giỏ hàng"/"Trống"/"Empty" **HOẶC** login dialog **HOẶC** redirect home/login. Chụp `S2_cart_content_state`.

---

### [TC_DAILY_026] Thêm vào Giỏ — Toast "Đã thêm vào giỏ"

- **S0**: Nếu dialog Điều khoản hiện → click "Đồng ý".
- **gen**: Nhập prompt → AI gen (poll 60s) → FAIL nếu nút vẫn disabled.
- **S1**: Chụp `S1_after_ai_gen`.
- **S2**: Click "Hoàn tất thiết kế" → Chụp `S2_confirmation_screen`.
- **S3**: Click "Đặt hàng" → Chụp `S3_order_modal_before_add`.
- **S4**: Click "Thêm vào giỏ" → chờ 2.5 giây. Chụp `S4_after_them_vao_gio`.
- **S5**: ASSERT toast: `:text('Đã thêm vào giỏ')` **HOẶC** `[class*='toast']/[role='alert']` hiển thị. Chụp `S5_toast_da_them_vao_gio`.

---

### [TC_DAILY_030] Mua ngay — Yêu cầu Đăng nhập (chưa đăng nhập)

- **S0**: Nếu dialog Điều khoản hiện → click "Đồng ý".
- **gen**: Nhập prompt → AI gen (poll 60s) → FAIL nếu nút vẫn disabled.
- **S1**: Chụp `S1_after_ai_gen`.
- **S2**: Click "Hoàn tất thiết kế" → Chụp `S2_confirmation_screen`.
- **S3**: Click "Đặt hàng" → Chụp `S3_order_modal_before_mua_ngay`.
- **S4**: Click "Mua ngay" → chờ 3 giây. Chụp `S4_after_mua_ngay`.
- **S5**: ASSERT đăng nhập được yêu cầu: URL chứa `login`/`signin`/`auth` **HOẶC** dialog email/password hiện **HOẶC** text "Đăng nhập" xuất hiện. Chụp `S5_login_required_shown`.
