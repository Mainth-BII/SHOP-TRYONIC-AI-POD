---
name: qa-functional-testing
description: QA functional test case writing standards. Covers step-by-step format, naming conventions, test types, expected result rules, and UI control viewpoint checklist for manual and automation-ready test cases.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# QA Functional Testing Patterns

> Test cases are executable specifications. Every step must be clear enough for a new tester to execute without asking questions.

---

## 0. The QA Agent Workflow (SOP)

Khi nhận được yêu cầu viết Test Case từ tài liệu (BA spec, Jira, Figma), Agent **BẮT BUỘC** phải tuân theo luồng 5 bước (5-Phase Flow) sau đây trước khi vội vàng spit ra test cases:

### Phase 1: Knowledge Acquisition (Phân tích tài liệu)
- **Đọc kỹ Spec/Requirements:** Trích xuất toàn bộ User Stories, Acceptance Criteria, Business Rules, Validation rules (min/max/format).
- **Đọc UI/UX Design (nếu có):** Ánh xạ UI elements trên Figma/Mockup với Spec. Identify các UI controls sẽ áp dụng Viewpoint (Section 11).

### Phase 2: Traceability & Gap Analysis (Lập Map)
- Lập mapping: `Feature → User Story → Business Rules`.
- **Socratic Trigger:** Nếu phát hiện Spec thiếu logic (VD: có max mà thiếu min, có happy path mà thiếu error message, logic mâu thuẫn), Agent phải DỪNG LẠI và hỏi (Ask for clarification) người dùng trước khi generate.

### Phase 3: Test Case Design (Áp dụng Rule)
- Chạy **Coverage Checklist (Section 9)** để đảm bảo mỗi Business Rule sinh ra đủ Happy Path, Negative, Boundary, Edge Case, Security (nếu cần).
- Chạy **UI Control Viewpoint (Section 11)** cho các màn hình để đảm bảo cover đủ Visual/Layout/Canvas checks.
- Bắt đầu Draft TC, áp dụng triệt để các **Writing Rules (Section 4, 5, 7, 8)**. Chú ý Rule Bắt buộc ở Step 1 (`1. Truy cập vào trang `).

### Phase 4: Self-Review & Refinement
- Tự đối chiếu draft TC với **Anti-Patterns (Section 10)**. Nếu vi phạm (ví dụ: gộp nhiều check vào 1 TC, từ ngữ mơ hồ), phải đập đi viết lại ngay.
- Đảm bảo Priority (P1/P2/P3) được assign đúng chuẩn (Section 6).

### Phase 5: Formatting & Export
- Format output ra bảng Markdown hoặc CSV đúng cấu trúc cột chuẩn (Section 2).
- Nếu user yêu cầu xuất file, áp dụng **Execution Export Format (Section 13)** dùng Python script để sinh ra Multi-sheet Excel chuẩn.

---

## 1. TC_ID Convention

| Pattern | Format | Example |
|---------|--------|---------|
| Standard | `TC_[FEATURE]_[3-digit number]` | `TC_LOGIN_001` |
| Sub-feature | `TC_[FEATURE]_[SUBFEATURE]_[3-digit number]` | `TC_CREDIT_DEDUCT_001` |
| Numbering | Sequential per feature, start from 001 | `TC_LOGIN_001`, `TC_LOGIN_002` |

**Rules:**
- FEATURE name: UPPERCASE, no spaces, use underscore
- Never reuse a TC_ID even if TC is deleted
- If feature is renamed, keep original TC_ID prefix for traceability

---

## 2. Test Case Structure (CSV Columns)

| Column | Required | Description |
|--------|----------|-------------|
| `TC_ID` | ✅ | Unique identifier per convention above |
| `Feature` | ✅ | Top-level feature name (e.g., Authentication) |
| `Module` | ✅ | Sub-module (e.g., Login, Logout, Reset Password). **CRITICAL_RULE**: Must be explicit if a feature has multiple methods. Example: Use `Signup (Email)` vs `Signup (Google)` instead of just `Signup`. Use `Zoom (UI Buttons)` vs `Zoom (Ctrl+Scroll)` instead of just `Zoom`. |
| `Title` | ✅ | One sentence — what this TC verifies |
| `Type` | ✅ | See Type table below |
| `Priority` | ✅ | P1 / P2 / P3 |
| `Precondition` | ✅ | System state before test starts |
| `Test_Data` | ✅ | Real values, use `|` to separate multiple values |
| `Steps` | ✅ | Numbered, click-level detail |
| `Expected_Result` | ✅ | Specific and measurable |
| `Related_UC` | ✅ | UC reference from BA document |

---

