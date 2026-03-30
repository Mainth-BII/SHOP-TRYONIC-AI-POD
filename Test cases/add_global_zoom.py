import pandas as pd
import glob

# Find latest csv
csv_pattern = "TC_POD-TShirt-Platform_v*_Full.csv"
csv_files = glob.glob(csv_pattern)
csv_files.sort(reverse=True)
csv_file = csv_files[0]

print(f"Opening {csv_file} to append global browser zoom cases...")

df = pd.read_csv(csv_file)

# Define new test cases
new_cases = [
    {
        "TC_ID": "TC_GLB_UI_001",
        "US_Mapping": "Global",
        "Feature": "Global UI",
        "Module": "Browser Responsiveness",
        "Title": "Platform: Zoom In trình duyệt (Browser Zoom) lên 200% không bị vỡ nét",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Mở bất kỳ trang nào (Gallery, Editor, Checkout)",
        "Test_Data": "N/A",
        "Steps": "1. Truy cập vào trang web trên Desktop (Chrome/Edge).\n2. Nhấn phím Ctrl và phím + (hoặc dùng Menu Browser) để Zoom In lên mức 150% - 200%.\n3. Cuộn trang và quan sát text, hình ảnh SVG, layout.",
        "Expected_Result": "Text và hình ảnh SVG vẫn giữ độ sắc nét, không bị pixelated (vỡ hạt). Bố cục (Layout) thích ứng responsive như màn hình tablet/mobile nhỏ, các phần tử không đè lên nhau (overlap) và vẫn đọc/click được bình thường."
    },
    {
        "TC_ID": "TC_GLB_UI_002",
        "US_Mapping": "Global",
        "Feature": "Global UI",
        "Module": "Browser Responsiveness",
        "Title": "Platform: Zoom Out trình duyệt xuống 50% hiển thị căn giữa hợp lý",
        "Type": "UI/UX",
        "Priority": "P2",
        "Precondition": "Mở bất kỳ trang nào",
        "Test_Data": "N/A",
        "Steps": "1. Truy cập vào trang web.\n2. Nhấn phím Ctrl và phím - (hoặc dùng Menu Browser) để Zoom Out xuống mức 50%.\n3. Quan sát tổng thể trang.",
        "Expected_Result": "Các phần tử thu nhỏ tỷ lệ đồng đều. Nội dung trang được căn giữa màn hình (center-aligned) hoặc dàn đều hợp lý với phần không gian viền (white-space) cân đối, không bị lệch hẳn sang một bên."
    }
]

# Append using concat
new_df = pd.DataFrame(new_cases)
df_updated = pd.concat([df, new_df], ignore_index=True)

# Save back to specific CSV to be caught by the export scripts
df_updated.to_csv(csv_file, index=False, quoting=1) # quoting=csv.QUOTE_ALL essentially

print("Successfully injected Global Zoom cases. Run export_tc_md.py and export_tc_multisheet.py next.")
