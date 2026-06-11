"""conftest cho luồng E2E full-flow.

KHÓA CỨNG: mọi test trong tests/e2e/ CHỈ chạy trên môi trường TEST.
Đây là tách bạch hoàn toàn với Daily (chạy PROD, dừng trước thanh toán):
luồng E2E được phép đi HẾT flow (đặt đơn + thanh toán sandbox) nên TUYỆT ĐỐI
không được chạy nhầm trên PROD.

Hai lớp bảo vệ:
  1. Collection guard: nếu --env != test → skip toàn bộ test e2e (fail-safe,
     không bao giờ đụng PROD kể cả khi gõ nhầm `pytest tests/ --env=prod`).
  2. Runtime assert: fixture autouse chốt lại env.name == 'test' lúc chạy.
"""
from __future__ import annotations
import time
import pytest


def pytest_collection_modifyitems(config, items):
    """Skip mọi test e2e nếu không phải --env=test (fail-safe, không đụng PROD)."""
    env_name = (config.getoption("--env") or "").lower()
    if env_name == "test":
        return
    skip_non_test = pytest.mark.skip(
        reason=f"E2E full-flow CHỈ chạy trên TEST (--env=test). Hiện: --env={env_name}",
    )
    for item in items:
        if "/e2e/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip_non_test)


@pytest.fixture(autouse=True)
def _assert_test_env(env):
    """Chốt chặn lần 2 lúc runtime — phòng trường hợp guard bị bỏ qua."""
    assert env.name == "test", (
        f"🚫 E2E full-flow chỉ được chạy trên TEST env, đang là '{env.name}'. "
        f"Dùng: pytest tests/e2e/ --env=test"
    )


@pytest.fixture(scope="session", autouse=True)
def _send_e2e_report():
    """Cuối session E2E → gom kết quả + gửi Google Chat (giống luồng daily).

    Dùng chung reporter send_daily_report, nhưng:
      - title riêng '🚀 Tryonic E2E Full Flow' để phân biệt với daily.
      - webhook lấy từ GOOGLE_CHAT_WEBHOOK_URL (workflow e2e map sang
        secret GOOGLE_CHAT_WEBHOOK_URL_E2E → gửi vào channel e2e riêng).
    """
    _start = time.time()
    yield
    _duration = round(time.time() - _start, 1)

    # Lấy ĐÚNG class mà pytest đã chạy qua __subclasses__ (không import theo path
    # — vì tests/e2e/ không có __init__.py nên import-path khác tên module pytest
    # dùng → sẽ ra class rỗng). Lọc theo SUITE_NAME bắt đầu 'E2E'.
    try:
        from production.daily.base_daily_test import BaseDailyTest
    except Exception as exc:
        print(f"[GoogleChat][E2E] import BaseDailyTest lỗi: {exc}")
        return

    suites: dict = {}
    for cls in BaseDailyTest.__subclasses__():
        name = getattr(cls, "_SUITE_NAME", "")
        if not str(name).upper().startswith("E2E"):
            continue
        if getattr(cls, "_results", None):
            try:
                cls._save_report()
            except Exception as exc:
                print(f"[E2E] _save_report({name}) lỗi: {exc}")
            suites[name] = {
                "title":   getattr(cls, "_REPORT_TITLE", name),
                "results": list(cls._results),
            }

    if not suites:
        print("[GoogleChat][E2E] Không có kết quả để gửi.")
        return

    import os as _os
    # Link GitHub Actions run (nếu chạy CI)
    _run_url = ""
    _gh_repo   = _os.getenv("GITHUB_REPOSITORY", "")
    _gh_run_id = _os.getenv("GITHUB_RUN_ID", "")
    if _gh_repo and _gh_run_id:
        _server = _os.getenv("GITHUB_SERVER_URL", "https://github.com")
        _run_url = f"{_server}/{_gh_repo}/actions/runs/{_gh_run_id}"

    _shots_base = _os.path.normpath(
        _os.path.join(_os.getcwd(), "screenshots", "e2e_lifecycle")
    )

    try:
        from utils.google_chat_reporter import send_daily_report
        send_daily_report(
            suites,
            total_duration=_duration,
            artifact_url=_run_url,
            screenshots_base=_shots_base,
            header_title="🚀 Tryonic E2E Full Flow",
        )
    except Exception as exc:
        print(f"[GoogleChat][E2E] Lỗi khi gửi report: {exc}")
