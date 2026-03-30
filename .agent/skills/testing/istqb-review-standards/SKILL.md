---
name: istqb-review-standards
description: ISTQB Foundation Level 4.0 + Advanced Level Test Analyst knowledge for test case review. Test design techniques, quality attributes, review types, coverage criteria, risk-based testing, and defect metrics.
---

# 📚 ISTQB Review Standards Skill

> **Source:** ISTQB Foundation Level Syllabus v4.0 (2024) + Advanced Level Test Analyst v4.0 (2025)
> **Purpose:** Cung cấp framework chuẩn quốc tế cho việc review test cases

---

## 1. TEST CASE QUALITY ATTRIBUTES (10 tiêu chí ISTQB)

Khi review bất kỳ test case nào, đánh giá theo 10 tiêu chí sau:

| # | Attribute | Mô tả | Check |
|---|---|---|---|
| 1 | **Correctness** | TC verify đúng test condition mong muốn | Steps + Expected Result khớp requirement |
| 2 | **Completeness** | Đầy đủ thông tin: test data, precondition, expected result | Không có field trống quan trọng |
| 3 | **Feasibility** | TC có thể thực thi được trong thực tế | Không yêu cầu điều kiện bất khả thi |
| 4 | **Clear Objective** | Mỗi TC test DUY NHẤT 1 behavior | Không có mega TC (15+ steps) |
| 5 | **No Duplicates** | Không trùng lặp giữa các TCs | Phát hiện duplicate/near-duplicate |
| 6 | **Consistency** | Format, ngôn ngữ, cấu trúc nhất quán | TC_ID, naming, steps format đồng nhất |
| 7 | **Precision** | Chỉ có 1 cách hiểu duy nhất | Expected Result không mơ hồ |
| 8 | **Traceability** | Map ngược được về requirement/risk | US_Mapping không trống, logic |
| 9 | **Maintainability** | Dễ cập nhật khi requirement thay đổi | Modular, không hardcode magic values |
| 10 | **Fault Detection** | Khả năng phát hiện lỗi thực tế cao | Negative, boundary, edge cases đầy đủ |

### Scoring Matrix
```
Per TC: 1 điểm/attribute đạt → max 10 điểm/TC
Overall: (Tổng điểm tất cả TCs) / (Số TCs × 10) × 100 = Quality Score %
```

---

## 2. TEST DESIGN TECHNIQUES (ISTQB Classification)

### 2.1 Black-Box Techniques (Specification-based)
Reviewer PHẢI kiểm tra TC có áp dụng đúng kỹ thuật thiết kế hay không:

#### Equivalence Partitioning (EP)
```
Chia input thành các lớp tương đương → 1 TC đại diện/lớp

Ví dụ: Field "Tuổi" (valid: 18-65)
├── Valid partition:   18 ≤ x ≤ 65 → TC với x=30 ✅
├── Invalid partition: x < 18      → TC với x=15 ✅
└── Invalid partition: x > 65      → TC với x=70 ✅

Review check: Có TC cho TỪNG partition (valid + invalid)?
```

#### Boundary Value Analysis (BVA)
```
Test các giá trị biên → nơi lỗi hay xảy ra nhất

2-value BVA:  boundary ± 1 neighbor
3-value BVA:  boundary ± 2 neighbors

Ví dụ: Password 8-20 chars
├── BVA min: 7 chars (invalid), 8 chars (valid)
├── BVA max: 20 chars (valid), 21 chars (invalid)

Review check: Có TC cho mỗi boundary value? Có cả min-1, min, max, max+1?
```

#### Decision Table Testing
```
Khi có nhiều conditions → actions phức tạp

Ví dụ: Checkout flow
| Condition          | R1  | R2  | R3  | R4  |
|---|---|---|---|---|
| Logged in?         | Y   | Y   | N   | N   |
| Cart not empty?    | Y   | N   | Y   | N   |
| → Allow checkout   | ✅  | ❌  | ❌  | ❌  |

Review check: Có đủ TC cho mỗi rule (combination)? Có collapse được rules không?
```

#### State Transition Testing
```
Khi object có nhiều trạng thái → chuyển đổi

Ví dụ: Order states
[New] → [Processing] → [Shipped] → [Delivered]
                     → [Cancelled]

Review check: Mỗi transition có TC? Có TC cho invalid transitions?
```

