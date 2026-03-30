"""Restructure test_cases_suite.md: 24 features → 8 sheets + CMS separate."""
import re, os
from collections import OrderedDict

BASE = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases"
SRC = os.path.join(BASE, "test_cases_suite.md")

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── FEATURE MAPPING: old feature name → new sheet name ───
FEATURE_MAP = {
    "REGISTRATION": "LOGIN",
    "LOGIN": "LOGIN",
    "ACCOUNT": "LOGIN",
    "PROFILE": "LOGIN",
    "GUEST MODE": "LOGIN",
    
    "DESIGN STUDIO - Chung": "DESIGN STUDIO",
    "DESIGN STUDIO - Sản phẩm": "DESIGN STUDIO",
    "DESIGN STUDIO - Ảnh của bạn": "DESIGN STUDIO",
    "DESIGN STUDIO - Thư viện": "DESIGN STUDIO",
    "EDITOR": "DESIGN STUDIO",
    "GALLERY": "DESIGN STUDIO",
    "SMART FIT": "DESIGN STUDIO",
    
    "DESIGN STUDIO - Tạo ảnh AI": "AI GENERATE",
    "AI GEN": "AI GENERATE",
    "AI GENERATE": "AI GENERATE",
    "CREDITS": "AI GENERATE",
    
    "DESIGN STUDIO - Đặt hàng": "ĐẶT HÀNG",
    "CART": "ĐẶT HÀNG",
    "PRODUCT": "ĐẶT HÀNG",
    
    "CHECKOUT": "THANH TOÁN",
    "PAYMENT": "THANH TOÁN",
    
    "ORDER": "ORDER",
    
    "HOME PAGE": "HOME",
    
    "CMS": "CMS",
}

# Module prefix for clarity when merging
MODULE_PREFIX = {
    "REGISTRATION": "Đăng ký",
    "LOGIN": "Đăng nhập",
    "ACCOUNT": "Tài khoản",
    "PROFILE": "Hồ sơ",
    "GUEST MODE": "Guest",
    "DESIGN STUDIO - Chung": "DS Chung",
    "DESIGN STUDIO - Sản phẩm": "DS Sản phẩm",
    "DESIGN STUDIO - Ảnh của bạn": "DS Ảnh của bạn",
    "DESIGN STUDIO - Thư viện": "DS Thư viện",
    "EDITOR": "Editor",
    "GALLERY": "Gallery",
    "SMART FIT": "Smart Fit",
    "DESIGN STUDIO - Tạo ảnh AI": "Tạo ảnh AI",
    "AI GEN": "AI Gen",
    "AI GENERATE": "AI Generate",
    "CREDITS": "Credits",
    "DESIGN STUDIO - Đặt hàng": "Đặt hàng",
    "CART": "Giỏ hàng",
    "PRODUCT": "Sản phẩm",
    "CHECKOUT": "Checkout",
    "PAYMENT": "Thanh toán",
    "ORDER": "Đơn hàng",
    "HOME PAGE": "Home",
    "CMS": "CMS",
}

# Parse features and their TC blocks
features = OrderedDict()
lines = content.split('\n')

current_feature = None
current_category = None
header_line = None
buffer = []

def flush():
    global current_feature, current_category, header_line, buffer
    if current_feature and current_category:
        if current_feature not in features:
            features[current_feature] = OrderedDict()
        if current_category not in features[current_feature]:
            features[current_feature][current_category] = []
        features[current_feature][current_category].extend(buffer)
    buffer = []

for line in lines:
    stripped = line.strip()
    
    # Match feature header
    m = re.match(r'^## .+Feature:\s*(.+)$', stripped)
    if m:
        flush()
        current_feature = m.group(1).strip()
        current_category = None
        continue
    
    # Match category
    m2 = re.match(r'^###\s+📌\s+(.+)$', stripped)
    if m2:
        flush()
        current_category = m2.group(1).strip()
        continue
    
    # Match TC row (starts with |)
    if stripped.startswith('| `TC_') or stripped.startswith('|`TC_'):
        buffer.append(line)
    elif stripped.startswith('| TC_ID'):
        pass  # skip header
    elif stripped.startswith('|:---'):
        pass  # skip separator

flush()

# Print stats
total = 0
for feat, cats in features.items():
    fc = sum(len(tcs) for tcs in cats.values())
    total += fc
    new_sheet = FEATURE_MAP.get(feat, "UNKNOWN")
    print(f"  {feat} ({fc} TCs) → {new_sheet}")
print(f"\nTotal: {total} TCs")

# ─── BUILD NEW STRUCTURE ───
NEW_ORDER = ["HOME", "DESIGN STUDIO", "AI GENERATE", "ĐẶT HÀNG", "THANH TOÁN", "ORDER", "LOGIN", "E2E FLOW"]
CAT_ORDER = ["UI/UX", "Validation", "Functional", "Functional (Logic & Behavior)", "Security", "Performance"]

