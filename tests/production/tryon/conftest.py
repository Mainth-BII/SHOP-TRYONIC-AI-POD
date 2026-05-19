"""Session-scope autosave: sau khi session kết thúc → lưu tryon report."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def _save_tryon_reports():
    yield
    from production.tryon.test_tryon_flow import TestTryonFlow
    if TestTryonFlow._results:
        TestTryonFlow._save_report()
