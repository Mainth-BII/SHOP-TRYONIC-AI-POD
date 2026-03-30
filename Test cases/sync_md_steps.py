import re

md_path = "test_cases_suite.md"

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix Headers
    if "| Expected Result |" in line and "| Steps |" not in line:
        line = line.replace("| Expected Result |", "| Steps | Expected Result |")
    elif "|:---|:---|:---|:---|:---|:---|:---|" in line and line.count("|:---|") == 7:
        line = line.replace("|:---|:---|:---|:---|:---|:---|:---|", "|:---|:---|:---|:---|:---|:---|:---|:---|")
    
    # Process Row Data
    if line.startswith("| `TC_"):
        parts = line.split("|")
        if len(parts) >= 9:
            module_name = parts[3].strip()
            steps_str = parts[7].strip()
            
            # Check if it lacks navigation
            nav_keywords = ['mở trang', 'vào trang', 'truy cập', 'vào dashboard', 'mở /', 'mở bảng', 'vào profile', 'vào my orders', 'mở ', 'vào ']
            first_step = steps_str.split('<br>')[0].lower()
            
            if not any(keyword in first_step for keyword in nav_keywords):
                step_parts = steps_str.split('<br>')
                new_step_parts = [f"1. Truy cập vào trang {module_name}"]
                
                for sp in step_parts:
                    match = re.match(r'^(\d+)(\.\s+.*)', sp.strip())
                    if match:
                        num = int(match.group(1))
                        rest = match.group(2)
                        new_step_parts.append(f"{num+1}{rest}")
                    else:
                        new_step_parts.append(sp)
                        
                parts[7] = " " + "<br>".join(new_step_parts) + " "
                line = "|".join(parts)
                
    new_lines.append(line)

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("test_cases_suite.md synchronized successfully.")
