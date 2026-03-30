#!/usr/bin/env python3
"""Find all test cases referencing old tab system in v28 test suite."""
import re

MD = r"e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite_v28.md"
lines = open(MD, "r", encoding="utf-8").readlines()

OLD_TAB_KEYWORDS = [
    "DS Sản phẩm", "DS Ảnh của bạn", "DS Thư viện",
    "DS Chung - Panel",
    "5 tabs",
    "Tạo ảnh AI - Panel",
]

print("=" * 80)
print("OUTDATED TAB/PANEL REFERENCES IN v28 TEST CASES")
print("=" * 80)
count = 0
for i, line in enumerate(lines, 1):
    for kw in OLD_TAB_KEYWORDS:
        if kw in line:
            m = re.search(r'`(TC_\w+)`', line)
            tc_id = m.group(1) if m else "SECTION/HEADER"
            display = line.strip()[:130]
            print(f"\nL{i}: [{tc_id}]")
            print(f"  KW: {kw}")
            count += 1
            break

print(f"\n{'='*80}")
print(f"TOTAL matches: {count}")