## 3. Test Types

| Type | Description | Example |
|------|-------------|---------|
| `Positive` | Happy path — valid input, expected success | Login with correct credentials |
| `Negative` | Invalid input or unauthorized action | Login with wrong password |
| `Boundary` | Min, max, min-1, max+1 values | Password length = 8, 7, 33, 32 |
| `Edge Case` | Unusual but valid scenarios | Login with email containing special chars |
| `UI/UX` | Visual integrity, layout, responsive | Button label, error message position |
| `API` | Direct API call validation | POST /login returns 200 with token |
| `Performance` | Response time under load condition | Login response < 2s under 100 concurrent users |

---

## 4. Steps — Writing Rules

**Level of detail: Click-level (every action is one step)**

### Format
```
1. [Action] [Object] [Value if applicable]
2. [Action] [Object] [Value if applicable]
...
N. Observe [what to look at]
```

### Good vs Bad Examples

| ❌ Bad | ✅ Good |
|--------|---------|
| Đăng nhập vào hệ thống | 1. Mở trình duyệt, truy cập [URL]<br>2. Nhập email: user@test.com vào field Email<br>3. Nhập password: Password123 vào field Password<br>4. Click button "Đăng nhập" |
| Thực hiện chức năng | 1. Click menu "Cài đặt"<br>2. Click tab "Tài khoản"<br>3. Tìm section "Đổi mật khẩu" |
| Kiểm tra kết quả | Quan sát màn hình sau khi click |

### Rules
- Mỗi step = 1 hành động duy nhất
- Ghi rõ giá trị test data ngay trong step (không để "nhập email hợp lệ")
- Step cuối luôn là "Quan sát [đối tượng cụ thể]"
- Không dùng từ mơ hồ: "phù hợp", "đúng", "hợp lệ" — phải ghi giá trị thực

---

## 5. Expected Result — Writing Rules

### Must Be
- **Specific**: Ghi rõ text, giá trị, trạng thái cụ thể
- **Measurable**: Có thể Pass/Fail rõ ràng, không cần phán xét
- **Complete**: Cover cả UI response + data change nếu có

### Good vs Bad Examples

| ❌ Bad | ✅ Good |
|--------|---------|
| Đăng nhập thành công | Hệ thống redirect sang trang Dashboard. Hiển thị tên user "Nguyễn Văn A" ở góc phải header |
| Hiển thị thông báo lỗi | Hiển thị message: "Email hoặc mật khẩu không đúng" màu đỏ bên dưới field Password |
| Hệ thống hoạt động đúng | Balance giảm từ 50 xuống 35. Màn hình hiển thị "Trừ 15 credit thành công" |
| UI hiển thị đúng | Button "Xác nhận" không bị cắt, hiển thị đủ text, không overflow container trên màn hình 375px |

### For UI/UX Test Cases
Expected result MUST specify:
- Text hiển thị chính xác (copy từ BA doc)
- Vị trí element (trên/dưới/cạnh element nào)
- Không bị clipped, overflow, hoặc hidden bởi container
- Responsive: viewport cụ thể (375px mobile, 768px tablet, 1280px desktop)

### Visual Integrity — Checklist khi viết UI TC
Khi BA document có layout/UI, kiểm tra và ghi vào TC:
- [ ] Fixed-width elements: có container cố định width không? → Test trên mobile có bị vỡ layout không?
- [ ] Tables/grids: có scroll ngang khi overflow không, hay bị ẩn?
- [ ] Buttons/CTAs: text không bị cắt, padding đủ, không bị hidden bởi overlay
- [ ] Error messages: hiển thị đúng vị trí, không bị đẩy ra ngoài viewport
- [ ] Forms: input fields không bị shrink hoặc overlap trên màn hình nhỏ

**Classify Visual Issues:**
| Severity | Condition |
|----------|-----------|
| UI/UX Blocker | Element bị hidden hoàn toàn, user không thể thao tác |
| UI/UX Major | Layout vỡ, text bị cắt làm mất nghĩa |
| UI/UX Minor | Spacing lệch, cosmetic không ảnh hưởng chức năng |

### For API Test Cases
Expected result MUST specify:
- HTTP status code
- Response body fields và giá trị
- Response time nếu là performance TC

---

## 6. Priority Assignment

| Priority | Assign When |
|----------|-------------|
| **P1** | Core business flow, payment, auth, data integrity |
| **P1** | User-facing error messages |
| **P2** | Alternative flows, secondary features |
| **P2** | Boundary values, edge cases |
| **P3** | Minor UI, cosmetic, nice-to-have |

**Rule:** Nếu feature này fail → user không dùng được sản phẩm → P1

