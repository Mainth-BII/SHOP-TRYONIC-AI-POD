# Part 1: Epic 1 (Auth) + Epic 2 (Templates) + Epic 3 (Products)
# Run gen_tc_all.py to combine all parts

EPIC1_AUTH = [
    # --- Registration (US-01) ---
    ["TC_AUTH_001","US-01","Registration","Signup","Đăng ký email/password hợp lệ","Positive","P0","Trang Signup mở","email: newuser@test.com | pass: Test@123","1. Mở trang /signup\n2. Nhập Name: Nguyễn Văn A\n3. Nhập Email: newuser@test.com\n4. Nhập Password: Test@123\n5. Click 'Đăng ký'","Hiển thị 'Đăng ký thành công'. Gửi email verify đến newuser@test.com. DB tạo record users.status=pending"],
    ["TC_AUTH_002","US-01","Registration","Signup","Đăng ký pass yếu thiếu số","Negative","P0","Trang Signup mở","pass: Abcdefgh","1. Nhập Password: Abcdefgh\n2. Click 'Đăng ký'","Hiển thị lỗi: 'Mật khẩu phải có ít nhất 8 ký tự, 1 chữ hoa, 1 số'. Không tạo account"],
    ["TC_AUTH_003","US-01","Registration","Signup","Đăng ký pass thiếu chữ hoa","Negative","P0","Trang Signup mở","pass: test@1234","1. Nhập Password: test@1234\n2. Click 'Đăng ký'","Hiển thị lỗi validation password"],
    ["TC_AUTH_004","US-01","Registration","Signup","Đăng ký email đã tồn tại","Negative","P0","Email existing@test.com đã có trong DB","email: existing@test.com","1. Nhập Email: existing@test.com\n2. Nhập Password: Test@123\n3. Click 'Đăng ký'","Hiển thị lỗi: 'Email đã được sử dụng'"],
    ["TC_AUTH_005","US-01","Registration","Signup","Đăng ký email format sai","Negative","P0","Trang Signup mở","email: invalid-email","1. Nhập Email: invalid-email\n2. Click 'Đăng ký'","Hiển thị lỗi: 'Email không hợp lệ'"],
    ["TC_AUTH_006","US-01","Registration","Signup","Đăng ký bỏ trống tất cả field","Negative","P0","Trang Signup mở","","1. Không nhập gì\n2. Click 'Đăng ký'","Hiển thị inline error cho tất cả required fields"],
    ["TC_AUTH_007","US-01","Registration","Signup","Boundary: password length = 7 (min-1)","Boundary","P1","Trang Signup mở","pass: Test@12","1. Nhập Password 7 ký tự: Test@12\n2. Click 'Đăng ký'","Hiển thị lỗi: password phải >= 8 ký tự"],
    ["TC_AUTH_008","US-01","Registration","Signup","Boundary: password length = 8 (min)","Boundary","P1","Trang Signup mở","pass: Test@123","1. Nhập Password 8 ký tự: Test@123\n2. Click 'Đăng ký'","Đăng ký thành công"],
    ["TC_AUTH_009","US-01","Registration","Signup","Email chứa ký tự đặc biệt hợp lệ","Edge Case","P2","Trang Signup mở","email: user+tag@test.com","1. Nhập Email: user+tag@test.com\n2. Hoàn tất form\n3. Click 'Đăng ký'","Đăng ký thành công. Email có dấu + được chấp nhận"],
    ["TC_AUTH_010","US-01","Registration","Signup","XSS injection trong field Name","Negative","P1","Trang Signup mở","name: <script>alert(1)</script>","1. Nhập Name: <script>alert(1)</script>\n2. Hoàn tất form\n3. Click 'Đăng ký'","Hệ thống sanitize input. Không execute script. Name lưu dạng escaped text"],
    # --- Signup UI/UX Test Cases (from Stitch Design) ---
    ["TC_AUTH_UI_015","US-01","Registration","UI/UX","Signup page: Tiêu đề hiển thị đúng","UI/UX","P1","Mở /signup","","1. Mở trang /signup\n2. Quan sát phần header form","Tiêu đề hiển thị: 'Đăng ký tài khoản'"],
    ["TC_AUTH_UI_016","US-01","Registration","UI/UX","Signup page: Field 'Họ và tên' placeholder","UI/UX","P2","Trang /signup","","1. Quan sát field 'Họ và tên'","Placeholder hiển thị: 'Nhập họ và tên của bạn'"],
    ["TC_AUTH_UI_017","US-01","Registration","UI/UX","Signup page: Field 'Xác nhận mật khẩu' hiện diện","UI/UX","P1","Trang /signup","","1. Quan sát danh sách các trường nhập","Có trường 'Xác nhận mật khẩu' bên dưới trường 'Mật khẩu'"],
    ["TC_AUTH_UI_018","US-01","Registration","UI/UX","Signup page: Checkbox Điều khoản","UI/UX","P1","Trang /signup","","1. Quan sát dòng trên nút Đăng ký","Hiển thị checkbox với text: 'Tôi đồng ý với Điều khoản và Chính sách của POD Platform'"],
    # --- Google OAuth (US-02) --- [Design: Button 'Tiếp tục với Google' outlined]
    ["TC_AUTH_011","US-02","Login","OAuth","Click 'Tiếp tục với Google' thành công","Positive","P0","Có tài khoản Google. Trang /login hiển thị","","1. Mở /login\n2. Click button 'Tiếp tục với Google'\n3. Chọn tài khoản Google\n4. Authorize permissions","Redirect về Dashboard. Header hiển thị tên + avatar từ Google. Session tạo 24h"],
    ["TC_AUTH_012","US-02","Login","OAuth","Google OAuth lần đầu - auto tạo account","Positive","P0","Email Google chưa có trong DB","","1. Click 'Tiếp tục với Google'\n2. Chọn tài khoản mới","Tạo account mới. DB: auth_provider=google. Redirect Dashboard"],
    ["TC_AUTH_013","US-02","Login","OAuth","Google OAuth - user deny permission","Negative","P1","","","1. Click 'Tiếp tục với Google'\n2. Cancel ở Google consent screen","Redirect về trang Login. Hiển thị: 'Đăng nhập bị hủy'. Trang login hiện lại đầy đủ"],
    ["TC_AUTH_014","US-02","Login","OAuth","Google OAuth - email trùng account email/pass","Edge Case","P1","Email đã đăng ký bằng email/pass","","1. Click 'Tiếp tục với Google' với email đã có","Liên kết account hoặc hiển thị lỗi trùng email (tùy BR)"],
    # --- Facebook OAuth (US-02b) --- [Design: Button 'Tiếp tục với Facebook' filled blue]
    ["TC_AUTH_015","US-02b","Login","OAuth","Click 'Tiếp tục với Facebook' thành công","Positive","P1","Có tài khoản Facebook","","1. Click button 'Tiếp tục với Facebook'\n2. Authorize","Đăng nhập thành công. Redirect Dashboard. Hiển thị tên từ FB"],
    ["TC_AUTH_016","US-02b","Login","OAuth","Facebook OAuth deny permission","Negative","P1","","","1. Click 'Tiếp tục với Facebook'\n2. Cancel permission","Redirect Login. Hiển thị thông báo hủy"],
    # --- Email Login (US-03) --- [Design: Email placeholder 'example@email.com', Password masked, Button 'Đăng nhập' purple]
    ["TC_AUTH_017","US-03","Login","Login","Đăng nhập email/pass đúng","Positive","P0","TK active, verified","email: user@test.com | pass: Test@123","1. Mở /login\n2. Nhập email: user@test.com vào field Email (placeholder: 'example@email.com')\n3. Nhập password: Test@123 vào field Mật khẩu\n4. Click button 'Đăng nhập' (purple)","Redirect Dashboard. Header hiển thị tên user. Session tạo"],
    ["TC_AUTH_018","US-03","Login","Login","Đăng nhập sai password","Negative","P0","TK active","email: user@test.com | pass: wrongpass","1. Nhập email: user@test.com\n2. Nhập password: wrongpass\n3. Click 'Đăng nhập'","Hiển thị: 'Email hoặc mật khẩu không đúng'. Không tiết lộ email tồn tại hay không"],
    ["TC_AUTH_019","US-03","Login","Login","Đăng nhập email chưa verify","Negative","P0","TK chưa verify email","","1. Nhập email/pass đúng\n2. Click 'Đăng nhập'","Hiển thị: 'Vui lòng xác thực email trước khi đăng nhập'. Link resend verify"],
    ["TC_AUTH_020","US-03","Login","Login","Đăng nhập email không tồn tại","Negative","P0","","email: ghost@test.com","1. Nhập email: ghost@test.com\n2. Nhập password bất kỳ\n3. Click 'Đăng nhập'","Hiển thị: 'Email hoặc mật khẩu không đúng' (thông báo chung, không tiết lộ)"],
    ["TC_AUTH_021","US-03","Login","Login","Đăng nhập bỏ trống cả Email và Mật khẩu","Negative","P0","Trang /login hiển thị","","1. Không nhập gì\n2. Click 'Đăng nhập'","Hiển thị inline error: 'Vui lòng nhập email' + 'Vui lòng nhập mật khẩu'"],
    ["TC_AUTH_022","US-03","Login","Login","Đăng nhập bỏ trống Password","Negative","P0","Trang /login","email: user@test.com","1. Nhập email: user@test.com\n2. Bỏ trống Mật khẩu\n3. Click 'Đăng nhập'","Hiển thị inline error dưới field Mật khẩu"],
    # --- Login UI/UX Test Cases (from Design Screenshot) ---
    ["TC_AUTH_UI_001","US-03","Login","UI/UX","Login page: Logo, Title, Subtitle hiển thị đúng","UI/UX","P1","Mở /login","","1. Mở trang /login\n2. Quan sát phần header","Logo 'POD Platform' hiển thị (icon kim cương + text). Title: 'Đăng nhập'. Subtitle: 'Chào mừng bạn quay lại!' — centered"],
    ["TC_AUTH_UI_002","US-03","Login","UI/UX","Login page: Placeholder Email field","UI/UX","P1","Trang /login, chưa nhập gì","","1. Quan sát field Email\n2. Kiểm tra placeholder","Placeholder hiển thị: 'example@email.com'. Icon mail ở bên trái. Label 'Email' phía trên"],
    ["TC_AUTH_UI_003","US-03","Login","UI/UX","Login page: Password field - Show/Hide toggle","UI/UX","P1","Trang /login","pass: Test@123","1. Nhập password: Test@123\n2. Quan sát field: characters masked (●●●●●●●●)\n3. Click icon eye (👁) bên phải field\n4. Quan sát password","Click eye → hiện text 'Test@123'. Click lại → mask lại. Icon lock ở bên trái"],
    ["TC_AUTH_UI_004","US-03","Login","UI/UX","Login page: Link 'Quên mật khẩu?' hoạt động","UI/UX","P1","Trang /login","","1. Quan sát link 'Quên mật khẩu?' (bên phải label 'Mật khẩu')\n2. Click link","Redirect sang trang Reset Password. Link hiển thị đúng vị trí, cùng hàng label 'Mật khẩu'"],
    ["TC_AUTH_UI_005","US-03","Login","UI/UX","Login page: Button 'Đăng nhập' style đúng","UI/UX","P1","Trang /login","","1. Quan sát button 'Đăng nhập'","Button full-width, background màu purple/indigo (#6366F1 hoặc tương tự), text trắng, border-radius rounded, font bold"],
    ["TC_AUTH_UI_006","US-03","Login","UI/UX","Login page: Button 'Tiếp tục với Google' style","UI/UX","P2","Trang /login","","1. Quan sát button 'Tiếp tục với Google'","Button outlined (border, no fill), full-width, có Google icon (G) bên trái text. Text: 'Tiếp tục với Google'"],
    ["TC_AUTH_UI_007","US-03","Login","UI/UX","Login page: Button 'Tiếp tục với Facebook' style","UI/UX","P2","Trang /login","","1. Quan sát button 'Tiếp tục với Facebook'","Button filled blue (#1877F2), full-width, có Facebook icon (f) bên trái text. Text: 'Tiếp tục với Facebook'"],
    ["TC_AUTH_UI_008","US-03","Login","UI/UX","Login page: Separator 'HOẶC' giữa OAuth và form","UI/UX","P2","Trang /login","","1. Quan sát giữa 2 OAuth buttons và email form","Hiển thị text 'HOẶC' với horizontal lines 2 bên. Centered, màu nhạt"],
    ["TC_AUTH_UI_009","US-03","Login","UI/UX","Login page: Link 'Đăng ký ngay' chuyển sang Signup","UI/UX","P1","Trang /login","","1. Quan sát cuối form: 'Chưa có tài khoản? Đăng ký ngay'\n2. Click 'Đăng ký ngay'","Redirect sang trang /signup. Link text 'Đăng ký ngay' có màu nổi bật (blue/purple)"],
    ["TC_AUTH_UI_010","US-03","Login","UI/UX","Login page: Footer links hiển thị đúng","UI/UX","P2","Trang /login","","1. Quan sát footer bên dưới form","Hiển thị 3 links: 'Điều khoản dịch vụ' | 'Chính sách bảo mật' | 'Trợ giúp'. Click mỗi link mở trang tương ứng"],
    ["TC_AUTH_UI_011","US-03","Login","UI/UX","Login page: Responsive mobile 375px","UI/UX","P1","Viewport 375px","","1. Resize browser 375px width\n2. Quan sát trang login","Card login full-width với padding. Buttons không bị cắt text. Form fields không overflow. Footer không bị đẩy ra ngoài"],
    ["TC_AUTH_UI_012","US-03","Login","UI/UX","Login page: Tab order (keyboard navigation)","UI/UX","P2","Trang /login","","1. Nhấn Tab liên tục từ đầu trang","Tab order: Google → Facebook → Email → Password → Đăng nhập → Quên mật khẩu → Đăng ký ngay"],
    ["TC_AUTH_UI_013","US-03","Login","UI/UX","Login page: Enter key submit form","UI/UX","P1","Trang /login, đã nhập email + pass","email: user@test.com | pass: Test@123","1. Nhập email + password\n2. Nhấn Enter","Form submit. Đăng nhập thành công (tương đương click button 'Đăng nhập')"],
    ["TC_AUTH_UI_014","US-03","Login","UI/UX","Login page: Email field autofocus","UI/UX","P2","Trang /login vừa load","","1. Mở /login lần đầu\n2. Quan sát cursor","Cursor tự focus vào field Email. Có thể bắt đầu nhập ngay"],
    # --- Rate Limit / Lock (Security from reference) ---
    ["TC_AUTH_023","US-03","Login","Security","Login sai 5 lần liên tiếp - lock account","Negative","P0","TK active","","1. Nhập sai password 5 lần liên tiếp\n2. Quan sát sau lần thứ 5","Account bị lock 15 phút. Hiển thị: 'Tài khoản bị khóa tạm thời. Vui lòng thử lại sau 15 phút'"],
    ["TC_AUTH_024","US-03","Login","Security","Login sai lần 4 - cảnh báo","Negative","P1","Đã sai 3 lần","","1. Nhập sai password lần thứ 4\n2. Xem thông báo","Hiển thị cảnh báo: 'Còn 1 lần nữa tài khoản sẽ bị khóa'"],
    ["TC_AUTH_025","US-03","Login","Security","Counter reset sau login thành công","Positive","P1","Đã sai 3 lần, chưa lock","","1. Đăng nhập đúng\n2. Logout\n3. Sai 1 lần\n4. Kiểm tra counter","Counter về 0 sau login thành công"],
    ["TC_AUTH_026","US-03","Login","Security","Lock per-account, không per-IP","Boundary","P1","2 máy khác IP","","1. Máy A sai 3 lần account X\n2. Máy B sai 2 lần account X","Account X bị lock dù login từ nhiều IP khác nhau"],
    ["TC_AUTH_027","US-03","Login","Security","Bypass OAuth khi account bị lock","Edge Case","P1","Account bị lock","","1. Account bị lock\n2. Thử login bằng 'Tiếp tục với Google' cùng email","Xử lý nhất quán: block hoặc cho phép OAuth. Không bypass mặc định"],
    ["TC_AUTH_028","US-03","Login","Security","Lock message không tiết lộ thông tin","Negative","P1","","email: ghost@test.com","1. Nhập email không tồn tại sai pass 5+ lần","Không hiển thị 'Email không tồn tại'. Thông báo chung. Counter không tăng cho email không tồn tại"],
    ["TC_AUTH_029","US-03","Login","Security","Admin unlock account trước 15 phút","Positive","P1","TK bị lock, Admin có quyền","","1. Admin vào portal\n2. Unlock tài khoản\n3. User thử login lại","Mở khóa ngay. User login thành công"],
    ["TC_AUTH_030","US-03","Login","Security","Concurrent login attempts (race condition)","Boundary","P1","","","1. Gửi đồng thời 10 request login sai\n2. Kiểm tra lock","Không bị race condition. Account lock sau đúng 5 lần thực sự"],
    ["TC_AUTH_031","US-03","Login","Security","Lock persist sau clear cookies","Edge Case","P1","Account bị lock","","1. Clear cookie/localStorage\n2. Sai thêm vào account đó","Vẫn bị lock. Lock server-side, không client-side"],
    ["TC_AUTH_032","US-03","Login","Security","Lock time chính xác 15 phút","Boundary","P1","Account vừa lock","","1. Thử login sau 14:50\n2. Thử login sau 15:00","14:50 vẫn lock. 15:00 có thể login"],
    ["TC_AUTH_033","US-03","Login","Security","API rate limit POST /api/login","Negative","P1","","","1. Gọi POST /api/login sai pass 5+ lần qua API\n2. Kiểm tra response","API trả 429 Too Many Requests hoặc lock. Không bypass được qua API"],
    ["TC_AUTH_034","US-03","Login","Security","Forgot password khi account bị lock","Positive","P2","Account bị lock","","1. Click link 'Quên mật khẩu?' trên trang login\n2. Nhập email bị lock\n3. Nhấn Send","Email reset vẫn được gửi. User có thể reset dù đang lock"],
    ["TC_AUTH_035","US-03","Login","Security","Audit log ghi nhận failed attempts","Positive","P2","Có quyền xem log","","1. Thực hiện 5 lần login sai\n2. Kiểm tra audit log","Log ghi đầy đủ: timestamp, IP, email, số lần thất bại, thời điểm lock"],
    ["TC_AUTH_036","US-03","Login","Security","Remember me session 30 ngày","Positive","P1","","","1. Tick 'Remember me'\n2. Login thành công\n3. Kiểm tra session expiry","Session kéo dài 30 ngày thay vì 24h mặc định"],
    # --- Guest Mode (US-03b, US-03c) ---
    ["TC_AUTH_037","US-03b","Guest Mode","Browser","Guest vào Editor thiết kế bình thường","Positive","P0","Chưa đăng nhập","","1. Truy cập /editor không login\n2. Add artwork/text\n3. Thao tác drag/resize","Cho phép thao tác bình thường. Data lưu localStorage"],
    ["TC_AUTH_038","US-03b","Guest Mode","Browser","Guest data persist khi refresh","Positive","P1","Guest đã có design","","1. Tạo design\n2. Refresh browser","Design vẫn còn từ localStorage"],
    ["TC_AUTH_039","US-03b","Guest Mode","Browser","Guest data mất khi clear storage","Edge Case","P2","Guest đã có design","","1. Clear localStorage\n2. Quay lại Editor","Design biến mất. Canvas trống"],
    ["TC_AUTH_040","US-03c","Guest Mode","Migration","Guest checkout → popup login, giữ data","Positive","P0","Guest có hàng trong cart","","1. Click 'Thanh toán'\n2. Popup Login hiện\n3. Đăng nhập","Giữ nguyên design + cart. Chuyển sang checkout"],
    ["TC_AUTH_041","US-03c","Guest Mode","Migration","Guest đăng ký mới tại popup checkout","Positive","P0","Guest có design","","1. Click 'Thanh toán'\n2. Chọn 'Đăng ký' trên popup\n3. Hoàn tất đăng ký","Account mới tạo. Design + cart migrate sang account"],
    # --- Reset Password (US-04) --- [Design: Link 'Quên mật khẩu?' trên login page]
    ["TC_AUTH_042","US-04","Account","Security","Reset password flow hoàn chỉnh","Positive","P0","Quên mật khẩu","email: user@test.com","1. Click link 'Quên mật khẩu?' trên trang login\n2. Nhập email: user@test.com\n3. Nhận email reset\n4. Click link trong email\n5. Nhập new pass: NewTest@123\n6. Confirm","Đổi pass thành công. Login với pass mới OK"],
    ["TC_AUTH_043","US-04","Account","Security","Reset link hết hạn sau 1h","Boundary","P1","Đã nhận link reset","","1. Chờ > 1 giờ\n2. Click link reset","Hiển thị: 'Link đã hết hạn. Vui lòng yêu cầu lại'"],
    ["TC_AUTH_044","US-04","Account","Security","Reset link dùng 1 lần","Negative","P1","Đã reset thành công","","1. Click lại link reset đã dùng","Hiển thị: 'Link đã được sử dụng'"],
    ["TC_AUTH_045","US-04","Account","Security","Reset password cho email không tồn tại","Negative","P1","","email: ghost@test.com","1. Nhập email: ghost@test.com\n2. Click 'Gửi'","Hiển thị thông báo chung (không tiết lộ email có tồn tại không)"],
    # --- Update Profile (US-05) ---
    ["TC_AUTH_046","US-05","Profile","Account","Cập nhật profile thành công","Positive","P1","Đã đăng nhập","phone: 0901234567","1. Vào Profile\n2. Sửa Phone: 0901234567\n3. Upload Avatar\n4. Click Save","Data lưu DB. Trang hiển thị data mới"],
    ["TC_AUTH_047","US-05","Profile","Account","Cập nhật avatar file > 5MB","Negative","P1","Đã đăng nhập","file: bigphoto.jpg (6MB)","1. Upload avatar > 5MB","Hiển thị lỗi: 'File quá lớn'"],
    ["TC_AUTH_048","US-05","Profile","Account","Phone format sai","Negative","P1","Đã đăng nhập","phone: abc123","1. Nhập Phone: abc123\n2. Click Save","Hiển thị lỗi format số điện thoại"],
]

