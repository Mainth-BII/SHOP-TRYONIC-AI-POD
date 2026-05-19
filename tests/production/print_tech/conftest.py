"""Session-scope autosave: sau khi session kết thúc → lưu print tech report."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def _save_print_tech_reports():
    yield
    from production.print_tech.test_print_tech_flow import TestPrintTechFlow
    if TestPrintTechFlow._results:
        TestPrintTechFlow._save_report()
