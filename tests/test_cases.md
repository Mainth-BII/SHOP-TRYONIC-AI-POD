# Test Cases — Tryonic AI POD (pre-launch.tryonic.ai)

**Feature:** AI Artwork Generation — Main Flow  
**URL:** https://pre-launch.tryonic.ai/  
**Created:** 2026-04-15  
**ISTQB Techniques:** EP, BVA, State Transition, Decision Table

---

## Use Cases

### UC-01: Homepage Loading
**Actor:** Anonymous user  
**Trigger:** Navigate to URL  
**Main Flow:** Page loads → React app mounts → UI elements rendered  
**Exit:** All critical elements visible

### UC-02: Artwork Generation (Happy Path)
**Actor:** Anonymous user  
**Trigger:** User enters description and clicks Generate  
**Main Flow:**
1. User enters story/description
2. Clicks "Tạo" / "Generate" button
3. Loading indicator appears
4. AI generates artwork (10-120 seconds)
5. Artwork image displayed with description
**Exit:** Image visible, non-zero dimensions, matches description intent

### UC-03: Input Validation
**Actor:** Anonymous user  
**Trigger:** User submits empty / invalid input  
**Main Flow:** Error/validation message shown, generation NOT triggered

### UC-04: Responsive Layout
**Actor:** Mobile / Tablet user  
**Trigger:** Visit on small screen  
**Main Flow:** Layout adapts, all elements reachable without horizontal scroll

---

## Test Cases

### Section 1: Homepage UI — TC_HOME

| TC_ID | Title | Type | Priority | Steps | Expected Result |
|---|---|---|---|---|---|
| TC_HOME_001 | Homepage loads successfully | ✅ Positive | P0 | 1. Truy cập https://pre-launch.tryonic.ai/ | Trang tải thành công, HTTP 200, React root render |
| TC_HOME_002 | Page title is correct | UI/UX | P1 | 1. Truy cập trang chủ | Title chứa "Tryonic" |
| TC_HOME_003 | Prompt input visible | ✅ Positive | P0 | 1. Truy cập trang chủ → kiểm tra input/textarea | Ô nhập mô tả hiển thị, có thể tương tác |
| TC_HOME_004 | Generate button visible | ✅ Positive | P0 | 1. Truy cập trang chủ → kiểm tra button | Button "Tạo" / "Generate" hiển thị, enabled |
| TC_HOME_005 | Page renders without JS errors | ✅ Positive | P1 | 1. Truy cập trang chủ, mở Console | Không có JS error trong console |
| TC_HOME_006 | Logo / brand visible | UI/UX | P2 | 1. Truy cập trang chủ | Logo Tryonic hiển thị đúng |

---

### Section 2: Artwork Generation — TC_GEN

| TC_ID | Title | Type | Priority | Steps | Expected Result |
|---|---|---|---|---|---|
| TC_GEN_001 | Generate artwork — valid Vietnamese prompt | ✅ Positive | P0 | 1. Truy cập trang chủ 2. Nhập "Tôi yêu bóng đá và màu xanh lá" 3. Click Generate | Artwork image xuất hiện trong vòng 120s, kích thước > 0 |
| TC_GEN_002 | Generate artwork — valid English prompt | ✅ Positive | P1 | 1. Truy cập trang chủ 2. Nhập "I love football and green" 3. Click Generate | Artwork image xuất hiện trong vòng 120s |
| TC_GEN_003 | Loading indicator shown during generation | ✅ Positive | P1 | 1. Truy cập trang chủ 2. Nhập prompt hợp lệ 3. Click Generate 4. Quan sát ngay sau click | Loading spinner / skeleton hiển thị trong khi chờ |
| TC_GEN_004 | Loading indicator disappears after generation | ✅ Positive | P1 | 1. Chờ artwork hoàn thành 2. Kiểm tra loading indicator | Loading indicator biến mất hoàn toàn |
| TC_GEN_005 | Generated image has valid dimensions | ✅ Positive | P0 | 1. Tạo artwork thành công 2. Kiểm tra naturalWidth/naturalHeight | img.naturalWidth > 0 và img.naturalHeight > 0 |
| TC_GEN_006 | Generated image is visible in viewport | ✅ Positive | P0 | 1. Tạo artwork thành công 2. Kiểm tra viewport | Image hiển thị trong viewport (ratio >= 0.5) |
| TC_GEN_007 | Artwork description displayed with image | ✅ Positive | P1 | 1. Tạo artwork 2. Kiểm tra text gần image | Mô tả / caption hiển thị gần ảnh kết quả |
| TC_GEN_008 | Generate second artwork replaces first | ✅ Positive | P1 | 1. Tạo artwork lần 1 2. Nhập prompt mới 3. Click Generate lại | Artwork mới thay thế artwork cũ |
| TC_GEN_009 | Artwork generation completes within 120s | ✅ Positive | P0 | 1. Bắt đầu đo thời gian 2. Nhập prompt, click Generate 3. Chờ image xuất hiện | Hoàn thành trong vòng 120 giây |

