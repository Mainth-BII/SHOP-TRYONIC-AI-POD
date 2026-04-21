# Chi tiết các bước Test (Daily Generate Flow)

Dưới đây là bảng tổng hợp các bước thực hiện (Steps) cho từng Test Case trong bộ `test_daily_generate.py`.

---

### [TC_DAILY_040] Home: Generate Flow
*Mục tiêu: Kiểm tra luồng tạo ảnh cơ bản từ Trang chủ sang Studio.*

- **S1**: Truy cập Trang chủ (`shop.tryonic.ai`).
- **S2**: Tìm ô nhập (input/textarea) ý tưởng AI.
- **S3**: Nhập nội dung prompt mẫu.
- **S4**: Kiểm tra nút **"Tạo ngay"** có hiển thị và khả dụng (enabled) hay không.
- **S5**: Click "Tạo ngay" và xác nhận trình duyệt chuyển hướng sang `/studio/`.

---

### [TC_DAILY_041] Studio: Canvas & Interface
*Mục tiêu: Đảm bảo giao diện Studio tải đầy đủ các thành phần cốt lõi.*

- **S1**: Truy cập trực tiếp vào Studio.
- **S2**: Kiểm tra vùng Canvas (bàn làm việc) có hiển thị không.
- **S3**: Kiểm tra nút **"Đặt hàng"** (Order) có xuất hiện không.
- **S4**: Kiểm tra thanh công cụ (Sidebar) bên trái có load không.

---

### [TC_DAILY_042] Studio: Toggle Front/Back
*Mục tiêu: Kiểm tra tính năng đổi mặt trước/sau của sản phẩm.*

- **S1**: Truy cập Studio.
- **S2**: Click nút **"Mặt sau"** và xác nhận giao diện chuyển đổi thành công.
- **S3**: Click nút **"Mặt trước"** để quay lại trạng thái ban đầu.

---

### [TC_DAILY_043] Studio: Library & AI Tab
*Mục tiêu: Kiểm tra tính năng mở Thư viện ảnh.*

- **S1**: Truy cập Studio.
- **S2**: Click nút **"Thư Viện"** trên thanh công cụ.
- **S3**: Xác nhận panel Thư viện mở ra và có chứa nội dung (Ảnh của bạn/Thêm ảnh).
- **S4**: Xác nhận tab/nhãn **"AI"** hiển thị trong panel.

---

### [TC_DAILY_044] Studio: Polling AI Result
*Mục tiêu: Chờ đợi và xác nhận AI tạo ảnh thành công.*

- **S1**: Mở Thư viện trong Studio.
- **S2**: Thực hiện Polling (tối đa 75 giây) để tìm kiếm các ảnh có nhãn **"AI"**.
- **S3**: Xác nhận có ít nhất 1 ảnh AI mới được sinh ra hoặc đã tồn tại.

---

### [TC_DAILY_045] Studio: Apply AI Image
*Mục tiêu: Áp dụng ảnh AI vừa tạo lên Canvas.*

- **S1**: Mở Thư viện.
- **S2**: Tìm và hover vào một card ảnh có nhãn "AI".
- **S3**: Click nút **"Thay thế"** hoặc click trực tiếp vào ảnh.
- **S4**: Xác nhận ảnh được đưa lên canvas (kiểm tra handle hoặc interface).

---

### [TC_DAILY_046] Studio: Prompt & Regenerate
*Mục tiêu: Kiểm tra tính năng sửa prompt và tạo lại ảnh ngay trong Studio.*

- **S1**: Tìm ô nhập prompt trong Studio.
- **S2**: Xóa prompt cũ và nhập prompt mới.
- **S3**: Click nút **"Tạo"** (Regenerate).
- **S4**: Xác nhận trạng thái **"Đang tạo"** (Loading) xuất hiện trên UI.

---

### [TC_DAILY_047] Studio: Manual Upload
*Mục tiêu: Tự tạo dữ liệu ảnh và kiểm tra tính năng tải ảnh thủ công.*

- **S1**: Sử dụng mã nguồn để tự sinh một file ảnh PNG test (`daily_test_upload.png`).
- **S2**: Mở Thư viện trong Studio.
- **S3**: Thực hiện Upload file vừa tạo thông qua input file ẩn.
- **S4**: Chờ quá trình upload hoàn tất.
- **S5**: Xác nhận ảnh mới xuất hiện đầu tiên trong danh sách **"Ảnh của bạn"**.

---

> [!TIP]
> Bạn có thể theo dõi quá trình thực thi các bước này thông qua hình ảnh minh chứng tương ứng trong thư mục `screenshots/daily/<TC_ID>/`.