new_features = OrderedDict()
for ns in NEW_ORDER:
    new_features[ns] = OrderedDict()

cms_features = OrderedDict()
cms_features["CMS"] = OrderedDict()

for old_feat, cats in features.items():
    new_sheet = FEATURE_MAP.get(old_feat, "UNKNOWN")
    if new_sheet == "CMS":
        target = cms_features["CMS"]
    elif new_sheet == "UNKNOWN":
        print(f"  ⚠️ UNMAPPED: {old_feat}")
        continue
    else:
        target = new_features[new_sheet]
    
    prefix = MODULE_PREFIX.get(old_feat, old_feat)
    
    for cat, tcs in cats.items():
        if cat not in target:
            target[cat] = []
        
        # Update module column: prepend prefix if module is generic
        updated_tcs = []
        for tc_line in tcs:
            # Parse table columns: | TC_ID | Mapping | Module | Title | ...
            cols = tc_line.split('|')
            if len(cols) >= 5:
                module_col = cols[3].strip()
                # If module is generic (Panel, Canvas, Bottom Bar, etc), prepend prefix
                if module_col in ('Panel', 'Canvas', 'Bottom Bar', 'Page', 'Header', 'Form', 'Dialog', 'Modal'):
                    cols[3] = f' {prefix} - {module_col} '
                elif not module_col.startswith(prefix.split()[0]) and module_col not in ('Responsive & Zoom', 'Responsive (iPhone)', 'Responsive (Android)', 'Responsive (iPad)', 'Responsive (Android Tablet)', 'Responsive (Landscape)'):
                    # Keep specific modules like "Chọn sản phẩm", "Gợi ý size", "Cài đặt hình ảnh", etc
                    if new_sheet in ("DESIGN STUDIO", "AI GENERATE", "ĐẶT HÀNG", "LOGIN") and old_feat != list(FEATURE_MAP.keys())[list(FEATURE_MAP.values()).index(new_sheet)]:
                        # Module from a different old feature - add prefix
                        cols[3] = f' {prefix} - {module_col} '
                tc_line = '|'.join(cols)
            updated_tcs.append(tc_line)
        
        target[cat].extend(updated_tcs)

# ─── ADD E2E FLOW TCS ───
e2e_tcs = {
    "Functional (Logic & Behavior)": [
        "| `TC_E2E_001` | `E2E` | Full Flow | E2E: Đăng ký → Đăng nhập → Tạo thiết kế → Đặt hàng thành công | ✅ Positive | **🔴 P0** | 1. Truy cập vào trang <br>2. Click 'Đăng ký'<br>3. Nhập thông tin: Name: Test User, Email: e2e@test.com, Password: Test@123<br>4. Click 'Đăng ký'<br>5. Đăng nhập với email/password vừa tạo<br>6. Click 'Thiết kế ngay' → Design Studio<br>7. Tab 'TẠO ẢNH AI' → Nhập mô tả → Click 'Tạo Artwork Mới'<br>8. Tab 'SẢN PHẨM' → Chọn màu Đen, Size L<br>9. Tab 'ĐẶT HÀNG' → Click 'Mua ngay'<br>10. Điền thông tin giao hàng → Xác nhận đơn | Đơn hàng tạo thành công. Hiển thị mã đơn. Credits trừ đúng |",
        "| `TC_E2E_002` | `E2E` | Full Flow | E2E: Upload ảnh → In lên áo → Thêm vào giỏ → Thanh toán | ✅ Positive | **🔴 P0** | 1. Đăng nhập<br>2. Mở Design Studio<br>3. Tab 'ẢNH CỦA BẠN' → Upload ảnh PNG<br>4. Click ảnh → Apply lên canvas<br>5. Tab 'SẢN PHẨM' → Chọn áo Trắng, Size M<br>6. Tab 'ĐẶT HÀNG' → Click 'Thêm vào giỏ'<br>7. Mở Giỏ hàng → Click 'Thanh toán'<br>8. Điền thông tin → Xác nhận | Đơn hàng tạo thành công từ ảnh upload |",
        "| `TC_E2E_003` | `E2E` | Full Flow | E2E: Chọn template thư viện → Đặt hàng nhiều size | ✅ Positive | **🟠 P1** | 1. Đăng nhập → Design Studio<br>2. Tab 'THƯ VIỆN' → Chọn template<br>3. Tab 'SẢN PHẨM' → Chọn áo, màu<br>4. Tab 'ĐẶT HÀNG' → Thêm S x2, M x1, L x3<br>5. Click 'Mua ngay' → Thanh toán | Đơn hàng với 6 áo (3 sizes) tạo thành công. Tổng giá đúng |",
        "| `TC_E2E_004` | `E2E` | Full Flow | E2E: Guest → Thiết kế → Bắt đăng nhập → Hoàn tất đơn | ✅ Positive | **🟠 P1** | 1. Truy cập Guest (không đăng nhập)<br>2. Click 'Thiết kế ngay'<br>3. Tạo thiết kế trên canvas<br>4. Tab 'ĐẶT HÀNG' → Click 'Mua ngay'<br>5. Hệ thống yêu cầu đăng nhập → Đăng nhập<br>6. Quay lại flow đặt hàng → Hoàn tất | Thiết kế được giữ nguyên sau đăng nhập. Đơn hàng tạo thành công |",
        "| `TC_E2E_005` | `E2E` | Full Flow | E2E: Đăng nhập → Tạo thiết kế → Xem đơn hàng | ✅ Positive | **🟠 P1** | 1. Đăng nhập<br>2. Tạo thiết kế → Đặt hàng thành công<br>3. Vào Profile/Đơn hàng<br>4. Tìm đơn hàng vừa tạo<br>5. Click xem chi tiết | Đơn hàng hiển thị đúng: ảnh thiết kế, sản phẩm, size, số lượng, giá, trạng thái 'Đang xử lý' |",
        "| `TC_E2E_006` | `E2E` | AI Flow | E2E: Nhập prompt AI → Generate → Chỉnh sửa → Đổi style → Đặt hàng | ✅ Positive | **🔴 P0** | 1. Đăng nhập (12 credits)<br>2. Design Studio → Tab 'TẠO ẢNH AI'<br>3. Nhập mô tả: 'Rồng Việt Nam phong cách watercolor'<br>4. Chọn style 'Watercolor' → Click 'Tạo Artwork Mới'<br>5. Artwork hiện trên canvas → Drag/resize<br>6. Tab 'SẢN PHẨM' → Chọn áo Đen, XL<br>7. Tab 'ĐẶT HÀNG' → Mua ngay → Thanh toán | Credits giảm 3 (12→9). Artwork đúng style. Đơn hàng thành công |",
    ]
}
new_features["E2E FLOW"] = e2e_tcs

