import pandas as pd
import glob
import os

csv_files = glob.glob('TC_POD-TShirt-Platform_v*_Full.csv')
csv_files.sort(reverse=True)
csv_file = csv_files[0]
print(f"Reading {csv_file}")

df = pd.read_csv(csv_file)

# Remove the Global UI entries
df = df[df['Feature'] != 'Global UI']

# Core screens to receive explicit UI/UX responsive & zoom tests
screens = ['Registration', 'Login', 'Gallery', 'Editor', 'Cart', 'Checkout', 'Payment', 'Order', 'Account']

new_cases = []
start_idx = 801 # Use high index to avoid TC_ID collision

for screen in screens:
    prefix = screen[:3].upper()
    
    # 1. Browser Zoom
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive & Zoom",
        "Title": f"Màn hình {screen}: Browser Zoom In/Out (50% - 200%) giữ nguyên layout",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": f"Mở trang {screen}",
        "Test_Data": "N/A",
        "Steps": f"1. Truy cập trang {screen}.\n2. Nhấn Ctrl/Cmd + [+] để Zoom In 200%.\n3. Nhấn Ctrl/Cmd + [-] để Zoom Out 50%.\n4. Cuộn và quan sát toàn màn hình.",
        "Expected_Result": "Text/SVG luôn sắc nét, không bị vỡ hạt (pixelated). Bố cục (Layout) thu phóng đúng tỷ lệ, không rớt dòng bậy bạ, không che lấp button quan trọng."
    })
    start_idx += 1
    
    # 2. Mobile/Tablet Responsive
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive & Zoom",
        "Title": f"Màn hình {screen}: Responsive Mobile & Tablet (iOS/Android, Ngang/Dọc)",
        "Type": "UI/UX",
        "Priority": "P0",
        "Precondition": f"Mở trang {screen} trên devtools hoặc máy thật",
        "Test_Data": "iPhone 14/15, Android S23/S24, iPad Pro",
        "Steps": f"1. Dùng DevTools (mô phỏng) hoặc Mobile Device thật mở trang {screen}.\n2. Kiểm tra layout màn hình dọc (Portrait) của Mobile.\n3. Xoay ngang điện thoại (Landscape).\n4. Kiểm tra tương tự cho màn hình Tablet (Dọc/Ngang).",
        "Expected_Result": "Không xuất hiện thanh cuộn ngang thừa. Các khối nội dung chuyển sang layout cột đơn (stacking) hợp lý cho Mobile. Nút bấm (Touch Targets) đủ lớn, dễ tap, không sát nhau."
    })
    start_idx += 1

new_df = pd.DataFrame(new_cases)
df_updated = pd.concat([df, new_df], ignore_index=True)

df_updated.to_csv(csv_file, index=False, quoting=1)
print(f"Successfully injected {len(new_cases)} specific responsive test cases across {len(screens)} screens!")