---

## 7. Precondition — Writing Rules

Mô tả trạng thái hệ thống **trước khi bắt đầu** TC, không phải setup steps.

| ❌ Bad | ✅ Good |
|--------|---------|
| Mở app | User đã có tài khoản active, chưa đăng nhập |
| Có dữ liệu | Database có sản phẩm ID=123, giá=150,000 VND, stock=10 |
| Đăng nhập rồi | User đã đăng nhập với role Admin, đang ở trang Dashboard |

---

## 8. Test Data — Writing Rules

- Luôn dùng **giá trị thực**, không dùng placeholder
- Dùng `|` để ngăn cách nhiều giá trị: `email: user@test.com | password: Pass@123`
- Boundary values ghi rõ: `password length: 7 (min-1), 8 (min), 32 (max), 33 (max+1)`
- Data nhạy cảm: dùng data giả nhưng đúng format (số thẻ test, email test)

---

## 8b. Test Steps — Writing Rules

- **Bắt buộc:** Mọi Test Case, không phân biệt Module hay Feature (kể cả UI/UX, Functional, Security), đều phải bắt đầu Step 1 bằng đúng câu lệnh điều hướng: `1. Truy cập vào trang `.
- Các step tiếp theo được đánh số thứ tự tuần tự (2, 3, 4...).
- Viết action rõ ràng (VD: `Click`, `Nhập`, `Chọn`, `Kéo thả`), không viết chung chung.

---

## 9. Coverage Checklist — Per Use Case

Mỗi Use Case phải có tối thiểu:

- [ ] **1 Positive TC** — happy path hoàn chỉnh từ đầu đến cuối
- [ ] **1 Negative TC cho mỗi Business Rule** — BR1 → TC Negative riêng, BR2 → TC Negative riêng, không gộp
- [ ] **1 Boundary TC cho mỗi boundary value** — mỗi field có min/max cần test: min-1, min, max, max+1
- [ ] **BVA mandatory cho MỌI text input/textarea** — tối thiểu 3 TCs: min length (1 char), max length (over limit), whitespace-only. Đây là yêu cầu ISTQB bắt buộc.
- [ ] **1 TC cho mỗi error message** — verify exact error message text như định nghĩa trong BA, không paraphrase
- [ ] **1 UI TC** nếu có màn hình — kiểm tra layout, text, responsive (bắt buộc check Visual Integrity)
- [ ] **1 API TC** nếu có endpoint liên quan — verify status code + response body
- [ ] **1 Security TC** nếu có login/auth/payment — XSS, injection, bypass, rate limit
- [ ] **1 Edge Case TC** — unusual but valid scenarios (empty state, concurrent, data migration)
- [ ] **1 TC cho MỖI button/link/interactive element** — Mọi nút bấm, link, toggle trên màn hình PHẢI có ít nhất 1 Functional TC kiểm tra hành vi khi click (xem **Section 16: Interactive Element Inventory**)

**Mapping rule:**
```
1 Business Rule   → tối thiểu 1 Negative TC
1 Boundary Field  → tối thiểu 4 Boundary TC (min-1, min, max, max+1)
1 Error Message   → tối thiểu 1 TC verify exact text
1 UC Main Flow    → tối thiểu 1 Positive TC
1 Auth/Login Flow → tối thiểu 5 Security TC (rate limit, lock, bypass, concurrent, audit log)
1 Payment Flow    → tối thiểu 3 TC (success, fail/timeout, callback error)
1 CRUD Feature    → tối thiểu 1 Edge Case TC (empty state, duplicate, inactive item)
```

### 9b. Security Testing Patterns — Mandatory for Auth/Payment

> **Bắt buộc áp dụng khi feature có login, authentication, hoặc payment.**

| Pattern | Kịch bản | Ví dụ TC |
|---------|----------|----------|
| **Rate Limit/Lock** | Login sai N lần → lock M phút | Login sai 5 lần → lock 15 phút |
| **Lock Scope** | Lock per-account, không per-IP | 2 máy khác IP cùng sai → vẫn lock |
| **Counter Reset** | Counter về 0 sau login thành công | Sai 3 lần → login đúng → sai 1 → counter = 1 |
| **Bypass Attempt** | OAuth login khi account bị lock | Google login cùng email đã bị lock |
| **Information Leak** | Error message không tiết lộ email tồn tại | "Email hoặc mật khẩu không đúng" (chung) |
| **Server-side Lock** | Lock persist sau clear cookies | Clear localStorage → vẫn lock |
| **Precise Timing** | Lock time chính xác (14:50 still locked) | Thử login 14:50 → lock. 15:00 → unlock |
| **API Rate Limit** | Gọi API login trực tiếp bypass UI | POST /api/login 5+ lần → 429 |
| **Concurrent Requests** | Race condition nhiều request đồng thời | 10 request sai cùng lúc → lock đúng |
| **Audit Log** | Log ghi nhận failed attempts | Log: timestamp, IP, email, số lần, lock time |
| **XSS/Injection** | Input chứa script tags, SQL | `<script>alert(1)</script>` trong Name |
| **Token/Session** | Session expiry, remember me | Default 24h, remember me 30d |

