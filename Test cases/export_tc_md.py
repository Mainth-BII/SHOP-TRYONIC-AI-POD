import pandas as pd
import os
import glob
import re

# Find the latest CSV file
csv_pattern = "TC_POD-TShirt-Platform_v*_Full.csv"
csv_files = glob.glob(csv_pattern)

if not csv_files:
    # fallback
    csv_path = "TC_POD-TShirt-Platform_v6_2026-03-16_Full.csv"
else:
    # Sort files to find the latest
    csv_files.sort(reverse=True)
    csv_path = csv_files[0]
print(f"Reading from {csv_path}")

md_path = "test_cases_suite.md"

if not os.path.exists(csv_path):
    print(f"File {csv_path} not found!")
    exit(1)

df = pd.read_csv(csv_path)
df = df.fillna("")

def get_custom_category(row):
    module = str(row['Module']).lower()
    title = str(row['Title']).lower()
    tc_type = str(row['Type']).lower()

    if 'security' in module or 'lock' in title or 'xss' in title or 'injection' in title:
        return 'Security'
    elif 'network' in module or 'timeout' in title or 'rate limit' in title or 'performance' in module:
        return 'Performance'
    elif 'ui/ux' in tc_type or 'ui' in module:
        return 'UI/UX'
    elif tc_type in ['negative', 'boundary'] or 'validation' in title:
        return 'Validation'
    else:
        return 'Functional (Logic & Behavior)'

df['CustomCategory'] = df.apply(get_custom_category, axis=1)

categories_order = ['UI/UX', 'Validation', 'Functional (Logic & Behavior)', 'Security', 'Performance']

md_content = [
    "# POD T-Shirt Platform — Comprehensive Test Case Suite (Auto-generated)",
    "",
    "> **Source:** Confluence BA Specifications & Stitch UI Design",
    "> **Version:** LATEST — Structured by Categories (UI/UX, Validation, Functional, Performance, Security)",
    "",
]

grouped_features = df.groupby('Feature', sort=False)

for feature, feature_df in grouped_features:
    md_content.append(f"## 🚀 Feature: {feature.upper()}")
    
    for cat in categories_order:
        cat_df = feature_df[feature_df['CustomCategory'] == cat]
        if not cat_df.empty:
            md_content.append(f"### 📌 {cat}")
            md_content.append("")
            md_content.append("| TC_ID | Mapping | Module | Title | Type | Priority | Expected Result |")
            md_content.append("|:---|:---|:---|:---|:---|:---|:---|")
            
            for _, row in cat_df.iterrows():
                # Clean up steps and expected result for inline table display
                steps = str(row['Steps']).replace('\n', '<br>')
                expected = str(row['Expected_Result']).replace('\n', '<br>')
                
                # Format Priority
                priority = row['Priority']
                if priority == 'P0': priority = f"**🔴 {priority}**"
                elif priority == 'P1': priority = f"**🟠 {priority}**"
                else: priority = f"**🟢 {priority}**"
                
                # Format Type
                tc_type = row['Type']
                if 'UI/UX' in tc_type: tc_type = f"🎨 {tc_type}"
                elif 'Negative' in tc_type: tc_type = f"⚠️ {tc_type}"
                else: tc_type = f"✅ {tc_type}"
                
                table_row = f"| `{row['TC_ID']}` | `{row['US_Mapping']}` | {row['Module']} | {row['Title']} | {tc_type} | {priority} | {steps} | {expected} |"
                md_content.append(table_row)
            md_content.append("")

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_content))

print(f"✅ Generated {md_path} successfully!")
