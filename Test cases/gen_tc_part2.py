# Part 2: Epic 4 (Editor) + Epic 5 (Checkout) + Epic 6 (Orders)

EPIC4_EDITOR = [
    # --- Upload (US-13) ---
    ["TC_DES_001","US-13","Editor","Upload","Upload PNG < 25MB thành công","Positive","P0","Editor mở","file: artwork.png (2MB)","1. Click Upload\n2. Chọn artwork.png\n3. Quan sát canvas","Ảnh hiện trên canvas. Layer mới tạo"],
    ["TC_DES_002","US-13","Editor","Upload","Upload JPG thành công","Positive","P0","Editor mở","file: photo.jpg (3MB)","1. Click Upload\n2. Chọn photo.jpg","Ảnh hiện trên canvas"],
    ["TC_DES_003","US-13","Editor","Upload","Upload file > 25MB","Negative","P0","Editor mở","file: huge.png (30MB)","1. Click Upload\n2. Chọn file 30MB","Hiển thị lỗi: 'File vượt quá 25MB'"],
    ["TC_DES_004","US-13","Editor","Upload","Upload file format không hỗ trợ (PDF)","Negative","P0","Editor mở","file: doc.pdf","1. Click Upload\n2. Chọn file PDF","Hiển thị lỗi: 'Chỉ hỗ trợ PNG/JPG'"],
    ["TC_DES_005","US-13","Editor","Upload","Upload file 0KB (empty)","Negative","P1","Editor mở","file: empty.png (0KB)","1. Upload file rỗng","Hiển thị lỗi file không hợp lệ"],
    ["TC_DES_006","US-13","Editor","Upload","Upload ảnh < 150 DPI - cảnh báo chất lượng","Negative","P0","Editor mở","file: lowres.jpg (72 DPI)","1. Upload ảnh 72 DPI","Hiển thị warning: 'Low Quality - May be blurry when printed'"],
    ["TC_DES_007","US-13","Editor","Upload","Upload file boundary = 25MB","Boundary","P1","Editor mở","file: exact25.png (25MB)","1. Upload file đúng 25MB","Upload thành công (= max cho phép)"],
    # --- Text (US-14) ---
    ["TC_DES_008","US-14","Editor","Text","Thêm text layer mới","Positive","P0","Editor mở","text: Hello World","1. Click 'Add Text'\n2. Nhập: Hello World\n3. Đổi Font: Roboto, Color: Red","Text hiện đúng style trên canvas"],
    ["TC_DES_009","US-14","Editor","Text","Text chứa tiếng Việt có dấu","Positive","P0","Editor mở","text: Xin chào Việt Nam","1. Nhập text tiếng Việt có dấu","Hiển thị đúng font + dấu. Không bị lỗi encoding"],
    ["TC_DES_010","US-14","Editor","Text","Text rỗng","Negative","P1","Editor mở","","1. Click 'Add Text'\n2. Không nhập gì\n3. Click ra ngoài","Không tạo layer rỗng hoặc tự xóa layer trống"],
    ["TC_DES_011","US-14","Editor","Text","Text rất dài (500+ ký tự)","Boundary","P1","Editor mở","text: 500 chars","1. Nhập text 500 ký tự","Text wrap hoặc warning. Không vỡ canvas"],
    # --- Drag/Resize/Rotate (US-15) ---
    ["TC_DES_012","US-15","Editor","Canvas","Drag artwork di chuyển vị trí","Positive","P0","Có layer trên canvas","","1. Click + hold artwork\n2. Kéo sang vị trí mới","Artwork di chuyển mượt theo chuột"],
    ["TC_DES_013","US-15","Editor","Canvas","Resize artwork giữ tỷ lệ","Positive","P0","Có layer","","1. Kéo corner handle","Artwork resize giữ aspect ratio"],
    ["TC_DES_014","US-15","Editor","Canvas","Rotate artwork 45°","Positive","P0","Có layer","","1. Kéo rotation handle","Artwork xoay đúng góc. Snap guides hiển thị"],
    ["TC_DES_015","US-15","Editor","Canvas","Artwork ngoài Safe Zone → warning","Positive","P0","Có artwork","","1. Kéo artwork ra ngoài vùng in","Warning: artwork ngoài safe zone. Đường viền đỏ"],
    # --- Layer Management (US-16) ---
    ["TC_DES_016","US-16","Editor","Layers","Bring to front/back layer","Positive","P1","Có 2+ layers chồng nhau","","1. Chọn layer dưới\n2. Click 'Bring to front'","Layer đó lên trên cùng"],
    ["TC_DES_017","US-16","Editor","Layers","Delete layer","Positive","P1","Có layer","","1. Chọn layer\n2. Click Delete/Backspace","Layer bị xóa. Canvas update"],
    # --- Undo/Redo (US-17) ---
    ["TC_DES_018","US-17","Editor","History","Undo thao tác vừa làm","Positive","P1","Đã add text + move","","1. Click Undo\n2. Quan sát canvas","Canvas quay về trạng thái trước đó"],
    ["TC_DES_019","US-17","Editor","History","Redo sau khi undo","Positive","P1","Đã undo 1 thao tác","","1. Click Redo","Canvas khôi phục thao tác đã undo"],
    ["TC_DES_020","US-17","Editor","History","Undo khi không có history","Boundary","P2","Canvas mới, chưa thao tác","","1. Click Undo","Undo disabled hoặc không có hiệu ứng"],
    # --- Save Design (US-18) ---
    ["TC_DES_021","US-18","Editor","Save","Save design vào My Designs","Positive","P0","Đã đăng nhập, design dở dang","","1. Click 'Save'\n2. Nhập tên design","Lưu thành công. Hiển thị ở My Designs. DB: user_designs record mới"],
    ["TC_DES_022","US-18","Editor","Save","Save design khi Guest → yêu cầu login","Negative","P0","Chưa đăng nhập","","1. Click 'Save'","Hiện popup login. Sau login → save + migrate"],
    ["TC_DES_023","US-18","Editor","Save","Load design đã save và tiếp tục chỉnh sửa","Positive","P0","Đã có saved design","","1. Vào My Designs\n2. Click design\n3. Chỉnh sửa","Design load đúng tất cả layers. Chỉnh sửa bình thường"],
    # --- 3D Mockup (US-19) ---
    ["TC_DES_024","US-19","Editor","Preview","Xem 3D mockup xoay được","Positive","P0","Có artwork trên canvas","","1. Click '3D View'","Model 3D hiển thị. Có thể xoay bằng chuột. Artwork hiện đúng vị trí"],
    ["TC_DES_025","US-19","Editor","Preview","3D mockup hiển thị Front + Back","Positive","P0","Có artwork cả 2 mặt","","1. Xoay 3D view","Thấy artwork mặt trước và mặt sau khi xoay"],
    # --- Editor UI/UX Test Cases (from Stitch Design) ---
    ["TC_DES_UI_026","US-13","Editor","UI/UX","Editor page: Menu công cụ trái hiển thị đúng text","UI/UX","P1","Mở /editor","","1. Quan sát cột bên trái","Hiển thị các nút: 'Artwork của tôi', 'Thêm Text', 'Thêm Hình ảnh', 'Thêm Icon'"],
    ["TC_ర్ణDES_UI_027","US-10","Editor","UI/UX","Editor page: Panel cấu hình phải hiển thị đúng","UI/UX","P1","Mở /editor","","1. Quan sát cột bên phải","Hiển thị tên SP (VD: 'T-shirt Premium Cotton'), Màu sắc (White, Black, Navy, Grey), Kích thước (S-2XL), Giá (VD: '349.000 đ'), nút 'Thêm vào giỏ hàng'"],
    ["TC_DES_UI_028","US-13","Editor","UI/UX","Editor page: Empty state màn hình Artwork của tôi","UI/UX","P2","User mới, mở Artwork của tôi","","1. Click 'Artwork của tôi'","Hiển thị: 'Kho thiết kế trống trơn'. Subtext: 'Tạo artwork từ AI hoặc upload thiết kế từ máy tính'. Nút: 'Tạo AI Artwork', 'Upload Design'"],
]