### 9c. Edge Case Depth Patterns — Mandatory Per Feature

> **Mỗi feature phải kiểm tra các kịch bản "unusual but valid" này.**

| Pattern | Áp dụng khi | Ví dụ |
|---------|------------|-------|
| **Empty State** | Bất kỳ danh sách nào | Giỏ hàng trống, My Orders trống, Gallery rỗng |
| **Double Submit** | Bất kỳ action nào | Double click Generate, double click Checkout |
| **Data Migration** | Guest → Login | Design + cart giữ nguyên sau đăng nhập |
| **Network Error** | Bất kỳ API call nào | Mất mạng giữa payment/generate |
| **Inactive/Deleted Item** | CRUD operations | Re-order SP đã ngưng bán |
| **Cross-device** | Login/session | Login nhiều device cùng lúc |
| **Encoding** | Text input | Tiếng Việt có dấu, emoji, special chars |
| **File Edge Cases** | Upload | File 0KB, file đúng max size, sai format |

---

## 10. Anti-Patterns — Never Do

| ❌ Anti-pattern | Vấn đề | ✅ Thay bằng |
|-----------------|--------|--------------|
| Steps gộp nhiều hành động | Không biết bước nào fail | Tách thành từng step đơn |
| Expected result dùng "đúng", "thành công" | Không thể Pass/Fail khách quan | Ghi text/giá trị cụ thể |
| **Expected result dùng "hoạt động bình thường"** | **BANNED PHRASE (ISTQB)** — không đo lường được | **Ghi behavior cụ thể: "chuyển sang page X", "hiển thị loading state"** |
| **Expected result dùng "hoặc" (A hoặc B)** | Mơ hồ — tester không biết Pass/Fail | **Chọn 1 expected result duy nhất, hoặc tách thành 2 TCs** |
| Test data dùng "[valid email]" | Executor phải tự đoán | Ghi `user@test.com` |
| 1 TC test nhiều behavior | Khi fail không biết lỗi ở đâu | Tách thành nhiều TC |
| Precondition thiếu state | Executor setup sai môi trường | Ghi đầy đủ trạng thái ban đầu |
| Skip negative TC | Bỏ sót lỗi validation quan trọng | Bắt buộc có negative cho mỗi BR |
| **Tạo nhiều sub-section Validation rải rác** | Khó quản lý, dễ bỏ sót | **Gộp TẤT CẢ validation TCs (BVA, XSS, empty, boundary) vào 1 section `📌 Validation` duy nhất** |
| **Thiếu BVA cho text input** | **Bỏ sót boundary bugs nghiêm trọng** | **Mọi text input/textarea phải có tối thiểu 3 BVA TCs** |
| **Negative TC để trong section Functional** | Gây nhầm lẫn test type | **Chuyển negative TCs về section Validation** |

---

---

## 11. UI Control Viewpoint — Checklist per Control Type

Khi gặp một UI control trong BA document, dùng bảng viewpoint tương ứng để đảm bảo không bỏ sót test scenario. Mỗi dimension = ít nhất 1 TC.

### Viewpoint Dimensions (áp dụng cho hầu hết control)

| Dimension | Kiểm tra gì |
|-----------|-------------|
| **Title** | Label/title hiển thị đúng text, đúng locale, không truncate |
| **Initial Value** | Giá trị mặc định khi control mới load — đúng spec chưa? |
| **Placeholder** | Placeholder text hiển thị khi chưa nhập, biến mất khi nhập |
| **Attribute** | Alignment, font, color, spacing, padding đúng design; ARIA role/label đúng |
| **Behaviour** | Tương tác click/hover/focus đúng spec; không layout shift |
| **Responsive** | Hiển thị đúng trên mobile (375px), tablet (768px), desktop (1280px) |
| **Select/Input** | Happy path chọn/nhập đúng giá trị |
| **Display** | Dữ liệu render đúng sau action (upload, save, load) |
| **Mapping data DB** | Sau khi save: data lưu đúng vào DB field `{tbl.field}` |
| **Format** | Date/number/currency format đúng locale; text wrap đúng |

