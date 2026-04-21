# MH03 — 🔐 Auth Modal (Smoke)

> File test: `tests/smoke/test_smoke_mh03_auth_modal.py` · Class: `TestSmokeMH03AuthModal`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_003** | Modal Đăng nhập | Email · Password · Submit · Google · Facebook hiển thị |
| **TC_014** | Form Đăng ký | Form "Tạo tài khoản" hiển thị từ modal |
| **TC_015** | Quên mật khẩu | Form reset email hiển thị |
| **TC_016** | Social Login popup | Popup Google → `google.com` · Popup Facebook → `facebook.com` |
| **TC_020** | Đổi mật khẩu | Trang load hoặc redirect login — không 404/500 |
| **TC_037** | Login email/password → Studio → 50 điểm | Đăng nhập thật → Tạo ngay → Studio load, 50 điểm hiển thị |
| **TC_044** | Login Gmail → Studio → 50 điểm | Google OAuth → Tạo ngay → Studio load, 50 điểm hiển thị |

> **Credentials**: `TEST_EMAIL` / `TEST_PASSWORD` (mặc định: `tester_beta_2026@yopmail.com`).
> TC_044 cần `GOOGLE_TEST_EMAIL` / `GOOGLE_TEST_PASSWORD` — nếu chưa set thì SKIP sau khi verify popup URL.

---

### [TC_DAILY_003] Modal Đăng nhập mở đầy đủ

- **S1**: Trang chủ → chờ load. Chụp `S1_home_before_click`.
- **S2**: Click nút **"Đăng nhập"** trong header → chờ 2 giây. Chụp `S2_login_modal_opened`.
- **S3**: `div[role="dialog"]` hiển thị.
- **S4–S10**: Kiểm tra từng phần tử: tiêu đề "Chào mừng trở lại!", Email, Password, Submit, Google, Facebook.
- **S11**: Chụp `S3_login_modal_full`.

---

### [TC_DAILY_014] Form Đăng ký

- **S1**: Mở Login modal. Chụp `S1_login_modal_opened`.
- **S2**: Click link **"Đăng ký"** trong modal (`force=True` để bypass Radix UI). Chụp `S2_register_form_opened`.
- **S3**: Xác nhận `input[type='email']` và `input[type='password']` hiển thị. Chụp `S3_register_form_full`.

---

### [TC_DAILY_015] Quên mật khẩu

- **S1**: Mở Login modal. Chụp `S1_login_modal_opened`.
- **S2**: Click link **"Quên mật khẩu"** (`force=True`). Chụp `S2_forgot_password_form`.
- **S3**: Email input hoặc text "Đặt lại mật khẩu" hiển thị. Chụp `S3_forgot_password_full`.

---

### [TC_DAILY_016] Social Login Popups

- **S1**: Mở modal → chụp `S1_login_modal_for_social`.
- **S2**: Click Google → `expect_popup` → URL chứa `google`/`accounts`. Chụp `S2_google_popup` → đóng.
- **S3**: Mở lại modal → click Facebook → `expect_popup` → URL chứa `facebook`. Chụp `S3_facebook_popup` → đóng.

---

### [TC_DAILY_020] Đổi mật khẩu — Trang/Redirect không crash

- **S1**: Thử lần lượt: `/profile` → `/account` → `/account/change-password` → `/change-password`. Lấy URL đầu tiên HTTP ≠ 404/500. Chụp `S1_after_navigate`.
- **S2**: PASS nếu redirect về `/login` **HOẶC** URL chứa profile/account/password **HOẶC** có form đổi mật khẩu. Chụp `S2_final_state`.
- **S3** *(tuỳ chọn)*: Nếu tìm thấy nút "Đổi mật khẩu" → click → chụp `S3_change_pw_section`.

> FAIL duy nhất: tất cả URL đều 404/500.

---

### [TC_DAILY_037] Login Email/Password → Tạo ngay → Studio → 50 điểm

- **S1**: Navigate home (`/`). Chụp `S1_home_loaded`.
- **S2**: Kiểm tra đã đăng nhập chưa — nếu có, tự động logout.
- **S3**: Click nút **"Đăng nhập"** trên header. Chụp `S2_login_modal_opened`.
- **S4**: Nhập `TEST_EMAIL` + `TEST_PASSWORD` vào modal. Chụp `S3_credentials_filled`.
- **S5**: Click nút **"Đăng nhập"** (submit). Chụp `S4_after_submit`.
- **S6**: ASSERT modal đóng + nút "Đăng nhập" biến mất khỏi header. Chụp `S5_login_success_header`.
- **S7**: Click **"Tạo ngay"** → `wait_for_url("**/studio**")`. Chụp `S6_studio_after_login`.
- **S8**: Kiểm tra text `50 điểm` hoặc `[class*="point"]:has-text("50")`. Chụp `S7_studio_points_check`.
- **PASS**: Đăng nhập OK + vào Studio OK. **[WARN]** nếu không tìm thấy "50 điểm" rõ ràng.

---

### [TC_DAILY_044] Login Gmail → Tạo ngay → Studio → 50 điểm

- **S1**: Navigate home (`/`). Chụp `S1_home_loaded`.
- **S2**: Logout nếu đang đăng nhập.
- **S3**: Click **"Đăng nhập"** → modal. Chụp `S2_login_modal_opened`.
- **S4**: Click **"Tiếp tục với Google"** → `expect_popup` → verify URL chứa `google`/`accounts`. Chụp `S3_google_popup_opened`.
- **S5a** *(nếu có env vars)*: Điền `GOOGLE_TEST_EMAIL` → Enter → điền password → Enter → chờ popup đóng.
- **S5b** *(không có env vars)*: SKIP sau khi verify popup URL.
- **S6**: Verify header không còn nút "Đăng nhập". Chụp `S5_main_page_after_google_login`.
- **S7**: Click **"Tạo ngay"** → Studio. Chụp `S6_studio_after_gmail_login`.
- **S8**: Kiểm tra 50 điểm. Chụp `S7_studio_points_check`.
- **PASS**: Google OAuth OK + Studio OK. **[SKIP]** nếu thiếu env vars. **[WARN]** 50 điểm.
