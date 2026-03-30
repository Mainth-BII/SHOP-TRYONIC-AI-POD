#!/usr/bin/env python3
"""
Fix outdated tab references in v28 test suite.
Based on source code analysis, Design Studio does NOT have tabs.
Actual architecture:
  - Right Panel: AIArtworkPanel (always visible)
  - ProductSelectorModal: popup for product selection
  - OrderModal: popup for ordering (from StatusBar button)
  - LibraryPanel: slide panel for library
  - TextEditingPanel / ImageSettingsPanel: conditional panels
"""
import re

MD = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v28.md"

with open(MD, "r", encoding="utf-8") as f:
    content = f.read()

# Track replacements
replacements = 0

# 1. Fix Module column: "DS Sản phẩm - Panel" → "DS Sản phẩm - Modal"
old_modules = {
    "DS Sản phẩm - Panel": "DS Sản phẩm - Modal",
    "DS Sản phẩm - Chọn sản phẩm": "DS Sản phẩm - Modal",
    "DS Sản phẩm - Gợi ý size": "DS Sản phẩm - Modal",
    "DS Ảnh của bạn - Panel": "DS Thư viện - Library Panel",
    "DS Ảnh của bạn - Cài đặt hình ảnh": "DS Thư viện - Library Panel",
    "DS Thư viện - Panel": "DS Thư viện - Library Panel",
    "DS Thư viện - Tìm kiếm mẫu": "DS Thư viện - Library Panel",
    "DS Chung - Panel": "DS Chung - AI Panel",
    "Tạo ảnh AI - Panel": "DS Chung - AI Panel",
}

for old, new in old_modules.items():
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        replacements += count
        print(f"  Module: '{old}' → '{new}' ({count}x)")

# 2. Fix step text: "Click tab 'SẢN PHẨM'" → "Mở ProductSelectorModal"
tab_step_fixes = {
    "Click tab 'SẢN PHẨM'": "Mở popup đổi sản phẩm (ProductSelectorModal)",
    "Tab 'SẢN PHẨM'": "Popup Sản phẩm (ProductSelectorModal)",
    "tab 'SẢN PHẨM'": "popup sản phẩm",
    "Click tab 'ẢNH CỦA BẠN'": "Mở thư viện ảnh (LibraryPanel từ sidebar)",
    "Tab 'ẢNH CỦA BẠN'": "Thư viện ảnh (LibraryPanel)",
    "tab 'ẢNH CỦA BẠN'": "thư viện ảnh",
    "Click tab 'THƯ VIỆN'": "Mở thư viện mẫu (LibraryPanel từ sidebar)",
    "Tab 'THƯ VIỆN'": "Thư viện mẫu (LibraryPanel)",
    "tab 'THƯ VIỆN'": "thư viện mẫu",
    "Click tab 'TẠO ẢNH AI'": "Trên AI Panel (mặc định hiển thị bên phải)",
    "Tab 'TẠO ẢNH AI'": "AI Panel (bên phải)",
    "tab 'TẠO ẢNH AI'": "AI Panel",
    "Click tab 'ĐẶT HÀNG'": "Click nút 'Đặt hàng' trên StatusBar → OrderModal",
    "Tab 'ĐẶT HÀNG'": "OrderModal (popup từ StatusBar)",
    "tab 'ĐẶT HÀNG'": "OrderModal",
}

for old, new in tab_step_fixes.items():
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        replacements += count
        print(f"  Steps: '{old}' → '{new}' ({count}x)")

# 3. Fix "5 tabs panel" description
content = content.replace(
    "5 tabs panel phải hiển thị đầy đủ",
    "Panel AI hiển thị đúng (luôn hiển thị bên phải)"
)
content = content.replace(
    "5 tabs: 'SẢN PHẨM', 'ẢNH CỦA BẠN', 'THƯ VIỆN', 'TẠO ẢNH AI', 'ĐẶT HÀNG'. Mỗi tab có icon tương ứng. Tab 'TẠO ẢNH AI' active mặc định",
    "AI Artwork Panel luôn hiển thị mặc định. Khi chọn text element → TextEditingPanel hiển thị. Khi chọn image → ImageSettingsPanel hiển thị. Không có hệ thống tabs"
)

