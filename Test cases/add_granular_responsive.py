import pandas as pd
import glob

# Load the latest CSV
csv_files = glob.glob('TC_POD-TShirt-Platform_v*_Full.csv')
csv_files.sort(reverse=True)
csv_file = csv_files[0]
print(f"Reading {csv_file}")

df = pd.read_csv(csv_file)

# We need to remove the previously added generic mobile/tablet test cases.
# We can identify them by checking if Title contains "Responsive Mobile & Tablet".
df = df[~df['Title'].str.contains('Responsive Mobile & Tablet', na=False, case=False)]

screens = ['Registration', 'Login', 'Gallery', 'Editor', 'Cart', 'Checkout', 'Payment', 'Order', 'Account']
new_cases = []
start_idx = 810 # Start higher to avoid overlaps

for screen in screens:
    prefix = screen[:3].upper()
    
    # 1. iPhone (Portrait)
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive (iPhone)",
        "Title": f"Màn hình {screen}: Responsive trên iPhone (Safari/Chrome, Dọc - Portrait)",
        "Type": "UI/UX",
        "Priority": "P0",
        "Precondition": f"Mở trang {screen} trên thiết bị thật iPhone (VD: iPhone 14/15/Pro Max)",
        "Test_Data": "Thiết bị: iPhone",
        "Steps": f"1. Truy cập trang {screen} trên iPhone ở chế độ cầm dọc (Portrait).\n2. Cuộn lên/xuống toàn trang.\n3. Tap thử các nút bấm, input field.",
        "Expected_Result": "Không xuất hiện thanh cuộn ngang thừa. Các khối nội dung hiển thị cột đơn (stacking). Các nút bấm (Touch Targets) không quá nhỏ, không nằm sát mép màn hình (có padding viền an toàn hợp lý)."
    })
    start_idx += 1

    # 2. Android (Portrait)
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive (Android)",
        "Title": f"Màn hình {screen}: Responsive trên Android Phone (Chrome, Dọc - Portrait)",
        "Type": "UI/UX",
        "Priority": "P0",
        "Precondition": f"Mở trang {screen} trên thiết bị thật Android (VD: Samsung S23/S24, Pixel)",
        "Test_Data": "Thiết bị: Android Phone",
        "Steps": f"1. Truy cập trang {screen} trên điện thoại Android chế độ cầm dọc (Portrait).\n2. Cuộn lên/xuống toàn bộ trang.\n3. Focus vào các input (bàn phím ảo hiện lên).",
        "Expected_Result": "Bố cục hoàn toàn responsive (tương tự iPhone). Đảm bảo thanh bar dưới cùng của trình duyệt Android hoặc bàn phím ảo không che khuất các nút CTA quan trọng. Màn hình không bị giật/nháy (flicker)."
    })
    start_idx += 1

    # 3. iPad (Portrait)
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive (iPad)",
        "Title": f"Màn hình {screen}: Responsive trên iPad (Safari, Dọc - Portrait)",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": f"Mở trang {screen} trên thiết bị iPad / iPad Pro",
        "Test_Data": "Thiết bị: iPad",
        "Steps": f"1. Truy cập trang {screen} trên iPad ở chế độ cầm dọc (Portrait).\n2. Quan sát bố cục.",
        "Expected_Result": "Màn hình căn giữa hợp lý hoặc duy trì layout multi-column của Desktop nếu đủ không gian. Không bị rớt nút, không bị trải rộng (stretch) hình ảnh quá mức làm nhòa tỷ lệ."
    })
    start_idx += 1

    # 4. Tablet Android (Portrait)
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive (Android Tablet)",
        "Title": f"Màn hình {screen}: Responsive trên Android Tablet (Chrome, Dọc - Portrait)",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": f"Mở trang {screen} trên Tablet Android (VD: Galaxy Tab)",
        "Test_Data": "Thiết bị: Android Tablet",
        "Steps": f"1. Truy cập trang {screen} trên Tablet Android ở chế độ cầm dọc (Portrait).\n2. Thao tác trên giao diện.",
        "Expected_Result": "Giao diện hoạt động trơn tru tương tự iPad, icon và text scale đúng chuẩn tỉ lệ (không quá bé hoặc quá khổng lồ)."
    })
    start_idx += 1

    # 5. Landscape (All Mobile/Tablet)
    new_cases.append({
        "TC_ID": f"TC_{prefix}_UI_{start_idx}",
        "US_Mapping": "Global",
        "Feature": screen,
        "Module": "Responsive (Landscape)",
        "Title": f"Màn hình {screen}: Responsive chế độ Xoay Ngang (Landscape - Điện thoại/Tablet)",
        "Type": "UI/UX",
        "Priority": "P0",
        "Precondition": f"Mở trang {screen} trên mọi thiết bị Mobile hoặc Tablet",
        "Test_Data": "Orientation: Landscape",
        "Steps": f"1. Từ trạng thái dọc, xoay ngang thiết bị di động (Landscape).\n2. Đảm bảo tính năng xoay màn hình của hệ điều hành được bật.\n3. Quan sát quá trình chuyển đổi giao diện.",
        "Expected_Result": "UI tự động sắp xếp lại chiều ngang phù hợp. Ở điện thoại, Sticky Footer/Header không chiếm quá nhiều không gian theo chiều dọc (để lại đủ không gian hiển thị nội dung). Không bị lủng layout trong lúc/sau khi xoay."
    })
    start_idx += 1

new_df = pd.DataFrame(new_cases)
df_updated = pd.concat([df, new_df], ignore_index=True)

df_updated.to_csv(csv_file, index=False, quoting=1)
print(f"Successfully injected {len(new_cases)} specific device/orientation responsive test cases across {len(screens)} screens!")
