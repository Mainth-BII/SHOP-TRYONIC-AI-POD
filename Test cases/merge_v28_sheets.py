"""
Merge v28 MD sheets:
  GIỎ HÀNG (CART) → ĐẶT HÀNG
  XÁC NHẬN ĐƠN HÀNG → THANH TOÁN
  ERROR PAGES & NOTIFICATIONS → HOME
  MY DESIGNS (Thiết kế của tôi) → DESIGN STUDIO
  
Then rebuild Excel with merged structure.
"""
import re, os

BASE = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases"
SRC = os.path.join(BASE, "test_cases_suite_v28.md")

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Parse sections by feature ───
# Split by "## 🚀 Feature:" markers
parts = re.split(r'(## 🚀 Feature:\s*)', content)
# parts[0] = header, then alternating [marker, content]

header = parts[0]
features = {}  # name -> full text (marker + content)
feat_order = []

i = 1
while i < len(parts):
    marker = parts[i]  # "## 🚀 Feature: "
    body = parts[i+1] if i+1 < len(parts) else ""
    # Extract feature name (first line of body)
    lines = body.split('\n', 1)
    feat_name = lines[0].strip()
    rest = lines[1] if len(lines) > 1 else ""
    features[feat_name] = rest
    feat_order.append(feat_name)
    i += 2

print(f"Found {len(features)} features: {feat_order}")

# ─── Define merges: source → target ───
MERGES = {
    "GIỎ HÀNG (CART)": "ĐẶT HÀNG",
    "XÁC NHẬN ĐƠN HÀNG (ORDER CONFIRMATION)": "THANH TOÁN",
    "ERROR PAGES & NOTIFICATIONS": "HOME",
    "MY DESIGNS (Thiết kế của tôi)": "DESIGN STUDIO",
}

for src_name, tgt_name in MERGES.items():
    if src_name in features and tgt_name in features:
        # Append source content to target with a separator
        merge_label = f"\n\n### 🔗 Merged from: {src_name}\n"
        features[tgt_name] = features[tgt_name].rstrip() + merge_label + features[src_name]
        del features[src_name]
        feat_order.remove(src_name)
        print(f"  ✅ Merged '{src_name}' → '{tgt_name}'")
    else:
        print(f"  ⚠️ Could not find '{src_name}' or '{tgt_name}'")

# ─── Rebuild MD ───
# Update header
header = header.replace(
    "v28 — Updated Headlines + Bổ sung màn hình thiếu (Cart, Profile, My Designs, AI Try-on, Error Pages)",
    "v28 — Updated Headlines + Bổ sung màn hình thiếu (Merged: 10 Sheets)"
)

output = header
for feat_name in feat_order:
    output += f"## 🚀 Feature: {feat_name}\n{features[feat_name]}"

# Save
OUT_MD = os.path.join(BASE, "test_cases_suite_v28.md")
with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write(output)

# Count
lines = output.split('\n')
tc_count = sum(1 for line in lines if '`TC_' in line and '|' in line)
feat_list = [n for n in feat_order]

print(f"\n📄 Saved: {OUT_MD}")
print(f"📊 Features: {len(feat_list)}")
for fn in feat_list:
    tcs = sum(1 for line in features[fn].split('\n') if '`TC_' in line and '|' in line)
    print(f"   📋 {fn}: {tcs} TCs")
print(f"📊 Total TCs: {tc_count}")