---

### Viewpoint theo từng Control Type

#### 🔤 Textbox / Input Field
| Dimension | Test case cần có |
|-----------|-----------------|
| Title | Label hiển thị đúng |
| Initial Value | Giá trị mặc định đúng spec |
| Placeholder | Placeholder visible → ẩn khi nhập |
| Attribute — Min/Max length | Nhập đúng min, min-1, max, max+1 |
| Attribute — Blank/NULL | Blank, NULL, space fullsize, space halfsize |
| Attribute — Special chars | `~!@#$%^&*()_+":?><{}` |
| Attribute — Character types | Numeric, alphabet, special, auto-convert (hoa↔thường, fullsize↔halfsize) |
| Attribute — State | Active / Inactive / Visible / Invisible |
| Responsive | Resize đúng trên các breakpoint |
| Mapping data DB | Data saved đúng field sau submit |

#### 🔘 Radio Button
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Tất cả unselected by default (trừ khi spec có default) |
| Behaviour | Chọn 1 → các option khác tự deselect |
| Attribute | ARIA checked state đúng |

#### ☑️ Checkbox
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Unchecked by default (trừ khi spec có default) |
| Behaviour | Check/uncheck toggle đúng; submit với giá trị checked/unchecked |
| Attribute | aria-checked đúng; keyboard Space toggle |

#### 📝 Textarea
| Dimension | Test case cần có |
|-----------|-----------------|
| Attribute | Size, border, font, placeholder đúng design |
| Behaviour | Nhập nhiều dòng không bị giới hạn (trừ maxlength) |
| Attribute — Maxlength | Nhập đúng max, max+1 |

#### 🔒 Password Field
| Dimension | Test case cần có |
|-----------|-----------------|
| Attribute | Size, border, placeholder đúng |
| Behaviour | Show/Hide toggle hoạt động đúng |
| Attribute — Min/Max | Boundary values |

#### 📁 File Upload
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Blank khi chưa upload |
| Behaviour — Allowed format | Upload đúng format → success |
| Behaviour — Disallowed format | Upload sai format → error message |
| Select — File size | size < max → allow; size = max → allow; size > max → error |
| Select — Empty file | Upload file 0KB → error |
| Select — Multiple files | Behavior đúng spec (allow/replace/error) |
| Display | Tên file hiển thị sau upload thành công |
| Mapping data DB | File path/data lưu đúng DB field |

#### 📊 Table / Grid
| Dimension | Test case cần có |
|-----------|-----------------|
| Header | Column header label đúng |
| Display | Dữ liệu render đúng từ API/DB |
| Behaviour | Sort, filter, search hoạt động đúng |
| Pagination | Chuyển trang đúng, hiển thị đúng số record |
| Responsive | Horizontal scroll khi overflow, không bị ẩn column |

#### 🔔 Modal / Popup Dialog
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Mở centered, focus trapped, body scroll locked, backdrop hiển thị |
| Behaviour | Đóng bằng X, Cancel, click backdrop, ESC key |
| Display DB Value | Edit mode pre-fill đúng dữ liệu từ DB |
| Attribute | aria-modal, role=dialog đúng |
| Form validation | Submit với required fields trống → inline error đúng vị trí |

#### 🍞 Snackbar / Toast
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Hiển thị đúng vị trí (top/bottom), đúng severity style |
| Behaviour | Auto-dismiss sau đúng duration; close icon hoạt động |
| Display | Text/variable interpolation đúng |
| Attribute | aria-live region đúng |

#### 🎨 Canvas / Editor Workspace
| Dimension | Test case cần có (Đặc thù Editor) |
|-----------|-----------------|
| Viewport | Zoom In/Out mượt mà bằng chuột/keyboard, focus đúng điểm |
| Viewport | Pan (Di chuyển vùng nhìn) khi Zoom sâu |
| Alignment | Smart Guides (Đường gióng ngang/dọc) hiển thị và bắt dính đúng |
| Keyboard | Hỗ trợ các Shortcuts cơ bản (Del, Undo/Redo, Copy/Paste) |
| Attribute | Layer Opacity điều chỉnh được và re-render chính xác |

#### 📈 Chart / Graph
| Dimension | Test case cần có |
|-----------|-----------------|
| Display data | Data đúng từ backend; min/max/avg đúng; negative/zero values |
| Function | Export to image/PDF; download CSV/Excel |
| Behaviour | Hover tooltip đúng data; click drill-down; zoom/filter/sort |
| Accuracy | Render đúng thời gian; không lag với large data |
| Resolution | Hiển thị đúng trên mobile/tablet/desktop |