### 2.2 White-Box Techniques (Structure-based)
```
Statement Coverage: Mọi dòng code được thực thi ít nhất 1 lần
Branch Coverage:    Mọi nhánh (if/else) được đi qua ít nhất 1 lần
Condition Coverage: Mọi điều kiện boolean được test cả true và false
```

### 2.3 Experience-Based Techniques
```
Error Guessing:    Tester dựa kinh nghiệm đoán chỗ hay lỗi
Exploratory:       Tester thiết kế + thực thi cùng lúc
Checklist-based:   Dùng checklist định sẵn để test
```

**Review check:** TC suite có mix đủ 3 nhóm kỹ thuật không? Thiếu nhóm nào?

---

## 3. REVIEW TYPES (ISTQB Process)

Agent A sử dụng kết hợp các review type:

| Type | Formality | Khi nào dùng | Đặc điểm |
|---|---|---|---|
| **Informal Review** | Thấp | Quick check nhỏ | Buddy check, no documentation |
| **Walkthrough** | Trung bình | Trình bày cho team | Author dẫn dắt, learning-focused |
| **Technical Review** | Cao | Kiểm tra kỹ thuật | Expert review, decision-making |
| **Inspection** | Rất cao | Audit chính thức | Moderator-led, checklist-based, metrics |

**Agent A mặc định sử dụng: Technical Review + Inspection hybrid**
- Checklist-based (ISTQB quality attributes)
- Metrics-driven (scoring)
- Documented output (Review Report)

### Review Process (6 giai đoạn ISTQB)
```
1. Planning       → Xác định scope, inputs, criteria
2. Initiation     → Phân phát tài liệu, set deadline
3. Individual     → Reviewer đọc + đánh giá từng TC
4. Communication  → Trao đổi findings
5. Fixing         → Author sửa issues (nếu được yêu cầu)
6. Reporting      → Xuất Review Report + metrics
```

---

## 4. COVERAGE CRITERIA FRAMEWORK

### 4.1 Requirements Coverage
```
Formula: (TCs mapped to requirements / Total requirements) × 100

Target: ≥ 95% cho P0 features, ≥ 80% cho P1, ≥ 60% cho P2
```

### 4.2 Test Type Coverage
Mỗi Feature PHẢI có đủ test types:

| Test Type | Minimum TCs | Ý nghĩa |
|---|---|---|
| Positive (Happy path) | ≥ 3 | Luồng chính hoạt động |
| Negative (Unhappy path) | ≥ 2 | Xử lý lỗi đúng |
| Boundary | ≥ 2 (nếu có input) | Giá trị biên |
| UI/UX | ≥ 3 | Visual, layout, style |
| Security | ≥ 1 (nếu có input) | XSS, injection |
| Responsive | 6 per screen | iPhone/Android/iPad/Tablet/Landscape/Zoom |

### 4.3 Defect Detection Effectiveness (DDE)
```
DDE = (Defects found during testing / Total defects including production) × 100

Target: ≥ 85% (industry benchmark)
TC suite chất lượng cao → DDE cao
```

---

## 5. RISK-BASED REVIEW PRIORITY

### Risk Assessment Matrix
```
Risk Level = Likelihood × Impact

| Impact ↓ \ Likelihood → | Low | Medium | High |
|---|---|---|---|
| High (Business critical)   | Medium | High   | Critical |
| Medium (Important)         | Low    | Medium | High     |
| Low (Nice-to-have)         | Info   | Low    | Medium   |
```

### Review Priority Order
```
1. 🔴 CRITICAL: Authentication, Payment, Core Business Flow
   → Review FIRST, MOST THOROUGH
2. 🟠 HIGH: Cart, Checkout, AI Generation, Data Input
   → Review SECOND, detailed
3. 🟡 MEDIUM: Profile, Gallery, Settings, CMS
   → Review THIRD, standard
4. 🟢 LOW: Help pages, Static content, Tooltips
   → Review LAST, lighter
```

---

## 6. ISTQB REVIEW CHECKLIST (Per TC)

