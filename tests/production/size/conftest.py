"""conftest.py cho tests/production/size/.

Hai nhiệm vụ:
  1. Autouse fixture chụp screenshot + ghi kết quả sau mỗi test case.
  2. Session-scope fixture lưu Markdown report cho từng sản phẩm sau khi session kết thúc.

Lý do dùng session-scope thay class-scope: pytest interleave parametrized tests
từ nhiều class → class-scope fixture re-enter nhiều lần → _results bị clear giữa chừng.
"""
import os
import pytest
from datetime import datetime

# Module-level dict tích lũy results trong suốt session (không bị clear)
_session_results: dict = {}   # {TestClass: [row, ...]}


# ── Hook: gắn rep_call vào item để fixture đọc trạng thái test ───────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{call.when}", rep)


# ── Autouse: chụp screenshot + ghi kết quả ───────────────────────────────────

@pytest.fixture(autouse=True)
def _auto_record(request, page):
    """Wrap mỗi test: chụp screenshot sau khi test kết thúc, ghi vào _session_results."""
    yield

    cls = request.cls
    if not cls or not hasattr(cls, "_results"):
        return

    # Đọc trạng thái từ rep_call (được gắn bởi hook trên)
    rep = getattr(request.node, "rep_call", None)
    if rep is None:
        status = "✅ PASS"
    elif rep.skipped:
        status = "⏭️ SKIP"
    elif rep.failed:
        status = "❌ FAIL"
    else:
        status = "✅ PASS"

    # ── Screenshot ─────────────────────────────────────────────────────
    shot_name = ""
    try:
        slug = getattr(cls, "_REPORT_SLUG", "size")
        shot_dir = os.path.join("screenshots", "production", "size_guide", slug)
        os.makedirs(shot_dir, exist_ok=True)
        ts  = datetime.now().strftime("%H%M%S")
        fn  = (request.node.originalname or request.node.name)[:30]
        shot_name = f"{fn}_{ts}.png"
        page.screenshot(path=os.path.join(shot_dir, shot_name))
    except Exception:
        shot_name = ""

    # ── Params từ parametrize ───────────────────────────────────────────
    params = {}
    if hasattr(request.node, "callspec"):
        params = request.node.callspec.params

    gender   = params.get("gender", "")
    height   = params.get("height", "")
    weight   = params.get("weight", "")
    label    = params.get("label", "")
    expected = (
        params.get("expected")
        or params.get("edge_size")
        or params.get("allowed")
        or ""
    )

    test_name = request.node.originalname or request.node.name
    chart_size = ""
    if height and weight:
        try:
            from ._helpers import get_expected_size
            product_code = getattr(cls, "_PRODUCT_CODE", "")
            if product_code:
                chart_size = get_expected_size(product_code, int(height), int(weight)) or ""
        except Exception:
            pass
    if not expected and chart_size:
        expected = f"~{chart_size}"
    # form_limit tests: kỳ vọng luôn là "không trả size" (không cần param)
    if test_name == "test_form_limit_validation" and not expected:
        expected = "không trả size"

    # Đọc kết quả AI thực tế từ page (popup vẫn còn mở sau test)
    actual_ai = ""
    try:
        from ._helpers import read_recommended_size, read_popup_message
        result = read_recommended_size(page)
        if result:
            actual_ai = result
        else:
            # Không có size → thử đọc validation/error message (dành cho invalid cases)
            msg = read_popup_message(page)
            if msg:
                actual_ai = msg
            elif test_name == "test_form_limit_validation" and status == "✅ PASS":
                actual_ai = "(form blocked)"
    except Exception:
        pass

    input_parts = []
    if gender:
        input_parts.append(str(gender))
    if height:
        input_parts.append(f"{height}cm")
    if weight:
        input_parts.append(f"{weight}kg")
    input_desc = " / ".join(input_parts)

    row = {
        "test_type":  test_name,
        "label":      label,
        "input":      input_desc,
        "expected":   str(expected) if expected else "",
        "chart_size": str(chart_size) if chart_size else "",
        "actual":     actual_ai,
        "status":     status,
        "screenshot": shot_name,
    }

    # Ghi vào cả cls._results (backward compat) VÀ _session_results
    cls._results.append(row)
    _session_results.setdefault(cls, []).append(row)


# ── Session-scope: lưu report sau khi toàn bộ session chạy xong ─────────────

@pytest.fixture(scope="session", autouse=True)
def _save_all_size_reports():
    """Lưu Markdown report cho từng sản phẩm sau khi session kết thúc."""
    yield
    for cls, rows in _session_results.items():
        if rows and hasattr(cls, "_save_report"):
            # Gán lại toàn bộ results rồi save
            cls._results = rows
            cls._save_report()