# ─── OUTPUT: Main file ───
def write_md(path, title, feat_dict):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\r\n\r\n")
        f.write("> **Source:** Confluence BA Specifications & Stitch UI Design\r\n")
        f.write("> **Version:** v27 — Restructured (8 Sheets)\r\n\r\n")
        
        TABLE_HEADER = "| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |\r\n"
        TABLE_SEP = "|:---|:---|:---|:---|:---|:---|:---|\r\n"
        
        for feat_name, categories in feat_dict.items():
            f.write(f"## 🚀 Feature: {feat_name}\r\n")
            
            # Write categories in order
            written_cats = set()
            for cat_name in CAT_ORDER:
                if cat_name in categories and categories[cat_name]:
                    f.write(f"### 📌 {cat_name}\r\n\r\n")
                    f.write(TABLE_HEADER)
                    f.write(TABLE_SEP)
                    for tc in categories[cat_name]:
                        tc_clean = tc.rstrip('\r\n')
                        f.write(f"{tc_clean}\r\n")
                    f.write("\r\n")
                    written_cats.add(cat_name)
            
            # Any remaining categories not in order
            for cat_name, tcs in categories.items():
                if cat_name not in written_cats and tcs:
                    f.write(f"### 📌 {cat_name}\r\n\r\n")
                    f.write(TABLE_HEADER)
                    f.write(TABLE_SEP)
                    for tc in tcs:
                        tc_clean = tc.rstrip('\r\n')
                        f.write(f"{tc_clean}\r\n")
                    f.write("\r\n")
            
            f.write("---\r\n\r\n")

# Write main file
main_out = os.path.join(BASE, "test_cases_suite_v27.md")
write_md(main_out, "POD T-Shirt Platform — Test Case Suite v27 (Restructured 8 Sheets)", new_features)

# Write CMS file
cms_out = os.path.join(BASE, "test_cases_cms.md")
write_md(cms_out, "POD T-Shirt Platform — CMS Test Cases", cms_features)

# ─── STATS ───
print("\n" + "="*60)
print("RESTRUCTURED OUTPUT:")
print("="*60)

main_total = 0
for feat, cats in new_features.items():
    count = sum(len(tcs) for tcs in cats.values())
    main_total += count
    print(f"  📋 {feat}: {count} TCs")

cms_total = sum(len(tcs) for tcs in cms_features["CMS"].values())
print(f"\n  📋 CMS (separate): {cms_total} TCs")
print(f"\n  ✅ Main file total: {main_total} TCs")
print(f"  ✅ CMS file total: {cms_total} TCs")
print(f"  ✅ Grand total: {main_total + cms_total} TCs (original: {total})")
print(f"\n  💾 Main: {main_out}")
print(f"  💾 CMS: {cms_out}")
