import csv
import io
import os

test_cases = [
    ["TC_AUTH_001","US-01","Registration","Signup","Đăng ký bằng Email/Password hợp lệ","Positive","P0","Trang Signup mở","","1. Nhập Name, Email, Password (Test@123)\n2. Click \"Đăng ký\"","Báo thành công, gửi mail verify","S01","Web","Not Run","","",""],
    ["TC_AUTH_002","US-01","Registration","Signup","Đăng ký với pass yếu (thiếu số)","Negative","P0","Trang Signup mở","","1. Nhập Password: \"Password\"","Báo lỗi: Min 8 chars, 1 uppercase, 1 number","S01","Web","Not Run","","",""],
    ["TC_AUTH_003","US-02","Login","OAuth","Đăng nhập bằng Google","Positive","P0","Đã có tài khoản Google","","1. Click \"Login Google\"","Đăng nhập thành công, auto tạo profile nếu mới","S01","Web","Not Run","","",""],
    ["TC_AUTH_004","US-02b","Login","OAuth","Đăng nhập bằng Facebook","Positive","P1","Đã có tài khoản Facebook","","1. Click \"Login Facebook\"","Đăng nhập thành công","S01","Web","Not Run","","",""],
    ["TC_AUTH_005","US-03","Login","Login","Đăng nhập bằng Email đã verify","Positive","P0","TK đã verify","","1. Nhập Email/Pass\n2. Click Login","Vào Dashboard, show User Name","S01","Web","Not Run","","",""],
    ["TC_AUTH_006","US-03b","Guest Mode","Browser","Thiết kế áo không cần đăng nhập (Try First)","Positive","P0","Chưa đăng nhập","","1. Vào Editor\n2. Add artwork/text","Cho phép thao tác bình thường, data lưu localStorage","S01","Web","Not Run","","",""],
    ["TC_AUTH_007","US-03c","Guest Mode","Migration","Yêu cầu đăng nhập khi nhấn Đặt hàng (Guest)","Positive","P0","Guest có hàng trong giỏ","","1. Click \"Thanh toán\"","Hiện popup Login/Register, giữ nguyên design + cart","S01","Web","Not Run","","",""],
    ["TC_AUTH_008","US-04","Account","Security","Reset password qua Email","Positive","P0","Quên mật khẩu","","1. Click \"Quên mật khẩu\"\n2. Nhập Email","Nhận link reset (hết hạn 1h), đổi pass thành công","S01","Web","Not Run","","",""],
    ["TC_AUTH_009","US-05","Profile","Account","Cập nhật Profile (Phone, Avatar, Address)","Positive","P1","Đã đăng nhập","","1. Sửa Profile\n2. Click Save","Hệ thống lưu và hiển thị data mới","S01","Web","Not Run","","",""],
    ["TC_TEM_001","US-06","Gallery","Browse","Duyệt Template Gallery","Positive","P0","Vào trang Template","","1. Scroll gallery","Load templates, cho phép chọn","F03","Web","Not Run","","",""],
    ["TC_TEM_002","US-07","Gallery","Search","Tìm kiếm Template theo keyword","Positive","P1","Trong danh sách template","Keyword: Vintage","1. Search \"Vintage\"","Show các bản mẫu khớp tên/tag","F03","Web","Not Run","","",""],
    ["TC_TEM_003","US-08","Gallery","Filter","Lọc Template theo Category","Positive","P1","Trong danh sách template","Category: Sport","1. Chọn Category: \"Sport\"","Show templates thể thao","F03","Web","Not Run","","",""],
    ["TC_TEM_004","US-09","Gallery","Editor","Mở Template vào Editor","Positive","P0","Thấy template ưng ý","","1. Click template","Template load vào Editor, cho phép thay text/layer","F03","Web","Not Run","","",""],
    ["TC_PRO_001","US-10","Product","Select","Chọn loại áo (T-shirt, Polo)","Positive","P0","Editor mở","","1. Chọn menu sản phẩm","Mockup đổi loại áo tương ứng","F05","Web","Not Run","","",""],
    ["TC_PRO_002","US-11","Product","Color","Chọn màu sắc áo realtime","Positive","P0","Editor mở","Color: Navy","1. Click swatch màu","Áo mockup đổi màu ngay lập tức","F05","Web","Not Run","","",""],
    ["TC_PRO_003","US-12","Product","Size","Xem Size Chart chuẩn","Positive","P0","Popup Size chart mở","","1. So bảng size (S-2XL)","Thông số Vai, Ngực... chính xác (cm)","F05","Web","Not Run","","",""],
    ["TC_PRO_004","US-12b","Smart Fit","AI Suggest","Gợi ý Size bằng AI (BMI)","Positive","P0","Popup Fit-Size","H:175, W:70, Gender:Nam","1. Nhập H, W, Gender","Show: \"Size L (Khớp 90%)\"","F05","Web","Not Run","","",""],
    ["TC_PRO_005","US-12c","Product","Skip Edit","Mua áo trơn (không thiết kế)","Positive","P0","Trang chi tiết SP","","1. Click \"Mua ngay\"","Add trơn vào giỏ, không mở Editor","F05","Web","Not Run","","",""],
    ["TC_DES_001","US-13","Editor","Upload","Upload ảnh cá nhân (PNG/JPG < 25MB)","Positive","P0","Editor mở","File: sample.png","1. Click Upload\n2. Chọn file","Ảnh hiện trên Canvas","F07","Web","Not Run","","",""],
    ["TC_DES_002","US-14","Editor","Text","Thêm và định dạng Text layers (font, color)","Positive","P0","Editor mở","","1. Click \"Add Text\"\n2. Đổi Font/Màu","Text hiện đúng style","F06","Web","Not Run","","",""],
    ["TC_DES_003","US-15","Editor","Canvas","Thao tác Layer (Drag, Resize, Rotate)","Positive","P0","Đã có layer","","1. Thao tác chuột","Layer đổi scale/rotate mượt mà","F06","Web","Not Run","","",""],
    ["TC_DES_004","US-16","Editor","Layers","Quản lý Layer order (Bring to front/back)","Positive","P1","Có >1 layer","","1. Click \"Bring to front\"","Layer đổi thứ tự hiển thị","F06","Web","Not Run","","",""],
    ["TC_DES_005","US-17","Editor","History","Undo/Redo thao tác thiết kế","Positive","P1","Có >2 thao tác","","1. Click Undo/Redo","Trạng thái canvas hồi phục chính xác","F06","Web","Not Run","","",""],
    ["TC_DES_006","US-18","Editor","Save","Save Design vào My Designs","Positive","P0","Design dở dang","","1. Click \"Save\"","Lưu vào My Designs, có thể load lại sau","F06","Web","Not Run","","",""],
    ["TC_DES_007","US-19","Editor","Preview","Xem 3D Mockup xoay được","Positive","P0","Có artwork trên canvas","","1. Click \"3D View\"","Hiển thị model 3D xoay được","F07","Web","Not Run","","",""],
    ["TC_DES_008","—","Editor","Quality","Cảnh báo ảnh low quality < 150 DPI","Negative","P0","Upload ảnh < 150 DPI","File: lowres.jpg (72 DPI)","1. Upload ảnh low-res","Warning \"Low Quality - May be blurry when printed\"","F09","Web","Not Run","","",""],
    ["TC_DES_009","—","Editor","Safe Zone","Cảnh báo artwork ngoài Safe Area","Positive","P0","Artwork trên canvas","","1. Kéo artwork ra ngoài vùng in","Hiện warning artwork ngoài safe zone","F07","Web","Not Run","","",""],
    ["TC_ORD_001","US-20","Cart","Add","Add to Cart (Size/Qty)","Positive","P0","Có design hoàn tất","Size: L, Qty: 1","1. Chọn Size, Qty\n2. Click \"Add to Cart\"","SP thêm vào giỏ: thumbnail, type, color, size, price","F10","Web","Not Run","","",""],
    ["TC_ORD_002","US-21","Checkout","Address","Nhập địa chỉ ship (City/Dist/Ward)","Positive","P0","Trang Checkout","Name: Van A, Phone: 090...","1. Nhập bưu cụ hợp lệ","Hệ thống tính phí ship","F10","Web","Not Run","","",""],
    ["TC_ORD_003","US-22","Checkout","Delivery","Chọn gói Delivery (Express/Standard)","Positive","P0","Trang Checkout","","1. Toggle gói vận chuyển","Tổng tiền cộng ship update realtime","F10","Web","Not Run","","",""],
    ["TC_ORD_004","US-23","Checkout","Discount","Áp mã Discount hợp lệ","Positive","P1","Trang Checkout","Code: PODNEW10","1. Nhập valid code","Tiền được trừ","F10","Web","Not Run","","",""],
    ["TC_ORD_005","US-23b","Checkout","Transparency","Xem biểu đồ Cost Breakdown","Positive","P0","Trang Checkout","","1. Click \"Tại sao giá này?\"","Hiện chart (Phôi + In + Ship)","F10","Web","Not Run","","",""],
    ["TC_ORD_006","US-24","Payment","Online","Thanh toán VNPay (ATM/QR)","Positive","P0","Đã Redirect VNPay","","1. Thực hiện thanh toán","Trạng thái đơn = \"Paid\", gửi email Receipt","F11","Web","Not Run","","",""],
    ["TC_ORD_007","US-25","Payment","Confirm","Xác nhận đơn hàng qua Email","Positive","P0","Thanh toán thành công","","1. Kiểm tra email","Nhận email xác nhận đơn hàng + Receipt","F11","Web","Not Run","","",""],
    ["TC_ORD_008","US-26","Order","List","Xem lịch sử đơn hàng","Positive","P0","TK đã có >1 đơn","","1. Vào \"My Orders\"","Hiện list: Order ID, Date, Total, Status","F12","Web","Not Run","","",""],
    ["TC_ORD_009","US-27","Order","Detail","Track trạng thái đơn (timeline)","Positive","P1","Đơn đang xử lý","","1. Click xem chi tiết","Show mốc status thực tế","F12","Web","Not Run","","",""],
    ["TC_ORD_010","US-28","Order","Action","Hủy đơn (khi Pending/Paid, chưa Processing)","Positive","P1","Đơn chưa Processing","","1. Click \"Cancel\"","Status = Cancelled","F12","Web","Not Run","","",""],
    ["TC_ORD_011","US-29","Order","Re-order","Re-order design trước đó","Positive","P1","Đơn đã hoàn thành","","1. Click \"Re-order\"","Tạo đơn mới với cùng design","F12","Web","Not Run","","",""],
    ["TC_ADM_001","US-30","CMS","Dash","Xem Dashboard thống kê kinh doanh","Positive","P0","Admin login","","1. Vào Dashboard","Show: Tổng đơn, Doanh thu, KH mới","F13","Web","Not Run","","",""],
    ["TC_ADM_002","US-31","CMS","Order","Phê duyệt đơn và cập nhật status","Positive","P0","CMS Order list","","1. Update Pending -> Confirmed","System notify user","F13","Web","Not Run","","",""],
    ["TC_ADM_003","US-32","CMS","Catalog","Quản lý Product (Active/Inactive)","Positive","P0","CMS Product list","","1. Toggle Inactive","Loại áo tương ứng ẩn khỏi web user","F13","Web","Not Run","","",""],
    ["TC_ADM_004","US-33","CMS","Gallery","Quản lý Gallery Templates","Positive","P0","CMS Template list","","1. Upload/Hide template","Web gallery update realtime","F13","Web","Not Run","","",""],
    ["TC_ADM_005","US-33b","CMS","Category","Sắp xếp artwork theo category + AI artworks","Positive","P1","CMS Gallery","","1. Gán category cho artwork","Gallery tổ chức theo danh mục","F13","Web","Not Run","","",""],
    ["TC_ADM_006","US-34","CMS","Promo","Quản lý Discount code (Mã, Hạn dùng)","Positive","P1","CMS Discount list","","1. Tạo mã mới","Mã có thể dùng ngay tại Checkout","F13","Web","Not Run","","",""],
    ["TC_ADM_007","US-35","CMS","User","Lock/Unlock tài khoản user","Positive","P0","CMS User detail","Lý do: Fraud","1. Click Lock (Lý do: Fraud)","User ko thể login, gửi email thông báo","F13","Web","Not Run","","",""],
    ["TC_ADM_008","US-36","CMS","Report","Export danh sách User CSV","Positive","P1","CMS User list","","1. Click Export","Tải CSV: name, email, phone, status, date, orders","F13","Web","Not Run","","",""],
    ["TC_ADM_009","US-36b","CMS","AI","Cấu hình giới hạn AI Quota hàng ngày","Positive","P0","CMS Settings","New limit: 20","1. Sửa lượt Gen: 10->20","Áp dụng cho toàn bộ user","F13","Web","Not Run","","",""],
    ["TC_AI_001","US-37","AI Gen","Engine","Nhập Prompt tạo Artwork (4 variations)","Positive","P0","Quota > 0, credits > 0","Prompt: Chú mèo phi hành gia | Style: Digital Art","1. Nhập Prompt VN + Style\n2. Click Gen","Tiêu 1 credit, loading state, trả về 4 ảnh preview","F14","Web","Not Run","","",""],
    ["TC_AI_002","US-38","AI Gen","Upscale","Upscale on Select (≥2048px)","Positive","P0","Đã gen 4 preview","","1. Click \"Dùng ngay\" trên 1 ảnh","Upscale 2k/4k, lưu My Gallery, chuyển sang Editor","F14","Web","Not Run","","",""],
    ["TC_AI_003","US-39","AI Gen","UX","Hiển thị Aha Moment trong khi render","Positive","P1","Đang render","","1. Quan sát màn hình","Rotate messages thú vị trong khi chờ","F14","Web","Not Run","","",""],
    ["TC_AI_004","—","AI Gen","Quota","Guest bị chặn sau 2 lượt/ngày","Negative","P0","Guest đã dùng 2 lượt","","1. Click \"Generate\"","Hiện \"Out of Credits\", gợi ý đăng ký","F14","Web","Not Run","","",""],
    ["TC_AI_005","—","AI Gen","Quota","User bị chặn sau 10 lượt/ngày","Negative","P0","User dùng hết 10 lượt","","1. Click \"Generate\"","Hiện \"Hết lượt tạo hôm nay\"","F14","Web","Not Run","","",""],
    ["TC_CRD_001","US-40","Credits","Profile","Xem số dư Credits trong Profile","Positive","P0","Đã login","","1. Nhìn header/profile","Show số dư thực tế","F15","Web","Not Run","","",""],
    ["TC_CRD_002","US-42","Credits","Spend","Dùng credits cho AI generate & upscale","Positive","P0","Có credits","","1. Thực hiện Gen/Upscale","Trừ balance, ko yêu cầu thanh toán riêng","F15","Web","Not Run","","",""],
    ["TC_CRD_003","US-42b","Credits","Daily Reset","Credits tự refill mỗi 24h","Positive","P0","Credits = 0","","1. Chờ qua ngày mới (00:00)","Balance tự refill về mức mặc định","F15","Web","Not Run","","",""],
]

headers = [
    "TC_ID", "US_Mapping", "Feature", "Module", "Title", "Type", "Priority",
    "Precondition", "Test_Data", "Steps", "Expected_Result",
    "Related_UC", "Environment", "Status", "Error_Message", "Screenshot_Path", "Executed_At"
]

output_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(output_dir, "TC_POD-TShirt-Platform_v2_2026-03-13.csv")

with io.open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(test_cases)

print(f"✅ CSV successfully generated!")
print(f"💾 File: {output_file}")
print(f"📋 Total: {len(test_cases)} test cases")
p0 = sum(1 for tc in test_cases if tc[6] == "P0")
p1 = sum(1 for tc in test_cases if tc[6] == "P1")
pos = sum(1 for tc in test_cases if tc[5] == "Positive")
neg = sum(1 for tc in test_cases if tc[5] == "Negative")
print(f"   P0: {p0} | P1: {p1}")
print(f"   Positive: {pos} | Negative: {neg}")