# 4. Fix "Switch giữa các tabs"
content = content.replace(
    "Switch giữa các tabs trên panel phải",
    "Panel phải chuyển đổi context theo element được chọn"
)
content = content.replace(
    "Click lần lượt: SẢN PHẨM → ẢNH CỦA BẠN → THƯ VIỆN → TẠO ẢNH AI → ĐẶT HÀNG",
    "Click text element → hiển thị TextEditingPanel. Click image → ImageSettingsPanel. Bỏ chọn → AI Panel hiển thị"
)
content = content.replace(
    "Mỗi tab khi click hiển thị nội dung tương ứng. Tab active có underline/highlight. Nội dung panel thay đổi mượt mà",
    "Panel chuyển đổi mượt mà giữa AI Panel, TextEditingPanel, ImageSettingsPanel dựa trên element selection"
)

# 5. Fix "→ Tab 'SẢN PHẨM'" in steps
content = content.replace("→ Tab 'SẢN PHẨM'", "→ Popup sản phẩm")
content = content.replace("→ Tab 'ĐẶT HÀNG'", "→ OrderModal")
content = content.replace("→ Tab 'THƯ VIỆN'", "→ LibraryPanel")
content = content.replace("Mở DS → Tab 'SẢN PHẨM'", "Mở DS → Click 'Đổi sản phẩm' trên StatusBar")
content = content.replace("Mở DS → Tab 'ẢNH CỦA BẠN'", "Mở DS → Click icon Thư viện trên sidebar")
content = content.replace("Mở DS → Tab 'THƯ VIỆN'", "Mở DS → Click icon Thư viện trên sidebar")
content = content.replace("Mở DS → Tab 'ĐẶT HÀNG'", "Mở DS → Click 'Đặt hàng' trên StatusBar")
content = content.replace("Mở Design Studio → Tab 'SẢN PHẨM'", "Mở DS → Click 'Đổi sản phẩm' trên StatusBar")
content = content.replace("Mở Design Studio → Tab 'ẢNH CỦA BẠN'", "Mở DS → Click icon Thư viện trên sidebar")
content = content.replace("Mở Design Studio → Tab 'THƯ VIỆN'", "Mở DS → Click icon Thư viện trên sidebar")  
content = content.replace("Mở Design Studio → Tab 'TẠO ẢNH AI'", "Trên AI Panel (mặc định)")
content = content.replace("Trong tab 'TẠO ẢNH AI'", "Trong AI Panel")
content = content.replace("trong tab 'TẠO ẢNH AI'", "trong AI Panel")
content = content.replace("Tab ĐẶT HÀNG", "OrderModal")

# 6. Fix general "Tab" → more specific references in steps
for old, new in [
    ("Tab 'SẢN PHẨM' active (underline/highlight). Panel hiển thị danh sách loại áo/sản phẩm có thể chọn",
     "ProductSelectorModal mở. Hiển thị danh sách loại áo/sản phẩm có thể chọn"),
    ("Tab 'ẢNH CỦA BẠN' active. Panel hiển thị khu vực upload ảnh cá nhân hoặc danh sách ảnh đã upload",
     "LibraryPanel mở. Panel hiển thị khu vực upload ảnh cá nhân hoặc danh sách ảnh đã upload"),
    ("Tab 'THƯ VIỆN' active. Panel hiển thị thư viện mẫu có sẵn (templates/artwork). Có thể chọn mẫu và apply lên canvas",
     "LibraryPanel mở. Panel hiển thị thư viện mẫu có sẵn (templates/artwork). Có thể chọn mẫu và apply lên canvas"),
    ("Tab 'ĐẶT HÀNG' active. Panel hiển thị form đặt hàng với thông tin sản phẩm, số lượng, và tùy chọn checkout",
     "OrderModal mở. Hiển thị form đặt hàng với thông tin sản phẩm, số lượng, và tùy chọn checkout"),
]:
    content = content.replace(old, new)

with open(MD, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Fixed {replacements}+ references in test_cases_suite_v28.md")
print("   All 'Tab' → Modal/Panel references updated")
