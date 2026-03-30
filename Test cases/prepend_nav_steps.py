import pandas as pd
import re

csv_path = 'TC_POD-TShirt-Platform_v4_2026-03-13.csv'
df = pd.read_csv(csv_path)

def add_navigation_step(row):
    steps_text = str(row['Steps'])
    if pd.isna(row['Steps']) or steps_text.strip() == '':
        return steps_text
        
    module_name = str(row['Module'])
    if pd.isna(row['Module']):
        module_name = ""
        
    # Check if a navigation step already exists at the start
    lines = steps_text.split('\n')
    first_line = lines[0].lower()
    nav_keywords = ['mở trang', 'vào trang', 'truy cập', 'vào dashboard', 'mở /', 'mở bảng', 'vào profile', 'vào my orders', 'vào my', 'vào ', 'mở ']
    
    # We also check if it starts with "1. Mở" or similar 
    if any(keyword in first_line for keyword in nav_keywords):
        return steps_text # Already has navigation
        
    new_lines = [f"1. Truy cập vào trang {module_name}"]
    
    for line in lines:
        match = re.match(r'^(\d+)(\.\s+.*)', line)
        if match:
            num = int(match.group(1))
            rest = match.group(2)
            new_lines.append(f"{num+1}{rest}")
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines)

# Apply the transformation
df['Steps'] = df.apply(add_navigation_step, axis=1)

# Overwrite the original CSV file
df.to_csv(csv_path, index=False, encoding='utf-8')
print("Successfully prepended navigation steps to all test cases in the CSV.")
