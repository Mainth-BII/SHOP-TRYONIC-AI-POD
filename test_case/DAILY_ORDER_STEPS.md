# Chi tiết các bước Test (Daily Order & Checkout Flow)

Dưới đây là bảng tổng hợp các bước thực hiện (Steps) cho từng Test Case trong bộ `test_daily_order.py`.

> ⚠️ **Lưu ý quan trọng về kết quả tạo đơn hàng:** 
> - **TC_020 → TC_024, TC_029:** Dừng trước bước "Thanh toán" (không tạo đơn hàng rác trên hệ thống).
> - **TC_025, TC_026, TC_027, TC_028:** Bấm "Thanh toán" thật — sẽ tạo đơn hàng **pending** trên hệ thống (sau đó 027, 028 sẽ Hủy đơn).

---

### [TC_DAILY_050] Studio → Order Modal Opens
*Mục tiêu: Kiểm tra nút "Đặt hàng" hoạt động và mở được form đặt hàng.*

- **S1**: Truy cập Studio (`/studio?category=t-shirts`).
- **S2**: Chờ trang load xong (3 giây).
- **S3**: Tìm và xác nhận nút **"Đặt hàng"** hiển thị.
- **S4**: Click nút "Đặt hàng".
- **S5**: Xác nhận form/modal đặt hàng xuất hiện (có chứa thông tin Size hoặc dialog).

---

### [TC_DAILY_051] Order Form: Size & Price
*Mục tiêu: Kiểm tra chọn size và giá hiển thị đúng (> 0).*

- **S1**: Truy cập Studio và mở Order form.
- **S2**: Tìm và click nút size **"S"** (hoặc size bất kỳ nếu không tìm thấy S).
- **S3**: Xác nhận element giá tiền hiển thị trên UI.
- **S4**: Kiểm tra giá trị số trong element giá > 0.

---

### [TC_DAILY_052] Order Form → Mua ngay → Checkout
*Mục tiêu: Kiểm tra luồng từ Order form sang Checkout form.*

- **S1**: Truy cập Studio và mở Order form.
- **S2**: Tìm nút **"Mua ngay"** trong form (skip nếu chưa hiển thị).
- **S3**: Click "Mua ngay".
- **S4**: Xác nhận Checkout form xuất hiện với các input: Tên, Số điện thoại, hoặc SĐT.

---

### [TC_DAILY_053] Checkout Form: Điền thông tin
*Mục tiêu: Kiểm tra form Checkout có thể điền đầy đủ thông tin.*

- **S1**: Truy cập Studio → Order form → click "Mua ngay".
- **S2**: Điền **Tên** (`Nguyen Van Test`) vào ô họ tên.
- **S3**: Điền **Số điện thoại** (`0901234567`) vào ô SĐT.
- **S4**: Điền **Email** (`dailytest@tryonic.ai`) vào ô email.
- **S5**: Chụp ảnh minh chứng form đã điền đầy đủ.

---

### [TC_DAILY_054] Checkout: Thêm địa chỉ mới
*Mục tiêu: Login thật → Checkout → click "Thêm địa chỉ mới" → chọn nhãn [Nhà] → điền đầy đủ thông tin → Lưu.*

- **S0**: Đăng nhập bằng tài khoản thật (real login, không dùng mock token).
- **S1**: Truy cập Studio → Đặt hàng → Mua ngay → Trang Checkout.
- **S2**: Click nút **"Thêm địa chỉ mới"** (hiển thị vì đã đăng nhập).
- **S3**: Chọn nhãn **[Nhà]**.
- **S4**: Điền **Tên người nhận** (`Nguyen Van Test`).
- **S5**: Điền **Số điện thoại** (`0901234567`).
- **S6**: Chọn **Tỉnh/Thành phố** → chọn option đầu tiên (Hồ Chí Minh).
- **S7**: Chọn **Quận/Huyện** → chọn option đầu tiên.
- **S8**: Chọn **Phường/Xã** → chọn option đầu tiên.
- **S9**: Điền **địa chỉ chi tiết** (`123 Duong Test`).
- **S10**: Click **"Lưu địa chỉ"**.
- **S11**: Xác nhận form đóng hoặc địa chỉ xuất hiện trong danh sách.

---

### [TC_DAILY_055] Guest Checkout → Thanh toán → QR
*Mục tiêu: Khách chưa đăng nhập → điền đầy đủ thông tin → click Thanh toán → màn hình QR hiển thị.*

- **S1**: Truy cập Studio → Đặt hàng → click **"Mua ngay"** (không login).
- **S2**: Trang Checkout hiển thị form nhập tay (không có địa chỉ lưu sẵn).
- **S3**: Điền **Tên** (`Nguyen Van Test`).
- **S4**: Điền **SĐT** (`0901234567`).
- **S5**: Điền **Email** (`dailytest@tryonic.ai`).
- **S6**: Chọn **Tỉnh → Quận → Phường** từ custom dropdown.
- **S7**: Điền **địa chỉ chi tiết**.
- **S8**: Click nút **"Thanh toán"** (có hiển thị tổng tiền).
- **S9**: Xác nhận màn hình **QR / PayOS** xuất hiện hoặc URL chuyển sang trang payment/order.

