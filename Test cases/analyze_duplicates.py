"""Analyze v29 test case markdown for duplicate TC IDs across features."""
import re
from collections import defaultdict

MD = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"

with open(MD, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse: feature → list of TC_IDs
features = {}
lines = content.split('\n')
cur_feat = None

for line in lines:
    s = line.strip()
    m = re.match(r'^## .+Feature:\s*(.+)$', s)
    if m:
        cur_feat = m.group(1).strip()
        if cur_feat not in features:
            features[cur_feat] = []
        continue
    if s.startswith('| `TC_') and cur_feat:
        tc_match = re.match(r'\|\s*`(TC_[^`]+)`', s)
        if tc_match:
            features[cur_feat].append(tc_match.group(1))

# Find duplicates
all_tc_ids = defaultdict(list)  # tc_id → [feature1, feature2, ...]
for feat, tc_ids in features.items():
    for tc_id in tc_ids:
        all_tc_ids[tc_id].append(feat)

print("=" * 70)
print("v29 TEST SUITE — DUPLICATE ANALYSIS")
print("=" * 70)

print(f"\n📊 Features: {len(features)}")
total = 0
for feat, tcs in features.items():
    print(f"  {feat}: {len(tcs)} TCs")
    total += tcs.__len__()
print(f"  TOTAL (with dupes): {total}")

# Unique count
unique_ids = set()
for feat, tcs in features.items():
    unique_ids.update(tcs)
print(f"  UNIQUE TC IDs: {len(unique_ids)}")
print(f"  DUPLICATES: {total - len(unique_ids)}")

# Show all duplicates
dupes = {tc_id: feats for tc_id, feats in all_tc_ids.items() if len(feats) > 1}
if dupes:
    print(f"\n🔴 DUPLICATE TC IDs ({len(dupes)}):")
    # Group by feature pair
    pair_groups = defaultdict(list)
    for tc_id, feats in sorted(dupes.items()):
        key = " ↔ ".join(sorted(feats))
        pair_groups[key].append(tc_id)
    
    for pair, tc_ids in sorted(pair_groups.items(), key=lambda x: -len(x[1])):
        print(f"\n  📋 {pair} ({len(tc_ids)} dupes):")
        for tc_id in tc_ids:
            print(f"     {tc_id}")

# Overlap analysis (same functional area, different TC IDs)
print("\n" + "=" * 70)
print("FUNCTIONAL OVERLAP — TC IDs UNIQUE BUT SAME AREA")
print("=" * 70)

ORDER_TCS = [tc for tc in features.get("ORDER", [])]
MY_ORDERS_TCS = [tc for tc in features.get("MY ORDERS (Đơn hàng của tôi)", [])]
print(f"\nORDER ({len(ORDER_TCS)} TCs): {ORDER_TCS}")
print(f"MY ORDERS ({len(MY_ORDERS_TCS)} TCs): {MY_ORDERS_TCS}")

# Check FOOTER vs HOME
FOOTER_TCS = [tc for tc in features.get("FOOTER", [])]
HOME_TCS = [tc for tc in features.get("HOME", [])]
print(f"\nFOOTER ({len(FOOTER_TCS)} TCs): {FOOTER_TCS}")
print(f"HOME ({len(HOME_TCS)} TCs — Footer is on Home page)")
