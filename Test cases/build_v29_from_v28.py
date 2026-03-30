"""
Build test_cases_suite_v29.md from v28:
1. Update header version
2. Update HOME section: AI Chat Hero UI (subtitle, style tags, input, greeting, action cards)
3. Update DESIGN STUDIO section: sidebar icons (Thư Viện, Thử Đồ)
4. Update DESIGN STUDIO: StatusBar pricing breakdown  
5. Append NEW: MY ORDERS (Đơn hàng của tôi) — full page with search, filter, cancel, detail
6. Append NEW: FOOTER — 4 sections + policy links
7. Append NEW: POLICY PAGES — 5 policy pages
"""
import re

SRC = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v28.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# ─── 1. Update header ────────────────────────────────────────────────
content = content.replace(
    "# POD T-Shirt Platform — Test Case Suite v28 (Updated + New Screens)",
    "# POD T-Shirt Platform — Test Case Suite v29 (Source Code Sync 2026-03-26)"
)
content = content.replace(
    "> **Version:** v28 — Updated Headlines + Bổ sung màn hình thiếu (Merged: 10 Sheets)",
    "> **Version:** v29 — Sync source code: AI Chat Hero, My Orders, Footer, Policy Pages, Library Flyout, OrderModal, StatusBar (Merged: 14 Sheets)"
)

# ─── 2. HOME: Update subtitle (TC_HOME_UI_007) ──────────────────────
content = content.replace(
    "Subtitle hiển thị mô tả ngắn gọn về dịch vụ thiết kế áo AI. Text xám, centered. Font size ~16-18px. (Content có thể thay đổi theo campaign)",
    "Subtitle hiển thị: 'Kể mình nghe ý tưởng của bạn — mình biến nó thành artwork trên áo trong vài giây!'. Text xám, centered. Font size ~16-18px"
)

# ─── 3. HOME: Update AI Input placeholder (TC_HOME_UI_008) ──────────
content = content.replace(
    "Placeholder hiển thị: 'Mô tả áo thun bạn muốn... VD: Áo minimalist hoa sak...'. Icon ảnh (image) ở bên trái input. Input có bo tròn lớn (~16px), shadow nhẹ",
    "Placeholder hiển thị: 'Bạn muốn kể gì trên áo?'. Input dạng chat conversational, bo tròn. Animated gradient border (teal-cyan). Có nút đính kèm ảnh tham khảo bên trái, nút 'Tạo ngay' bên phải"
)

# ─── 4. HOME: Update Generate button (TC_HOME_UI_009) ────────────────
content = content.replace(
    "Nút hiển thị: text 'Generate' + icon sparkle ✨. Background tím gradient, text trắng, bo tròn. Nút nằm liền bên phải input",
    "Nút hiển thị: text 'Tạo ngay' + icon Wand2 ✨. Background teal gradient (#0D9488), text trắng, bo tròn. Nút nằm bên phải input"
)

# ─── 5. HOME: Update 6 Style Tags (TC_HOME_UI_010) ───────────────────
content = content.replace(
    "Hiển thị đầy đủ 6 tags: 'Minimalist', 'Streetwear', 'Anime', 'Vintage', 'Y2K', 'Abstract Art'. Mỗi tag có icon riêng, bo tròn full, border 1px. Font size ~14px",
    "Hiển thị đầy đủ 6 tags: 'Tối giản', 'Streetwear', 'Anime', 'Retro', 'Y2K vibes', 'Nghệ thuật'. Mỗi tag có emoji riêng (🎯🔥🌸🎸✨🎨), bo tròn full, gradient border khi selected. Font size ~14px"
)

# ─── 6. HOME: Update Style Tag titles in Functional TCs ──────────────
content = content.replace(
    "Click tag 'Minimalist'",
    "Click tag 'Tối giản'"
)
content = content.replace(
    "Tag 'Minimalist' highlight",
    "Tag 'Tối giản' highlight"
)
content = content.replace(
    "Click tag 'Vintage' và verify style được áp dụng",
    "Click tag 'Retro' và verify style được áp dụng"
)
content = content.replace(
    "Click tag 'Vintage' (📷 icon)",
    "Click tag 'Retro' (🎸 icon)"
)
content = content.replace(
    "Tag 'Vintage' highlight",
    "Tag 'Retro' highlight"
)
content = content.replace(
    "Click tag 'Abstract Art' và verify style được áp dụng",
    "Click tag 'Nghệ thuật' và verify style được áp dụng"
)
content = content.replace(
    "Click tag 'Abstract Art' (🖌️ icon)",
    "Click tag 'Nghệ thuật' (🎨 icon)"
)
content = content.replace(
    "Tag 'Abstract Art' highlight",
    "Tag 'Nghệ thuật' highlight"
)
content = content.replace(
    "Click tag 'Y2K' và verify style được áp dụng",
    "Click tag 'Y2K vibes' và verify style được áp dụng"
)
content = content.replace(
    "Click tag 'Y2K' (✨ icon)",
    "Click tag 'Y2K vibes' (✨ icon)"
)
content = content.replace(
    "Tag 'Y2K' highlight",
    "Tag 'Y2K vibes' highlight"
)

