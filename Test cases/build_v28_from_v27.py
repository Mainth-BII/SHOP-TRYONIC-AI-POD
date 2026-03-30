"""
Build test_cases_suite_v28.md from v27:
1. Update header version
2. Update TC_HOME_UI_006 headline
3. Update TC_HOME_UI_007 subtitle
4. Update TC_AUTH_UI_001 login title/subtitle
5. Update TC_AUTH_UI_002 email placeholder
6. Update TC_DS_UI_001 & TC_DS_UI_002 header credits
7. Append NEW test cases for missing screens
"""
import re

SRC = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v27.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v28.md"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# ─── 1. Update header ────────────────────────────────────────────────
content = content.replace(
    "# POD T-Shirt Platform — Test Case Suite v27 (Restructured 8 Sheets)",
    "# POD T-Shirt Platform — Test Case Suite v28 (Updated + New Screens)"
)
content = content.replace(
    "> **Version:** v27 — Restructured (8 Sheets)",
    "> **Version:** v28 — Updated Headlines + Bổ sung màn hình thiếu (Cart, Profile, My Designs, AI Try-on, Error Pages)"
)

# ─── 2. TC_HOME_UI_006 — Headline changed ───────────────────────────
content = content.replace(
    "Headline hiển thị: 'Biến ý tưởng thành áo thun trong 30 giây'. Phần 'áo thun trong 30 giây' có màu tím (#7C3AED). Font size lớn (~48-56px), bold",
    "Headline hiển thị: 'Mỗi chiếc áo, một câu chuyện'. Phần highlight có màu tím gradient. Font size lớn (~48-56px), bold"
)
content = content.replace(
    "Home page: Headline text đúng nội dung",
    "Home page: Headline text đúng nội dung (Updated v28)"
)

# ─── 3. TC_HOME_UI_007 — Subtitle ───────────────────────────────────
content = content.replace(
    "Subtitle hiển thị: 'Chỉ cần mô tả — AI sẽ thiết kế cho bạn. Chất liệu premium, giao tận nơi.' Text xám, italic, centered. Font size ~16-18px",
    "Subtitle hiển thị mô tả ngắn gọn về dịch vụ thiết kế áo AI. Text xám, centered. Font size ~16-18px. (Content có thể thay đổi theo campaign)"
)

# ─── 4. TC_AUTH_UI_001 — Login title/subtitle ───────────────────────
content = content.replace(
    "Logo 'POD Platform' hiển thị (icon kim cương + text). Title: 'Đăng nhập'. Subtitle: 'Chào mừng bạn quay lại!' — centered",
    "Icon login (→]) hiển thị centered. Title: 'Chào mừng trở lại!'. Subtitle: 'Lưu thiết kế và nhận thêm nhiều Credits miễn phí.' — centered. Login dạng modal popup overlay"
)

# ─── 5. TC_AUTH_UI_002 — Email placeholder ───────────────────────────
content = content.replace(
    "Placeholder hiển thị: 'example@email.com'. Icon mail ở bên trái. Label 'Email' phía trên",
    "Placeholder hiển thị: 'name@example.com'. Label 'EMAIL' phía trên (uppercase). Không có icon mail bên trái"
)

# ─── 6. TC_DS_UI_001 — Header Design Studio ─────────────────────────
content = content.replace(
    "Header hiển thị: ← 'Quay lại' (trái), Logo 'Tryonic' icon (trái), text 'Design Studio' (giữa), Credits + icon User + icon Giỏ hàng (phải)",
    "Header hiển thị: ← 'Quay lại' (trái), Logo 'Tryonic' icon (trái), text 'Design Studio' (giữa), Credits badge + nút 'Chia sẻ' + icon User + icon Giỏ hàng (phải)"
)