EPIC2_TEMPLATES = [
    # --- Browse Gallery (US-06) ---

    ["TC_AUTH_022","US-03","Login","Security","Login sai lần 4 - cảnh báo","Negative","P1","Đã sai 3 lần","","1. Nhập sai password lần thứ 4\n2. Xem thông báo","Hiển thị cảnh báo: 'Còn 1 lần nữa tài khoản sẽ bị khóa'"],
    ["TC_AUTH_023","US-03","Login","Security","Counter reset sau login thành công","Positive","P1","Đã sai 3 lần, chưa lock","","1. Đăng nhập đúng\n2. Logout\n3. Sai 1 lần\n4. Kiểm tra counter","Counter về 0 sau login thành công"],
    ["TC_AUTH_024","US-03","Login","Security","Lock per-account, không per-IP","Boundary","P1","2 máy khác IP","","1. Máy A sai 3 lần account X\n2. Máy B sai 2 lần account X","Account X bị lock dù login từ nhiều IP khác nhau"],
    ["TC_AUTH_025","US-03","Login","Security","Bypass OAuth khi account bị lock","Edge Case","P1","Account bị lock","","1. Account bị lock\n2. Thử login bằng Google OAuth cùng email","Xử lý nhất quán: block hoặc cho phép OAuth. Không bypass mặc định"],
    ["TC_AUTH_026","US-03","Login","Security","Lock message không tiết lộ thông tin","Negative","P1","","email: ghost@test.com","1. Nhập email không tồn tại sai pass 5+ lần","Không hiển thị 'Email không tồn tại'. Thông báo chung. Counter không tăng cho email không tồn tại"],
    ["TC_AUTH_027","US-03","Login","Security","Admin unlock account trước 15 phút","Positive","P1","TK bị lock, Admin có quyền","","1. Admin vào portal\n2. Unlock tài khoản\n3. User thử login lại","Mở khóa ngay. User login thành công"],
    ["TC_AUTH_028","US-03","Login","Security","Concurrent login attempts (race condition)","Boundary","P1","","","1. Gửi đồng thời 10 request login sai\n2. Kiểm tra lock","Không bị race condition. Account lock sau đúng 5 lần thực sự"],
    ["TC_AUTH_029","US-03","Login","Security","Lock persist sau clear cookies","Edge Case","P1","Account bị lock","","1. Clear cookie/localStorage\n2. Sai thêm vào account đó","Vẫn bị lock. Lock server-side, không client-side"],
    ["TC_AUTH_030","US-03","Login","Security","Lock time chính xác 15 phút","Boundary","P1","Account vừa lock","","1. Thử login sau 14:50\n2. Thử login sau 15:00","14:50 vẫn lock. 15:00 có thể login"],
    ["TC_AUTH_031","US-03","Login","Security","API rate limit POST /api/login","Negative","P1","","","1. Gọi POST /api/login sai pass 5+ lần qua API\n2. Kiểm tra response","API trả 429 Too Many Requests hoặc lock. Không bypass được qua API"],
    ["TC_AUTH_032","US-03","Login","Security","Forgot password khi account bị lock","Positive","P2","Account bị lock","","1. Vào Forgot Password\n2. Nhập email bị lock\n3. Nhấn Send","Email reset vẫn được gửi. User có thể reset dù đang lock"],
    ["TC_AUTH_033","US-03","Login","Security","Audit log ghi nhận failed attempts","Positive","P2","Có quyền xem log","","1. Thực hiện 5 lần login sai\n2. Kiểm tra audit log","Log ghi đầy đủ: timestamp, IP, email, số lần thất bại, thời điểm lock"],
    ["TC_AUTH_034","US-03","Login","Security","Remember me session 30 ngày","Positive","P1","","","1. Tick 'Remember me'\n2. Login thành công\n3. Kiểm tra session expiry","Session kéo dài 30 ngày thay vì 24h mặc định"],
    # --- Guest Mode (US-03b, US-03c) ---
    ["TC_AUTH_035","US-03b","Guest Mode","Browser","Guest vào Editor thiết kế bình thường","Positive","P0","Chưa đăng nhập","","1. Truy cập /editor không login\n2. Add artwork/text\n3. Thao tác drag/resize","Cho phép thao tác bình thường. Data lưu localStorage"],
    ["TC_AUTH_036","US-03b","Guest Mode","Browser","Guest data persist khi refresh","Positive","P1","Guest đã có design","","1. Tạo design\n2. Refresh browser","Design vẫn còn từ localStorage"],
    ["TC_AUTH_037","US-03b","Guest Mode","Browser","Guest data mất khi clear storage","Edge Case","P2","Guest đã có design","","1. Clear localStorage\n2. Quay lại Editor","Design biến mất. Canvas trống"],
    ["TC_AUTH_038","US-03c","Guest Mode","Migration","Guest checkout → popup login, giữ data","Positive","P0","Guest có hàng trong cart","","1. Click 'Thanh toán'\n2. Popup Login hiện\n3. Đăng nhập","Giữ nguyên design + cart. Chuyển sang checkout"],
    ["TC_AUTH_039","US-03c","Guest Mode","Migration","Guest đăng ký mới tại popup checkout","Positive","P0","Guest có design","","1. Click 'Thanh toán'\n2. Chọn 'Đăng ký' trên popup\n3. Hoàn tất đăng ký","Account mới tạo. Design + cart migrate sang account"],
    # --- Reset Password (US-04) ---
    ["TC_AUTH_040","US-04","Account","Security","Reset password flow hoàn chỉnh","Positive","P0","Quên mật khẩu","email: user@test.com","1. Click 'Quên mật khẩu'\n2. Nhập email: user@test.com\n3. Nhận email reset\n4. Click link\n5. Nhập new pass: NewTest@123\n6. Confirm","Đổi pass thành công. Login với pass mới OK"],
    ["TC_AUTH_041","US-04","Account","Security","Reset link hết hạn sau 1h","Boundary","P1","Đã nhận link reset","","1. Chờ > 1 giờ\n2. Click link reset","Hiển thị: 'Link đã hết hạn. Vui lòng yêu cầu lại'"],
    ["TC_AUTH_042","US-04","Account","Security","Reset link dùng 1 lần","Negative","P1","Đã reset thành công","","1. Click lại link reset đã dùng","Hiển thị: 'Link đã được sử dụng'"],
    ["TC_AUTH_043","US-04","Account","Security","Reset password cho email không tồn tại","Negative","P1","","email: ghost@test.com","1. Nhập email: ghost@test.com\n2. Click 'Gửi'","Hiển thị thông báo chung (không tiết lộ email có tồn tại không)"],
    # --- Update Profile (US-05) ---
    ["TC_AUTH_044","US-05","Profile","Account","Cập nhật profile thành công","Positive","P1","Đã đăng nhập","phone: 0901234567","1. Vào Profile\n2. Sửa Phone: 0901234567\n3. Upload Avatar\n4. Click Save","Data lưu DB. Trang hiển thị data mới"],
    ["TC_AUTH_045","US-05","Profile","Account","Cập nhật avatar file > 5MB","Negative","P1","Đã đăng nhập","file: bigphoto.jpg (6MB)","1. Upload avatar > 5MB","Hiển thị lỗi: 'File quá lớn'"],
    ["TC_AUTH_046","US-05","Profile","Account","Phone format sai","Negative","P1","Đã đăng nhập","phone: abc123","1. Nhập Phone: abc123\n2. Click Save","Hiển thị lỗi format số điện thoại"],
]

