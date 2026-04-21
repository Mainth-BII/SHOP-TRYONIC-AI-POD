# Chi tiết các bước Test (Daily Customization Flow)

Dưới đây là bảng tổng hợp các bước thực hiện (Steps) cho bộ test `test_daily_customize.py`.

---

### [TC_DAILY_070] Studio: Product Color Change
*Mục tiêu: Đảm bảo tính năng đổi màu áo hoạt động và cập nhật trên UI.*

- **S1**: Truy cập Studio.
- **S2**: Tìm panel/nút chọn màu (Color Swatches).
- **S3**: Click chọn màu "Đen" (Black).
- **S4**: Xác nhận màu sắc được áp dụng (Kiểm tra class `active` hoặc screenshot).
- **S5**: Click chọn màu "Trắng" (White) để quay lại.

---

### [TC_DAILY_071] Studio: Size Chart Modal
*Mục tiêu: Kiểm tra bảng size hiển thị đúng thông số hỗ trợ người dùng.*

- **S1**: Mở form **"Đặt hàng"** (Order Modal).
- **S2**: Tìm link hoặc nút **"Bảng size"** (Size Chart).
- **S3**: Click vào link và xác nhận Modal Bảng size xuất hiện.
- **S4**: Kiểm tra sự tồn tại của các thông số (Dài áo, Ngực, Vai...).
- **S5**: Đóng Modal Bảng size.

---

### [TC_DAILY_072] Studio: Switch Product Category
*Mục tiêu: Đổi từ T-shirt sang sản phẩm khác mà không mất dữ liệu thiết kế (nếu có).*

- **S1**: Tại Studio, tìm nút/dropdown chọn loại sản phẩm.
- **S2**: Chọn **"Áo Hoodie"** (hoặc sản phẩm khác).
- **S3**: Xác nhận giao diện sản phẩm thay đổi (URL hoặc hình dạng áo).
- **S4**: Kiểm tra artwork AI vẫn được giữ lại trên áo mới.

---

### [TC_DAILY_073] Studio: Front/Back High-Level Toggle
*Mục tiêu: Đảm bảo artwork có thể được quản lý riêng biệt trên từng mặt.*

- **S1**: Áp dụng ảnh AI vào **Mặt trước**.
- **S2**: Chuyển sang **Mặt sau**.
- **S3**: Xác nhận Mặt sau đang trống (hoặc cho phép thêm ảnh khác).
- **S4**: Quay lại Mặt trước và kiểm tra ảnh cũ vẫn ở đó.

---

### [TC_DAILY_074] Studio: Zoom/Drag UI Check
*Mục tiêu: Kiểm tra các handle điều khiển Artwork hiển thị khi click vào ảnh.*

- **S1**: Click vào Artwork trên Canvas.
- **S2**: Xác nhận các nút điều khiển (Resize, Rotate, Delete) xuất hiện quanh ảnh.
- **S3**: Chụp ảnh minh chứng trạng thái selected.

---

> [!TIP]
> Luồng này đóng vai trò quan trọng trong việc chuyển đổi từ "người xem" sang "người mua" bằng cách cá nhân hóa sản phẩm.