# ─── 7. TC_DS_UI_002 — Credits badge ────────────────────────────────
content = content.replace(
    "Hiển thị: '12 Credits' + nút 'Nạp'. Credits badge có icon coin/circle",
    "Hiển thị: '12 Credits' + nút 'Chia sẻ' (thay vì Nạp). Credits badge có icon coin/circle"
)

# ─── 8. Append NEW test cases ────────────────────────────────────────
NEW_SECTIONS = r"""

---

## 🚀 Feature: GIỎ HÀNG (CART)
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_CART_UI_001` | `US-20` | Giỏ hàng - Layout | MH Giỏ hàng: Layout danh sách sản phẩm | 🎨 UI/UX | **🔴 P0** | 1. Click icon Giỏ hàng trên header<br>2. Quan sát layout | Hiển thị danh sách sản phẩm đã thêm. Mỗi item có: ảnh thumbnail thiết kế, tên sản phẩm, màu, size, input số lượng (+/-), giá, nút xóa (X). Header: 'Giỏ hàng (N sản phẩm)' |
| `TC_CART_UI_002` | `US-20` | Giỏ hàng - Layout | MH Giỏ hàng: Tổng tiền và nút Thanh toán | 🎨 UI/UX | **🔴 P0** | 1. Mở MH Giỏ hàng (có sản phẩm)<br>2. Quan sát phần bottom | Hiển thị: Tạm tính (giá × qty), Phí ship (nếu đã chọn), Tổng cộng (font lớn, bold). Nút 'Thanh toán' full-width, background đậm, text trắng |
| `TC_CART_UI_003` | `US-20` | Giỏ hàng - Empty | MH Giỏ hàng: Empty state khi giỏ trống | 🎨 UI/UX | **🟠 P1** | 1. Mở MH Giỏ hàng (chưa thêm sản phẩm)<br>2. Quan sát nội dung | Hiển thị empty state: icon giỏ hàng trống + text 'Giỏ hàng trống' + nút CTA 'Thiết kế ngay' hoặc 'Khám phá sản phẩm' |
| `TC_CART_UI_860` | `Global` | Responsive & Zoom | MH Giỏ hàng: Browser Zoom In/Out (50%-200%) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Giỏ hàng<br>2. Zoom In 200% / Zoom Out 50% | Layout giữ nguyên. Nút Thanh toán không bị che khuất. Danh sách sản phẩm scrollable |
| `TC_CART_UI_861` | `Global` | Responsive (iPhone) | MH Giỏ hàng: Responsive iPhone (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập MH Giỏ hàng trên iPhone Portrait<br>2. Thao tác với các items | Không thanh cuộn ngang. Items hiển thị dạng card stacking. Nút xóa dễ tap. Touch targets ≥44px |
| `TC_CART_UI_862` | `Global` | Responsive (Android) | MH Giỏ hàng: Responsive Android Phone (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập MH Giỏ hàng trên Android Portrait | Tương tự iPhone. Bàn phím ảo không che nút Thanh toán |
| `TC_CART_UI_863` | `Global` | Responsive (iPad) | MH Giỏ hàng: Responsive iPad (Portrait) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Giỏ hàng trên iPad Portrait | Layout 2 cột (danh sách + tổng tiền) hoặc 1 cột hợp lý |
| `TC_CART_UI_864` | `Global` | Responsive (Android Tablet) | MH Giỏ hàng: Responsive Android Tablet (Portrait) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Giỏ hàng trên Tablet Android Portrait | Tương tự iPad. Touch targets đủ lớn |
| `TC_CART_UI_865` | `Global` | Responsive (Landscape) | MH Giỏ hàng: Responsive Landscape | 🎨 UI/UX | **🔴 P0** | 1. Xoay ngang thiết bị từ dọc | UI tự sắp xếp lại. Nút Thanh toán vẫn hiển thị đầy đủ |

### 📌 Validation

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_CART_V_001` | `US-20` | Giỏ hàng - Qty | Cập nhật số lượng = 0 | ⚠️ Negative | **🟠 P1** | 1. Mở Giỏ hàng<br>2. Giảm qty xuống 0 | Hiển thị confirm xóa item hoặc tự động xóa. Qty tối thiểu = 1 |
| `TC_CART_V_002` | `US-20` | Giỏ hàng - Qty | Nhập số lượng bằng chữ | ⚠️ Negative | **🟢 P2** | 1. Mở Giỏ hàng<br>2. Nhập qty: 'abc' | Input chỉ nhận số. Không crash |
| `TC_CART_V_003` | `US-20` | Giỏ hàng - Qty | Số lượng vượt tối đa (>100) | ⚠️ Negative | **🟢 P2** | 1. Mở Giỏ hàng<br>2. Nhập qty: 999 | Giới hạn tối đa hoặc hiển thị warning |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_CART_F_001` | `US-20` | Giỏ hàng - Qty | Tăng số lượng sản phẩm (+) | ✅ Positive | **🔴 P0** | 1. Mở Giỏ hàng<br>2. Click nút + tăng qty từ 1 → 3 | Qty hiển thị = 3. Tổng giá = Đơn giá × 3. Cập nhật realtime |
| `TC_CART_F_002` | `US-20` | Giỏ hàng - Qty | Giảm số lượng sản phẩm (-) | ✅ Positive | **🔴 P0** | 1. Mở Giỏ hàng (qty = 3)<br>2. Click nút - giảm qty → 2 | Qty = 2. Tổng giá cập nhật. Nút - disabled khi qty = 1 |
| `TC_CART_F_003` | `US-20` | Giỏ hàng - Delete | Xóa sản phẩm khỏi giỏ | ✅ Positive | **🔴 P0** | 1. Mở Giỏ hàng<br>2. Click nút xóa (X) trên item<br>3. Confirm xóa | Item biến mất. Tổng giá cập nhật. Badge giỏ hàng trên header giảm. Nếu hết item → empty state |
| `TC_CART_F_004` | `US-20` | Giỏ hàng - Checkout | Click nút 'Thanh toán' từ giỏ hàng | ✅ Positive | **🔴 P0** | 1. Mở Giỏ hàng (có ≥1 item)<br>2. Click 'Thanh toán' | Chuyển sang trang Checkout. Thông tin sản phẩm, qty, giá truyền đúng. Nếu chưa login → popup login |
| `TC_CART_F_005` | `US-20` | Giỏ hàng - Persist | Refresh trang → giỏ hàng vẫn giữ nguyên | ✅ Positive | **🟠 P1** | 1. Thêm sản phẩm vào giỏ<br>2. Refresh trình duyệt<br>3. Mở lại giỏ hàng | Giỏ hàng giữ nguyên items, qty, thông tin. Data persist qua localStorage hoặc server |
| `TC_CART_F_006` | `US-20` | Giỏ hàng - Multiple | Thêm cùng sản phẩm nhưng khác size/màu | ✅ Positive | **🟠 P1** | 1. Thêm áo Trắng L vào giỏ<br>2. Thêm áo Đen M vào giỏ | 2 items riêng biệt hiển thị trong giỏ. Tổng = giá item 1 + giá item 2 |

---

## 🚀 Feature: PROFILE / ACCOUNT
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_PROF_UI_001` | `US-05` | Profile - Layout | MH Profile: Layout thông tin cá nhân | 🎨 UI/UX | **🟠 P1** | 1. Đăng nhập → Click icon User<br>2. Chọn Profile/Hồ sơ<br>3. Quan sát layout | Hiển thị: Avatar (có thể click upload mới), Tên người dùng, Email (read-only nếu OAuth), Số điện thoại (editable), Nút 'Lưu thay đổi' |
| `TC_PROF_UI_002` | `US-05` | Profile - Avatar | Avatar mặc định khi chưa upload | 🎨 UI/UX | **🟢 P2** | 1. Đăng nhập user mới (chưa upload avatar)<br>2. Quan sát avatar | Hiển thị avatar mặc định (placeholder icon hoặc initials). Có icon camera/upload overlay khi hover |
| `TC_PROF_UI_860` | `Global` | Responsive & Zoom | MH Profile: Browser Zoom In/Out (50%-200%) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Profile<br>2. Zoom In/Out | Layout giữ nguyên. Form fields không bị tràn |
| `TC_PROF_UI_861` | `Global` | Responsive (iPhone) | MH Profile: Responsive iPhone (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập MH Profile trên iPhone Portrait | Form fields full-width. Avatar centered trên. Nút Lưu dễ tap |
| `TC_PROF_UI_862` | `Global` | Responsive (Android) | MH Profile: Responsive Android (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập MH Profile trên Android Portrait | Tương tự iPhone. Bàn phím ảo không che fields |
| `TC_PROF_UI_863` | `Global` | Responsive (iPad) | MH Profile: Responsive iPad (Portrait) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Profile trên iPad Portrait | Form căn giữa hoặc 2 cột hợp lý |
| `TC_PROF_UI_864` | `Global` | Responsive (Android Tablet) | MH Profile: Responsive Android Tablet (Portrait) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập MH Profile trên Tablet Android | Tương tự iPad |
| `TC_PROF_UI_865` | `Global` | Responsive (Landscape) | MH Profile: Responsive Landscape | 🎨 UI/UX | **🔴 P0** | 1. Xoay ngang | UI tự sắp xếp phù hợp |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_PROF_F_001` | `US-05` | Profile - Edit | Cập nhật tên người dùng | ✅ Positive | **🟠 P1** | 1. Mở Profile<br>2. Sửa tên → 'Nguyễn Văn B'<br>3. Click 'Lưu' | Tên cập nhật thành công. Header hiển thị tên mới. Toast 'Đã lưu thay đổi' |
| `TC_PROF_F_002` | `US-05` | Profile - Avatar | Upload ảnh avatar mới (PNG/JPG < 5MB) | ✅ Positive | **🟠 P1** | 1. Mở Profile<br>2. Click avatar → Chọn ảnh mới<br>3. Quan sát | Avatar cập nhật. Preview hiển thị ảnh mới. Ảnh crop tròn |
| `TC_PROF_F_003` | `US-05` | Profile - Phone | Cập nhật số điện thoại | ✅ Positive | **🟠 P1** | 1. Mở Profile<br>2. Nhập SĐT: 0901234567<br>3. Click 'Lưu' | SĐT lưu thành công. Hiển thị đúng trên profile |
| `TC_PROF_F_004` | `US-05` | Profile - Logout | Click Đăng xuất | ✅ Positive | **🟠 P1** | 1. Mở Profile menu<br>2. Click 'Đăng xuất' | Session hủy. Redirect về trang chủ. Header hiển thị trạng thái Guest |

---

## 🚀 Feature: MY DESIGNS (Thiết kế của tôi)
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_MYDES_UI_001` | `US-18` | My Designs - Layout | MH My Designs: Grid thiết kế đã lưu | 🎨 UI/UX | **🟠 P1** | 1. Đăng nhập → Vào My Designs<br>2. Quan sát layout | Hiển thị grid/list các thiết kế đã lưu. Mỗi item có: ảnh preview mockup, tên thiết kế, ngày tạo/sửa, nút chỉnh sửa/xóa |
| `TC_MYDES_UI_002` | `US-18` | My Designs - Empty | Empty state khi chưa có thiết kế | 🎨 UI/UX | **🟢 P2** | 1. Đăng nhập user mới<br>2. Mở My Designs | Hiển thị: 'Bạn chưa có thiết kế nào' + nút 'Tạo thiết kế mới' |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_MYDES_F_001` | `US-18` | My Designs - Load | Click thiết kế → Mở trong Editor | ✅ Positive | **🟠 P1** | 1. Mở My Designs<br>2. Click 1 thiết kế | Design load vào Editor với tất cả layers đúng. Có thể tiếp tục chỉnh sửa |
| `TC_MYDES_F_002` | `US-18` | My Designs - Delete | Xóa thiết kế đã lưu | ✅ Positive | **🟠 P1** | 1. Mở My Designs<br>2. Click nút xóa trên thiết kế<br>3. Confirm | Thiết kế bị xóa khỏi danh sách. Confirm dialog trước khi xóa |
| `TC_MYDES_F_003` | `US-18` | My Designs - Rename | Đổi tên thiết kế | ✅ Positive | **🟢 P2** | 1. Mở My Designs<br>2. Click tên thiết kế → Nhập tên mới<br>3. Save | Tên cập nhật thành công |

---

## 🚀 Feature: AI TRY-ON (Thử đồ với AI)
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_TRYON_UI_001` | `US-DS-02` | AI Try-on - Layout | MH Thử đồ AI: Layout tổng quan | 🎨 UI/UX | **🟠 P1** | 1. Mở Design Studio (có artwork)<br>2. Click 'Thử Đồ với AI' trên sidebar | Mở modal/panel Thử Đồ AI. Hiển thị: upload zone ảnh người, preview kết quả, nút 'Tạo ảnh thử đồ'. Có hướng dẫn upload ảnh phù hợp |
| `TC_TRYON_UI_002` | `US-DS-02` | AI Try-on - Upload | Upload zone ảnh người | 🎨 UI/UX | **🟠 P1** | 1. Mở modal Thử Đồ AI<br>2. Quan sát upload zone | Hiển thị: drag & drop area, text 'Tải ảnh chân dung/toàn thân', icon upload. Accepted formats: PNG, JPG |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_TRYON_F_001` | `US-DS-02` | AI Try-on - Generate | Upload ảnh người → Tạo ảnh thử đồ | ✅ Positive | **🟠 P1** | 1. Mở Thử Đồ AI<br>2. Upload ảnh chân dung<br>3. Click 'Tạo ảnh thử đồ' | Loading state hiển thị. Kết quả: ảnh người mặc áo thun với thiết kế hiện tại. Trừ credits tương ứng |
| `TC_TRYON_F_002` | `US-DS-02` | AI Try-on - Download | Tải ảnh thử đồ về máy | ✅ Positive | **🟢 P2** | 1. Tạo ảnh thử đồ thành công<br>2. Click nút Download | Ảnh được tải về định dạng PNG/JPG. Resolution đủ cao |

### 📌 Validation

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_TRYON_V_001` | `US-DS-02` | AI Try-on - Upload | Upload ảnh không phải người | ⚠️ Negative | **🟠 P1** | 1. Mở Thử Đồ AI<br>2. Upload ảnh phong cảnh (không có người) | Hiển thị lỗi: 'Không phát hiện được người trong ảnh' hoặc kết quả không chính xác. Không crash |
| `TC_TRYON_V_002` | `US-DS-02` | AI Try-on - Canvas | Thử đồ khi canvas trống (không có artwork) | ⚠️ Negative | **🟠 P1** | 1. Mở Design Studio (canvas trống)<br>2. Click 'Thử Đồ với AI' | Hiển thị thông báo: 'Vui lòng thêm thiết kế trước' hoặc tạo ảnh thử đồ với áo trơn |

---

## 🚀 Feature: XÁC NHẬN ĐƠN HÀNG (ORDER CONFIRMATION)
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_CONF_UI_001` | `US-25` | Confirmation - Layout | MH Xác nhận đơn: Mã đơn và chi tiết | 🎨 UI/UX | **🟠 P1** | 1. Hoàn tất thanh toán thành công<br>2. Quan sát trang xác nhận | Hiển thị: icon thành công (✓), 'Đặt hàng thành công!', Mã đơn (#ORD-XXXX), Chi tiết sản phẩm (ảnh, tên, size, qty, giá), Tổng thanh toán, Địa chỉ giao hàng |
| `TC_CONF_UI_002` | `US-25` | Confirmation - CTA | Nút CTA sau khi đặt hàng | 🎨 UI/UX | **🟢 P2** | 1. Quan sát trang xác nhận đơn | Hiển thị 2 nút CTA: 'Xem đơn hàng' (→ Order Detail) và 'Tiếp tục mua sắm' (→ Home). Nút nổi bật, dễ click |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_CONF_F_001` | `US-25` | Confirmation - Navigate | Click 'Xem đơn hàng' → Chi tiết đơn | ✅ Positive | **🟠 P1** | 1. Trang xác nhận đơn<br>2. Click 'Xem đơn hàng' | Chuyển sang trang chi tiết đơn. Hiển thị timeline trạng thái |
| `TC_CONF_F_002` | `US-25` | Confirmation - Navigate | Click 'Tiếp tục mua sắm' → Home | ✅ Positive | **🟢 P2** | 1. Trang xác nhận đơn<br>2. Click 'Tiếp tục mua sắm' | Redirect về trang chủ /home/ |

---

## 🚀 Feature: ERROR PAGES & NOTIFICATIONS
### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_ERR_UI_001` | `Global` | Error - 404 | Trang 404: URL không tồn tại | 🎨 UI/UX | **🟠 P1** | 1. Truy cập URL không tồn tại (VD: /abc123)<br>2. Quan sát trang | Hiển thị trang 404 thân thiện: illustration, text 'Trang không tồn tại', nút 'Về trang chủ'. KHÔNG hiển thị lỗi kỹ thuật |
| `TC_ERR_UI_002` | `Global` | Error - Network | Mất kết nối mạng → thông báo | 🎨 UI/UX | **🟢 P2** | 1. Đang duyệt web<br>2. Ngắt kết nối mạng<br>3. Thực hiện thao tác | Hiển thị toast/banner: 'Mất kết nối mạng' hoặc xử lý gracefully. Không blank screen |
| `TC_TOAST_UI_001` | `Global` | Notification - Toast | Toast/Snackbar: Vị trí và thời gian hiển thị | 🎨 UI/UX | **🟢 P2** | 1. Thực hiện action trigger toast (VD: thêm giỏ hàng)<br>2. Quan sát toast message | Toast xuất hiện top-right hoặc bottom-center. Tự biến mất sau 3-5s. Có thể click dismiss. Không che khuất nút quan trọng |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_ERR_F_001` | `Global` | Error - Navigation | 404 → Click 'Về trang chủ' | ✅ Positive | **🟢 P2** | 1. Truy cập URL không tồn tại<br>2. Click nút 'Về trang chủ' | Redirect về /home/ thành công |
| `TC_ERR_F_002` | `Global` | Error - Direct URL | Truy cập SPA route trực tiếp (deep link) | ✅ Positive | **🟠 P1** | 1. Nhập trực tiếp URL: /design-studio hoặc /login<br>2. Quan sát | Trang load đúng (SPA routing). Không trả 404 cho các route hợp lệ |
"""

content = content.rstrip()
content += NEW_SECTIONS

with open(DST, "w", encoding="utf-8") as f:
    f.write(content)

# ─── Stats ───────────────────────────────────────────────────────────
lines = content.split("\n")
tc_count = sum(1 for line in lines if "`TC_" in line and "|" in line)
features = [line for line in lines if line.strip().startswith("## 🚀")]

print(f"✅ Created: {DST}")
print(f"📊 Total lines: {len(lines)}")
print(f"📊 Total TCs (approx): {tc_count}")
print(f"📊 Features ({len(features)}):")
for f_name in features:
    print(f"   {f_name.strip()}")
