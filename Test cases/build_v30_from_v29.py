"""
Build v30 from v29: Add test cases for git commits 7b263ce + 6d3077e

New features:
1. PROFILE PAGE (profile/page.tsx) → Merge into LOGIN sheet
2. ADDRESS PICKER (AddressPicker.tsx) → Merge into LOGIN + THANH TOÁN
3. CHECKOUT PAGE UPGRADE (checkout/page.tsx now uses AddressPicker) → Update THANH TOÁN
4. CHECKOUT MODAL (CheckoutModal.tsx — 3-step drawer) → Update THANH TOÁN
5. STUDIO TOPBAR (StudioTopBar.tsx — /profile link) → Update DESIGN STUDIO
6. ORDER MODAL (OrderModal.tsx — selectedSize prop) → Update ĐẶT HÀNG
"""
import re

SRC = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v30.md"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# ─── 1. Update header ─────────────────────────────────
content = content.replace(
    "# POD T-Shirt Platform — Test Case Suite v29 (Final)",
    "# POD T-Shirt Platform — Test Case Suite v30 (Final)"
)
content = content.replace(
    "> **Version:** v29",
    "> **Version:** v30"
)

# ─── 2. PROFILE PAGE TCs → append to LOGIN sheet ─────
# These go under LOGIN > UI/UX, Functional, Validation, Security

PROFILE_UI = """| `TC_PROF_UI_001` | `US-PROF-01` | Profile - Header | Profile: Header hiển thị 'Quay lại Studio' + logo Tryonic + nút 'Lưu thay đổi' | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /profile | Header sticky: nút ArrowLeft 'Quay lại Studio', logo Palette+Tryonic, nút gradient teal 'Lưu thay đổi' |
| `TC_PROF_UI_002` | `US-PROF-01` | Profile - Avatar | Profile: Avatar section hiển thị đúng | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /profile<br>2. Quan sát avatar | Avatar tròn 96px, gradient teal, hiển thị chữ cái đầu tên. Có camera icon góc dưới phải. Click để upload ảnh |
| `TC_PROF_UI_003` | `US-PROF-01` | Profile - Stats | Profile: 3 Stats cards hiển thị đúng | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /profile<br>2. Quan sát stats | 3 cards grid: Credits (teal icon), Đơn hàng (blue icon), Thiết kế (purple icon). Hiển thị số + label |
| `TC_PROF_UI_004` | `US-PROF-01` | Profile - Contact | Profile: Form thông tin liên hệ hiển thị đúng | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /profile<br>2. Quan sát section 'Thông tin liên hệ' | 2 fields: Email (icon Mail) + Số điện thoại (icon Phone). Input bo tròn, focus ring teal |
| `TC_PROF_UI_005` | `US-PROF-01` | Profile - Address | Profile: Section 'Địa chỉ giao hàng (tối đa 5)' hiển thị | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /profile<br>2. Scroll đến section địa chỉ | Heading có icon MapPin + text 'Địa chỉ giao hàng' + '(tối đa 5)'. AddressPicker component render bên dưới |
| `TC_PROF_UI_006` | `US-PROF-01` | Profile - Security | Profile: Section Bảo mật hiển thị | 🎨 UI/UX | **🟢 P2** | 1. Truy cập /profile<br>2. Scroll đến section bảo mật | Card có icon Shield + text 'Bảo mật'. Nút 'Thay đổi' mật khẩu |
| `TC_PROF_UI_007` | `US-PROF-01` | Profile - Join Date | Profile: Ngày tham gia hiển thị đúng format | 🎨 UI/UX | **🟢 P2** | 1. Truy cập /profile | Text 'Tham gia từ [ngày]' format vi-VN (tháng/năm), icon CalendarDays |"""

