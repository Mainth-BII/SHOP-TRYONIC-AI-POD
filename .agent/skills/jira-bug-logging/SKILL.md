---
name: jira-bug-logging
description: "Quy trình cho phép các QA Agent tự động log bug, tạo ticket lên Jira thông qua REST API (Basic Auth)."
# 🐞 Jira Bug Logging Skill

Kỹ năng này cung cấp các nguyên tắc và công cụ để AI Agent đóng vai trò là một **Chuyên gia QA (Senior QA/Tester)**, tự động mô tả, đánh giá và khởi tạo thẻ Bug (Issue) chuyên nghiệp lên hệ thống Jira Cloud của dự án (mặc định là `TAS`).

---

## 🏗️ Nguyên lý & Persona

1. **Đóng vai Chuyên gia QA:**
   - Bạn là một Senior QA chuyên nghiệp. Mọi Bug log (báo cáo lỗi) phải mạch lạc, logic, đúng trọng tâm kỹ thuật, đi kèm bằng chứng (Evidence) rõ ràng.
   - Vị trí hiện tại: `.env` phải chứa `JIRA_EMAIL` và `JIRA_API_TOKEN` hợp lệ.

2. **Cấu trúc Bug Chuyên Nghiệp Tối Thiểu:**
   - **Summary (Tiêu đề):** `[QA] [<Môi trường>] - [<Tên Phân hệ>] Mô tả ngắn gọn lỗi` (VD: `[QA] [TEST] - [Design Studio] Size và Màu trên StatusBar không thể click trực tiếp`).
   - **Environment:** Trình duyệt, OS, Viewport (Desktop/Mobile) đang test.
   - **Steps to Reproduce (Các bước tái hiện):** Phải viết dưới dạng list 1, 2, 3...
   - **Actual Result (Hiện trạng):** Lỗi là gì, UI bị méo, API trả 500, hay không submit được?
   - **Expected Result (Kết quả kỳ vọng):** Đúng spec/UI sẽ như thế nào.
   - **Root Cause Analysis (Phân tích nguyên nhân):** Dựa vào log console, network hay log server để phán đoán lỗi thuộc trách nhiệm của bên nào: `Frontend` (UI/UX, logic React), `Backend` (Lỗi API, logic DB), hoặc `AI System` (Không gen được ảnh, prompt sai).
   - **Impact Scope (Mức độ ảnh hưởng):** Đánh giá tính năng này hỏng sẽ kéo theo các luồng luân chuyển nào hỏng theo (VD: "Người dùng không thể thanh toán", "Mất data user").
   - **Blocked Test Cases:** Ghi rõ ID của các Test Case bị chặn (Fail) bởi Bug này (VD: `TC-POD-152`, `TC-POD-153`).
   - **Evidence (Hình ảnh/Video):** BẮT BUỘC phải đính kèm evidence (screenshot/video lỗi từ `.agent/output` hoặc được cấp) nếu có.

3. **Luồng Attach Evidence Của Atlassian Jira:**
   - Token & Email + `X-Atlassian-Token: no-check` dùng cho mọi API request.
   - Evidence đính kèm sẽ được script lo thông qua endpoint `/rest/api/2/issue/{issueIdOrKey}/attachments` bằng chuẩn Multipart/form-data.

---
   - Bất cứ khi nào Agent khảo sát (Explore) web hoặc mã nguồn và xác định chắc chắn đó là 1 sự cố nghiệm trọng.

---

## 🛠️ Công Cụ Cấp Phát (Scripts)

Agent **KHÔNG ĐƯỢC PHÉP CHẠY RAW CURL CỨNG**. Thay vào đó, bạn phải sử dụng script cung cấp sẵn của thư mục này để Log qua Python CLI:

### 1. `scripts/log_jira_ticket.py`
Script xử lý gọi API nhanh chóng, đảm bảo auth bypass các chính sách XSRF của Atlassian. Thư mục chứa script là: `.agent/skills/jira-bug-logging/scripts`.

**Cách dùng mẫu từ Terminal/bash_command:**
```bash
python .agent/skills/jira-bug-logging/scripts/log_jira_ticket.py \
  --project "TAS" \
  --type "Bug" \
  --env "TEST" \
  --cause "Frontend" \
  --summary "[Design Studio] Khung password bị lệch trên Mobile" \
  --desc "Khi resize trình duyệt xuống 375px, khung mật khẩu bị méo..." \
  --impact_scope "Luồng Login/Register bị khựng trên thiết bị màn nhỏ." \
  --blocked_tcs "TC-LOGIN-001, TC-LOGIN-002" \
  --attachment "/duong/dan/anh/loi.png"
```
*(Lưu ý: Script sẽ tự động ghép Tiêu đề thành `[QA] [TEST] - [Design Studio] Khung password...` dựa trên cờ `--env` và `--summary`).*

---

## 🚦 Quy Trình Bắt Buộc (Socratic Gate)

**QUAN TRỌNG:** Agent tuyệt đối **KHÔNG ĐƯỢC TỰ ĐỘNG BẮN HÀNG LOẠT BUGS MÀ KHÔNG CÓ REPORT/ON-WATCHING CỦA USER.**
1. Trước khi log bug tự động, Agent phải tóm tắt lại danh sách Bugs sẽ log (Summary Preview).
2. Hãy hỏi User: *"Đã sẵn sàng push {N} bugs này lên Jira board chưa?"*
3. Chỉ thực thi file script sau khi có lệnh đồng ý (`ok`, `log đi`...).