---

### [TC_DAILY_056] Logged-in Checkout → Thanh toán → QR
*Mục tiêu: Đã đăng nhập → Checkout tự điền địa chỉ → click Thanh toán → màn hình QR hiển thị.*

- **S0**: Đăng nhập bằng tài khoản thật.
- **S1**: Truy cập Studio → Đặt hàng → click **"Mua ngay"**.
- **S2**: Trang Checkout hiển thị địa chỉ đã lưu (tự động điền).
- **S3**: Xác nhận section địa chỉ có dữ liệu (tên/Hồ Chí Minh/nhãn Nhà).
- **S4**: Kiểm tra email xác nhận (tự điền hoặc nhập nếu trống).
- **S5**: Click nút **"Thanh toán"** (có hiển thị tổng tiền).
- **S6**: Xác nhận màn hình **QR / PayOS** xuất hiện hoặc URL chuyển sang trang payment/order.

---

### [TC_DAILY_057] Guest: Hủy thanh toán & Xem đơn hàng
*Mục tiêu: Guest đặt hàng → màn hình QR → Hủy → Xem chi tiết đơn hàng → click "Đơn hàng của tôi".*

- **S1**: Thực hiện luồng đặt hàng của Guest đến màn hình QR (giống TC_DAILY_055).
- **S2**: Tại màn hình QR, click nút **"Hủy"** hoặc "Hủy thanh toán".
- **S3**: Trong popup xác nhận, click **"Xác nhận hủy"**.
- **S4**: Popup "Thanh toán đã bị hủy" hiện ra, click nút **"Xem đơn hàng"**.
- **S5**: Xác nhận đã chuyển đến trang Chi tiết đơn hàng (`/order/...`).
- **S6**: Kiểm tra trạng thái đơn hàng là **"Chờ xác nhận"** hoặc **"Chưa thanh toán"**.
- **S7**: Kiểm tra các thông tin cơ bản (mã đơn, tên, SĐT) hiển thị đúng.
- **S8**: Click vào link/nút **"Đơn hàng của tôi"**.
- **S9**: Xác nhận hệ thống yêu cầu đăng nhập (hiện popup Login hoặc chuyển đến trang Login).

---

### [TC_DAILY_058] Logged-in: Hủy thanh toán & Quay lại thiết kế
*Mục tiêu: User đã đăng nhập → đặt hàng → màn hình QR → Hủy → Quay lại thiết kế → kiểm tra trong "Đơn hàng của tôi".*

- **S1**: Đăng nhập bằng tài khoản thật.
- **S2**: Thực hiện luồng đặt hàng đến màn hình QR (giống TC_DAILY_056).
- **S3**: Tại màn hình QR, click nút **"Hủy"** hoặc "Hủy thanh toán".
- **S4**: Trong popup xác nhận, click **"Xác nhận hủy"**.
- **S5**: Popup "Thanh toán đã bị hủy" hiện ra, click nút **"Quay lại thiết kế"**.
- **S6**: Xác nhận đã quay lại trang Studio (`/studio`).
- **S7**: Truy cập trang **"Đơn hàng của tôi"** (`/my-orders`).
- **S8**: Tìm đơn hàng vừa tạo và xác nhận trạng thái là **"Chờ xác nhận"** hoặc **"Chưa thanh toán"**.

---

### [TC_DAILY_059] Order Form: Back from Checkout Preserves State
*Mục tiêu: Từ form Đặt hàng, chọn size/số lượng → Mua ngay → trang Checkout → nhấn Back → kiểm tra state được giữ nguyên và có thể sửa lại.*

- **S1**: Truy cập Studio và mở form "Hoàn tất đơn hàng".
- **S2**: Chọn một size (ví dụ: 'L') và tăng số lượng lên 2.
- **S3**: Click nút **"Mua ngay"** để chuyển sang trang Checkout.
- **S4**: Tại trang Checkout, click nút **Back** của trình duyệt.
- **S5**: Xác nhận đã quay lại form "Hoàn tất đơn hàng".
- **S6**: Kiểm tra size 'L' vẫn đang được chọn và số lượng vẫn là 2.
- **S7**: Thử thay đổi lựa chọn: chọn size 'M' và giảm số lượng về 1.
- **S8**: Xác nhận có thể chỉnh sửa thành công.
- **S9**: Click nút đóng form để quay về màn hình thiết kế (Studio).

---

> [!TIP]
> Ảnh minh chứng từng bước được lưu tại `screenshots/daily/order/<TC_ID>/`.
> Chạy riêng nhóm này: `pytest tests/daily/test_daily_order.py -v`