PROFILE_FUNC = """| `TC_PROF_F_001` | `US-PROF-02` | Profile - Save | Profile: Lưu thay đổi thành công | ✅ Positive | **🔴 P0** | 1. Truy cập /profile<br>2. Sửa tên + phone<br>3. Click 'Lưu thay đổi' | Nút chuyển thành 'Đã lưu!' (check icon, bg green). Data lưu vào localStorage. customer_token sync tên mới |
| `TC_PROF_F_002` | `US-PROF-02` | Profile - Avatar Upload | Profile: Upload avatar mới | ✅ Positive | **🟠 P1** | 1. Click avatar hoặc camera icon<br>2. Chọn file ảnh | Ảnh hiển thị ngay (createObjectURL). Avatar thay đổi từ chữ cái sang ảnh |
| `TC_PROF_F_003` | `US-PROF-02` | Profile - Back to Studio | Profile: Nút 'Quay lại Studio' hoạt động | ✅ Positive | **🟠 P1** | 1. Click 'Quay lại Studio' | Redirect về /studio |
| `TC_PROF_F_004` | `US-PROF-02` | Profile - Autofill Token | Profile: Auto-fill từ customer_token | ✅ Positive | **🟠 P1** | 1. Đăng nhập via Google<br>2. Vào /profile | Tên + email auto-fill từ customer_token. Không ghi đè data đã lưu trước |
| `TC_PROF_F_005` | `US-PROF-02` | Profile - Stats Count | Profile: Stats đếm đúng | ✅ Positive | **🟢 P2** | 1. Truy cập /profile | Credits = 12 (default), totalOrders = 0, totalDesigns = 0 hoặc giá trị thực từ localStorage |"""

PROFILE_VALID = """| `TC_PROF_V_001` | `US-PROF-03` | Profile - Empty Name | Profile: Lưu với tên rỗng | ⚠️ Negative | **🟠 P1** | 1. Xóa hết tên<br>2. Click Lưu | Cho phép lưu (no validation on name) — data lưu với name rỗng |
| `TC_PROF_V_002` | `US-PROF-03` | Profile - Invalid Email | Profile: Email format sai | ⚠️ Negative | **🟢 P2** | 1. Nhập email không hợp lệ 'abc@@'<br>2. Click Lưu | Browser validation type='email' ngăn. Hoặc data lưu as-is |
| `TC_PROF_V_003` | `US-PROF-03` | Profile - No Token | Profile: Truy cập khi chưa đăng nhập | ⚠️ Negative | **🟠 P1** | 1. Xóa customer_token<br>2. Truy cập /profile | Hiển thị DEFAULT_PROFILE (tên rỗng, avatar '?', credits 12) |"""

PROFILE_SEC = """| `TC_PROF_S_001` | `US-PROF-04` | Profile - XSS Name | Profile: XSS injection qua name field | 🔒 Security | **🔴 P0** | 1. Nhập '<script>alert(1)</script>' vào tên<br>2. Lưu | Không execute script. Text render as-is trong React |
| `TC_PROF_S_002` | `US-PROF-04` | Profile - LocalStorage Tamper | Profile: Sửa localStorage trực tiếp | 🔒 Security | **🟠 P1** | 1. Sửa user_profile trong DevTools<br>2. Refresh | App handle JSON.parse error gracefully, fallback DEFAULT_PROFILE |"""

# ─── 3. ADDRESS PICKER TCs → append to LOGIN + THANH TOÁN ─────

ADDR_UI = """| `TC_ADDR_UI_001` | `US-ADDR-01` | Address Picker - Card | AddressPicker: Card hiển thị tên + SĐT + label + địa chỉ | 🎨 UI/UX | **🟠 P1** | 1. Mở Profile hoặc Checkout<br>2. Quan sát address cards | Card có radio circle, tên bold, SĐT, label tag (Nhà/Công ty), địa chỉ full. Border teal khi selected |
| `TC_ADDR_UI_002` | `US-ADDR-01` | Address Picker - Default | AddressPicker: Badge 'Mặc định' hiển thị | 🎨 UI/UX | **🟠 P1** | 1. Quan sát address card có isDefault=true | Badge teal '⭐ Mặc định' hiển thị. Không có nút Star vì đã là default |
| `TC_ADDR_UI_003` | `US-ADDR-01` | Address Picker - Actions | AddressPicker: Nút Star/Edit/Delete hiển thị | 🎨 UI/UX | **🟢 P2** | 1. Quan sát hàng actions | Star (đặt mặc định), Pencil (sửa), Trash2 (xóa). Nút xóa ẩn khi chỉ còn 1 địa chỉ |
| `TC_ADDR_UI_004` | `US-ADDR-01` | Address Picker - Add Button | AddressPicker: Nút 'Thêm địa chỉ mới' hiển thị | 🎨 UI/UX | **🟢 P2** | 1. Quan sát bên dưới cards | Nút border dashed 'Thêm địa chỉ mới (N/5)'. Ẩn khi đã 5 địa chỉ |
| `TC_ADDR_UI_005` | `US-ADDR-01` | Address Picker - Form | AddressPicker: Form thêm/sửa hiển thị inline | 🎨 UI/UX | **🟠 P1** | 1. Click 'Thêm địa chỉ mới'<br>2. Quan sát form | Form inline: Label (Nhà/Công ty/Khác buttons), Họ tên*, SĐT*, Email, 3 dropdowns Tỉnh/Quận/Phường, Địa chỉ chi tiết*, nút Lưu + Hủy |"""

