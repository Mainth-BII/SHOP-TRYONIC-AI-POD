import re

md_path = "test_cases_suite.md"

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.startswith("| `TC_"):
        parts = line.split("|")
        if len(parts) >= 9:
            steps_str = parts[7].strip()
            # Replace exactly the first step if it matches
            if steps_str.lower().startswith('1. truy cập vào trang'):
                step_parts = steps_str.split('<br>')
                if step_parts:
                    step_parts[0] = "1. Truy cập vào trang "
                    parts[7] = " " + "<br>".join(step_parts) + " "
                line = "|".join(parts)
    new_lines.append(line)

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("test_cases_suite.md navigation steps changed to exactly 'Truy cập vào trang '.")
