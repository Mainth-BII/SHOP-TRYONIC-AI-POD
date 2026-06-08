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