# ─── 7. DS: Update sidebar tools list (TC_DS_UI_003) ─────────────────
content = content.replace(
    "Hiển thị 6 công cụ theo thứ tự: Hoàn Tác, Làm Lại, Mặt Sau, Thu Phóng, Thử Đồ với AI, Chia Sẻ. Mỗi công cụ có icon + text label",
    "Hiển thị 7 công cụ theo thứ tự: Hoàn Tác, Làm Lại, Mặt Sau, Thu Phóng, Thư Viện, Thử Đồ với AI, Chia Sẻ. Mỗi công cụ có icon + text label. 'Thử Đồ với AI' disabled khi chưa có artwork"
)

# ─── 8. DS: Update Bottom Bar/StatusBar (TC_DS_UI_008) ────────────────
content = content.replace(
    "Hiển thị: 'Áo Thun Cotton Gildan 5000', Màu: Trắng (toggle tròn), Size: L, 'Tạm tính: 150.000đ', text 'Giá chưa bao gồm phí in', nút 'Đặt hàng'",
    "Hiển thị: Tên SP + Màu + Size + print info. Link 'Đổi sản phẩm' → mở ProductSelectorModal. 'Tạm tính: 150.000đ' + popover chi tiết giá (Giá áo 120K, Phí in DTG 30K, Phí thiết kế 5K). Nút 'Đặt hàng' → mở OrderModal. Desktop only (hidden lg:flex)"
)

