import pandas as pd
import io

csv_file = r'e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_v6_2026-03-16_Full.csv'

df = pd.read_csv(csv_file)

# Drop any existing Zoom or Pan cases so we can cleanly re-insert them without duplicates
drop_mask = df['TC_ID'].isin(['TC_DES_UI_029', 'TC_DES_UI_030', 'TC_UIUX_001', 'TC_UIUX_002'])
df = df[~drop_mask]

# Create clean, distinct test cases for Zoom and Pan
new_cases = [
    {
        "TC_ID": "TC_DES_UI_029a",
        "US_Mapping": "US-15",
        "Feature": "Editor",
        "Module": "Canvas Viewpoint",
        "Title": "Canvas: Zoom In / Zoom Out (bằng UI Buttons)",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Mở trang Editor",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang Editor\n2. Click nút + (Zoom In) và nút - (Zoom Out) trên UI",
        "Expected_Result": "Canvas và các layer phóng to/thu nhỏ mượt mà. Tâm zoom focus vào giữa màn hình.",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_DES_UI_029b",
        "US_Mapping": "US-15",
        "Feature": "Editor",
        "Module": "Canvas Viewpoint",
        "Title": "Canvas: Zoom In / Zoom Out (bằng Ctrl + Scroll)",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Mở trang Editor",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang Editor\n2. Nhấn giữ phím Ctrl và lăn chuột lên (Zoom In) / xuống (Zoom Out)",
        "Expected_Result": "Canvas và các layer phóng to/thu nhỏ mức zoom tương ứng mượt mà. Tâm zoom focus vào vị trí con trỏ chuột.",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_DES_UI_030a",
        "US_Mapping": "US-15",
        "Feature": "Editor",
        "Module": "Canvas Viewpoint",
        "Title": "Canvas: Pan (Di chuyển vùng nhìn bằng Space + Drag)",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Mở trang Editor, mức zoom > 100%",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang Editor và zoom canvas lớn hơn màn hình\n2. Nhấn giữ phím Space và click kéo thả chuột (Drag)",
        "Expected_Result": "Con trỏ đổi thành hình bàn tay (hand tool). Vùng nhìn di chuyển mượt mà lên/xuống/trái/phải để xem các góc khác của thiết kế.",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_DES_UI_030b",
        "US_Mapping": "US-15",
        "Feature": "Editor",
        "Module": "Canvas Viewpoint",
        "Title": "Canvas: Pan (Di chuyển vùng nhìn bằng Thanh Cuộn chuột/Scrollbars)",
        "Type": "UI/UX",
        "Priority": "P2",
        "Precondition": "Mở trang Editor, mức zoom > 100%",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang Editor và zoom canvas lớn hơn màn hình\n2. Kéo thả các thanh scroll ngang/dọc trên màn hình (nếu có) hoặc dùng con lăn chuột",
        "Expected_Result": "Vùng nhìn di chuyển chính xác theo thanh cuộn hỗ trợ người dùng không quen phím tắt.",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    }
]

df_new = pd.concat([df, pd.DataFrame(new_cases)], ignore_index=True)

# Remove any duplicated rows (just to be safe against double-merges)
df_new = df_new.drop_duplicates(subset=['TC_ID', 'Title'])

# Export back to CSV
df_new.to_csv(csv_file, index=False, encoding='utf-8-sig', quoting=1)
print("Updated CSV with distinct Zoom/Pan cases successfully!")