EPIC5_CHECKOUT = [
    # --- Add to Cart (US-20) ---
    ["TC_ORD_001","US-20","Cart","Add","Add designed product vào giỏ","Positive","P0","Design hoàn tất","size:L, qty:1","1. Chọn Size L, Qty 1\n2. Click 'Add to Cart'","Giỏ hàng +1 item: thumbnail, type, color, size L, giá, qty 1"],
    ["TC_ORD_002","US-20","Cart","Add","Add với qty = 0","Negative","P1","Design hoàn tất","qty: 0","1. Nhập Qty: 0\n2. Click 'Add to Cart'","Validation: qty phải >= 1"],
    ["TC_ORD_003","US-20","Cart","Add","Add áo trơn vào giỏ","Positive","P0","Trang SP trơn","size:M, color:White","1. Chọn Size M, Color White\n2. Click 'Add to Cart'","Giỏ hàng +1 áo trơn White M"],
    ["TC_ORD_004","US-20","Cart","Add","Add nhiều SP khác nhau vào giỏ","Positive","P1","","","1. Add T-shirt Design L\n2. Add Polo trơn M","Giỏ hàng hiện 2 items đúng"],
    # --- Shipping Address (US-21) ---
    ["TC_ORD_005","US-21","Checkout","Address","Nhập địa chỉ đầy đủ","Positive","P0","Trang Checkout","Name: Văn A | Phone: 0901234567 | City: HCM","1. Nhập Name, Phone, Address\n2. Chọn City/Dist/Ward","Tính phí ship. Hiển thị tổng tiền"],
    ["TC_ORD_006","US-21","Checkout","Address","Bỏ trống Phone","Negative","P0","Trang Checkout","","1. Bỏ trống Phone\n2. Click tiếp","Hiển thị lỗi: 'Vui lòng nhập số điện thoại'"],
    ["TC_ORD_007","US-21","Checkout","Address","Phone format sai","Negative","P1","Trang Checkout","phone: abc","1. Nhập Phone: abc","Validation error: format SĐT không hợp lệ"],
    # --- Delivery (US-22) ---
    ["TC_ORD_008","US-22","Checkout","Delivery","Chọn Standard delivery","Positive","P0","Trang Checkout, có address","","1. Chọn 'Standard (3-5 ngày)'","Tổng tiền = SP + phí Standard. Update realtime"],
    ["TC_ORD_009","US-22","Checkout","Delivery","Đổi sang Fast Delivery","Positive","P0","Đang chọn Standard","","1. Đổi sang 'Fast (1-2 ngày)'","Phí ship tăng. Tổng cập nhật realtime"],
    # --- Discount (US-23) ---
    ["TC_ORD_010","US-23","Checkout","Discount","Áp mã giảm giá hợp lệ","Positive","P1","Trang Checkout","code: PODNEW10","1. Nhập code: PODNEW10\n2. Click 'Áp dụng'","Tiền giảm. Badge hiển thị mã đã áp"],
    ["TC_ORD_011","US-23","Checkout","Discount","Áp mã hết hạn","Negative","P1","","code: EXPIRED01","1. Nhập code hết hạn","Hiển thị: 'Mã giảm giá đã hết hạn'"],
    ["TC_ORD_012","US-23","Checkout","Discount","Áp mã không tồn tại","Negative","P1","","code: FAKECODEXYZ","1. Nhập mã không tồn tại","Hiển thị: 'Mã giảm giá không hợp lệ'"],
    ["TC_ORD_013","US-23","Checkout","Discount","Áp 2 mã cùng lúc","Edge Case","P2","","","1. Áp mã 1 thành công\n2. Áp mã 2","Tùy BR: thay thế mã cũ hoặc báo chỉ dùng 1 mã"],
    # --- Cost Breakdown (US-23b) ---
    ["TC_ORD_014","US-23b","Checkout","Transparency","Xem Cost Breakdown chart","Positive","P0","Trang Checkout","","1. Click 'Tại sao giá này?'","Hiện chart: Phôi áo + Chi phí in + Phí ship. Tổng khớp"],
    # --- Online/Other Payment (US-24) ---
    ["TC_ORD_015","US-24","Payment","Online","Thanh toán Chuyển khoản ngân hàng thành công","Positive","P0","Trang Checkout","","1. Chọn 'Chuyển khoản ngân hàng'\n2. Hoàn tất thanh toán","Status đơn = 'Chờ xác nhận'. Email Receipt gửi"],
    ["TC_ORD_016","US-24","Payment","Online","Thanh toán bằng Ví POD Credits","Positive","P0","Có đủ Credits","","1. Chọn 'Ví POD (25 credits)'\n2. Thanh toán","Trừ credit. Status đơn = 'Chờ xác nhận'"],
    ["TC_ORD_017","US-24","Payment","Online","Ví POD không đủ Credits","Negative","P1","Thiếu Credits","","1. Chọn 'Ví POD'","Hiển thị báo lỗi không đủ số dư. Chọn phương thức khác"],
    # --- Check UI/UX (from Stitch) ---
    ["TC_ORD_UI_018","US-20","Checkout","UI/UX","Checkout page: Layout và text hiển thị đúng","UI/UX","P1","Mở /checkout","","1. Quan sát block Giỏ hàng và Phương thức","Tiêu đề hiện 'Giỏ hàng (2 sản phẩm)'. Shipping options: 'Standard (3-5 ngày)', 'Fast (1-2 ngày)'. Payment options: 'Ví POD', 'Chuyển khoản', 'COD'"],
]

