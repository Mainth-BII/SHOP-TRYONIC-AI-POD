# Part 3: Epic 7 (Admin) + Epic 8 (AI) + Epic 9 (Credits)

EPIC7_ADMIN = [
    ["TC_ADM_001","US-30","CMS","Dash","Dashboard hiển thị tổng quan","Positive","P0","Admin login","","1. Vào Dashboard","Show: Tổng đơn, Doanh thu, KH mới, biểu đồ"],
    ["TC_ADM_002","US-30","CMS","Dash","Dashboard data realtime khi có đơn mới","Positive","P1","Admin đang xem Dashboard","","1. User tạo đơn mới\n2. Refresh Dashboard","Data cập nhật: tổng đơn +1"],
    ["TC_ADM_003","US-31","CMS","Order","Duyệt đơn: Pending → Confirmed","Positive","P0","CMS Order list, đơn Pending","","1. Click đơn Pending\n2. Click 'Xác nhận'","Status → Confirmed. User nhận notification"],
    ["TC_ADM_004","US-31","CMS","Order","Cập nhật status: Confirmed → Processing → Shipping","Positive","P0","Đơn Confirmed","","1. Update Processing\n2. Update Shipping","Mỗi lần update → user nhận email"],
    ["TC_ADM_005","US-31","CMS","Order","Export đơn hàng CSV","Positive","P1","CMS Order list","","1. Click 'Export'\n2. Kiểm tra file","File CSV có đủ cột: Order ID, Date, User, Total, Status"],
    ["TC_ADM_006","US-32","CMS","Catalog","Toggle product Inactive","Positive","P0","CMS Product list, SP đang Active","","1. Toggle SP sang Inactive","SP ẩn khỏi web user. Admin vẫn thấy"],
    ["TC_ADM_007","US-32","CMS","Catalog","Toggle product Active lại","Positive","P0","SP đang Inactive","","1. Toggle Active","SP hiện lại trên web user"],
    ["TC_ADM_008","US-32","CMS","Catalog","Inactive SP đang có trong giỏ hàng user","Edge Case","P1","User đã add SP vào giỏ","","1. Admin Inactive SP đó","Giỏ hàng user hiện warning/remove SP"],
    ["TC_ADM_009","US-33","CMS","Gallery","Upload template mới","Positive","P0","CMS Template list","file: template.png","1. Click 'Upload Template'\n2. Upload file + đặt tên/category","Template xuất hiện trên web gallery"],
    ["TC_ADM_010","US-33","CMS","Gallery","Hide template","Positive","P0","Template đang hiện","","1. Toggle Hide","Template ẩn khỏi gallery. User không thấy"],
    ["TC_ADM_011","US-33b","CMS","Category","Gán category cho artwork","Positive","P1","CMS Gallery","","1. Chọn artwork\n2. Gán category: Music","Artwork hiện trong filter Music trên web"],
    ["TC_ADM_012","US-34","CMS","Promo","Tạo discount code mới","Positive","P1","CMS Discount list","code: SUMMER25, discount: 25%","1. Nhập code, %, ngày hết hạn\n2. Save","Mã tạo thành công. User dùng được"],
    ["TC_ADM_013","US-34","CMS","Promo","Tạo code trùng tên","Negative","P1","Code SUMMER25 đã tồn tại","","1. Tạo code trùng SUMMER25","Lỗi: 'Mã đã tồn tại'"],
    ["TC_ADM_014","US-35","CMS","User","Lock tài khoản user","Positive","P0","CMS User detail","","1. Click Lock\n2. Nhập lý do: Fraud\n3. Confirm","User bị lock. Không thể login. Email thông báo gửi"],
    ["TC_ADM_015","US-35","CMS","User","Unlock tài khoản user","Positive","P0","User bị lock","","1. Click Unlock\n2. Confirm","User mở khóa. Login bình thường. Email gửi"],
    ["TC_ADM_016","US-35","CMS","User","Soft Delete user","Positive","P1","CMS User detail","","1. Click Delete\n2. Confirm warning popup","User soft-deleted. Không hiện trong list Active"],
    ["TC_ADM_017","US-35","CMS","User","Search user theo email","Positive","P0","CMS User list","email: user@test.com","1. Nhập email vào search\n2. Enter","Hiển thị đúng user matching"],
    ["TC_ADM_018","US-35","CMS","User","Filter users: Locked only","Positive","P1","CMS User list","","1. Filter: Locked","Chỉ hiện users bị lock"],
    ["TC_ADM_019","US-36","CMS","Report","Export Users CSV","Positive","P1","CMS User list","","1. Click Export Users","Download CSV: name, email, phone, status, signup date, total orders"],
    ["TC_ADM_020","US-36","CMS","Report","Export Users CSV encoding tiếng Việt","Positive","P1","Có user tên tiếng Việt","","1. Export CSV\n2. Mở Excel","Tên tiếng Việt hiển thị đúng (UTF-8 BOM)"],
    ["TC_ADM_021","US-36b","CMS","AI","Cấu hình AI quota: 10 → 20","Positive","P0","CMS Settings","new limit: 20","1. Sửa daily limit: 20\n2. Save","Toàn bộ user có 20 lượt/ngày kể từ lúc save"],
    ["TC_ADM_022","US-36b","CMS","AI","Cấu hình AI quota = 0 (disable)","Boundary","P1","CMS Settings","new limit: 0","1. Sửa daily limit: 0\n2. Save","Tất cả user không thể generate AI. Hiện 'AI tạm ngưng'"],
    ["TC_ADM_023","US-36b","CMS","AI","Cấu hình AI quota nhập chữ","Negative","P1","CMS Settings","value: abc","1. Nhập 'abc' vào field limit","Validation: chỉ nhận số nguyên dương"],
    # --- CMS UI/UX Test Cases (from Stitch Design) ---
    ["TC_ADM_UI_024","US-30","CMS","UI/UX","CMS Dashboard: Layout thẻ thống kê","UI/UX","P1","Mở Dashboard","","1. Quan sát row đầu tiên","Hiển thị 4 thẻ: Tổng doanh thu, Đơn hàng mới, Người dùng mới, Lượt xem trang"],
    ["TC_ADM_UI_025","US-31","CMS","UI/UX","CMS Orders: Trạng thái lọc hiển thị đúng","UI/UX","P1","Mở Quản lý đơn hàng","","1. Nhấn vào bộ lọc trạng thái","Hiển thị list: Chờ xác nhận, Đang chuẩn bị, Đang giao, Đã giao, Đã hủy"],
]