ADDR_FUNC = """| `TC_ADDR_F_001` | `US-ADDR-02` | Address Picker - Add | AddressPicker: Thêm địa chỉ mới | ✅ Positive | **🔴 P0** | 1. Click 'Thêm địa chỉ mới'<br>2. Điền form<br>3. Click 'Lưu địa chỉ' | Địa chỉ mới xuất hiện trong danh sách. Auto-select. Lưu vào localStorage |
| `TC_ADDR_F_002` | `US-ADDR-02` | Address Picker - Edit | AddressPicker: Sửa địa chỉ | ✅ Positive | **🔴 P0** | 1. Click icon Pencil<br>2. Sửa thông tin<br>3. Click 'Cập nhật' | Thông tin cập nhật trên card. Title form là 'Sửa địa chỉ'. localStorage sync |
| `TC_ADDR_F_003` | `US-ADDR-02` | Address Picker - Delete | AddressPicker: Xóa địa chỉ | ✅ Positive | **🟠 P1** | 1. Click icon Trash2 | Địa chỉ biến mất. Nếu xóa default → first remaining becomes default. Auto-select first |
| `TC_ADDR_F_004` | `US-ADDR-02` | Address Picker - Set Default | AddressPicker: Đặt mặc định | ✅ Positive | **🟠 P1** | 1. Click icon Star trên non-default card | Badge '⭐ Mặc định' chuyển sang card mới. Old card mất badge. localStorage sync |
| `TC_ADDR_F_005` | `US-ADDR-02` | Address Picker - Select | AddressPicker: Chọn địa chỉ | ✅ Positive | **🔴 P0** | 1. Click vào card khác | Border teal chuyển sang card clicked. Radio dot filled. onSelect callback fired |
| `TC_ADDR_F_006` | `US-ADDR-02` | Address Picker - Label | AddressPicker: Chọn label tag | ✅ Positive | **🟢 P2** | 1. Mở form thêm<br>2. Click 'Công ty' | Button 'Công ty' highlight teal border. Label lưu vào địa chỉ |
| `TC_ADDR_F_007` | `US-ADDR-02` | Address Picker - Seed Data | AddressPicker: Seed data lần đầu | ✅ Positive | **🟢 P2** | 1. Xóa tryonic_addresses từ localStorage<br>2. Refresh | 2 addresses mẫu xuất hiện: 'Nhà' (default) + 'Công ty'. localStorage ghi SEED_ADDRESSES |"""

ADDR_VALID = """| `TC_ADDR_V_001` | `US-ADDR-03` | Address Picker - Required | AddressPicker: Submit form thiếu field bắt buộc | ⚠️ Negative | **🔴 P0** | 1. Click 'Thêm địa chỉ mới'<br>2. Để trống Họ tên<br>3. Click 'Lưu' | Error 'Bắt buộc' hiển thị dưới field Họ tên. Không lưu |
| `TC_ADDR_V_002` | `US-ADDR-03` | Address Picker - Max 5 | AddressPicker: Thêm quá 5 địa chỉ | ✅ Boundary | **🟠 P1** | 1. Thêm đến 5 địa chỉ<br>2. Quan sát nút thêm | Nút 'Thêm địa chỉ mới' biến mất khi đủ 5 (MAX_ADDRESSES) |
| `TC_ADDR_V_003` | `US-ADDR-03` | Address Picker - Delete Last | AddressPicker: Xóa khi chỉ còn 1 | ⚠️ Negative | **🟠 P1** | 1. Xóa đến còn 1 địa chỉ<br>2. Quan sát nút Trash | Nút Trash2 ẩn đi (addresses.length > 1 check). Không cho xóa hết |"""