```markdown
## Individual TC Review Card — TC_ID: [___]

### A. Structural Check
- [ ] TC_ID follows naming convention
- [ ] US_Mapping present and valid
- [ ] Feature/Module correctly assigned
- [ ] Priority aligned with risk level
- [ ] Type (Positive/Negative/UI-UX/Boundary) correctly set

### B. Steps Quality (ISTQB Precision)
- [ ] Step 1 = "1. Truy cập vào trang" (project convention)
- [ ] Each step = exactly 1 action (atomic)
- [ ] Steps are self-contained (no external context needed)
- [ ] Test data is specific, not placeholder
- [ ] Tab/click/input actions are at UI element level

### C. Expected Result Quality (ISTQB Completeness)
- [ ] Measurable and specific (not "works correctly")
- [ ] Includes exact text, values, or states
- [ ] UI assertions: colors, positions, visibility
- [ ] Error messages: exact text quoted
- [ ] Redirect/navigation: exact URL/route

### D. Test Design Technique
- [ ] EP applied: valid + invalid partitions covered
- [ ] BVA applied: boundary values ± 1 tested
- [ ] Decision logic: all condition combinations
- [ ] State: valid + invalid transitions
- [ ] Error guessing: common failure modes

### E. Coverage Contribution
- [ ] Maps to a unique requirement (not duplicate)
- [ ] Adds coverage value (not redundant)
- [ ] Part of the minimum test type coverage
```

---

## 7. COMMON DEFECTS IN TEST CASES (ISTQB Defect Taxonomy)

| Defect Type | Description | Severity |
|---|---|---|
| **Missing Negative** | Requirement has constraint but no negative TC | High |
| **Vague Expected** | "Should work" instead of specific assertion | High |
| **Missing Boundary** | Numeric/text field without BVA | Medium |
| **Over-scoped TC** | Tests 3+ behaviors in 1 TC | Medium |
| **Broken Traceability** | TC has no/wrong US_Mapping | Medium |
| **Duplicate TC** | Same behavior tested by 2+ TCs | Low |
| **Wrong Priority** | P2 for login failure, P0 for tooltip color | High |
| **Missing Precondition** | TC needs logged-in user but not stated | Medium |
| **Generic Responsive** | "Works on mobile" without device specifics | High |
| **Orphan TC** | TC exists but feature was removed | Low |

---

## 8. TEST SUITE STRUCTURE STANDARDS

> **Source:** Patterns established during v28→v29 modernization (2026-03-26)
> **Purpose:** Đảm bảo test suite luôn nhất quán, dễ đọc, dễ maintain khi scale

### 8.1 Sheet Organization (Feature-based)

Mỗi sheet trong Excel = 1 Feature. Tên sheet ≤ 31 ký tự.

```
Rule: Gom features cùng khu vực vào 1 sheet, không để riêng lẻ
├── ✅ DESIGN STUDIO (gồm: My Designs, AI Try-on, Library)
├── ✅ HOME (gồm: Footer, Error Pages)
├── ✅ LOGIN (gồm: Profile/Account)
├── ✅ ĐẶT HÀNG (gồm: Giỏ hàng/Cart)
├── ✅ THANH TOÁN (gồm: Xác nhận đơn hàng)
└── ❌ Tránh: Sheet riêng cho sub-feature (FOOTER, PROFILE, AI TRY-ON riêng)
```

### 8.2 Category Format (5 Standard Categories)

Mỗi sheet có **tối đa 5 categories**, luôn theo thứ tự cố định:

| # | Category | Nội dung | Khi nào bỏ qua |
|---|---|---|---|
| 1 | `📌 UI/UX` | Giao diện, layout, responsive, style, empty state | Không bao giờ (luôn có) |
| 2 | `📌 Functional` | Happy path, positive, logic, edge case, E2E | Không bao giờ |
| 3 | `📌 Validation` | Negative, boundary, error handling | Hiếm khi bỏ |
| 4 | `📌 Security` | XSS, injection, auth bypass, brute force | Bỏ nếu không có input |
| 5 | `📌 Performance` | Timeout, network, lazy load, concurrent | Bỏ nếu không relevant |

**Classification rules:**
```
TC Type column chứa:
├── 🎨 UI/UX        → Category: UI/UX
├── ✅ Positive      → Category: Functional
├── ✅ Edge Case     → Category: Functional (hoặc Validation nếu negative)
├── ⚠️ Negative     → Category: Validation
├── ✅ Boundary      → Category: Validation
└── Context-based:
    ├── old_category chứa "security" → Security
    ├── old_category chứa "performance" → Performance
    └── title chứa "XSS/injection/csrf" → Security
```