---

### Section 3: Input Validation — TC_VAL (Negative)

| TC_ID | Title | Type | Priority | Steps | Expected Result |
|---|---|---|---|---|---|
| TC_VAL_001 | Empty prompt — submit disabled or error shown | ⚠️ Negative | P1 | 1. Truy cập trang chủ 2. Không nhập gì 3. Click Generate | Button bị disabled HOẶC thông báo lỗi "vui lòng nhập" xuất hiện |
| TC_VAL_002 | Whitespace-only prompt | ⚠️ Negative | P1 | 1. Nhập "   " (spaces only) 2. Click Generate | Validation lỗi xuất hiện, không gửi request |
| TC_VAL_003 | Single character prompt (BVA min) | ⚠️ Negative | P2 | 1. Nhập "A" 2. Click Generate | Validation lỗi (quá ngắn) HOẶC artwork gen thành công |
| TC_VAL_004 | Very long prompt BVA (1000+ chars) | ⚠️ Negative | P2 | 1. Nhập chuỗi 1000 ký tự 2. Click Generate | Input bị cắt bớt HOẶC validation lỗi "quá dài" |
| TC_VAL_005 | Special characters in prompt | ⚠️ Negative | P2 | 1. Nhập "<script>alert(1)</script>" 2. Click Generate | XSS không thực thi; input được sanitize |
| TC_VAL_006 | SQL injection attempt | ⚠️ Negative | P2 | 1. Nhập "'; DROP TABLE users; --" 2. Click Generate | Input được xử lý an toàn, không có lỗi server |
| TC_VAL_007 | Emoji-only prompt | UI/UX | P3 | 1. Nhập "🎨🌈🎸" 2. Click Generate | Artwork được tạo HOẶC validation message |

---

### Section 4: Responsive UI — TC_UI

| TC_ID | Title | Type | Priority | Steps | Expected Result |
|---|---|---|---|---|---|
| TC_UI_001 | iPhone Portrait (390x844) — input visible | UI/UX | P1 | 1. Resize/emulate 390x844 2. Truy cập trang 3. Kiểm tra input | Input hiển thị không bị cắt, trong viewport |
| TC_UI_002 | iPhone Portrait — generate button reachable | UI/UX | P1 | 1. Resize 390x844 2. Kiểm tra button | Button trong viewport, không bị che |
| TC_UI_003 | iPhone Portrait — full artwork generation flow | UI/UX | P1 | 1. Resize 390x844 2. Nhập prompt 3. Generate | Artwork hiển thị đúng trên màn hình nhỏ |
| TC_UI_004 | Android Portrait (360x740) — layout not broken | UI/UX | P2 | 1. Resize 360x740 2. Truy cập trang | Không có horizontal scroll, layout đúng |
| TC_UI_005 | iPad Portrait (768x1024) — all elements visible | UI/UX | P2 | 1. Resize 768x1024 2. Truy cập trang | Tất cả elements hiển thị đúng |

---

## Summary

| Category | Count | P0 | P1 | P2 | P3 |
|---|---|---|---|---|---|
| Homepage UI | 6 | 2 | 2 | 2 | 0 |
| Artwork Generation | 9 | 4 | 5 | 0 | 0 |
| Input Validation | 7 | 0 | 2 | 4 | 1 |
| Responsive UI | 5 | 0 | 3 | 2 | 0 |
| **Total** | **27** | **6** | **12** | **8** | **1** |
