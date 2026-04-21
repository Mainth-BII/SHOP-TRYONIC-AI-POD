---
trigger: always_on
---

# GEMINI.md — Tryonic QA Workspace Rules

> File này định nghĩa cách AI hoạt động trong workspace QA Tryonic.
> Cập nhật: 2026-04-02

---

## CRITICAL: AGENT & SKILL PROTOCOL

> **MANDATORY:** Đọc agent file + skills TRƯỚC KHI thực hiện. Không ngoại lệ.

### Modular Skill Loading
Agent activated → Check frontmatter `skills:` → Read SKILL.md → Apply.

**Rule Priority:** P0 (GEMINI.md) > P1 (Agent .md) > P2 (SKILL.md)

---

## 🔴 QUY TRÌNH QUẢN LÝ TEST CASE (BẮT BUỘC)

> **MANDATORY**: Đối với mọi yêu cầu thêm, sửa, hoặc xóa test case trong Excel:
>
> 1. **Kích hoạt Workflow**: Tuân thủ `@[workflows/testcase_update_protocol]`.
> 2. **Lập kế hoạch trước**: Phân tích ảnh hưởng → Chia nhỏ → Trình bày → Đợi duyệt.
> 3. **Chỉnh sửa có chọn lọc**: Chỉ sửa case cần thiết. `Action Type = Modified`, `Notes = ✅ Updated v31...`.
> 4. **Không tóm tắt**: KHÔNG BAO GIỜ rút gọn bước. Đủ 14-16 bước v31.
> 5. **Bảo toàn dữ liệu**: KHÔNG thay đổi dòng không liên quan.
> 6. **Bài học kinh nghiệm**: Đọc `@[.agent/LESSON_LEARNED.md]` trước khi bắt đầu.

---

## 📥 REQUEST CLASSIFIER

| Request Type | Trigger | Action |
|---|---|---|
| **QUESTION** | "what is", "explain" | Text Response |
| **SURVEY** | "analyze", "overview" | Research, no file |
| **SIMPLE CODE** | "fix", "add" (1 file) | Inline Edit |
| **COMPLEX CODE** | "build", "create", "implement" | Plan → Approve → Execute |
| **SLASH CMD** | /test, /debug, /plan... | Workflow-specific |

---

## 🤖 INTELLIGENT AGENT ROUTING

> 🔴 **MANDATORY:** Follow `@[skills/intelligent-routing]` protocol.

### Auto-Selection Protocol
1. **Analyze** user request (silent)
2. **Select** best agent
3. **Announce**: `🤖 Applying knowledge of @[agent-name]...`
4. **Apply** agent rules

### Available Agents

| Agent | Domain | Trigger |
|---|---|---|
| `orchestrator` | Điều phối multi-agent | Task phức tạp |
| `project-planner` | Lập kế hoạch | Module test mới |
| `qa-playwright-engineer` | Viết Playwright script | Auto test |
| `tryonic/qa-analyst-agent` | Viết test case từ BA | Tạo TC |
| `tryonic/qa-playwright-runner` | Chạy test + báo cáo | Execute test |
| `tryonic/qa-review-expert` | Review TC quality | Kiểm tra TC |
| `debugger` | Debug root cause | Test fail |

---

## TIER 0: UNIVERSAL RULES (Always Active)

### 🌐 Language Handling
1. **Respond in user's language** (Vietnamese)
2. **Code comments/variables** in English
3. **Reports**: Viết bằng tiếng Việt

### 🧹 Clean Code
**ALL code MUST follow `@[skills/clean-code]`.**
- Concise, self-documenting
- AAA Pattern for tests
- No over-engineering

### 🗺️ System Map
- Agents: `.agent/agents/`
- Skills: `.agent/skills/`
- Workflows: `.agent/workflows/`

### 🧠 Read → Understand → Apply
```
❌ WRONG: Read agent → Start coding
✅ CORRECT: Read → Understand WHY → Apply PRINCIPLES → Code
```

### 📚 Continuous Learning (AUTO — Mọi task QA)
> **MANDATORY**: Trước MỌI task QA, đọc `docs/istqb/` để áp dụng kiến thức.

| Task | Đọc trước | Áp dụng |
|---|---|---|
| Tạo/Update TC | `istqb_reference.md` | EP, BVA, Decision Table, State Transition |
| Viết test script | `istqb_advanced_reference.md` | POM, Data-Driven, Pyramid |
| Run test | `istqb_advanced_reference.md` | Metrics, Defect format |
| Debug fail | `istqb_advanced_reference.md` | RCA (5 Whys) |

**Workflow chi tiết**: `@[workflows/learn]`

---

## 🛑 SOCRATIC GATE

| Request Type | Action |
|---|---|
| New Feature / Build | ASK 3 strategic questions |
| Code Edit / Bug Fix | Confirm understanding first |
| Vague request | Ask Purpose, Scope, Priority |

**Protocol:** Never Assume → Ask → Wait → Then implement.
Full protocol: `@[skills/qa-planning]`

---

## TIER 1: QA-SPECIFIC RULES

### Project Type: QA Automation
- **Primary Agent**: `qa-playwright-engineer`
- **Test Framework**: Playwright (Python)
- **Test URL**: `https://shop.tryonic.ai/`

### Gemini Mode Mapping

| Mode | Agent | Behavior |
|---|---|---|
| **plan** | `project-planner` | Plan only, NO CODE |
| **ask** | - | Ask questions |
| **edit** | `orchestrator` | Execute per plan |

---

## 📁 QUICK REFERENCE

### Agents (7)
`orchestrator`, `project-planner`, `qa-playwright-engineer`, `debugger`
`tryonic/qa-analyst-agent`, `tryonic/qa-playwright-runner`, `tryonic/qa-review-expert`

### Skills (7)
`tryonic-testcase-management`, `webapp-testing`, `testing-patterns`, `clean-code`
`qa-planning`, `intelligent-routing`, `powershell-windows`

### Workflows (6)
`/testcase_update_protocol`, `/test`, `/debug`, `/plan`, `/status`, `/orchestrate`

### Key Files
- `LESSON_LEARNED.md` — Bài học kinh nghiệm
- `docs/PROJECT_GUIDE.md` — Hướng dẫn sử dụng dự án

---
