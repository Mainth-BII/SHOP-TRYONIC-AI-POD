import pandas as pd
import io

# Load the comprehensive old data
file_v4 = r'e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_v4_2026-03-13.csv'
df_old = pd.read_csv(file_v4)

# Load the new AI generated data that contains the UI/UX cases
file_v5 = r'e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_v5_2026-03-16_AI_Generated.csv'
df_new = pd.read_csv(file_v5)

# We want to extract just the UI/UX specific Editor viewpoint test cases from df_new
# because df_old already has all the other functionality (like Auth, Cart, Admin).
ui_ux_cases = df_new[df_new['TC_ID'].astype(str).str.startswith('TC_UIUI', na=False) | df_new['TC_ID'].astype(str).str.startswith('TC_UIUX', na=False) | df_new['Type'].str.contains('UI/UX', case=False, na=False)]

# Also extract the AI & Credits epics if they aren't in df_old
ai_cases = df_new[df_new['TC_ID'].astype(str).str.startswith('TC_AI', na=False)]

# Combine df_old with these missing cases
# Ensure columns match (they should)
df_combined = pd.concat([df_old, ui_ux_cases, ai_cases], ignore_index=True)

# Strict Step 1 Enforcement
# Rule: it MUST start with exactly "1. Truy cập vào trang \n2. "
def enforce_step_1(step_text):
    if not isinstance(step_text, str) or not step_text.strip():
        return "1. Truy cập vào trang "
    
    lines = step_text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return "1. Truy cập vào trang "
        
    first_line = lines[0]
    
    # Check if first line already contains the phrase exactly
    if first_line.startswith("1. Truy cập vào trang "):
        return "\n".join(lines)
        
    # Check if it has an old variation of Truy cap vao trang
    if "Truy cập vào" in first_line:
        lines[0] = "1. Truy cập vào trang "
        # Optionally re-number subsequent ones if they are missing numbers, but usually they are 2., 3.
        # Ensure second line is 2.
    else:
        # Prepend the step
        lines.insert(0, "1. Truy cập vào trang ")
        # Renumber the rest
        new_lines = []
        for idx, line in enumerate(lines):
            # remove old numbering like "1. ", "2. ", "Step 1: "
            cleaned = line.lstrip('0123456789. -').strip()
            if line.startswith("Step"):
                cleaned = line.split(":", 1)[-1].strip() if ":" in line else line.split(" ", 2)[-1].strip()
            if idx == 0:
                 new_lines.append(line) # keep the exact string for step 1
            else:
                 new_lines.append(f"{idx+1}. {cleaned}")
        lines = new_lines
        
    return "\n".join(lines)

df_combined['Steps'] = df_combined['Steps'].apply(enforce_step_1)

# Save to a new CSV V6 mapping
output_csv = r'e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_v6_2026-03-16_Full.csv'
df_combined.to_csv(output_csv, index=False, encoding='utf-8-sig', quoting=1) # quoting=1 means csv.QUOTE_ALL essentially, safely quoting newlines

print(f"✅ Successfully combined. Old rows: {len(df_old)}, New UI/AI cases added: {len(ui_ux_cases) + len(ai_cases)}.")
print(f"✅ Total rows exported to V6: {len(df_combined)}")

