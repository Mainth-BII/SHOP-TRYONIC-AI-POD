# Chi tiết các bước Test (Daily Auth Flow) — V4 (Successful Login & Logout)

Tài liệu này tổng hợp các bước thực thực hiện cho bộ test `test_daily_auth.py`, bao gồm các luồng xác thực thực tế.

---

## 1. Bảng Tổng Hợp (Summary Table)

| TC ID | Mục tiêu | Pre-condition | Loại Case | Trạng thái Mong đợi |
| :--- | :--- | :--- | :--- | :--- |
| **030** | Đăng nhập Email | Chưa đăng nhập | **Success** | Vào hệ thống, hiện nút Hồ sơ |
| **031** | Sai mật khẩu | Chưa đăng nhập | Validation | Hiện lỗi "Vui lòng kiểm tra..." |
| **034** | Entry: Studio | Chưa đăng nhập | Entry Point | Hiện Modal Đăng nhập |
| **035** | Entry: Checkout | Chưa đăng nhập | Contextual | Hiện Modal Đăng nhập |
| **036** | Login Google | Chưa đăng nhập | Social | Hiện màn hình Pass của Google |
| **037** | Login Facebook | Chưa đăng nhập | Social | Hiện màn hình Login Facebook |
| **038** | Khóa tài khoản | Chưa đăng nhập | Security | Hiện lỗi "Tài khoản bị tạm khóa" |
| **039** | **Đăng xuất** | **Đã đăng nhập** | **Success** | Quay lại trạng thái Guest |
| **032** | Xem Hồ sơ | Đã đăng nhập | Auth Access | Hiện thông tin cá nhân |
| **033** | Xem Đơn hàng | Đã đăng nhập | Auth Access | Hiện danh sách đơn hàng |

---

## 2. Chi tiết các bước thực hiện mới

### [TC_DAILY_060] Login: Đăng nhập thành công
- **Pre-condition**: Guest.
- **Steps**:
    1. Truy cập trang chủ.
    2. Nhập `tester_beta_2026@yopmail.com` / `Admin@12Password@123`.
    3. Click **"Đăng nhập"**.
- **Expected Result**: Modal đóng. Header xuất hiện nút Profile với nội dung **"Tryonic"**.

### [TC_DAILY_069] Logout: Đăng xuất hệ thống
- **Pre-condition**: Đã đăng nhập.
- **Steps**:
    1. Tại Header, click vào nút Profile (**Tryonic**).
    2. Click vào tùy chọn **"Đăng xuất"**.
- **Expected Result**: Hệ thống xóa token. Header hiện lại nút **"Đăng nhập"**.

### [TC_DAILY_066] Social: Google Login
- **Pre-condition**: Guest.
- **Steps**:
    1. Click "Tiếp tục với Google".
    2. Nhập `mainth@bccii.co.jp` vào cửa sổ popup của Google.
- **Expected Result**: Google chuyển sang màn hình yêu cầu Mật khẩu.

---

> [!TIP]
> Các test case 032, 033, 039 sử dụng cơ chế **Mock Token** để giả lập trạng thái đã đăng nhập, giúp tiết kiệm thời gian chạy test và giảm tải cho server AI.
