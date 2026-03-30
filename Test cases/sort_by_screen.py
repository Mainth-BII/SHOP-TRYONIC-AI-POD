"""
Sort TCs with multi-key ordering within each category:
  1. Screen (grouped by defined order per feature)
  2. Module (alphabetically within same screen)
  3. Priority (P0 → P1 → P2 → P3)
  4. TC_ID (natural sort)

Result: When you open the Excel, TCs flow logically:
  Same Screen → Same Module → Most important first → ID order
"""
import re, os
from collections import OrderedDict

MD = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29_final.md"

TABLE_HDR = "| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |"
TABLE_SEP = "|:---|:---|:---|:---|:---|:---|:---|"

# ─── Screen detection (same logic) ───
SCREEN_MAP_BY_FEATURE = {"ORDER": "MH Đơn hàng", "E2E FLOW": "E2E"}

SCREEN_ORDER = {
    "HOME": [
        "MH Trang chủ", "MH Footer",
        "Toast/Snackbar", "Error Page", "SPA Routing",
    ],
    "DESIGN STUDIO": [
        "DS - Header", "DS - Sidebar", "DS - Canvas", "DS - Editor/Canvas",
        "DS - AI Panel", "DS - StatusBar",
        "DS - Popup Sản phẩm", "DS - Popup Gợi ý size",
        "DS - Thư viện Ảnh", "DS - Thư viện Mẫu",
        "DS - Gallery", "DS - Smart Fit",
        "DS - AI Try-on", "DS - OrderModal",
        "DS - Credits", "DS - Share", "DS - User Menu",
        "DS - Auth Modal", "DS - Cart Drawer",
        "DS - Mobile Panel",
        "MH My Designs",
        "DS - Chung", "DS - Responsive",
    ],
    "AI GENERATE": ["DS - AI Panel", "MH Credits"],
    "ĐẶT HÀNG": ["DS - OrderModal", "MH Chi tiết SP", "MH Giỏ hàng", "Header"],
    "THANH TOÁN": ["MH Checkout", "MH Thanh toán", "MH Xác nhận đơn"],
    "LOGIN": ["MH Đăng nhập", "MH Đăng ký", "MH Tài khoản", "MH Hồ sơ", "MH Guest", "MH Profile"],
    "MY ORDERS (Đơn hàng của tôi)": [
        "MH My Orders", "MH My Orders - Tìm", "MH My Orders - Filter",
        "MH Chi tiết đơn", "MH My Orders - Hủy",
    ],
    "POLICY PAGES (Chính sách)": [
        "MH Policy", "Policy - Hướng dẫn", "Policy - Thanh toán",
        "Policy - Vận chuyển", "Policy - Đổi trả", "Policy - Bảo mật", "Policy - Error",
    ],
}

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