#### 🗺️ Map Control
| Dimension | Test case cần có |
|-----------|-----------------|
| Labels | Visible, không overlap, readable ở các zoom level |
| Resolution | Hiển thị đúng trên các breakpoint |
| Search | Tìm kiếm địa điểm đúng kết quả |
| Behaviour | Zoom in/out; marker click; layer toggle |

#### 🧭 Sidebar / Navigation Menu
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Current route highlighted; collapsed state có tooltip |
| Behaviour | Click item → highlight update; parent expand |
| Display DB Value | Items đúng với role-based visibility từ server |
| Attribute | Truncate với tooltip khi label dài |

#### 🧩 Stepper / Wizard
| Dimension | Test case cần có |
|-----------|-----------------|
| Initial Value | Step 1 active; future steps disabled |
| Behaviour | Next/Back navigation đúng; step header highlight |
| Gate validation | Required fields trống → không qua step; error hiển thị |
| Display DB Value | Summary step hiển thị đúng collected values |

#### 📎 Button / Link / Hyperlink
| Dimension | Test case cần có |
|-----------|-----------------|
| Title | Label đúng text, đúng locale |
| Attribute | Màu sắc, kích thước đúng state (default/hover/focus/disabled) |
| Behaviour | Click đúng action; disabled không clickable |

#### 🖼️ Image / Icon
| Dimension | Test case cần có |
|-----------|-----------------|
| Display | Ảnh load đúng, không broken, đúng kích thước |
| Initial Value | Placeholder hiển thị khi ảnh chưa load |
| Mapping data DB | URL/path lấy đúng từ DB |

#### ⬇️ Download / Export
| Dimension | Test case cần có |
|-----------|-----------------|
| Format file | Đúng định dạng (PDF/Excel/CSV) theo spec |
| Data | Dữ liệu trong file export đúng và đầy đủ |
| Behaviour | Download trigger đúng; không bị block bởi browser |

---

## 12. Viewpoint — Quick Reference khi viết TC

Trước khi viết TC cho bất kỳ màn hình nào, chạy qua checklist nhanh:

```
0. 🔴 INVENTORY: Liệt kê TẤT CẢ buttons, links, toggles, icons clickable trên màn hình → Mỗi element = ít nhất 1 TC (Section 16)
1. Control này thuộc loại gì? → Tra bảng viewpoint tương ứng
2. Có dimension nào chưa có TC không? → Thêm vào
3. Validation rules từ BA → Mỗi rule = 1 Negative TC
4. Error messages → Mỗi message = 1 TC verify exact text
5. Có DB mapping không? → Thêm TC check data lưu đúng field
6. Responsive cần test không? → Thêm TC cho 375px / 768px / 1280px
```

---

## 13. Test Execution Export Format (MANDATORY)

Khi được yêu cầu xuất file Test Case bằng Python script hoặc ra Excel, bắt buộc phải tuân thủ cấu trúc Multi-Sheet sau đây để phục vụ cho quá trình Test Execution (hỗ trợ 2 Rounds):

### 13.1. General Structure
File Excel phải bao gồm các sheet theo thứ tự sau:
1. `Cover Page`: Các thông tin dự án (Company Name, Project Name, Test Case Name, Function, Version, Browser, Platform).
2. `Reference Document`: Bao gồm tên tài liệu (SRS, UI/UX Design), Link/Path (Confluence, Figma), và Description.
3. `Change History`: Bảng lịch sử thay đổi (Version, Date, Description, Author).
4. `Execution Summary`: Bảng master tổng hợp tiến độ test (Pass/Fail/Untested) có apply công thức Excel tự động tính toán.
5. `{Feature_Name} Sheets`: Mỗi Epic/Feature phải được tách thành 1 sheet riêng biệt (VD: Registration, Gallery...).

### 13.2. Feature Sheet Format
Trong mỗi sheet Feature, các dòng TC phải được gom nhóm bằng các Header theo 5 block Category: `UI/UX`, `Validation`, `Functional (Logic & Behavior)`, `Security`, `Performance`.

