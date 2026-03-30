import os
import sys
import json
import base64
import argparse
import urllib.request
import urllib.error

def main():
    parser = argparse.ArgumentParser(description="Tự động log Bug lên hệ thống Jira Cloud của công ty.")
    parser.add_argument("--project", default="TAS", help="Jira Project Key (Mặc định: TAS)")
    parser.add_argument("--type", default="Bug", help="Loại thẻ (Mặc định: Bug)")
    parser.add_argument("--env", default="TEST", help="Môi trường test (TEST/UAT/PROD)")
    parser.add_argument("--cause", choices=["Frontend", "Backend", "AI System", "Unknown"], default="Unknown", help="Phân tích nguyên nhân lỗi (Frontend/Backend/AI)")
    parser.add_argument("--summary", required=True, help="Tiêu đề Bug ngắn gọn")
    parser.add_argument("--desc", required=True, help="Mô tả chi tiết và step to reproduce")
    parser.add_argument("--impact_scope", default="", help="Mức độ ảnh hưởng (Các luồng bị ảnh hưởng)")
    parser.add_argument("--blocked_tcs", default="", help="Các Test Case ID bị block bởi lỗi này")
    parser.add_argument("--attachment", help="Đường dẫn file HÌNH ẢNH hoặc VIDEO chứng minh lỗi đính kèm")
    
    args = parser.parse_args()
    
    # 1. Parsing Credentials
    env_dict = {}
    
    # Thử tìm file .env từ thư mục hiện tại lên dần gốc dự án (phòng khi được gọi từ các folder con)
    env_path = ".env"
    current_dir = os.path.abspath(os.getcwd())
    while not os.path.exists(env_path) and current_dir != os.path.dirname(current_dir):
        current_dir = os.path.dirname(current_dir)
        env_path = os.path.join(current_dir, ".env")
        
    if not os.path.exists(env_path):
        print("❌ KHÔNG TÌM THẤY FILE .env chứa JIRA_EMAIL và JIRA_API_TOKEN!")
        sys.exit(1)
        
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, val = line.split("=", 1)
                    env_dict[key.strip()] = val.strip()

    # Xóa các ký tự unicode tàng hình có thể bị lẫn khi copy-paste
    email = env_dict.get("JIRA_EMAIL", "").strip().encode("ascii", "ignore").decode("ascii")
    token = env_dict.get("JIRA_API_TOKEN", "").strip().encode("ascii", "ignore").decode("ascii")
    jira_url = env_dict.get("JIRA_URL", "https://tryonic-ai.atlassian.net").strip().rstrip("/")
    project_key = args.project if args.project else env_dict.get("JIRA_PROJECT_KEY", "TAS").strip()

    if not email or not token or email == "your_email@domain.com":
        print("❌ Vui lòng cập nhật đúng Email và Token trong file .env!")
        sys.exit(1)

    # 2. Tạo kết nối mã hóa
    api_url = f"{jira_url}/rest/api/2/issue"
    
    final_desc = args.desc
    if args.cause != "Unknown":
        final_desc += f"\n\n---\n📌 **Root Cause Analysis (Dự kiến):** Lỗi xuất phát từ hệ thống **[{args.cause}]**"
    if args.impact_scope:
        final_desc += f"\n⚠️ **Mức độ ảnh hưởng (Impact Scope):** {args.impact_scope}"
    if args.blocked_tcs:
        final_desc += f"\n⛔ **Blocked Test Cases:** {args.blocked_tcs}"
        
    final_summary = args.summary if args.summary.startswith("[QA]") else f"[QA] [{args.env}] - {args.summary}"

    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": final_summary,
            "description": final_desc,
            "issuetype": {"name": args.type}
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    auth_str = f"{email}:{token}"
    b64_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')

    # 3. Yêu cầu request & Vượt tường lửa CSRF của Atlassian
    req = urllib.request.Request(api_url, data=data)
    req.add_header('Authorization', f'Basic {b64_auth}')
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-Atlassian-Token', 'no-check')
    req.add_header('User-Agent', 'TryonicQA-Agent/1.0') # Fake là ứng dụng để né CSRF Web

    # 4. Thực thi log
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            issue_key = result.get('key')
            browse_url = f"{jira_url}/browse/{issue_key}"
            print(f"✅ ĐÃ LOG THÀNH CÔNG: [{issue_key}] {args.summary}")
            print(f"🔗 URL: {browse_url}")
            
            # 5. Đính kèm Evidence
            if args.attachment and os.path.exists(args.attachment):
                print(f"📎 Đang tải lên file đính kèm: {os.path.basename(args.attachment)} ...")
                attach_url = f"{jira_url}/rest/api/2/issue/{issue_key}/attachments"
                
                boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                filename = os.path.basename(args.attachment)
                
                with open(args.attachment, 'rb') as f_attach:
                    file_data = f_attach.read()
                    
                body = (
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                    'Content-Type: application/octet-stream\r\n\r\n'
                ).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
                
                req_att = urllib.request.Request(attach_url, data=body)
                req_att.add_header('Authorization', f'Basic {b64_auth}')
                req_att.add_header('X-Atlassian-Token', 'no-check')
                req_att.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
                req_att.add_header('User-Agent', 'TryonicQA-Agent/1.0')
                
                try:
                    with urllib.request.urlopen(req_att) as response_att:
                        print("✅ Đã đính kèm Evidence (Hình ảnh/Video) thành công!")
                except Exception as e_att:
                    print(f"⚠️ Bug đã tạo, nhưng đính kèm file thất bại: {e_att}")
                    if hasattr(e_att, 'read'):
                        print(e_att.read().decode('utf-8'))
                        
            sys.exit(0)

            
    except urllib.error.HTTPError as e:
        print(f"❌ Lỗi HTTP: {e.code} - {e.reason}")
        raw = e.read().decode('utf-8')
        try:
            err_json = json.loads(raw)
            print(json.dumps(err_json, indent=2))
        except json.JSONDecodeError:
            print(raw)
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Có lỗi kết nối bất ngờ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