EPIC2_TEMPLATES = [
    # --- Browse Gallery (US-06) ---
    ["TC_TEM_001","US-06","Gallery","Browse","Duyệt template gallery load thành công","Positive","P0","Vào trang Template","","1. Mở /templates\n2. Scroll xuống","Load templates. Lazy load khi scroll"],
    ["TC_TEM_002","US-06","Gallery","Browse","Gallery load empty state","Edge Case","P1","DB không có template nào","","1. Mở /templates","Hiển thị empty state: 'Chưa có template nào'"],
    ["TC_TEM_003","US-06","Gallery","Browse","Gallery load hình bị lỗi/broken","Negative","P1","Template có image URL broken","","1. Mở /templates","Hiển thị placeholder image. Không crash page"],
    # --- Search (US-07) ---
    ["TC_TEM_004","US-07","Gallery","Search","Tìm kiếm template theo keyword khớp","Positive","P1","Có template 'Vintage Rock'","keyword: Vintage","1. Nhập 'Vintage' vào search\n2. Enter","Hiển thị templates có tên/tag chứa 'Vintage'"],
    ["TC_TEM_005","US-07","Gallery","Search","Tìm kiếm keyword không khớp","Negative","P1","","keyword: xyznotexist","1. Search 'xyznotexist'","Hiển thị: 'Không tìm thấy template phù hợp'"],
    ["TC_TEM_006","US-07","Gallery","Search","Tìm kiếm keyword rỗng","Boundary","P2","","","1. Search với text rỗng","Hiển thị tất cả templates (hoặc không thay đổi)"],
    ["TC_TEM_007","US-07","Gallery","Search","Search XSS injection","Negative","P1","","keyword: <script>alert(1)</script>","1. Nhập script tag vào search","Không execute. Sanitize input"],
    # --- Filter (US-08) ---
    ["TC_TEM_008","US-08","Gallery","Filter","Lọc theo category Sport","Positive","P1","Có templates category Sport","","1. Chọn filter: Sport","Chỉ hiện templates thuộc Sport"],
    ["TC_TEM_009","US-08","Gallery","Filter","Lọc category không có template","Edge Case","P2","Category rỗng","","1. Chọn category trống","Hiển thị empty state"],
    ["TC_TEM_010","US-08","Gallery","Filter","Kết hợp Search + Filter","Positive","P1","","keyword: Rock | cat: Music","1. Search 'Rock'\n2. Filter: Music","Chỉ hiện templates Music chứa 'Rock'"],
    # --- Open in Editor (US-09) ---
    ["TC_TEM_011","US-09","Gallery","Editor","Click template mở Editor","Positive","P0","Gallery loaded","","1. Click 1 template","Template load vào Editor canvas. Các layer có thể chỉnh sửa"],
    ["TC_TEM_012","US-09","Gallery","Editor","Mở template khi chưa login (Guest)","Positive","P0","Chưa đăng nhập","","1. Click template","Template vẫn load vào Editor (Guest mode)"],
]

