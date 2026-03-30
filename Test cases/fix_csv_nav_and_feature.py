import pandas as pd
import re

csv_path = 'TC_POD-TShirt-Platform_v4_2026-03-13.csv'
df = pd.read_csv(csv_path)

# Fix Feature name
df['Feature'] = df['Feature'].replace('EDITOR', 'Editor')

# Fix Steps
def fix_nav_step(steps_text):
    text = str(steps_text)
    if text.strip() == '' or pd.isna(steps_text):
        return text
    
    lines = text.split('\n')
    if lines[0].lower().startswith('1. truy cập vào trang'):
        # Just replace the first line entirely
        lines[0] = "1. Truy cập vào trang "
    return '\n'.join(lines)

df['Steps'] = df['Steps'].apply(fix_nav_step)
df.to_csv(csv_path, index=False, encoding='utf-8')
print("CSV fixed.")
