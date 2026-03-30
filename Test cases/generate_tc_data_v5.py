import csv
import io
import os

test_cases = [
    # Epic 1: Auth & Account
    ["TC_AUTH_001", "US-01", "Authentication", "Register", "Verify successful registration with valid email", "Positive", "P0", "No existing account", "Email: test@gmail.com | Pass: Valid123!", "1. Truy cập vào trang \n2. Nhấn nút Đăng ký\n3. Nhập email và password hợp lệ\n4. Nhấn Xong", "Hệ thống tạo tài khoản mới và đăng nhập tự động", "UC01", "Prod", "Untested", "", "", ""],
    ["TC_AUTH_002", "US-01", "Authentication", "Register", "Verify registration with invalid password formats", "Negative", "P1", "None", "Pass: 123 | Pass: abc", "1. Truy cập vào trang \n2. Nhấn đăng ký\n3. Nhập password không đủ ký tự\n4. Nhấn Submit", "Hệ thống báo lỗi 'Mật khẩu phải từ 8 ký tự'", "UC01", "Prod", "Untested", "Mật khẩu phải từ 8 ký tự", "", ""],
    ["TC_AUTH_003", "US-03b", "Authentication", "Guest Access", "Verify Guest Try First, Login Later flow", "Positive", "P0", "Not logged in", "", "1. Truy cập vào trang \n2. Chọn một template bất kỳ\n3. Mở Editor", "Editor được mở ra bình thường không yêu cầu login chặn ngang", "UC01", "Prod", "Untested", "", "", ""],
    ["TC_AUTH_004", "US-03c", "Authentication", "Guest Access", "Verify login prompt on Add to Cart for guest", "Positive", "P0", "Guest has a design", "", "1. Truy cập vào trang \n2. Mở Editor và thiết kế\n3. Nhấn Add to Cart", "Popup Login hiện lên yêu cầu đăng nhập trước khi mua", "UC01", "Prod", "Untested", "", "", ""],

    # Epic 2: Template
    ["TC_TPL_001", "US-06", "Template", "Gallery", "Verify browsing template categories", "Positive", "P0", "None", "Category: Music", "1. Truy cập vào trang \n2. Mở Template Gallery\n3. Chọn category Music", "Hiển thị danh sách các template thuộc Music", "UC03", "Prod", "Untested", "", "", ""],
    
    # Epic 4: Editor (Canvas) - CORE UI/UX
    ["TC_EDT_001", "US-13", "Editor", "Upload", "Verify uploading valid artwork", "Positive", "P0", "In Editor", "File: image.png (10MB)", "1. Truy cập vào trang \n2. Mở màn hình Editor\n3. Nhấn nút Upload\n4. Chọn ảnh hợp lệ", "Ảnh được tải lên và hiển thị trên Canvas", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_EDT_002", "US-13", "Editor", "Upload", "Verify boundary upload file > 25MB", "Boundary", "P1", "In Editor", "File: huge.jpg (26MB)", "1. Truy cập vào trang \n2. Mở Editor\n3. Upload file 26MB", "Báo lỗi vượt quá giới hạn 25MB", "UC03", "Prod", "Untested", "File size exceeds 25MB", "", ""],
    ["TC_UIUX_001", "US-15", "Editor", "Canvas Viewpoint", "Verify Zoom In/Out via Ctrl+Scroll", "UI/UX", "P1", "Has artwork on canvas", "Zoom 200%", "1. Truy cập vào trang \n2. Mở Editor\n3. Nhấn giữ Ctrl và lăn chuột lên/xuống", "Canvas phóng to/thu nhỏ mức zoom tương ứng mượt mà", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_UIUX_002", "US-15", "Editor", "Canvas Viewpoint", "Verify Pan Canvas via Space+Drag", "UI/UX", "P1", "Zoomed in at 200%", "Pan action", "1. Truy cập vào trang \n2. Mở Editor zoom 200%\n3. Nhấn giữ phím Space và click kéo chuột", "Con trỏ đổi thành bàn tay, kéo canvas di chuyển góc nhìn", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_UIUX_003", "US-15", "Editor", "Canvas Viewpoint", "Verify Smart Guides magnetic alignment", "UI/UX", "P1", "Has 2 artwork layers", "Drag relative", "1. Truy cập vào trang \n2. Mở Editor\n3. Kéo layer A di chuyển lại gần layer B / tâm canvas", "Chớp xuất hiện đường viền (guide) đỏ/xanh báo đã căn giữa/trái/phải", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_UIUX_004", "US-15", "Editor", "Canvas Viewpoint", "Verify Keyboard Shortcuts mapping", "UI/UX", "P1", "Text layer selected", "Ctrl+C, Ctrl+V, Delete", "1. Truy cập vào trang \n2. Mở Editor\n3. Chọn layer Text\n4. Nhấn Ctrl+C rồi Ctrl+V rồi Delete", "Copy ra layer mới và sau đó xóa layer thành công", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_UIUX_005", "US-16", "Editor", "Canvas Viewpoint", "Verify Layer Opacity slider", "UI/UX", "P1", "Artwork selected", "Opacity 50%", "1. Truy cập vào trang \n2. Mở Editor\n3. Chọn layer\n4. Kéo thanh trượt thay đổi Opacity xuống 50%", "Layer trở nên trong suốt 50%, nhìn xuyên thấu xuống background", "UC03", "Prod", "Untested", "", "", ""],
    ["TC_UIUX_006", "US-19", "Editor", "3D Mockup Viewpoint", "Verify 3D view toggle and performance", "Positive", "P0", "Design applied", "Toggle 3D", "1. Truy cập vào trang \n2. Nhấn nút 3D View", "Load 3D model xoay được, texture áo phủ đúng vùng thiết kế", "UC03", "Prod", "Untested", "", "", ""],

    # Epic 8: AI Generation & Epic 9: Credits
    ["TC_AI_001", "US-37", "AI Generate", "Generation", "Verify AI generates exactly 4 variations", "Positive", "P0", "User has >= 1 credit", "Prompt: 'Cyberpunk cat'", "1. Truy cập vào trang \n2. Chọn tool AI\n3. Nhập từ khóa Cyberpunk cat\n4. Nhấn Generate", "Hệ thống trừ 1 credit, loading, trả về đúng 4 hình ảnh preview", "UC02", "Prod", "Untested", "", "", ""],
    ["TC_AI_002", "US-42", "AI Generate", "Quota Boundary", "Verify Guest 2 generations max per day", "Boundary", "P0", "Guest IP", "Gen 3rd time", "1. Truy cập vào trang \n2. Dùng AI generate 2 lần\n3. Thử generate lần thứ 3", "Lần 3 báo lỗi 'Out of credits' hoặc 'Đăng nhập để nhận thêm'", "UC02", "Prod", "Untested", "Out of credits", "", ""],
    ["TC_AI_003", "US-42b", "AI Generate", "Refill Logic", "Verify daily reset logic of Free User credits", "Positive", "P0", "Free User with 0 credits", "Wait 24h", "1. Truy cập vào trang \n2. Cài đặt thời gian qua 24h (admin)\n3. Check số dư", "Số dư credit tự động reset về 10", "UC02", "Prod", "Untested", "", "", ""],

    # Epic 5: Checkout
    ["TC_CHK_001", "US-24", "Checkout", "Payment", "Verify VNPay logic positive", "Positive", "P0", "Item in cart", "VNPay URL", "1. Truy cập vào trang \n2. Vào giỏ hàng\n3. Nhấn Checkout, chọn VNPay\n4. Hoàn tất thanh toán sandbox", "Chuyển đơn hàng sang trạng thái Paid, hiện Success page", "UC04", "Prod", "Untested", "", "", ""],
    ["TC_CHK_002", "US-24", "Checkout", "Payment", "Verify canceling payment redirects correctly", "Negative", "P1", "At VNPay Screen", "Cancel button", "1. Truy cập vào trang \n2. Init VNPay thanh toán\n3. Nhấn Hủy giao dịch trên VNPay", "Quay lại trang Checkout kèm thông báo 'Giao dịch bị hủy'", "UC04", "Prod", "Untested", "Giao dịch bị hủy", "", ""],
    
    # Epic 7: Admin
    ["TC_ADM_001", "US-30", "Admin", "Dashboard", "Verify admin metrics calculations", "Positive", "P1", "Admin login", "Date: Today", "1. Truy cập vào trang \n2. Vào Admin Dashboard", "Biểu đồ và tổng doanh thu hiển thị đúng số liệu thực tế", "UC05", "Prod", "Untested", "", "", ""]
]

dir_path = "e:/BII/QA-NEW/Tool/antigravity-tryonic-main/Test cases"
os.makedirs(dir_path, exist_ok=True)
csv_file = os.path.join(dir_path, "TC_POD-TShirt-Platform_v5_2026-03-16_AI_Generated.csv")

with io.open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    # Headers MUST match the QA analyst rules
    writer.writerow(["TC_ID", "US_Mapping", "Feature", "Module", "Title", "Type", "Priority", "Precondition", "Test_Data", "Steps", "Expected_Result", "Related_UC", "Environment", "Status", "Error_Message", "Screenshot_Path", "Executed_At"])
    writer.writerows(test_cases)

print(f"✅ Generated {len(test_cases)} high-quality core Test Cases to {csv_file}")