EPIC3_PRODUCTS = [
    # --- Product Type (US-10) ---
    ["TC_PRO_001","US-10","Product","Select","Chọn loại áo T-shirt","Positive","P0","Editor mở","","1. Click menu sản phẩm\n2. Chọn 'T-shirt Round Neck'","Mockup đổi sang T-shirt. Canvas resize đúng vùng in"],
    ["TC_PRO_002","US-10","Product","Select","Chọn loại áo Polo","Positive","P0","Editor mở","","1. Chọn 'Polo'","Mockup đổi sang Polo. Vùng in khác T-shirt"],
    ["TC_PRO_003","US-10","Product","Select","Switch sản phẩm giữ nguyên design","Edge Case","P1","Đã có artwork trên T-shirt","","1. Đổi từ T-shirt sang Polo","Design giữ nguyên. Warning nếu artwork lấn safe zone mới"],
    # --- Color (US-11) ---
    ["TC_PRO_004","US-11","Product","Color","Chọn màu realtime mockup","Positive","P0","Editor mở","color: Navy","1. Click swatch Navy","Áo mockup đổi màu Navy ngay. Artwork không bị ảnh hưởng"],
    ["TC_PRO_005","US-11","Product","Color","Đổi màu nhiều lần liên tiếp","Boundary","P1","Editor mở","","1. Click Navy\n2. Click White\n3. Click Red nhanh liên tục","Mockup update mượt, không lag/flicker"],
    # --- Size Chart (US-12) ---
    ["TC_PRO_006","US-12","Product","Size","Xem Size Chart S-2XL hiển thị đúng","Positive","P0","","","1. Click 'Bảng size'\n2. Đọc thông số","Hiển thị bảng: S/M/L/XL/2XL với Vai/Ngực/Dài áo (cm). Data chính xác"],
    ["TC_PRO_007","US-12","Product","Size","Size Chart responsive mobile","UI/UX","P2","Mobile 375px","","1. Mở bảng size trên mobile","Bảng scroll ngang hoặc stack. Không bị cắt cột"],
    # --- Smart Fit (US-12b) ---
    ["TC_PRO_008","US-12b","Smart Fit","AI","Gợi ý size - input hợp lệ","Positive","P0","Popup Fit-Size","H:175, W:70, Gender:Nam","1. Nhập H:175, W:70, Gender:Nam\n2. Click 'Gợi ý'","Hiển thị: 'Size L (Khớp 90%)' hoặc tương tự"],
    ["TC_PRO_009","US-12b","Smart Fit","AI","Gợi ý size - BMI cao","Boundary","P1","","H:160, W:100, Gender:Nam","1. Nhập H:160, W:100\n2. Click 'Gợi ý'","Gợi ý size 2XL hoặc thông báo vượt range"],
    ["TC_PRO_010","US-12b","Smart Fit","AI","Gợi ý size - input rỗng","Negative","P1","","","1. Không nhập gì\n2. Click 'Gợi ý'","Hiển thị lỗi: 'Vui lòng nhập đủ thông tin'"],
    ["TC_PRO_011","US-12b","Smart Fit","AI","Gợi ý size - input chữ vào field số","Negative","P1","","H:abc","1. Nhập H: abc\n2. Click 'Gợi ý'","Validation: chỉ nhận số"],
    # --- Plain Product (US-12c) ---
    ["TC_PRO_012","US-12c","Product","Plain","Mua áo trơn không cần Editor","Positive","P0","Trang chi tiết SP","","1. Click 'Mua ngay'\n2. Chọn Size, Qty","Add trơn vào giỏ. Không mở Editor"],
    ["TC_PRO_013","US-12c","Product","Plain","Mua áo trơn chọn màu","Positive","P0","Trang chi tiết SP","color:Black, size:L","1. Chọn màu Black\n2. Chọn Size L\n3. Click 'Thêm vào giỏ'","Giỏ hàng hiện: Áo trơn Black, Size L"],
]

ALL_PART1 = EPIC1_AUTH + EPIC2_TEMPLATES + EPIC3_PRODUCTS
print(f"Part 1: {len(ALL_PART1)} test cases (Auth:{len(EPIC1_AUTH)}, Templates:{len(EPIC2_TEMPLATES)}, Products:{len(EPIC3_PRODUCTS)})")