EPIC6_ORDERS = [
    # --- Order History (US-26) ---
    ["TC_ORD_019","US-26","Order","List","Xem danh sách đơn hàng","Positive","P0","Đã có 3+ đơn","","1. Vào 'My Orders'","Hiển thị list: Order ID, Date, Total, Status. Mới nhất trước"],
    ["TC_ORD_020","US-26","Order","List","Danh sách đơn rỗng","Edge Case","P1","TK mới, chưa có đơn","","1. Vào 'My Orders'","Empty state: 'Bạn chưa có đơn hàng nào'"],
    # --- Track Status (US-27) ---
    ["TC_ORD_021","US-27","Order","Detail","Track trạng thái đơn - timeline","Positive","P1","Đơn đang xử lý","","1. Click vào 1 đơn hàng","Show timeline giống Stitch: Chờ xác nhận -> Đang xử lý -> Đang giao -> Đã nhận hàng"],
    ["TC_ORD_022","US-27","Order","Detail","Xem chi tiết đơn: SP, giá, địa chỉ","Positive","P1","Có đơn hoàn tất","","1. Click đơn hàng","Hiện chi tiết: thumbnail, product type, color, size, price, địa chỉ ship"],
    # --- Cancel Order (US-28) ---
    ["TC_ORD_023","US-28","Order","Action","Hủy đơn status Chờ xác nhận","Positive","P1","Đơn Chờ xác nhận","","1. Click 'Hủy đơn'\n2. Confirm","Status → Cancelled. Email thông báo hủy"],
    ["TC_ORD_024","US-28","Order","Action","Hủy đơn status Đang xử lý → không cho phép","Negative","P1","Đơn đang xử lý","","1. Xem trang đơn hàng","Button 'Hủy' disabled hoặc ẩn. Không hủy được"],
    # --- Re-order (US-29) ---
    ["TC_ORD_025","US-29","Order","Re-order","Re-order design cũ","Positive","P1","Có đơn Đã nhận hàng","","1. Click 'Đặt lại'\n2. Chọn Size/Qty","Tạo đơn mới với cùng design. Vào Cart"],
    ["TC_ORD_026","US-29","Order","Re-order","Re-order sản phẩm đã ngưng bán","Edge Case","P2","SP đã Inactive","","1. Click 'Đặt lại'","Hiển thị: 'Sản phẩm này không còn bán'. Không cho re-order"],
    # --- Order UI/UX Test Cases (from Stitch Design) ---
    ["TC_ORD_UI_027","US-27","Order","UI/UX","Order details: Pipeline visual hiển thị mượt","UI/UX","P2","Xem đơn hàng","","1. Quan sát thanh trạng thái","UI hiển thị các step Chờ xác nhận -> Đang xử lý -> Đang giao -> Đã nhận hàng nối với nhau. Step hiện tại highlighted màu nổi bật"],
]

ALL_PART2 = EPIC4_EDITOR + EPIC5_CHECKOUT + EPIC6_ORDERS
print(f"Part 2: {len(ALL_PART2)} TCs (Editor:{len(EPIC4_EDITOR)}, Checkout:{len(EPIC5_CHECKOUT)}, Orders:{len(EPIC6_ORDERS)})")
