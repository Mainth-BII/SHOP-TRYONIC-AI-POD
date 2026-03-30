"""Analyze category structure of each feature in v29 merged test suite."""
import re

MD = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v29.md"
with open(MD, 'r', encoding='utf-8') as f:
    lines = f.readlines()

cur_feat = None
for i, line in enumerate(lines):
    s = line.strip()
    
    # Feature header
    feat_m = re.match(r'^## .+Feature:\s*(.+)$', s)
    if feat_m:
        cur_feat = feat_m.group(1).strip()
        print(f"\n{'='*60}")
        print(f"FEATURE: {cur_feat}")
        print(f"{'='*60}")

    # Any ### heading (category headers)
    if s.startswith('###') and cur_feat:
        # Count TCs until next ### or ##
        tc_count = 0
        for j in range(i+1, min(i+200, len(lines))):
            ls = lines[j].strip()
            if ls.startswith('###') or ls.startswith('##'):
                break
            if '`TC_' in ls and ls.startswith('|'):
                tc_count += 1
        print(f"  L{i+1:4d}: {s[:80]} ({tc_count} TCs)")
