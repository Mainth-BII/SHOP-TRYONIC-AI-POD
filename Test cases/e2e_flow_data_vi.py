"""Dữ liệu test E2E Flow - Luồng kết hợp đầy đủ từ đầu đến cuối."""

COLUMNS_E2E = [
    "STT",
    "TC_ID",
    "Tên luồng E2E",
    "Loại luồng",
    "Các bước thực hiện (Full Steps)",
    "Dữ liệu đầu vào",
    "Kết quả mong đợi (cuối luồng)",
    "Độ ưu tiên",
    "Expected_Result",
    "Actual_Result",
    "Thời gian thực thi",
    "Screenshot / Evidence",
    "Ghi chú / Bug"
]
COL_WIDTHS_E2E = [5, 16, 35, 16, 80, 35, 45, 10, 16, 16, 14, 22, 35]

E2E_FLOW_DATA = {
    # ============================================================
    # HAPPY PATH — LUỒNG CHÍNH THÀNH CÔNG
    # ============================================================
    "✅ HAPPY PATH — LUỒNG CHÍNH": [
        ("TC_E2E_001", "Happy Path: Mua ngay — Guest (Không đăng nhập)",
         "Happy Path",
         "1. Truy cập Home\n"
         "2. Nhập ý tưởng [Bạn muốn kể gì trên áo?]\n"
         "3. Chọn phong cách: Tối giản\n"
         "4. Click [Tạo ngay] → Chuyển sang Design Studio\n"
         "5. View hộp thoại Try-AI Designer: 3 artwork hiển thị\n"
         "6. Click chọn 1 artwork → Click [Dùng ảnh này]\n"
         "7. View [Cài đặt hình ảnh] trên áo\n"
         "8. Chỉnh Width/Height, Căn giữa\n"
         "9. Click [Đặt hàng] → Click [Mua ngay]\n"
         "10. MH Checkout: Nhập địa chỉ nhận hàng, chọn thanh toán COD\n"
         "11. Click [Thanh toán + Số tiền]\n"
         "12. MH Đặt hàng thành công: Hiển thị mã đơn\n"
         "13. Click [Xem đơn hàng]",
         "Ý tưởng: 'Rồng Việt Nam phong cách watercolor'\nPhong cách: Tối giản\nThông tin: Nguyễn Văn A, 0901234567, Q1 TPHCM\nThanh toán: COD",
         "Đặt hàng thành công, hiển thị mã đơn, xem được chi tiết đơn hàng",
         "P0", ""),

        ("TC_E2E_002", "Happy Path: Mua ngay — Đã đăng nhập",
         "Happy Path",
         "1. Đăng nhập tài khoản trước\n"
         "2. Truy cập Home → Nhập ý tưởng → Chọn phong cách\n"
         "3. Click [Tạo ngay] → Design Studio\n"
         "4. View 3 artwork → Chọn 1 → [Dùng ảnh này]\n"
         "5. Cài đặt hình ảnh: Xóa nền ON, Căn giữa\n"
         "6. [Đặt hàng] → [Mua ngay]\n"
         "7. MH Checkout: Thông tin tự động auto-fill từ Profile\n"
         "8. Kiểm tra auto-fill đúng → Chọn thanh toán\n"
         "9. Click [Thanh toán] → Thành công\n"
         "10. Xem đơn hàng",
         "Ý tưởng: 'Mèo galaxy neon'\nPhong cách: Sáng tạo\nUser đã login Google",
         "Auto-fill đúng thông tin, đặt hàng thành công, xem đơn hàng OK",
         "P0", ""),

        ("TC_E2E_003", "Happy Path: Thêm giỏ hàng → Thanh toán",
         "Happy Path",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. Design Studio → View 3 artwork → [Dùng ảnh này]\n"
         "3. Cài đặt hình ảnh → Chỉnh sửa OK\n"
         "4. [Đặt hàng] → Click [Thêm giỏ hàng]\n"
         "5. Kiểm tra badge giỏ hàng +1, thông báo thành công\n"
         "6. Mở Giỏ hàng → Kiểm tra sản phẩm\n"
         "7. Click [Thanh toán ngay] trong giỏ\n"
         "8. MH Checkout → Nhập thông tin → Thanh toán\n"
         "9. Đặt hàng thành công → Xem đơn",
         "Ý tưởng: 'Phong cảnh Hội An'\nSize: L",
         "Sản phẩm vào giỏ, checkout từ giỏ thành công, mã đơn hiển thị",
         "P0", ""),
    ],

    # ============================================================
    # LUỒNG TỪ THƯ VIỆN MẪU & UPLOAD ẢNH
    # ============================================================
    "📂 LUỒNG TỪ THƯ VIỆN MẪU & UPLOAD ẢNH": [
        ("TC_E2E_027", "Chọn từ mẫu có sẵn → Dùng template → Checkout (Guest)",
         "Template",
         "1. Truy cập Home\n"
         "2. Click [Chọn từ mẫu có sẵn] — 'Khám phá thư viện mẫu'\n"
         "3. Chuyển sang MH Thư viện mẫu\n"
         "4. Duyệt danh mục → Click chọn 1 template\n"
         "5. Template apply lên canvas Design Studio\n"
         "6. View [Cài đặt hình ảnh] → Chỉnh W/H, Căn giữa\n"
         "7. [Đặt hàng] → [Mua ngay]\n"
         "8. MH Checkout: Nhập thông tin → Thanh toán\n"
         "9. Đặt hàng thành công → Xem đơn hàng",
         "Entry: Home → [Chọn từ mẫu có sẵn]\nTemplate: chọn mẫu bất kỳ\nGuest — COD",
         "Template apply đúng trên canvas, chỉnh sửa OK, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_028", "Chọn từ mẫu có sẵn → Sửa template → Checkout (Đăng nhập)",
         "Template",
         "1. Đăng nhập trước\n"
         "2. Home → Click [Chọn từ mẫu có sẵn]\n"
         "3. Thư viện mẫu → Chọn template\n"
         "4. Template lên canvas → Click [Sửa với AI]\n"
         "5. Ảnh template đính kèm tự động → Nhập prompt sửa\n"
         "6. [Tạo Artwork mới] → View 3 artwork\n"
         "7. [Dùng ảnh này] → Cài đặt hình ảnh\n"
         "8. [Đặt hàng] → Checkout (auto-fill) → Thành công",
         "Entry: Home → [Chọn từ mẫu có sẵn]\nSửa: 'Đổi phong cách tối giản'\nUser đã login",
         "Template + AI sửa thành công, auto-fill, đặt hàng OK",
         "P0", ""),

        ("TC_E2E_029", "Chọn từ mẫu có sẵn → Thêm giỏ hàng → Checkout",
         "Template",
         "1. Home → [Chọn từ mẫu có sẵn] → Thư viện mẫu\n"
         "2. Chọn template → Apply lên canvas\n"
         "3. Cài đặt hình ảnh → Xóa nền, Căn giữa\n"
         "4. [Đặt hàng] → [Thêm giỏ hàng]\n"
         "5. Badge giỏ +1, toast thành công\n"
         "6. Mở Giỏ hàng → [Thanh toán ngay]\n"
         "7. Checkout → Thành công",
         "Entry: Home → [Chọn từ mẫu có sẵn]\nXóa nền ON\nThêm giỏ hàng",
         "Template vào giỏ, checkout từ giỏ thành công",
         "P1", ""),

        ("TC_E2E_030", "Tải lên ảnh của bạn → Upload file → Checkout (Guest)",
         "Upload",
         "1. Truy cập Home\n"
         "2. Click [Tải lên ảnh của bạn] — 'Sử dụng file thiết kế riêng'\n"
         "3. Hộp thoại Upload → Chọn file PNG/JPG từ máy\n"
         "4. Ảnh upload thành công → Apply lên canvas Design Studio\n"
         "5. View [Cài đặt hình ảnh]: Xóa nền, Chỉnh W/H, Căn giữa\n"
         "6. [Đặt hàng] → [Mua ngay]\n"
         "7. MH Checkout: Nhập thông tin → Thanh toán\n"
         "8. Đặt hàng thành công → Xem đơn hàng",
         "Entry: Home → [Tải lên ảnh của bạn]\nFile: logo_company.png (1200x1200)\nGuest — COD",
         "Ảnh upload hiển thị đúng trên canvas, chỉnh sửa OK, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_031", "Tải lên ảnh → Sửa với AI → Checkout (Đăng nhập)",
         "Upload",
         "1. Đăng nhập trước\n"
         "2. Home → [Tải lên ảnh của bạn] → Upload file PNG\n"
         "3. Ảnh lên canvas → Click [Sửa với AI]\n"
         "4. Ảnh gốc đính kèm tự động → Nhập: 'Thêm viền neon glow'\n"
         "5. [Tạo Artwork mới] → View 3 artwork\n"
         "6. [Dùng ảnh này] → Cài đặt → Căn giữa\n"
         "7. [Đặt hàng] → Checkout (auto-fill) → Thành công",
         "Entry: Home → [Tải lên ảnh của bạn]\nFile: my_design.jpg\nSửa: 'Thêm viền neon glow'\nUser đã login",
         "Upload + AI enhance thành công, auto-fill, đặt hàng OK",
         "P0", ""),

        ("TC_E2E_032", "Tải lên ảnh → Thêm giỏ hàng → Upload ảnh khác → Thêm giỏ → Checkout",
         "Upload",
         "1. Home → [Tải lên ảnh của bạn] → Upload file 1\n"
         "2. Ảnh 1 lên canvas → Cài đặt → [Thêm giỏ hàng]\n"
         "3. Quay lại Home → [Tải lên ảnh của bạn] → Upload file 2\n"
         "4. Ảnh 2 lên canvas → Cài đặt → [Thêm giỏ hàng]\n"
         "5. Giỏ hàng: 2 SP upload khác nhau\n"
         "6. [Thanh toán ngay] → Checkout → Thành công",
         "File 1: team_logo.png\nFile 2: event_poster.jpg\nMulti-item upload checkout",
         "2 SP upload khác nhau trong giỏ, tổng tiền đúng, checkout OK",
         "P1", "Multi-upload test"),
    ],

    # ============================================================
    # LUỒNG SỬA ARTWORK — LOOP DESIGN
    # ============================================================
    "🔄 LUỒNG SỬA ARTWORK — LOOP DESIGN": [
        ("TC_E2E_004", "Sửa tiếp 1 lần → Dùng ảnh → Checkout",
         "Sửa tiếp",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. Design Studio → View 3 artwork\n"
         "3. Nhập [Bạn muốn sửa gì?]: 'Đổi tông màu ấm hơn'\n"
         "4. Click [Sửa tiếp] → AI tạo lại 3 artwork mới\n"
         "5. Duyệt ảnh bằng [>] [<] → Chọn ảnh ưng ý\n"
         "6. Click [Dùng ảnh này]\n"
         "7. Cài đặt hình ảnh → Căn giữa\n"
         "8. [Đặt hàng] → [Mua ngay] → Checkout → Thành công",
         "Ý tưởng gốc: 'Hoa sen Việt Nam'\nSửa: 'Đổi tông màu ấm hơn'",
         "Artwork mới phản ánh chỉnh sửa, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_005", "Sửa tiếp nhiều lần (3 lần loop) → Dùng ảnh",
         "Sửa tiếp",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. View 3 artwork → [Sửa tiếp] lần 1: 'Thêm hiệu ứng glow'\n"
         "3. View 3 artwork mới → [Sửa tiếp] lần 2: 'Làm đậm nét hơn'\n"
         "4. View 3 artwork mới → [Sửa tiếp] lần 3: 'Giảm màu nền'\n"
         "5. View 3 artwork cuối → [Dùng ảnh này]\n"
         "6. Cài đặt hình ảnh → Đặt hàng → Checkout → Thành công",
         "3 lần sửa liên tiếp với prompt khác nhau",
         "Mỗi lần sửa tạo artwork mới đúng prompt, cuối cùng đặt hàng OK",
         "P1", "Loop stress test"),

        ("TC_E2E_006", "Sửa với AI → Tạo artwork mới từ ảnh gốc → Checkout",
         "Sửa với AI",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. View 3 artwork → [Dùng ảnh này]\n"
         "3. Cài đặt hình ảnh → Xem preview trên áo\n"
         "4. Click [Sửa với AI]\n"
         "5. MH Tạo artwork mới: Ảnh gốc đã đính kèm tự động\n"
         "6. Nhập: 'Sửa màu sáng lên, thêm tia nắng'\n"
         "7. Click [Tạo Artwork mới] → View 3 artwork mới\n"
         "8. [Dùng ảnh này] → Cài đặt → Đặt hàng → Checkout → Thành công",
         "Ảnh gốc + Sửa: 'Sửa màu sáng lên, thêm tia nắng'",
         "AI tạo artwork dựa trên gốc + prompt sửa, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_007", "Chọn mẫu này → Chỉnh canvas → Đặt hàng",
         "Chọn mẫu",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. View 3 artwork → [Dùng ảnh này]\n"
         "3. View artwork trên áo canvas\n"
         "4. Click [Chọn mẫu này] → MH Cài đặt hình ảnh\n"
         "5. Bật Xóa nền, chỉnh W/H, Thứ tự lớp, Căn giữa\n"
         "6. Kéo/drag artwork trên canvas trực tiếp\n"
         "7. [Đặt hàng] → [Mua ngay] → Checkout → Thành công",
         "Chỉnh: Xóa nền ON, W=250, H=300, Căn giữa",
         "Artwork hiển thị đúng tùy chỉnh trên áo, đặt hàng OK",
         "P0", ""),

        ("TC_E2E_008", "Sửa tiếp → Sửa với AI → Chọn mẫu → Checkout (Full loop)",
         "Kết hợp",
         "1. Home → [Tạo ngay] → View 3 artwork\n"
         "2. [Sửa tiếp] → View 3 artwork mới → [Dùng ảnh này]\n"
         "3. Canvas → [Sửa với AI] → Nhập prompt → [Tạo Artwork mới]\n"
         "4. View 3 artwork mới → [Dùng ảnh này]\n"
         "5. Canvas → [Chọn mẫu này] → Cài đặt hình ảnh\n"
         "6. Chỉnh sửa → [Đặt hàng] → Checkout → Thành công",
         "Kết hợp cả 3 nút: Sửa tiếp + Sửa với AI + Chọn mẫu",
         "Mọi bước chuyển đổi mượt, artwork cuối cùng đúng, đặt hàng OK",
         "P1", "Full combination test"),
    ],

    # ============================================================
    # LUỒNG CHECKOUT — CÁC HÌNH THỨC ĐĂNG NHẬP
    # ============================================================
    "💳 LUỒNG CHECKOUT — ĐĂNG NHẬP": [
        ("TC_E2E_009", "Guest → Đăng nhập Facebook tại Checkout → Thanh toán",
         "Checkout Login",
         "1. Home → Tạo artwork → Dùng ảnh → Cài đặt → [Đặt hàng] → [Mua ngay]\n"
         "2. MH Checkout (chưa đăng nhập)\n"
         "3. Click [Đăng nhập qua Facebook]\n"
         "4. Popup Facebook OAuth → Đăng nhập thành công\n"
         "5. Thông tin tự động auto-fill\n"
         "6. Chọn thanh toán → [Thanh toán] → Thành công",
         "Tài khoản Facebook hợp lệ",
         "Login Facebook OK, auto-fill thông tin, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_010", "Guest → Đăng nhập Google tại Checkout → Thanh toán",
         "Checkout Login",
         "1. Home → Tạo artwork → Dùng ảnh → Cài đặt → [Đặt hàng] → [Mua ngay]\n"
         "2. MH Checkout → Click [Đăng nhập qua Google]\n"
         "3. Popup Google OAuth → Đăng nhập OK\n"
         "4. Auto-fill → Thanh toán → Thành công",
         "Tài khoản Google hợp lệ",
         "Login Google OK, auto-fill đúng, đặt hàng thành công",
         "P0", ""),

        ("TC_E2E_011", "Guest → Đăng nhập Email tại Checkout → Thanh toán",
         "Checkout Login",
         "1. Home → Tạo artwork → Dùng ảnh → Cài đặt → [Đặt hàng] → [Mua ngay]\n"
         "2. MH Checkout → Click [Đăng nhập qua Email]\n"
         "3. Nhập Email + Password → Đăng nhập\n"
         "4. Auto-fill → Thanh toán → Thành công",
         "Email: test@example.com, Pass: ****",
         "Login Email OK, auto-fill đúng, đặt hàng thành công",
         "P1", ""),

        ("TC_E2E_012", "Thêm giỏ hàng nhiều sản phẩm → Checkout cùng lúc",
         "Multi-item",
         "1. Home → Tạo artwork 1 → Dùng ảnh → [Thêm giỏ hàng]\n"
         "2. Home → Tạo artwork 2 (ý tưởng khác) → Dùng ảnh → [Thêm giỏ hàng]\n"
         "3. Mở Giỏ hàng → Kiểm tra 2 sản phẩm\n"
         "4. [Thanh toán ngay] → Checkout → Kiểm tra tổng tiền 2 SP\n"
         "5. Thanh toán → Thành công",
         "SP1: 'Rồng watercolor' Size M\nSP2: 'Mèo galaxy' Size L",
         "Giỏ hàng đúng 2 SP, tổng tiền chính xác, đặt hàng OK",
         "P0", ""),
    ],

    # ============================================================
    # LUỒNG CHỈNH SỬA HÌNH ẢNH NÂNG CAO
    # ============================================================
    "⚙️ LUỒNG CHỈNH SỬA HÌNH ẢNH NÂNG CAO": [
        ("TC_E2E_013", "Xóa nền → Resize → Căn giữa → Đặt hàng",
         "Chỉnh sửa",
         "1. Home → Tạo artwork → [Dùng ảnh này]\n"
         "2. Cài đặt hình ảnh: Bật [Xóa nền]\n"
         "3. Chỉnh Width = 200, Height = 300\n"
         "4. Chọn Vị trí: [Căn giữa]\n"
         "5. Preview trên áo → OK\n"
         "6. [Đặt hàng] → [Mua ngay] → Checkout → Thành công",
         "Xóa nền: ON\nW: 200, H: 300\nVị trí: Căn giữa",
         "Artwork không nền, đúng kích thước, căn giữa, đặt hàng OK",
         "P0", ""),

        ("TC_E2E_014", "Drag trên canvas → Thay đổi layer → Đặt hàng",
         "Chỉnh sửa",
         "1. Home → Tạo artwork → [Dùng ảnh này]\n"
         "2. Kéo (drag) artwork đến vị trí mong muốn trên canvas\n"
         "3. Resize bằng handle góc\n"
         "4. Thứ tự lớp: [Đưa lên trên]\n"
         "5. Kiểm tra preview → [Đặt hàng] → Checkout → Thành công",
         "Drag: Vị trí ngực trái\nLayer: Đưa lên trên",
         "Artwork ở đúng vị trí drag, layer đúng, đặt hàng OK",
         "P1", ""),

        ("TC_E2E_015", "Chỉnh sửa → Undo/Tắt xóa nền → Đặt hàng",
         "Chỉnh sửa",
         "1. Home → Tạo artwork → [Dùng ảnh này]\n"
         "2. Bật [Xóa nền] → kiểm tra ảnh không nền\n"
         "3. TẮT [Xóa nền] → kiểm tra nền hiện lại\n"
         "4. Chỉnh kích thước cuối cùng → Căn giữa\n"
         "5. [Đặt hàng] → Checkout → Thành công",
         "Xóa nền: ON → OFF → verify",
         "Toggle xóa nền hoạt động đúng 2 chiều, đặt hàng OK",
         "P1", ""),
    ],

    # ============================================================
    # LUỒNG MOBILE / RESPONSIVE
    # ============================================================
    "📱 LUỒNG MOBILE / RESPONSIVE": [
        ("TC_E2E_016", "Full flow trên Mobile 375px (iPhone SE)",
         "Mobile",
         "1. Mobile 375px: Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. Design Studio mobile → View 3 artwork (swipe)\n"
         "3. [Dùng ảnh này] → Cài đặt hình ảnh mobile\n"
         "4. Chỉnh sửa trên canvas touch → Pinch zoom/drag\n"
         "5. [Đặt hàng] → [Mua ngay] → Checkout mobile\n"
         "6. Nhập form → Thanh toán → Thành công",
         "Viewport: 375x667\nTouch: Swipe, Pinch, Drag",
         "Mọi bước responsive đúng, touch hoạt động, đặt hàng OK",
         "P0", ""),

        ("TC_E2E_017", "Full flow trên Tablet 768px (iPad)",
         "Tablet",
         "1. Tablet 768px: Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. Design Studio → View artwork → [Dùng ảnh]\n"
         "3. Cài đặt hình ảnh (sidebar/panel layout)\n"
         "4. [Đặt hàng] → Checkout → Thành công",
         "Viewport: 768x1024",
         "Layout tablet hiển thị đúng, không bị vỡ UI, đặt hàng OK",
         "P1", ""),
    ],

    # ============================================================
    # LUỒNG NEGATIVE / GIÁN ĐOẠN
    # ============================================================
    "⚠️ LUỒNG NEGATIVE / GIÁN ĐOẠN": [
        ("TC_E2E_018", "Refresh trang giữa Bước Cài đặt hình ảnh",
         "Negative",
         "1. Home → Tạo artwork → [Dùng ảnh này]\n"
         "2. Cài đặt hình ảnh: chỉnh W/H, xóa nền\n"
         "3. *** REFRESH TRANG (F5) ***\n"
         "4. Kiểm tra: artwork và cài đặt có được giữ lại không?\n"
         "5. Nếu giữ lại → tiếp tục Đặt hàng → Checkout → Thành công\n"
         "6. Nếu mất → phải tạo lại từ đầu",
         "F5 refresh tại bước Cài đặt hình ảnh",
         "Artwork và settings được giữ lại (hoặc recover được), UX rõ ràng",
         "P1", ""),

        ("TC_E2E_019", "Back browser từ Checkout → quay lại Design Studio",
         "Negative",
         "1. Home → Tạo → Dùng ảnh → Cài đặt → [Đặt hàng] → [Mua ngay]\n"
         "2. Đang ở MH Checkout\n"
         "3. *** CLICK BACK BROWSER ***\n"
         "4. Kiểm tra: quay lại Design Studio, artwork còn trên canvas?\n"
         "5. Tiếp tục [Đặt hàng] lại → Checkout → Thành công",
         "Browser Back tại Checkout",
         "Quay lại DS bình thường, artwork không mất, đặt lại được",
         "P1", ""),

        ("TC_E2E_020", "Mất mạng khi AI đang tạo artwork",
         "Negative",
         "1. Home → Nhập ý tưởng → [Tạo ngay]\n"
         "2. *** MẤT KẾT NỐI MẠNG khi AI đang xử lý ***\n"
         "3. Kiểm tra: hiển thị lỗi mạng + nút [Thử lại]\n"
         "4. Bật lại mạng → Click [Thử lại]\n"
         "5. AI tạo artwork OK → tiếp tục flow → Checkout → Thành công",
         "Tắt WiFi tại bước AI generate",
         "Lỗi mạng xử lý gracefully, retry hoạt động, không mất data",
         "P1", ""),

        ("TC_E2E_021", "Checkout → Submit form với field trống",
         "Negative",
         "1. Home → Tạo → Dùng ảnh → Cài đặt → [Đặt hàng] → [Mua ngay]\n"
         "2. MH Checkout: BỎ TRỐNG một số field bắt buộc\n"
         "3. Click [Thanh toán]\n"
         "4. Kiểm tra: hiển thị lỗi validation rõ ràng\n"
         "5. Sửa lại field → Submit lại → Thành công",
         "Để trống: SĐT, Địa chỉ",
         "Validation lỗi đúng field, sửa lại và submit OK",
         "P0", ""),

        ("TC_E2E_022", "Không chọn ảnh/không nhập ý tưởng → luồng bị chặn",
         "Negative",
         "1. Home → KHÔNG nhập ý tưởng → Click [Tạo ngay]\n"
         "2. Kiểm tra: hiển thị lỗi validation\n"
         "3. Nhập ý tưởng → [Tạo ngay] → View 3 artwork\n"
         "4. KHÔNG chọn ảnh nào → thử [Dùng ảnh này]\n"
         "5. Kiểm tra xử lý khi chưa select ảnh\n"
         "6. Chọn ảnh → tiếp tục flow → Checkout → Thành công",
         "(trống ý tưởng) + (không chọn ảnh)",
         "Validation chặn đúng chỗ, hướng dẫn user rõ, flow recover được",
         "P0", ""),
    ],

    # ============================================================
    # LUỒNG ĐẶC BIỆT
    # ============================================================
    "🔥 LUỒNG ĐẶC BIỆT": [
        ("TC_E2E_023", "Tạo 2 đơn hàng liên tiếp cùng session",
         "Đặc biệt",
         "1. Home → Tạo artwork 1 → Dùng ảnh → [Đặt hàng] → [Mua ngay] → Checkout → Thành công (Đơn 1)\n"
         "2. Quay lại Home → Tạo artwork 2 (ý tưởng khác)\n"
         "3. Dùng ảnh → [Đặt hàng] → [Mua ngay] → Checkout → Thành công (Đơn 2)\n"
         "4. Kiểm tra: 2 đơn hàng riêng biệt, mã khác nhau",
         "Đơn 1: 'Rồng VN' COD\nĐơn 2: 'Hoa sen' Chuyển khoản",
         "2 đơn hàng tạo thành công, mã khác nhau, không conflict",
         "P1", ""),

        ("TC_E2E_024", "Thêm giỏ → Sửa artwork → Thêm giỏ lại → Checkout",
         "Đặc biệt",
         "1. Home → Tạo artwork → Dùng ảnh → [Thêm giỏ hàng] (SP bản gốc)\n"
         "2. Quay lại canvas → [Sửa với AI] → Nhập prompt → Tạo mới\n"
         "3. Dùng ảnh mới → [Thêm giỏ hàng] (SP bản sửa)\n"
         "4. Giỏ hàng: kiểm tra 2 SP khác nhau (gốc vs sửa)\n"
         "5. Checkout toàn bộ giỏ → Thành công",
         "SP1: artwork gốc\nSP2: artwork đã sửa AI",
         "Giỏ có 2 SP khác nhau, thumbnail đúng, checkout OK",
         "P1", ""),

        ("TC_E2E_025", "Full flow với phong cách khác: 3D / Anime / Trừu tượng",
         "Đặc biệt",
         "1. Home → Ý tưởng: 'Samurai Nhật Bản'\n"
         "2. Chọn phong cách: 3D (hoặc Anime, Trừu tượng)\n"
         "3. [Tạo ngay] → View 3 artwork phong cách 3D\n"
         "4. Dùng ảnh → Cài đặt → Đặt hàng → Checkout → Thành công\n"
         "5. Kiểm tra artwork thật sự giống phong cách đã chọn",
         "Phong cách: 3D\nÝ tưởng: 'Samurai Nhật Bản'",
         "Artwork đúng phong cách 3D, không bị lẫn style, đặt hàng OK",
         "P1", "Lặp lại với Anime, Trừu tượng"),

        ("TC_E2E_026", "Input chứa ký tự đặc biệt / emoji → Full flow",
         "Đặc biệt",
         "1. Home → Ý tưởng: '🐉 Rồng & Phượng <b>HTML</b> @#$%'\n"
         "2. [Tạo ngay] → AI xử lý được prompt đặc biệt\n"
         "3. View artwork → Dùng ảnh → Cài đặt → Đặt hàng\n"
         "4. Checkout → Thông tin bình thường → Thành công",
         "Ý tưởng chứa: emoji, HTML, special chars",
         "Không XSS, AI xử lý được, full flow thành công",
         "P1", "Security + Functional"),
    ],
}