**KHÔNG được:**
- ❌ `📌 Functional (Logic & Behavior)` — gom vào Functional
- ❌ `📌 Functional — Source Code Verified` — gom vào Functional
- ❌ `📌 Validation — Chung` — gom vào Validation
- ❌ `#### 🆕 Sub-sub heading` — KHÔNG dùng sub-sub heading
- ❌ `### 🔗 Merged from: ...` — KHÔNG dùng, gom TCs vào category phù hợp

### 8.3 TC Sorting Order (Multi-key)

TCs trong mỗi category PHẢI được sắp xếp theo 4 cấp:

```
Sort key priority:
1. Screen    → Grouped by screen (defined order per feature)
2. Module    → Alphabetical within same screen
3. Priority  → P0 before P1 before P2
4. TC_ID     → Natural sort (TC_HOME_001 < TC_HOME_010)
```

**Screen Order per Feature (ví dụ DESIGN STUDIO):**
```
DS - Header → DS - Sidebar → DS - Canvas → DS - Editor/Canvas
→ DS - AI Panel → DS - StatusBar
→ DS - Popup Sản phẩm → DS - Popup Gợi ý size
→ DS - Thư viện Ảnh → DS - Thư viện Mẫu
→ DS - Gallery → DS - Smart Fit → DS - AI Try-on
→ DS - OrderModal → DS - Credits → DS - Share
→ DS - User Menu → DS - Auth Modal → DS - Cart Drawer
→ DS - Mobile Panel → MH My Designs
→ DS - Chung → DS - Responsive
```

**Kết quả mong đợi khi mở Excel:**
```
📌 Functional
├── 🖥️ DS - Header:
│   ├── 📁 DS Header - Credits (P0 TCs first)
│   ├── 📁 DS Header - Share
│   └── 📁 DS Header - User
├── 🖥️ DS - Sidebar:
│   ├── 📁 Sidebar (P1 TCs)
│   └── ...
└── 🖥️ DS - Responsive:
    └── ...
```

### 8.4 Deduplication Rules

Khi merge/update test suite, PHẢI check:

```
1. Exact TC_ID duplicates:
   → Script: count TC_IDs, group by feature, flag if count > 1
   → Fix: Xóa bản trùng, giữ bản chi tiết hơn

2. Functional overlap (khác ID, cùng scenario):
   → Detect: 2 sheets cùng test "Đơn hàng" (ORDER vs MY ORDERS)
   → Fix: Merge sheet cũ vào sheet mới, giữ unique TCs

3. Standalone vs Merged duplicates:
   → Detect: Feature vừa có standalone section VÀ "🔗 Merged from:" section
   → Fix: Xóa standalone, giữ merged section trong parent feature
```

### 8.5 Version Update Workflow

Quy trình cập nhật test suite khi có phiên bản mới:

```
Phase 1: Source Code Research
├── Đọc git log (commits since last version)
├── Phân tích TSX/component files mới/thay đổi
└── Output: Danh sách new features + changed features

Phase 2: Gap Analysis
├── So sánh existing TCs vs source code
├── Identify: New TCs cần thêm (~70+ mỗi version)
├── Identify: Obsolete TCs cần xóa/update (~30+ mỗi version)
└── Output: Gap Analysis Report (implementation_plan.md)

Phase 3: Build Script
├── Python script build_v{N}_from_v{N-1}.py
├── String replacements cho updated content
├── Append new feature sections
└── Output: test_cases_suite_v{N}.md

Phase 4: Merge & Dedup
├── Script detect + remove duplicate TC_IDs
├── Merge overlapping sheets
└── Output: Verified 0 duplicates

Phase 5: Standardize
├── Re-classify TCs vào 5 standard categories
├── Multi-key sort: Screen → Module → Priority → TC_ID
└── Output: Clean, sorted markdown

Phase 6: Excel Build
├── Python script build_v{N}_excel.py
├── Parse markdown → feature sheets + Cover + Execution Summary
├── Data validations, conditional formatting, auto-filter
└── Output: TC_POD-TShirt-Platform_ExecutionSummary_v{N}_{date}.xlsx
```

