# 🧪 Tryonic QA — Test Automation Workspace

> Hệ thống QA tự động cho [Tryonic Shop](https://admin.shop.tryonic.ai/home/) — nền tảng thiết kế áo POD tích hợp AI.

---

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright
pip install playwright
playwright install
```

## Cấu trúc Dự án

```
📁 .agent/          → AI Agents, Skills, Workflows
📁 docs/            → Tài liệu dự án (PROJECT_GUIDE, AGENT_FLOW, BA specs)
📁 Test cases/      → Test case Excel (master), scripts, JSON
📁 source/          → Source code ứng dụng
📁 tests/           → Playwright auto test scripts
```

## Tài liệu

| File | Nội dung |
|---|---|
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) | Hướng dẫn sử dụng toàn diện |
| [docs/AGENT_FLOW.md](docs/AGENT_FLOW.md) | Luồng hoạt động AI agents |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Lịch sử thay đổi |

## Hệ thống AI

| Thành phần | Số lượng | Chi tiết |
|---|---|---|
| **Agents** | 7 | orchestrator, planner, playwright-engineer, analyst, runner, reviewer, debugger |
| **Skills** | 7 | tryonic-tc-management, webapp-testing, testing-patterns, clean-code, qa-planning, intelligent-routing, powershell |
| **Workflows** | 6 | /testcase_update_protocol, /test, /debug, /plan, /status, /orchestrate |

## License

MIT