EPIC8_AI = [
    ["TC_AI_001","US-37","AI Gen","Engine","Nhập prompt → 4 preview ảnh","Positive","P0","Đã login, credits > 0","prompt: Chú mèo phi hành gia | style: Digital Art","1. Nhập prompt tiếng Việt\n2. Chọn style: Digital Art\n3. Click 'Generate'","Loading state. Trả về 4 ảnh preview low-res trong 30-60s. Trừ 1 credit"],
    ["TC_AI_002","US-37","AI Gen","Engine","Prompt rỗng","Negative","P0","","","1. Không nhập prompt\n2. Click 'Generate'","Validation: 'Vui lòng nhập mô tả'"],
    ["TC_AI_003","US-37","AI Gen","Engine","Prompt chứa nội dung nhạy cảm","Negative","P0","","prompt: violent content","1. Nhập prompt vi phạm policy\n2. Click 'Generate'","Từ chối: 'Nội dung không phù hợp'. Không trừ credit"],
    ["TC_AI_004","US-37","AI Gen","Engine","Prompt rất dài (1000+ ký tự)","Boundary","P1","","prompt: 1000 chars","1. Nhập prompt 1000+ ký tự\n2. Click 'Generate'","Truncate hoặc warning max length"],
    ["TC_AI_005","US-37","AI Gen","Engine","Generate khi đang generate (double click)","Edge Case","P1","Đang render","","1. Click 'Generate' 2 lần nhanh","Chỉ 1 request được xử lý. Button disabled khi đang loading"],
    ["TC_AI_006","US-38","AI Gen","Upscale","Chọn 1 ảnh → upscale ≥2048px","Positive","P0","Có 4 preview","","1. Click 'Dùng ngay' trên ảnh 1","Upscale 2k/4k. Lưu My Gallery. Chuyển sang Editor"],
    ["TC_AI_007","US-38","AI Gen","Upscale","Upscale khi hết credits","Negative","P0","Credits = 0","","1. Click 'Dùng ngay'","Hiển thị: 'Hết credits'. Gợi ý chờ reset hoặc mua thêm"],
    ["TC_AI_008","US-39","AI Gen","UX","Aha Moment messages khi render","Positive","P1","Đang render","","1. Quan sát loading state","Messages xoay vui: 'Đang pha màu...', 'AI đang vẽ...'"],
    ["TC_AI_009","—","AI Gen","Quota","Guest: 2 lượt/ngày","Negative","P0","Guest đã dùng 2 lượt","","1. Click 'Generate' lần thứ 3","Hiển thị: 'Out of Credits'. Gợi ý đăng ký tài khoản"],
    ["TC_AI_010","—","AI Gen","Quota","Free user: 10 lượt/ngày","Negative","P0","User đã dùng 10 lượt","","1. Click 'Generate' lần thứ 11","Hiển thị: 'Hết lượt tạo hôm nay'. Gợi ý chờ reset"],
    ["TC_AI_011","—","AI Gen","Quota","Quota reset lúc 00:00","Boundary","P1","User hết quota hôm nay","","1. Chờ qua 00:00\n2. Thử Generate","Quota reset. Generate thành công"],
    ["TC_AI_012","—","AI Gen","Network","Generate khi mất mạng giữa chừng","Negative","P1","Đang render","","1. Ngắt mạng giữa quá trình render","Timeout message. Không trừ credit nếu chưa có kết quả"],
    # --- AI UI/UX Test Cases (from Stitch Design) ---
    ["TC_AI_UI_013","US-37","AI Gen","UI/UX","AI page: UI form cấu hình layout","UI/UX","P1","Mở AI Generator","","1. Quan sát layout input form","Input placeholder: 'Mô tả ý tưởng của bạn'. Styles: Digital Art, Realistic, Watercolor, Anime, Oil Painting. Thanh trượt 1-4 hình"],
    ["TC_AI_UI_014","US-37","AI Gen","UI/UX","AI page: Hiển thị chi phí generate","UI/UX","P1","Mở AI Generator","","1. Thay đổi số lượng ảnh","Hiển thị text: 'Tiêu tốn: X credits' (Vd: 'Tiêu tốn: 5 credits' khi generate 4 hình)"],
]