def detect_screen(feature, module, tc_id, title):
    mod = module.lower(); ttl = title.lower(); tid = tc_id.upper()
    if feature in SCREEN_MAP_BY_FEATURE: return SCREEN_MAP_BY_FEATURE[feature]
    if feature == "HOME":
        if tid.startswith('TC_ERR') or tid.startswith('TC_TOAST'):
            if 'toast' in mod or 'notification' in mod: return "Toast/Snackbar"
            if '404' in mod or 'network' in mod: return "Error Page"
            if 'direct url' in mod or 'navigation' in mod: return "SPA Routing"
            return "Error Page"
        if 'footer' in mod or tid.startswith('TC_FT'): return "MH Footer"
        return "MH Trang chủ"
    if feature == "LOGIN":
        if any(k in mod for k in ['đăng ký', 'signup', 'registration']): return "MH Đăng ký"
        if any(k in mod for k in ['đăng nhập', 'login']): return "MH Đăng nhập"
        if any(k in mod for k in ['tài khoản', 'account']): return "MH Tài khoản"
        if any(k in mod for k in ['hồ sơ', 'profile']): return "MH Hồ sơ"
        if any(k in mod for k in ['guest']): return "MH Guest"
        if 'responsive' in mod:
            if 'login' in ttl or 'đăng nhập' in ttl: return "MH Đăng nhập"
            if 'signup' in ttl or 'đăng ký' in ttl: return "MH Đăng ký"
            return "MH Đăng nhập"
        return "MH Đăng nhập"
    if feature == "DESIGN STUDIO":
        if tid.startswith('TC_MYDES'): return "MH My Designs"
        if any(k in mod for k in ['ds sản phẩm', 'sản phẩm', 'chọn sản phẩm']): return "DS - Popup Sản phẩm"
        if any(k in mod for k in ['ds ảnh', 'upload', 'cài đặt hình ảnh']): return "DS - Thư viện Ảnh"
        if any(k in mod for k in ['ds thư viện', 'thư viện', 'tìm kiếm mẫu']): return "DS - Thư viện Mẫu"
        if any(k in mod for k in ['gợi ý size']): return "DS - Popup Gợi ý size"
        if any(k in mod for k in ['gallery']): return "DS - Gallery"
        if any(k in mod for k in ['smart fit']): return "DS - Smart Fit"
        if any(k in mod for k in ['editor', 'zoom']): return "DS - Editor/Canvas"
        if any(k in mod for k in ['canvas', 'toolbar']): return "DS - Canvas"
        if any(k in mod for k in ['bottom bar', 'statusbar']): return "DS - StatusBar"
        if any(k in mod for k in ['sidebar']): return "DS - Sidebar"
        if any(k in mod for k in ['tryon', 'thử đồ', 'try-on', 'tryon modal']): return "DS - AI Try-on"
        if any(k in mod for k in ['ai panel', 'ai chat', 'variant', 'artwork']): return "DS - AI Panel"
        if any(k in mod for k in ['auth modal', 'inline auth']): return "DS - Auth Modal"
        if any(k in mod for k in ['cart drawer']): return "DS - Cart Drawer"
        if any(k in mod for k in ['share', 'chia sẻ']): return "DS - Share"
        if any(k in mod for k in ['credit']): return "DS - Credits"
        if any(k in mod for k in ['user', 'menu']): return "DS - User Menu"
        if any(k in mod for k in ['mobile', 'panel', 'drawer']): return "DS - Mobile Panel"
        if 'responsive' in mod: return "DS - Responsive"
        if 'header' in mod: return "DS - Header"
        if any(k in mod for k in ['giỏ hàng']): return "DS - Cart Drawer"
        return "DS - Chung"
    if feature == "AI GENERATE":
        if any(k in mod for k in ['credit']): return "MH Credits"
        return "DS - AI Panel"
    if feature == "ĐẶT HÀNG":
        if tid.startswith('TC_CART'): return "MH Giỏ hàng"
        if any(k in mod for k in ['giỏ hàng', 'cart']): return "MH Giỏ hàng"
        if any(k in mod for k in ['sản phẩm', 'product']): return "MH Chi tiết SP"
        if any(k in mod for k in ['đặt hàng', 'thanh toán', 'order']): return "DS - OrderModal"
        if any(k in mod for k in ['header']): return "Header"
        if 'responsive' in mod: return "DS - OrderModal"
        return "DS - OrderModal"
    if feature == "THANH TOÁN":
        if tid.startswith('TC_CONF'): return "MH Xác nhận đơn"
        if any(k in mod for k in ['checkout']): return "MH Checkout"
        if any(k in mod for k in ['thanh toán', 'payment']): return "MH Thanh toán"
        if 'responsive' in mod: return "MH Checkout"
        return "MH Checkout"
    if feature == "MY ORDERS (Đơn hàng của tôi)":
        if 'responsive' in mod or 'zoom' in mod: return "MH My Orders"
        if 'detail' in mod or 'chi tiết' in mod: return "MH Chi tiết đơn"
        if 'cancel' in mod or 'hủy' in mod: return "MH My Orders - Hủy"
        if 'search' in mod or 'tìm' in mod: return "MH My Orders - Tìm"
        if 'filter' in mod or 'status' in mod: return "MH My Orders - Filter"
        if 're-order' in mod or 'đặt lại' in mod: return "MH My Orders"
        return "MH My Orders"
    if feature == "POLICY PAGES (Chính sách)":
        if 'hướng dẫn' in mod or 'mua hàng' in mod: return "Policy - Hướng dẫn"
        if 'thanh toán' in mod: return "Policy - Thanh toán"
        if 'vận chuyển' in mod: return "Policy - Vận chuyển"
        if 'đổi trả' in mod: return "Policy - Đổi trả"
        if 'bảo mật' in mod: return "Policy - Bảo mật"
        if 'invalid' in mod: return "Policy - Error"
        if 'layout' in mod or 'chính sách khác' in mod: return "MH Policy"
        if 'navigate' in mod: return "MH Policy"
        return "MH Policy"
    return feature

def parse_tc_cols(line):
    """Extract all columns from TC row."""
    cols = [c.strip() for c in line.split('|')[1:-1]]
    if len(cols) >= 7:
        return {
            'tc_id': cols[0].strip('` '),
            'mapping': cols[1],
            'module': cols[2],
            'title': cols[3],
            'type': cols[4],
            'priority': cols[5],
            'raw': line,
        }
    return None