> **🔴 SECTION ORGANIZATION RULE (MANDATORY):**
> - Mỗi test type (UI/UX, Validation, Functional...) CHỈ xuất hiện **đúng 1 lần** per Feature sheet.
> - **CẤM** tạo sub-section rải rác như `Validation — BVA`, `Functional — Sidebar`, `Functional — Bottom Bar`. Gộp TẤT CẢ Validation TCs (BVA, XSS, empty, boundary) vào 1 section `📌 Validation`. Gộp TẤT CẢ Functional TCs (sidebar, bottom bar, canvas, state transitions) vào 1 section `📌 Functional`.
> - Responsive TCs nằm trong `📌 UI/UX`, KHÔNG tạo section `📌 Responsive` riêng.
> - Negative TCs (dù là Undo negative, empty input...) PHẢI nằm trong `📌 Validation`, không để trong `📌 Functional`.
**Yêu cầu về UI/UX của File (Professional Standard):**
- **Đồng bộ Font:** Dùng chung 1 Font (VD: *Calibri*) trên toàn bộ Workbook.
- **Header Cell Color:** Sync cùng dải màu mảng (ví dụ: xanh dương đậm) và căn giữa.
- **Cover Page:** Format trang bìa chuẩn Document, bắt buộc **xóa đường lưới (Gridlines)** để nhìn mượt và sạch.

