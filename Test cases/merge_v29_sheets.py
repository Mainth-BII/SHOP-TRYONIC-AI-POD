"""
Merge v29 test cases: 13 sheets → 9 sheets.
1. Remove PROFILE / ACCOUNT standalone (already in LOGIN via Auth TCs)
2. Remove AI TRY-ON standalone (already in DESIGN STUDIO via SC TCs)
3. Merge ORDER → MY ORDERS (keep TC_ORD_025, TC_ORD_026 re-order TCs)
4. Merge FOOTER → HOME
5. Fix AI GENERATE duplicate TC_IDs (TC_AI_001, TC_AI_002, TC_AI_003)
"""
import re

SRC = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29_merged.md"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

# ─── 1. Update header ────────────────────────────────────────────────
content = content.replace(
    "# POD T-Shirt Platform — Test Case Suite v29 (Source Code Sync 2026-03-26)",
    "# POD T-Shirt Platform — Test Case Suite v29 (Merged — 9 Sheets)"
)
content = content.replace(
    "> **Version:** v29 — Sync source code: AI Chat Hero, My Orders, Footer, Policy Pages, Library Flyout, OrderModal, StatusBar (Merged: 14 Sheets)",
    "> **Version:** v29 — Merged 9 Sheets. Sync source code: AI Chat Hero, My Orders, Footer, Policy Pages, Library Flyout, OrderModal, StatusBar. Deduped from 580→~535 TCs"
)

# ─── 2. Remove standalone PROFILE / ACCOUNT section ──────────────────
# Find and remove the entire "## 🚀 Feature: PROFILE / ACCOUNT" section
# (appears AFTER E2E and BEFORE AI TRY-ON at the end of the file)
profile_pattern = re.compile(
    r'\n---\n\n## 🚀 Feature: PROFILE / ACCOUNT\n.*?(?=\n---\n\n## 🚀 Feature:|$)',
    re.DOTALL
)
content = profile_pattern.sub('', content)

# ─── 3. Remove standalone AI TRY-ON section ───────────────────────────
tryon_pattern = re.compile(
    r'\n---\n\n## 🚀 Feature: AI TRY-ON \(Thử đồ với AI\)\n.*?(?=\n---\n\n## 🚀 Feature:|$)',
    re.DOTALL
)
content = tryon_pattern.sub('', content)

# ─── 4. Merge ORDER → MY ORDERS ──────────────────────────────────────
# Extract the 2 unique re-order TCs from ORDER section
reorder_tcs = """
### 📌 Functional — Re-order (từ ORDER cũ)

| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |
|:---|:---|:---|:---|:---|:---|:---|
| `TC_ORD_025` | `US-29` | Re-order | Re-order design cũ | ✅ Positive | **🟠 P1** | 1. Mở My Orders<br>2. Click 'Đặt lại'<br>3. Chọn Size/Qty | Tạo đơn mới với cùng design. Vào Cart |
| `TC_ORD_026` | `US-29` | Re-order | Re-order sản phẩm đã ngưng bán | ✅ Edge Case | **🟢 P2** | 1. Mở My Orders<br>2. Click 'Đặt lại' | Hiển thị: 'Sản phẩm này không còn bán'. Không cho re-order |
"""

# Remove entire ORDER section
order_pattern = re.compile(
    r'\n---\n\n+## 🚀 Feature: ORDER\n.*?(?=\n---\n\n+## 🚀 Feature:|$)',
    re.DOTALL
)
content = order_pattern.sub('', content)

# Append re-order TCs to MY ORDERS section (before the closing ---)
# Find MY ORDERS section end and add before closing
my_orders_end = content.find("## 🚀 Feature: MY ORDERS")
if my_orders_end != -1:
    # Find the end of MY ORDERS (next feature or end of file)
    next_feature = content.find("\n---\n\n## 🚀 Feature:", my_orders_end + 10)
    if next_feature == -1:
        # MY ORDERS is the last section, append before end
        content = content.rstrip() + "\n" + reorder_tcs + "\n---\n"
    else:
        # Insert reorder TCs before the --- separator
        content = content[:next_feature] + "\n" + reorder_tcs + content[next_feature:]

# ─── 5. Merge FOOTER → HOME ──────────────────────────────────────────
# Extract FOOTER TCs
footer_section_match = re.search(
    r'## 🚀 Feature: FOOTER\n(.*?)(?=\n---\n\n## 🚀 Feature:|$)',
    content, re.DOTALL
)
footer_content = ""
if footer_section_match:
    footer_content = footer_section_match.group(1).strip()

# Remove standalone FOOTER section
footer_pattern = re.compile(
    r'\n---\n\n## 🚀 Feature: FOOTER\n.*?(?=\n---\n\n## 🚀 Feature:|$)',
    re.DOTALL
)
content = footer_pattern.sub('', content)

# Add FOOTER TCs to HOME section (before the HOME section ends)
if footer_content:
    footer_merged = f"""

---

### 🔗 Merged from: FOOTER
{footer_content}
"""
    # Find end of HOME section
    home_start = content.find("## 🚀 Feature: HOME")
    if home_start != -1:
        next_feat_after_home = content.find("\n---\n\n## 🚀 Feature:", home_start + 10)
        if next_feat_after_home != -1:
            content = content[:next_feat_after_home] + "\n" + footer_merged + content[next_feat_after_home:]

# ─── 6. Fix AI GENERATE duplicate TC_IDs ──────────────────────────────
# The duplicates are in "Functional (Logic & Behavior)" section
# Remove the SECOND occurrence of TC_AI_001, TC_AI_002, TC_AI_003
# They appear as the last 2 rows in that section with different text

# TC_AI_001 duplicate (the second one)
content = content.replace(
    "| `TC_AI_001` | `US-37` | AI Generate - Generation | Verify AI generates exactly 4 variations | ✅ Positive | **🔴 P0** | 1. Truy cập vào trang <br>2. Chọn tool AI<br>3. Nhập từ khóa Cyberpunk cat<br>4. Nhấn Generate | Hệ thống trừ 1 credit, loading, trả về đúng 4 hình ảnh preview |",
    ""
)

# TC_AI_002 duplicate (in Validation section - the second occurrence)
content = content.replace(
    "| `TC_AI_002` | `US-42` | AI Generate - Quota Boundary | Verify Guest 2 generations max per day | ✅ Boundary | **🔴 P0** | 1. Truy cập vào trang <br>2. Dùng AI generate 2 lần<br>3. Thử generate lần thứ 3 | Lần 3 báo lỗi 'Out of credits' hoặc 'Đăng nhập để nhận thêm' |",
    ""
)

# TC_AI_003 duplicate (the second one)
content = content.replace(
    "| `TC_AI_003` | `US-42b` | AI Generate - Refill Logic | Verify daily reset logic of Free User credits | ✅ Positive | **🔴 P0** | 1. Truy cập vào trang <br>2. Cài đặt thời gian qua 24h (admin)<br>3. Check số dư | Số dư credit tự động reset về 10 |",
    ""
)

# Clean up multiple blank lines
content = re.sub(r'\n{4,}', '\n\n\n', content)
# Clean up empty table rows (lines with only pipes)
content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

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