# ─── 9. Append NEW feature sections ─────────────────────────────────
NEW_SECTIONS = r"""

---

## 🚀 Feature: MY ORDERS (Đơn hàng của tôi)

### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_MO_UI_001` | `US-26` | My Orders - Header | MH My Orders: Header hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Đăng nhập → Click User avatar → 'Đơn hàng của tôi'<br>2. Quan sát header | Header hiển thị: nút '← Studio' quay về studio, tiêu đề 'Đơn hàng của tôi' + count badge (số đơn hàng) |
| `TC_MO_UI_002` | `US-26` | My Orders - Search | Ô tìm kiếm đơn hàng hiển thị | 🎨 UI/UX | **🟠 P1** | 1. Mở My Orders<br>2. Quan sát ô tìm kiếm | Placeholder: 'Tìm theo mã đơn hoặc tên sản phẩm...'. Icon search bên trái. Bo tròn, full-width |
| `TC_MO_UI_003` | `US-26` | My Orders - Status Tabs | 7 status tabs hiển thị đầy đủ | 🎨 UI/UX | **🔴 P0** | 1. Mở My Orders<br>2. Quan sát thanh tab trạng thái | 7 tabs: 'Tất cả', 'Chờ xác nhận', 'Đã xác nhận', 'Đang in', 'Đang giao', 'Đã giao', 'Đã hủy'. Mỗi tab có count badge. Tab active có highlight teal |
| `TC_MO_UI_004` | `US-26` | My Orders - Card | Order card hiển thị thông tin | 🎨 UI/UX | **🟠 P1** | 1. Mở My Orders (có ≥1 đơn)<br>2. Quan sát card đơn hàng | Card hiển thị: mã đơn (#TRY-XXX), ngày đặt, status badge (màu theo trạng thái), preview items (max 2), tổng tiền. Có nút 'Chi tiết' |
| `TC_MO_UI_005` | `US-26` | My Orders - Empty | Empty state khi chưa có đơn hàng | 🎨 UI/UX | **🟢 P2** | 1. Mở My Orders (user mới, chưa đặt đơn)<br>2. Quan sát nội dung | Hiển thị: 'Chưa có đơn hàng nào' + nút CTA 'Thiết kế ngay' → navigate về Design Studio |
| `TC_MO_UI_006` | `US-26` | My Orders - Loading | Loading state (skeleton) | 🎨 UI/UX | **🟢 P2** | 1. Truy cập My Orders (mạng chậm)<br>2. Quan sát loading | Skeleton animation (pulse blocks) thay cho cards đơn hàng. Không blank screen |
| `TC_MO_UI_860` | `Global` | Responsive & Zoom | MH My Orders: Browser Zoom (50%-200%) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập My Orders<br>2. Zoom In 200% / Zoom Out 50% | Layout giữ nguyên. Tabs wrap xuống hàng nếu cần. Cards vẫn hiển thị đầy đủ |
| `TC_MO_UI_861` | `Global` | Responsive (iPhone) | MH My Orders: Responsive iPhone (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập My Orders trên iPhone Portrait | Tabs scroll ngang hoặc wrap. Cards full-width stacking. Nút Chi tiết dễ tap (≥44px) |
| `TC_MO_UI_862` | `Global` | Responsive (Android) | MH My Orders: Responsive Android Phone (Portrait) | 🎨 UI/UX | **🔴 P0** | 1. Truy cập My Orders trên Android Portrait | Tương tự iPhone. Không thanh cuộn ngang thừa |
| `TC_MO_UI_863` | `Global` | Responsive (iPad) | MH My Orders: Responsive iPad (Portrait) | 🎨 UI/UX | **🟠 P1** | 1. Truy cập My Orders trên iPad Portrait | Cards có thể 2 cột hoặc 1 cột hợp lý. Tabs hiển thị đủ trên 1 hàng |
| `TC_MO_UI_864` | `Global` | Responsive (Android Tablet) | MH My Orders: Responsive Android Tablet | 🎨 UI/UX | **🟠 P1** | 1. Truy cập My Orders trên Tablet Android | Tương tự iPad |
| `TC_MO_UI_865` | `Global` | Responsive (Landscape) | MH My Orders: Responsive Landscape | 🎨 UI/UX | **🔴 P0** | 1. Xoay ngang thiết bị | UI tự sắp xếp phù hợp. Tabs vẫn hiển thị |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_MO_F_001` | `US-26` | My Orders - Search | Tìm kiếm theo mã đơn | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Nhập mã đơn 'TRY-001' vào ô tìm kiếm | Danh sách filter hiển thị chỉ đơn hàng có mã TRY-001. Realtime filtering khi gõ |
| `TC_MO_F_002` | `US-26` | My Orders - Search | Tìm kiếm theo tên sản phẩm | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Nhập 'Premium Cotton' vào ô tìm kiếm | Hiển thị đơn hàng chứa SP 'Premium Cotton' |
| `TC_MO_F_003` | `US-26` | My Orders - Filter | Click tab 'Chờ xác nhận' | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Click tab 'Chờ xác nhận' | Chỉ hiển thị đơn hàng có trạng thái 'Chờ xác nhận'. Count badge cập nhật. Tab active highlight |
| `TC_MO_F_004` | `US-26` | My Orders - Filter | Click tab 'Đã giao' | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Click tab 'Đã giao' | Chỉ hiển thị đơn hàng đã giao. Count badge đúng |
| `TC_MO_F_005` | `US-26` | My Orders - Filter | Click tab 'Tất cả' hiển thị toàn bộ | ✅ Positive | **🟢 P2** | 1. Đang ở tab filter khác<br>2. Click 'Tất cả' | Hiển thị toàn bộ đơn hàng. Count badge = tổng đơn |
| `TC_MO_F_006` | `US-27` | My Orders - Detail | Click 'Chi tiết' mở CustomerOrderDetailModal | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Click nút 'Chi tiết' trên 1 đơn hàng | Mở modal chi tiết: mã đơn, trạng thái, timeline, danh sách items (ảnh, tên, màu, size, qty, giá), thông tin giao hàng. Có nút đóng (X) |
| `TC_MO_F_007` | `US-28` | My Orders - Cancel | Click 'Hủy đơn' khi trạng thái 'Chờ xác nhận' | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Tìm đơn trạng thái 'Chờ xác nhận'<br>3. Click 'Hủy đơn' | Hiển thị confirm dialog: 'Bạn có chắc muốn hủy đơn hàng #TRY-XXX?'. Xác nhận → đơn chuyển sang 'Đã hủy'. Toast 'Đã hủy đơn hàng' |
| `TC_MO_F_008` | `US-26` | My Orders - Navigate | Click '← Studio' quay về Design Studio | ✅ Positive | **🟢 P2** | 1. Mở My Orders<br>2. Click nút '← Studio' trên header | Navigate về /studio. Design Studio hiển thị đầy đủ |

### 📌 Validation

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_MO_V_001` | `US-26` | My Orders - Search | Tìm kiếm không có kết quả | ⚠️ Negative | **🟢 P2** | 1. Mở My Orders<br>2. Nhập 'xyznotexist123' | Hiển thị: 'Không tìm thấy đơn hàng'. Không crash |
| `TC_MO_V_002` | `US-28` | My Orders - Cancel | Hủy đơn khi trạng thái 'Đang in' | ⚠️ Negative | **🟠 P1** | 1. Mở My Orders<br>2. Tìm đơn trạng thái 'Đang in' | Nút 'Hủy đơn' ẩn hoặc disabled. Không cho phép hủy đơn đang sản xuất |
| `TC_MO_V_003` | `US-28` | My Orders - Cancel | Hủy đơn khi trạng thái 'Đã giao' | ⚠️ Negative | **🟠 P1** | 1. Mở My Orders<br>2. Tìm đơn trạng thái 'Đã giao' | Nút 'Hủy đơn' ẩn. Không cho hủy đơn đã giao |

---

## 🚀 Feature: FOOTER

### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_FT_UI_001` | `US-HP-04` | Footer - Sản phẩm | Cột 'Sản phẩm' hiển thị 4 links | 🎨 UI/UX | **🟠 P1** | 1. Truy cập trang Home<br>2. Scroll xuống Footer<br>3. Quan sát cột 'Sản phẩm' | Heading 'SẢN PHẨM' (uppercase, trắng, bold). 4 links: 'Áo thun', 'Polo', 'Tạo AI Artwork', 'Thư viện mẫu'. Mỗi link hover → teal (#0D9488). Tất cả trỏ về /studio |
| `TC_FT_UI_002` | `US-HP-04` | Footer - Chính sách | Cột 'Chính sách' hiển thị 5 links | 🎨 UI/UX | **🟠 P1** | 1. Quan sát cột 'Chính sách' trong Footer | Heading 'CHÍNH SÁCH'. 5 links: 'Hướng dẫn mua hàng' → /pages/huong-dan-mua-hang, 'Chính sách thanh toán' → /pages/chinh-sach-thanh-toan, 'Chính sách vận chuyển' → /pages/chinh-sach-van-chuyen, 'Chính sách đổi trả' → /pages/chinh-sach-doi-tra, 'Bảo mật thông tin' → /pages/chinh-sach-bao-mat |
| `TC_FT_UI_003` | `US-HP-04` | Footer - Hỗ trợ | Cột 'Hỗ trợ' hiển thị 3 links | 🎨 UI/UX | **🟠 P1** | 1. Quan sát cột 'Hỗ trợ' trong Footer | Heading 'HỖ TRỢ'. 3 links: 'Theo dõi đơn hàng' → /studio/my-orders, 'Câu hỏi thường gặp' → #, 'Liên hệ CSKH' → # |
| `TC_FT_UI_004` | `US-HP-04` | Footer - Liên hệ | Cột 'Liên hệ' hiển thị 4 items | 🎨 UI/UX | **🟠 P1** | 1. Quan sát cột 'Liên hệ' trong Footer | Heading 'LIÊN HỆ'. 4 items với icon teal: 📞 '1900 xxxx', ✉️ 'support@tryonic.ai', 💬 'Zalo: Shop Tryonic', 📍 'TP. Hồ Chí Minh, Việt Nam' |
| `TC_FT_UI_005` | `US-HP-04` | Footer - Bottom | Bottom bar: Logo + copyright + policy links | 🎨 UI/UX | **🟠 P1** | 1. Quan sát bottom bar Footer | Hiển thị: Logo gradient teal 'T' + text 'Shop Tryonic', '© 2026 Shop Tryonic — Mọi quyền được bảo lưu.', 2 links: 'Bảo mật' → /pages/chinh-sach-bao-mat, 'Đổi trả' → /pages/chinh-sach-doi-tra |
| `TC_FT_UI_006` | `US-HP-04` | Footer - Layout | Footer responsive 4 cột grid | 🎨 UI/UX | **🟢 P2** | 1. Quan sát Footer trên desktop<br>2. Resize mobile | Desktop: 4 cột grid (md:grid-cols-4). Mobile: 2 cột (grid-cols-2). Background bg-slate-900, text gray-300 |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_FT_F_001` | `US-HP-04` | Footer - Navigate | Click link 'Chính sách thanh toán' | ✅ Positive | **🟠 P1** | 1. Scroll xuống Footer<br>2. Click 'Chính sách thanh toán' | Navigate đến /pages/chinh-sach-thanh-toan. Trang policy hiển thị đầy đủ |
| `TC_FT_F_002` | `US-HP-04` | Footer - Navigate | Click link 'Theo dõi đơn hàng' | ✅ Positive | **🟠 P1** | 1. Scroll xuống Footer<br>2. Click 'Theo dõi đơn hàng' | Navigate đến /studio/my-orders. Trang My Orders hiển thị |
| `TC_FT_F_003` | `US-HP-04` | Footer - Navigate | Click link 'Áo thun' trong cột Sản phẩm | ✅ Positive | **🟢 P2** | 1. Click 'Áo thun' trong Footer<br>2. Quan sát | Navigate đến /studio. Design Studio hiển thị |

---

## 🚀 Feature: POLICY PAGES (Chính sách)

### 📌 UI/UX

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_POL_UI_001` | `US-HP-04` | Policy - Hướng dẫn mua hàng | Trang hướng dẫn mua hàng hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /pages/huong-dan-mua-hang<br>2. Quan sát nội dung | Hiển thị: header với icon + tiêu đề 'Hướng dẫn mua hàng', nút back, 7 steps: Truy cập → Chọn SP → Tạo Artwork → Chỉnh sửa → Preview → Đặt hàng → Thanh toán. Footer 'Chính sách khác' grid hiển thị |
| `TC_POL_UI_002` | `US-HP-04` | Policy - Thanh toán | Trang chính sách thanh toán hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /pages/chinh-sach-thanh-toan<br>2. Quan sát nội dung | Hiển thị: phương thức MoMo only, thông tin SSL 256-bit, bảng phí giao hàng. Có link 'Chính sách khác' |
| `TC_POL_UI_003` | `US-HP-04` | Policy - Vận chuyển | Trang chính sách vận chuyển hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /pages/chinh-sach-van-chuyen<br>2. Quan sát nội dung | Hiển thị: Standard 5-7 ngày (miễn phí ≥500K), Express 2-3 ngày (30K). Bảng chi tiết phí |
| `TC_POL_UI_004` | `US-HP-04` | Policy - Đổi trả | Trang chính sách đổi trả hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /pages/chinh-sach-doi-tra<br>2. Quan sát nội dung | Hiển thị: thời hạn 7 ngày, điều kiện đổi trả, quy trình 3 bước. Có icon minh họa |
| `TC_POL_UI_005` | `US-HP-04` | Policy - Bảo mật | Trang bảo mật thông tin hiển thị đầy đủ | 🎨 UI/UX | **🟠 P1** | 1. Truy cập /pages/chinh-sach-bao-mat<br>2. Quan sát nội dung | Hiển thị: tuân thủ NĐ 13/2023, SSL encryption, bcrypt hashing, chính sách xử lý dữ liệu. Format các section rõ ràng |
| `TC_POL_UI_006` | `US-HP-04` | Policy - Layout | 'Chính sách khác' grid hiển thị trên mỗi trang | 🎨 UI/UX | **🟢 P2** | 1. Truy cập bất kỳ trang policy<br>2. Scroll xuống phần 'Chính sách khác' | Hiển thị grid các trang policy liên quan (trừ trang hiện tại). Mỗi card có icon + title. Click navigate đúng |

### 📌 Functional

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_POL_F_001` | `US-HP-04` | Policy - Navigate | Click 'Về trang chủ' | ✅ Positive | **🟢 P2** | 1. Mở bất kỳ trang policy<br>2. Click link 'Về trang chủ' | Navigate đến /home. Trang chủ hiển thị |
| `TC_POL_F_002` | `US-HP-04` | Policy - Navigate | Click card 'Chính sách khác' navigate đúng | ✅ Positive | **🟠 P1** | 1. Mở /pages/huong-dan-mua-hang<br>2. Click card 'Chính sách vận chuyển' trong 'Chính sách khác' | Navigate đến /pages/chinh-sach-van-chuyen. Trang hiển thị đúng |
| `TC_POL_F_003` | `US-HP-04` | Policy - Navigate | Click nút back trên header | ✅ Positive | **🟢 P2** | 1. Mở trang policy<br>2. Click nút ← (back) trên header | Quay về trang trước hoặc trang chủ |

### 📌 Validation

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_POL_V_001` | `US-HP-04` | Policy - Invalid | Truy cập slug không tồn tại | ⚠️ Negative | **🟠 P1** | 1. Truy cập /pages/slug-khong-ton-tai<br>2. Quan sát trang | Hiển thị error: 'Trang không tồn tại' với nút 'Về trang chủ'. Không crash, không blank |
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
