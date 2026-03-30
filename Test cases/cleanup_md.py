"""Clean up duplicate sections in test_cases_suite.md and regenerate Excel"""
import os

path = r'E:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\test_cases_suite.md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Before: {len(lines)} lines")

# Find the FIRST complete DS Validation section ending (has TC_DS_016 Undo negative)
# The consolidated content ends around line 655 with the DS Validation + TC_DS_016
# After that, lines 656+ are old duplicated sections that need to be removed

# Strategy: find the SECOND occurrence of "### 📌 SEO & Accessibility" (the old duplicate)
seo_count = 0
cut_start = None
for i, line in enumerate(lines):
    if 'SEO' in line and 'Accessibility' in line and '📌' in line:
        seo_count += 1
        if seo_count == 2:
            cut_start = i
            break

if cut_start:
    # Remove from cut_start to end (keeping only a trailing newline)
    lines = lines[:cut_start] + ['\n']
    print(f"After: {len(lines)} lines (removed from line {cut_start+1})")
else:
    print("No duplicate found, checking alternate pattern...")
    # Try finding second "DESIGN STUDIO" header
    ds_count = 0
    for i, line in enumerate(lines):
        if 'Feature: DESIGN STUDIO' in line:
            ds_count += 1
            if ds_count == 2:
                cut_start = i - 1  # include the ## line above
                lines = lines[:cut_start] + ['\n']
                print(f"After: {len(lines)} lines (removed from line {cut_start+1})")
                break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done!")
