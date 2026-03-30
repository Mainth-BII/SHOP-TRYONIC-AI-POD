import pandas as pd
import io

csv_file = r'e:\BII\QA-NEW\Tool\antigravity-tryonic-main\Test cases\TC_POD-TShirt-Platform_v6_2026-03-16_Full.csv'

df = pd.read_csv(csv_file)

# 1. Update Module for US-01 Registration cases
us01_mask = (df['Feature'] == 'Registration') & (df['US_Mapping'] == 'US-01')
df.loc[us01_mask, 'Module'] = 'Signup (Email)'

# 2. Add the missing Google and Facebook cases
new_rows = [
    {
        "TC_ID": "TC_AUTH_UI_019",
        "US_Mapping": "US-02",
        "Feature": "Registration",
        "Module": "Signup (Google)",
        "Title": "Signup page: Button 'Đăng ký với Google' hiển thị",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Trang /signup",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang \n2. Quan sát UI các nút liên kết MXH",
        "Expected_Result": "Button outlined (border, no fill), full-width, có Google icon. Text: 'Đăng ký với Google'",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_AUTH_UI_020",
        "US_Mapping": "US-02b",
        "Feature": "Registration",
        "Module": "Signup (Facebook)",
        "Title": "Signup page: Button 'Đăng ký với Facebook' hiển thị",
        "Type": "UI/UX",
        "Priority": "P1",
        "Precondition": "Trang /signup",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang \n2. Quan sát UI các nút liên kết MXH",
        "Expected_Result": "Button filled blue (#1877F2), full-width, có Facebook icon. Text: 'Đăng ký với Facebook'",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_AUTH_049",
        "US_Mapping": "US-02",
        "Feature": "Registration",
        "Module": "Signup (Google)",
        "Title": "Đăng ký bằng Google thành công",
        "Type": "Positive",
        "Priority": "P0",
        "Precondition": "Email Google chưa đăng ký, Trang Signup mở",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang \n2. Click 'Đăng ký với Google'\n3. Xác thực màn hình Consent",
        "Expected_Result": "Hệ thống tạo tài khoản mới. DB: auth_provider=google. Redirect Dashboard",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    },
    {
        "TC_ID": "TC_AUTH_050",
        "US_Mapping": "US-02b",
        "Feature": "Registration",
        "Module": "Signup (Facebook)",
        "Title": "Đăng ký bằng Facebook thành công",
        "Type": "Positive",
        "Priority": "P0",
        "Precondition": "Email FB chưa đăng ký, Trang Signup mở",
        "Test_Data": "",
        "Steps": "1. Truy cập vào trang \n2. Click 'Đăng ký với Facebook'\n3. Xác thực Facebook App",
        "Expected_Result": "Hệ thống tạo tài khoản mới ngay lập tức. Redirect Dashboard. Hiển thị thông báo chào mừng",
        "Related_UC": "", "Environment": "", "Status": "", "Error_Message": "", "Screenshot_Path": "", "Executed_At": ""
    }
]

df_new = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

# 3. Fix the mapping for TC_ORD_015
df_new.loc[df_new['TC_ID'] == 'TC_ORD_015', 'US_Mapping'] = 'US-25'

# Sort by Feature, then TC_ID so registration cases group together nicely
df_new['Feature_Order'] = pd.Categorical(df_new['Feature'], ["Registration", "Login", "Account", "Profile", "Gallery", "Product", "Editor", "Cart", "Checkout", "Payment", "Order", "CMS", "AI Gen", "Credits"])
df_new = df_new.sort_values(by=['Feature_Order', 'TC_ID']).drop(columns=['Feature_Order'])

df_new.to_csv(csv_file, index=False, encoding='utf-8-sig', quoting=1)
print("Updated CSV successfully!")
