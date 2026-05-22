"""Session-scope autosave: sau khi session kết thúc → lưu report + gửi Google Chat."""
import time
import pytest


@pytest.fixture(scope="session", autouse=True)
def _save_daily_reports():
    _session_start = time.time()
    yield
    _duration = round(time.time() - _session_start, 1)

    from production.daily.test_price_checkout  import TestDailyPriceCheckout
    from production.daily.test_size_guide      import TestDailySizeGuide
    from production.daily.test_checkout_summary import TestDailyCheckoutSummary
    from production.daily.test_tryon           import TestDailyTryon
    from production.daily.test_print_tech      import TestDailyPrintTech
    from production.daily.test_artwork         import TestDailyArtwork
    from production.daily.test_header          import TestDailyHeader
    from production.daily.test_footer          import TestDailyFooter
    from production.daily.test_profile         import TestDailyProfile
    from production.daily.test_library_delete  import TestDailyLibraryDelete

    _ALL_CLASSES = (
        TestDailyPriceCheckout, TestDailySizeGuide, TestDailyCheckoutSummary,
        TestDailyTryon, TestDailyPrintTech, TestDailyArtwork,
        TestDailyHeader, TestDailyFooter, TestDailyProfile,
        TestDailyLibraryDelete,
    )

    # ── Lưu markdown + CSV từng suite ────────────────────────────────────────
    suites: dict = {}
    for cls in _ALL_CLASSES:
        if cls._results:
            cls._save_report()
            suites[cls._SUITE_NAME] = {
                "title":   cls._REPORT_TITLE,
                "results": list(cls._results),
            }

    # ── Gửi báo cáo tổng hợp lên Google Chat ─────────────────────────────────
    try:
        import os as _os
        _screenshots_base = _os.path.normpath(
            _os.path.join(
                _os.path.dirname(_os.path.abspath(__file__)),  # tests/production/daily/
                "..", "..", "..",                               # project root
                "screenshots", "daily",
            )
        )

        # Build GitHub Actions run URL (nếu đang chạy trên CI)
        _run_url = ""
        _gh_server = _os.getenv("GITHUB_SERVER_URL", "https://github.com")
        _gh_repo   = _os.getenv("GITHUB_REPOSITORY", "")
        _gh_run_id = _os.getenv("GITHUB_RUN_ID", "")
        if _gh_repo and _gh_run_id:
            _run_url = f"{_gh_server}/{_gh_repo}/actions/runs/{_gh_run_id}"

        from utils.google_chat_reporter import send_daily_report
        send_daily_report(
            suites,
            total_duration=_duration,
            artifact_url=_run_url,
            screenshots_base=_screenshots_base,
        )
    except Exception as exc:
        print(f"[GoogleChat] Lỗi khi gửi report: {exc}")