# ─── 4. CHECKOUT PAGE UPGRADE TCs → THANH TOÁN ─────

CHECKOUT_FUNC = """| `TC_CK_F_ADDR_001` | `US-CK-ADDR` | Checkout - AddressPicker | Checkout: Chọn địa chỉ từ AddressPicker | ✅ Positive | **🔴 P0** | 1. Vào checkout<br>2. Chọn địa chỉ saved | AddressPicker render trong section 'Địa chỉ nhận hàng'. Chọn = form valid. Nút thanh toán enabled |
| `TC_CK_F_ADDR_002` | `US-CK-ADDR` | Checkout - Flash Discount | Checkout: Flash discount -20k auto-apply | ✅ Positive | **🟠 P1** | 1. Vào checkout<br>2. Quan sát pricing | Line 'Ưu đãi Freeship + Giảm 20k' hiển thị. Shipping fee gạch ngang. −50,000đ (30k ship + 20k flash) |
| `TC_CK_F_ADDR_003` | `US-CK-ADDR` | Checkout - Promo on Checkout | Checkout: Nhập mã khuyến mại trên checkout | ✅ Positive | **🟠 P1** | 1. Click 'Nhập mã khuyến mại'<br>2. Nhập 'TRYONIC10'<br>3. Click 'Áp dụng' | Mã applied: -10% tổng. Line hiển thị 'Mã TRYONIC10 (−10%)'. Có nút X để xóa |
| `TC_CK_F_ADDR_004` | `US-CK-ADDR` | Checkout - Savings Compare | Checkout: So sánh tiết kiệm vs Local Brand | ✅ Positive | **🟢 P2** | 1. Scroll đến trust section | Hiển thị 'Sản phẩm tương đương tại Local Brand: ~350,000₫' + PiggyBank icon 'Tiết kiệm ~151k' |"""

CHECKOUT_VALID = """| `TC_CK_V_ADDR_001` | `US-CK-ADDR` | Checkout - No Address | Checkout: Submit khi chưa chọn địa chỉ | ⚠️ Negative | **🔴 P0** | 1. Vào checkout<br>2. Không chọn địa chỉ nào<br>3. Click 'Thanh toán' | Scroll đến section-shipping. Nút disabled (gray) khi isFormValid=false |
| `TC_CK_V_ADDR_002` | `US-CK-ADDR` | Checkout - Invalid Promo | Checkout: Nhập mã khuyến mại sai | ⚠️ Negative | **🟠 P1** | 1. Click 'Nhập mã khuyến mại'<br>2. Nhập 'INVALID'<br>3. Click 'Áp dụng' | Error đỏ 'Mã không hợp lệ'. Không áp dụng giảm giá |"""

# ─── 5. TOPBAR PROFILE LINK → DESIGN STUDIO ─────

TOPBAR_FUNC = """| `TC_DS_F_PROF_001` | `US-TB-PROF` | DS - User Menu | TopBar: Link 'Hồ sơ cá nhân' trong user dropdown | ✅ Positive | **🟠 P1** | 1. Đăng nhập<br>2. Hover user avatar dropdown | Menu item 'Hồ sơ cá nhân' (UserCircle icon) hiển thị. Link href='/profile' |
| `TC_DS_F_PROF_002` | `US-TB-PROF` | DS - User Menu | TopBar: Click 'Hồ sơ cá nhân' navigate đúng | ✅ Positive | **🟠 P1** | 1. Click 'Hồ sơ cá nhân' | Navigate đến /profile page. Profile page load thành công |"""

# ─── 6. ORDER MODAL selectedSize → ĐẶT HÀNG ─────