Ngoài các cột cơ bản của TC, form Execute **bắt buộc bổ sung** các cột Tracking:
- **Action Type (アクション):** Cột định nghĩa thay đổi TC với **Dropdown List (Data Validation)** bắt buộc chọn 1 trong: `Add new`, `Update`, `Delete`. Mặc định fill "Add new". Nằm ngay sau Expected Result.
- **Create TCs Type:** Bắt buộc dùng **Dropdown List** chọn `By AI` (cho case được tạo bởi AI/Automation) hoặc `By Manual` (cho case dựa trên con người viết tay).
- **Execution Type (実行タイプ):** Bắt buộc dùng **Dropdown List** chọn: `Auto`, `Manual` (để phân biệt execution platform thực tế).
- **Round 1 Tracking:** Nhóm 4 cột: `Result (結果)`, `Test date`, `Tester`, `ID Bug`. Trong đó cột **Result bắt buộc gắn Dropdown List** với các option: `Untested`, `Pass`, `Fail`, `N/A`.
- **Round 2 Tracking:** Tương tự Round 1 (gắn Dropdown List cho Result) để tiện re-test bug.
- **Evidence & Notes:** 2 cột trước cột Review.
- **Review_Manual (Feedback):** Cột cuối cùng, header **vàng gold** (#FFC000), width 35px. Dùng cho quy trình review manual — QA Lead gõ feedback trực tiếp vào đây. Agent sẽ đọc feedback và cập nhật TC tương ứng. Format feedback: `[OK]` (pass), `[FIX] <mô tả cần sửa>`, `[ADD] <cần thêm TC mới>`, `[DELETE] <lý do xóa>`.

### 13.3. Execution Summary Format
Bảng Summary phải chia làm 2 block riêng biệt (Block tính tổng cho Round 1 và Block tính tổng cho Round 2). Mỗi block phải đủ:
- `Pass (合格)`, `Fail (不合格)`, `Untested (未実行)`, `N/A (対象外)`, `Total test case (テスト数合計)`.
- Tỷ lệ `%Progress (Tested/Total)` và `%Progress (Pass/Total)`.
- **Logic:** Phải sử dụng công thức (như `COUNTIF`) trên các file script xuất Excel để trỏ về đúng cột `Result` của từng sheet Feature. Khi QA điền Pass/Fail, bảng Summary phải nhảy số tự động Realtime.

---

> **Remember:** Một tester mới không quen feature phải đọc TC này và execute được ngay, không cần hỏi thêm. Nếu họ phải hỏi — TC chưa đủ tốt.

---

## 14. Test Pipeline & Auto-Versioning Standards (MANDATORY)

To ensure the Single Source of Truth remains intact across all file formats, the QA export pipeline MUST follow this strict synchronization rule:

1. **The Origin File:** The latest `TC_..._Full.csv` is the ONLY source of truth. Python scripts must dynamically read the highest `vX` CSV in the directory (e.g., using `glob` and sort). **DO NOT HARDCODE** file paths in the scripts.
2. **Auto-Increment Versioning:** If a new generated file is required, the script must parse the current version (`v17`), increment it (`v18`), and apply it universally to:
   - The output file names (`TC_POD-TShirt-Platform_ExecutionSummary_v18_2026-03-16.xlsx`)
   - The Cover Page 'Document Version' inside the Excel sheet.
   - The Markdown Title in `test_cases_suite.md`.
3. **Execution Order:** Always execute the pipeline in exact order: Merge/Append raw data to the CSV -> Export to Markdown -> Export to Multisheet Excel. Failure to do so breaks the sync.

---

## 15. Granular Device & Orientation Responsive Testing (MANDATORY)

To prevent testers from missing device-specific UI issues, UI/UX Responsive test cases MUST NOT use generic "Mobile/Tablet" terminology. 

For **every** frontend screen/feature (e.g. Registration, Editor, Checkout), you **MUST generate 5 distinct responsive test cases**:
1. **iPhone (Portrait)**: Check layout staking and touch target sizes on an iPhone (e.g. 14/15 Pro Max).
2. **Android (Portrait)**: Check layout on Android. **Must** explicitly include a step to test the virtual keyboard (bàn phím ảo) behavior to ensure it does not overlap CTA buttons.
3. **iPad (Portrait)**: Check tablet layout scaling on iOS.
4. **Android Tablet (Portrait)**: Check tablet layout scaling on Android.
5. **Landscape (Mobile/Tablet)**: Check the UI when rotating horizontally. **Must** verify that sticky headers/footers do not consume all the vertical screen space, leaving room for content.

*Example Module Naming:* `Responsive (iPhone)`, `Responsive (Android)`, `Responsive (iPad)`, `Responsive (Android Tablet)`, `Responsive (Landscape)`.

---

## 16. Interactive Element Inventory Rule (MANDATORY)

> **🔴 BẮT BUỘC:** Trước khi viết TC cho BẤT KỲ màn hình/tab/panel nào, Agent PHẢI thực hiện "Button Inventory" — liệt kê TẤT CẢ các phần tử tương tác (interactive elements) có trên màn hình đó.

### 16.1 Quy trình Inventory

```
Pha 1: SCAN — Quét toàn bộ màn hình
  → Liệt kê MỌI: buttons, links, toggles, icons clickable, tabs, selectors, sliders, switches
  → Ghi lại exact label/text của từng element

Pha 2: MAP — Đối chiếu với TC đã có
  → Mỗi element đã có TC chưa? 
  → Element nào CHƯA có TC → PHẢI thêm ngay

Pha 3: VERIFY — Đảm bảo 100% coverage
  → Đếm: Số elements vs Số TCs → Phải ≥ 1:1
  → Nếu thiếu → Agent tự bổ sung trước khi hoàn thành
```

### 16.2 Checklist per Element Type

| Element Type | TC tối thiểu cần có |
|-------------|---------------------|
| **Button** (VD: 'Đổi sản phẩm', 'Gợi ý size', 'Tạo Artwork') | 1 UI/UX (hiển thị, vị trí, style) + 1 Functional (click → kết quả) |
| **Link/Hyperlink** | 1 Functional (click → navigate đúng đích) |
| **Toggle/Switch** | 1 Functional (ON→OFF, OFF→ON) + 1 UI (trạng thái visual) |
| **Tab** | 1 Functional (click → content change) + 1 UI (active state) |
| **Icon clickable** | 1 Functional (click → action) |
| **Dropdown/Select** | 1 Functional (open → select → close) + 1 UI (options hiển thị đúng) |
| **Color Swatch** | 1 Functional (click → apply color) + 1 UI (active highlight) |
| **Size Selector** | 1 Functional (click → apply size) + 1 UI (active highlight) |
| **Modal trigger** | 1 Functional (click → modal open) + 1 Functional (modal close) |

### 16.3 Lỗi NGHIÊM TRỌNG — Missing Button Coverage

> **Nếu trên màn hình có nút `[Đổi sản phẩm]` nhưng KHÔNG có TC nào test click nút đó → đây là lỗi coverage nghiêm trọng.**

**Anti-pattern:**
```
❌ WRONG: Chỉ viết TC cho "đổi màu" và "đổi size" mà QUÊN nút "Đổi sản phẩm" và "Gợi ý size"
✅ CORRECT: Liệt kê TẤT CẢ buttons trước → viết TC cho TỪNG button → không bỏ sót
```

### 16.4 Example — DS Tab 'SẢN PHẨM' Inventory

```
Màn hình: Design Studio → Tab 'SẢN PHẨM'
Elements found:
  ✅ [Tab SẢN PHẨM]     → TC_DS_022 (click tab)
  ✅ [Color Swatches]    → TC_DS_018 (đổi màu), TC_DSP_UI_002 (UI)
  ✅ [Size Selector]     → TC_DS_019 (đổi size), TC_DSP_UI_003 (UI)
  ✅ [Nút Đổi sản phẩm] → TC_DSP_F_003 (click), TC_DSP_UI_005 (UI)
  ✅ [Nút Gợi ý size]   → TC_DSP_F_004 (click), TC_DSP_UI_006 (UI)
  Total: 5 elements → 9 TCs ✅ Full coverage
```

### 16.5 Trigger Rule

**Bắt buộc chạy Inventory khi:**
- Viết TC cho màn hình/feature mới
- Nhận yêu cầu "mở rộng coverage"
- Sau khi review manual phát hiện thiếu
- Khi có UI update (thêm/xóa button)