EPIC9_CREDITS = [
    ["TC_CRD_001","US-40","Credits","Profile","Xem số dư credits trong header/profile","Positive","P0","Đã login, balance=10","","1. Nhìn header","Hiển thị: '10 credits'"],
    ["TC_CRD_002","US-40","Credits","Profile","Balance update sau khi dùng","Positive","P0","Balance=10","","1. Generate 1 ảnh AI\n2. Nhìn header","Balance: 10 → 9. Update realtime"],
    ["TC_CRD_003","US-42","Credits","Spend","Dùng credits cho AI generate","Positive","P0","Balance > 0","","1. Click Generate\n2. Kiểm tra balance","Trừ credit đúng số lượng. Không yêu cầu thanh toán"],
    ["TC_CRD_004","US-42","Credits","Spend","Dùng credits cho upscale","Positive","P0","Balance >= 3","","1. Click 'Dùng ngay' (upscale)\n2. Kiểm tra balance","Trừ credits cho upscale"],
    ["TC_CRD_005","US-42","Credits","Spend","Dùng credits khi balance = 0","Negative","P0","Balance = 0","","1. Thử Generate","Hiển thị: 'Hết credits'. Không cho thực hiện"],
    ["TC_CRD_006","US-42b","Credits","Daily Reset","Credits refill mỗi 24h","Positive","P0","Balance = 0, hết ngày","","1. Chờ qua 00:00\n2. Kiểm tra balance","Balance tự refill về mức mặc định (vd: 10 credits)"],
    ["TC_CRD_007","US-42b","Credits","Daily Reset","Partial usage → reset full","Positive","P1","Balance = 3 (đã dùng 7/10)","","1. Chờ qua 00:00\n2. Kiểm tra balance","Balance refill full = 10 (không cộng dồn 3+10)"],
    ["TC_CRD_008","US-42b","Credits","Daily Reset","Reset đúng theo timezone","Boundary","P1","","","1. Kiểm tra thời điểm reset","Reset lúc 00:00 theo timezone server/user"],
    # --- Credits UI/UX Test Cases (from Stitch Design) ---
    ["TC_CRD_UI_009","US-40","Credits","UI/UX","Wallet page: Header card số dư","UI/UX","P1","Mở trang Ví Credits","","1. Quan sát card số dư màu tím","Hiển thị: 'Số dư hiện tại: [X] Credits'. Nút: 'Nạp thêm Credits', 'Rút Credits'"],
    ["TC_CRD_UI_010","US-41","Credits","UI/UX","Wallet page: Lịch sử và Tabs","UI/UX","P2","Mở trang Ví Credits","","1. Quan sát bảng lịch sử giao dịch","Có Tabs: 'Tất cả', 'Nhận', 'Sử dụng'. Bảng có: Ngày giao dịch, Loại, Nội dung, Số tiền (+/-), Số dư sau giao dịch. (vd: 'Chào mừng (+5)', 'Mua hàng (+10)')"],
    ["TC_CRD_UI_011","US-41","Credits","UI/UX","Wallet page: Empty state","UI/UX","P2","Ví mới chưa có GD","","1. Mở trang Ví Credits","Hiển thị empty state: 'Chưa có giao dịch credits nào'"],
]

ALL_PART3 = EPIC7_ADMIN + EPIC8_AI + EPIC9_CREDITS
print(f"Part 3: {len(ALL_PART3)} TCs (Admin:{len(EPIC7_ADMIN)}, AI:{len(EPIC8_AI)}, Credits:{len(EPIC9_CREDITS)})")