ORDER_FUNC = """| `TC_ORD_F_SIZE_001` | `US-ORD-SIZE` | DS - OrderModal | OrderModal: Truyền selectedSize prop | ✅ Positive | **🟢 P2** | 1. Chọn size trên canvas<br>2. Mở OrderModal | Size đã chọn trước đó auto-select trong OrderTab |"""

# ─── 7. CHECKOUT MODAL 3-STEP TCs → THANH TOÁN ─────

CKMODAL_UI = """| `TC_CKM_UI_001` | `US-CKM-01` | Checkout Modal - Header | CheckoutModal: Step indicator 1/2 hiển thị | 🎨 UI/UX | **🟠 P1** | 1. Mở CheckoutModal | Header: progress dots (active bar teal), title 'Bước 1/2 — Thông tin nhận hàng'. Nút X đóng |
| `TC_CKM_UI_002` | `US-CKM-01` | Checkout Modal - Drawer | CheckoutModal: Drawer slide-in từ phải | 🎨 UI/UX | **🟠 P1** | 1. Mở CheckoutModal | Drawer 480px max-width, slide từ phải (slideInRight animation). Backdrop blur |"""

CKMODAL_FUNC = """| `TC_CKM_F_001` | `US-CKM-02` | Checkout Modal - Step 1 | CheckoutModal: Step 1 Shipping + Auth | ✅ Positive | **🔴 P0** | 1. Mở CheckoutModal<br>2. Điền form shipping | Auth banner với Facebook/Google/Email. Form: Họ tên*, SĐT*, Email, Tỉnh/Quận/Phường, Địa chỉ*. 'Tiếp tục →' enabled khi valid |
| `TC_CKM_F_002` | `US-CKM-02` | Checkout Modal - Auth Login | CheckoutModal: Login auto-fill form | ✅ Positive | **🟠 P1** | 1. Click Facebook hoặc Google | Mock login → auto-fill tất cả fields. Badge xanh 'Đã đăng nhập'. Auth banner biến mất |
| `TC_CKM_F_003` | `US-CKM-02` | Checkout Modal - Skip Auth | CheckoutModal: Bỏ qua đăng nhập | ✅ Positive | **🟠 P1** | 1. Click 'Tiếp tục không cần tài khoản →' | Auth banner biến mất. Form vẫn enable để điền manual |
| `TC_CKM_F_004` | `US-CKM-02` | Checkout Modal - Step 2 | CheckoutModal: Step 2 Confirm + Payment | ✅ Positive | **🔴 P0** | 1. Điền form → Click 'Tiếp tục'<br>2. Xem Step 2 | CountdownBanner 15:00. Shipping summary. Order items + sizes. Pricing breakdown. Trust badges (Đổi size 7 ngày, BH 14 ngày). Cost bars. MoMo payment |
| `TC_CKM_F_005` | `US-CKM-02` | Checkout Modal - Submit | CheckoutModal: Thanh toán thành công | ✅ Positive | **🔴 P0** | 1. Step 2 → Click 'Thanh toán' | Processing spinner 1.5s. Step 3: Check icon, 'Đặt hàng thành công!', order code #TRY-XXXXXX, +10 Bonus Credits celebration card |
| `TC_CKM_F_006` | `US-CKM-02` | Checkout Modal - Bonus Credits | CheckoutModal: +10 Bonus Credits celebration | ✅ Positive | **🟠 P1** | 1. Sau khi thanh toán thành công | Card amber gradient: Sparkles icon, '+10 Bonus Credits'. Text: 'Credits này không bị reset hàng ngày'. Button 'Dùng ngay tạo AI Artwork'. localStorage credit updated |
| `TC_CKM_F_007` | `US-CKM-02` | Checkout Modal - Back Step | CheckoutModal: Nút '← Quay lại' giữa steps | ✅ Positive | **🟠 P1** | 1. Step 2 → Click '← Quay lại' | Quay về Step 1, form data giữ nguyên |"""

