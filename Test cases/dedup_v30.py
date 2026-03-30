"""Check and remove duplicates in v30 test suite."""
import re
from collections import defaultdict

FILE = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v30.md"

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Find exact TC_ID duplicates
tc_map = {}
exact_dupes = []
for i, line in enumerate(lines):
    m = re.search(r'`(TC_\w+)`', line)
    if m and line.strip().startswith('|'):
        tid = m.group(1)
        if tid in tc_map:
            exact_dupes.append((tid, tc_map[tid], i))
        else:
            tc_map[tid] = i

print(f"Total TCs: {len(tc_map) + len(exact_dupes)}")
print(f"Unique TC_IDs: {len(tc_map)}")

if exact_dupes:
    print(f"\n❌ {len(exact_dupes)} EXACT DUPLICATE TC_IDs:")
    lines_to_remove = set()
    for tid, first_line, dupe_line in exact_dupes:
        print(f"  {tid}: line {first_line+1} (keep) vs line {dupe_line+1} (remove)")
        lines_to_remove.add(dupe_line)
    
    # Remove duplicate lines
    new_lines = [l for i, l in enumerate(lines) if i not in lines_to_remove]
    with open(FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"\n✅ Removed {len(lines_to_remove)} duplicate lines")
else:
    print("\n✅ 0 exact duplicate TC_IDs")

# 2. Find functional overlaps (same title, different ID)
titles = defaultdict(list)
for i, line in enumerate(lines):
    m = re.search(r'`(TC_\w+)`', line)
    if m and line.strip().startswith('|'):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        if len(cols) >= 4:
            title = cols[3].strip().lower()
            titles[title].append((m.group(1), i+1))

overlaps = {t: ids for t, ids in titles.items() if len(ids) > 1}
if overlaps:
    print(f"\n⚠️ {len(overlaps)} POTENTIAL functional overlaps (same title, different ID):")
    for title, ids in sorted(overlaps.items()):
        print(f"  Title: \"{title[:70]}\"")
        for tid, ln in ids:
            print(f"    → {tid} (line {ln})")
else:
    print("\n✅ 0 functional overlaps (same title)")

# 3. Recount
with open(FILE, "r", encoding="utf-8") as f:
    final = f.read()
final_count = sum(1 for l in final.split('\n') if '`TC_' in l and l.strip().startswith('|'))
print(f"\n📊 Final TC count: {final_count}")