def extract_priority(priority_str):
    """Extract P0/P1/P2/P3 from priority string."""
    m = re.search(r'P(\d)', priority_str)
    if m: return int(m.group(1))
    return 9

def natural_sort_key(tc_id):
    """Natural sort: TC_HOME_UI_001 < TC_HOME_UI_010."""
    parts = re.split(r'(\d+)', tc_id)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

def get_screen_idx(screen, feature):
    order = SCREEN_ORDER.get(feature, [])
    if screen in order: return order.index(screen)
    return 999

def multi_sort_key(item, feature):
    """Sort key: Screen → Module → Priority → TC_ID."""
    screen, tc = item
    cols = tc
    return (
        get_screen_idx(screen, feature),  # 1. Screen order
        screen,                            # 1b. Alphabetic fallback
        cols['module'],                    # 2. Module alphabetic
        extract_priority(cols['priority']),# 3. Priority P0→P1→P2
        natural_sort_key(cols['tc_id']),   # 4. TC_ID natural
    )

# ─── Parse ───
with open(MD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_lines = []
features = OrderedDict()
feature_order = []
cur_feat = None
cur_cat = None
in_header = True

for line in lines:
    s = line.rstrip('\r\n')
    feat_m = re.match(r'^## .+Feature:\s*(.+)$', s.strip())
    if feat_m:
        in_header = False
        cur_feat = feat_m.group(1).strip()
        if cur_feat not in features:
            features[cur_feat] = OrderedDict()
            feature_order.append(cur_feat)
        cur_cat = None
        continue
    if in_header:
        header_lines.append(s)
        continue
    cat_m = re.match(r'^### .+ (.+)$', s.strip())
    if cat_m and cur_feat:
        cur_cat = cat_m.group(1).strip()
        continue
    if s.strip().startswith('| `TC_') and cur_feat and cur_cat:
        cols = parse_tc_cols(s)
        if cols:
            screen = detect_screen(cur_feat, cols['module'], cols['tc_id'], cols['title'])
            if cur_cat not in features[cur_feat]:
                features[cur_feat][cur_cat] = []
            features[cur_feat][cur_cat].append((screen, cols))

# ─── Reconstruct with multi-key sorting ───
output = []
for line in header_lines:
    if 'v29' in line and 'Suite' in line:
        line = '# POD T-Shirt Platform — Test Case Suite v29 (Final)'
    if 'Version' in line and 'v29' in line:
        line = '> **Version:** v29 — Final. 9 Sheets × 5 Categories. TCs sorted by Screen → Module → Priority → ID. Source code sync 2026-03-26'
    output.append(line)

CATEGORY_ORDER = ["UI/UX", "Functional", "Validation", "Security", "Performance"]

for feat_name in feature_order:
    cats = features[feat_name]
    output.append('')
    output.append('---')
    output.append('')
    output.append(f'## 🚀 Feature: {feat_name}')
    
    for cat in CATEGORY_ORDER:
        if cat not in cats or not cats[cat]:
            continue
        
        tc_list = cats[cat]
        tc_list.sort(key=lambda x: multi_sort_key(x, feat_name))
        
        output.append('')
        output.append(f'### 📌 {cat}')
        output.append('')
        output.append(TABLE_HDR)
        output.append(TABLE_SEP)
        
        for screen, cols in tc_list:
            output.append(cols['raw'])
    
    output.append('')

content = '\n'.join(output)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

# ─── Detailed Stats ───
tc_count = sum(1 for line in output if '`TC_' in line and line.strip().startswith('|'))
print(f"✅ Created: {os.path.basename(DST)}")
print(f"📊 Total lines: {len(output)}, Total TCs: {tc_count}")
print()

for feat_name in feature_order:
    cats = features[feat_name]
    feat_total = sum(len(v) for v in cats.values())
    print(f"{'='*65}")
    print(f"📋 {feat_name} ({feat_total} TCs)")
    print(f"{'='*65}")
    for cat in CATEGORY_ORDER:
        if cat not in cats or not cats[cat]:
            continue
        tc_sorted = sorted(cats[cat], key=lambda x: multi_sort_key(x, feat_name))
        # Show grouping
        prev_screen = None
        prev_module = None
        for screen, cols in tc_sorted:
            if screen != prev_screen:
                if prev_screen: print()
                print(f"  [{cat}] 🖥️ {screen}:")
                prev_module = None
            if cols['module'] != prev_module:
                print(f"         📁 {cols['module']}")
            prev_screen = screen
            prev_module = cols['module']
        print()