CKMODAL_VALID = """| `TC_CKM_V_001` | `US-CKM-03` | Checkout Modal - Invalid Step1 | CheckoutModal: 'Tiếp tục' khi form empty | ⚠️ Negative | **🔴 P0** | 1. Không điền gì<br>2. Click 'Tiếp tục →' | Nút disabled (bg-gray-300, cursor-not-allowed). Không chuyển step |
| `TC_CKM_V_002` | `US-CKM-03` | Checkout Modal - Countdown Zero | CheckoutModal: Countdown hết giờ | ✅ Boundary | **🟢 P2** | 1. Chờ countdown về 0:00 | Banner biến mất (seconds <= 0 return null). Ưu đãi hết hạn |"""

# ─── Insert TCs into correct positions ───

# Helper: find end of category within a feature
def find_category_end(content, feature, category):
    """Find the line position after last TC in feature>category."""
    feat_start = content.find(f"## 🚀 Feature: {feature}")
    if feat_start == -1:
        return -1
    
    cat_marker = f"### 📌 {category}"
    cat_pos = content.find(cat_marker, feat_start)
    if cat_pos == -1:
        return -1
    
    # Find next ### or ## after this category
    next_section = content.find("\n### ", cat_pos + len(cat_marker))
    next_feature = content.find("\n## ", cat_pos + len(cat_marker))
    
    if next_section == -1: next_section = len(content)
    if next_feature == -1: next_feature = len(content)
    
    end_pos = min(next_section, next_feature)
    
    # Find last TC row before end
    last_tc = content.rfind("\n| `TC_", cat_pos, end_pos)
    if last_tc == -1:
        return cat_pos + len(cat_marker) + 1
    
    # Find end of that line
    line_end = content.find("\n", last_tc + 1)
    return line_end

# Insert Profile TCs into LOGIN
for category, tcs in [
    ("UI/UX", PROFILE_UI),
    ("Functional", PROFILE_FUNC),
    ("Validation", PROFILE_VALID),
    ("Security", PROFILE_SEC),
]:
    pos = find_category_end(content, "LOGIN", category)
    if pos != -1:
        content = content[:pos] + "\n" + tcs.strip() + content[pos:]

# Insert Address TCs into LOGIN (UI/UX, Functional, Validation)
for category, tcs in [
    ("UI/UX", ADDR_UI),
    ("Functional", ADDR_FUNC),
    ("Validation", ADDR_VALID),
]:
    pos = find_category_end(content, "LOGIN", category)
    if pos != -1:
        content = content[:pos] + "\n" + tcs.strip() + content[pos:]

# Insert Checkout upgrade TCs into THANH TOÁN
for category, tcs in [
    ("Functional", CHECKOUT_FUNC),
    ("Validation", CHECKOUT_VALID),
]:
    pos = find_category_end(content, "THANH TOÁN", category)
    if pos != -1:
        content = content[:pos] + "\n" + tcs.strip() + content[pos:]

# Insert CheckoutModal TCs into THANH TOÁN
for category, tcs in [
    ("UI/UX", CKMODAL_UI),
    ("Functional", CKMODAL_FUNC),
    ("Validation", CKMODAL_VALID),
]:
    pos = find_category_end(content, "THANH TOÁN", category)
    if pos != -1:
        content = content[:pos] + "\n" + tcs.strip() + content[pos:]

# Insert TopBar profile link into DESIGN STUDIO > Functional
pos = find_category_end(content, "DESIGN STUDIO", "Functional")
if pos != -1:
    content = content[:pos] + "\n" + TOPBAR_FUNC.strip() + content[pos:]

# Insert OrderModal selectedSize into ĐẶT HÀNG > Functional
pos = find_category_end(content, "ĐẶT HÀNG", "Functional")
if pos != -1:
    content = content[:pos] + "\n" + ORDER_FUNC.strip() + content[pos:]

# ─── Write output ───
with open(DST, "w", encoding="utf-8") as f:
    f.write(content)

# ─── Stats ───
lines = content.split("\n")
tc_count = sum(1 for line in lines if "`TC_" in line and line.strip().startswith("|"))
features = [line for line in lines if line.strip().startswith("## 🚀")]

print(f"✅ Created: {DST.split(chr(92))[-1]}")
print(f"📊 Total lines: {len(lines)}")
print(f"📊 Total TCs: {tc_count}")
print(f"📊 Features ({len(features)}):")
for f_name in features:
    print(f"   {f_name.strip()}")
