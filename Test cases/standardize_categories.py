"""
Standardize v29 test case categories: 
- Parse all TCs from each feature
- Re-classify into 5 standard categories: UI/UX, Functional, Validation, Security, Performance
- Remove #### sub-sub-headings and 🔗 Merged from: headers  
- Output clean markdown with uniform format
"""
import re, os

SRC = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"
DST = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29_clean.md"

TABLE_HDR = "| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |"
TABLE_SEP = "|:---|:---|:---|:---|:---|:---|:---|"

CATEGORY_ORDER = ["UI/UX", "Functional", "Validation", "Security", "Performance"]

def classify_tc(tc_row, old_category):
    """Classify TC into standard category based on Type column + old category context."""
    cols = [c.strip() for c in tc_row.split('|')[1:-1]]
    if len(cols) < 6:
        return "Functional"
    
    tc_type = cols[4].strip().lower()
    tc_title = cols[3].strip().lower()
    old_cat = old_category.lower()
    
    # Security: explicit security category or XSS/injection in title
    if 'security' in old_cat:
        return "Security"
    if any(k in tc_title for k in ['xss', 'injection', 'sql', 'csrf', 'brute', 'token', 'jwt', 'auth bypass']):
        return "Security"
    
    # Performance: explicit category
    if 'performance' in old_cat:
        return "Performance"
    if any(k in tc_title for k in ['timeout', 'latency', 'mạng', 'mất mạng', 'lazy load']):
        return "Performance"
    
    # UI/UX: type contains UI/UX emoji or keyword
    if 'ui/ux' in tc_type or '🎨' in tc_type:
        return "UI/UX"
    
    # Validation: negative, boundary, edge case 
    if '⚠️' in tc_type or 'negative' in tc_type:
        return "Validation"
    if 'boundary' in tc_type:
        return "Validation"
    if 'edge case' in tc_type and ('sai' in tc_title or 'lỗi' in tc_title or 'không' in tc_title or 'rỗng' in tc_title or 'hết' in tc_title):
        return "Validation"
    
    # Everything else → Functional
    return "Functional"

# ─── Parse features ───
with open(SRC, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract header (before first feature)
header_lines = []
features = {}  # name → {category: [tc_rows]}
feature_order = []

cur_feat = None
cur_cat = None
in_header = True

for line in lines:
    s = line.rstrip('\r\n')
    
    # Feature header
    feat_m = re.match(r'^## .+Feature:\s*(.+)$', s.strip())
    if feat_m:
        in_header = False
        cur_feat = feat_m.group(1).strip()
        if cur_feat not in features:
            features[cur_feat] = {}
            feature_order.append(cur_feat)
        cur_cat = None
        continue
    
    if in_header:
        header_lines.append(s)
        continue
    
    # Category header: ### 📌 ... or ### 🔗 ... or #### 🆕 ...
    cat_m = re.match(r'^###\s+.+?\s+(.+)$', s.strip())
    if cat_m and cur_feat:
        cur_cat = cat_m.group(1).strip()
        # Normalize: remove "— Source Code Verified" etc suffixes for classification
        continue
    
    sub_m = re.match(r'^####\s+.+?\s+(.+)$', s.strip())
    if sub_m and cur_feat:
        # Sub-sub heading, keep current category context
        continue
    
    # TC row
    if s.strip().startswith('| `TC_') and cur_feat and cur_cat is not None:
        std_cat = classify_tc(s, cur_cat)
        if std_cat not in features[cur_feat]:
            features[cur_feat][std_cat] = []
        features[cur_feat][std_cat].append(s)
        continue

# ─── Reconstruct clean markdown ───
output = []

# Update header
for line in header_lines:
    if 'Deduped from' in line:
        line = '> **Version:** v29 — Merged 9 Sheets, 5 Standard Categories. Sync source code: AI Chat Hero, My Orders, Footer, Policy Pages, Library Flyout, OrderModal, StatusBar'
    if 'Merged — 9 Sheets' in line:
        line = '# POD T-Shirt Platform — Test Case Suite v29 (Clean — 9 Sheets × 5 Categories)'
    output.append(line)

for feat_name in feature_order:
    cats = features[feat_name]
    
    output.append('')
    output.append('---')
    output.append('')
    output.append(f'## 🚀 Feature: {feat_name}')
    
    for cat in CATEGORY_ORDER:
        if cat not in cats or not cats[cat]:
            continue
        
        tcs = cats[cat]
        output.append('')
        output.append(f'### 📌 {cat}')
        output.append('')
        output.append(TABLE_HDR)
        output.append(TABLE_SEP)
        
        for tc_row in tcs:
            output.append(tc_row)
    
    output.append('')

content = '\n'.join(output)

with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

# ─── Stats ───
tc_count = sum(1 for line in output if '`TC_' in line and line.strip().startswith('|'))
feat_count = len(feature_order)

print(f"✅ Created: {os.path.basename(DST)}")
print(f"📊 Total lines: {len(output)}")
print(f"📊 Total TCs: {tc_count}")
print(f"📊 Features: {feat_count}")
print()

for feat_name in feature_order:
    cats = features[feat_name]
    total = sum(len(v) for v in cats.values())
    cat_breakdown = ', '.join(f"{c}: {len(cats[c])}" for c in CATEGORY_ORDER if c in cats and cats[c])
    print(f"  📋 {feat_name}: {total} TCs → [{cat_breakdown}]")
