"""Session-scope autosave: sau khi session kết thúc → lưu report + gửi Google Chat."""
import time
import pytest

# ── Thứ tự ưu tiên chạy test ─────────────────────────────────────────────────
# test_artwork phải chạy trước test_print_tech và test_tryon
# để design vừa tạo có thể được dùng ngay bởi 2 test AI sau.
_TEST_ORDER = [
    "test_artwork_smoke",       # 1 — tạo artwork (AI generation)
    "test_auth_smoke",          # 2
    "test_checkout_with_coupon_giam20",  # 3
    "test_footer_smoke",        # 4
    "test_forgot_password_smoke",  # 5
    "test_header_smoke",        # 6
    "test_library_delete_image",   # 7
    "test_library_delete_new_artwork",  # 8
    "test_profile_smoke",       # 9
    "test_ai_size_smoke",       # 10
    "test_buynow_checkout_price",  # 11
    "test_cart_checkout_price",    # 12
    "test_print_tech_smoke",    # 13 — phải sau artwork
    "test_tryon_smoke",         # 14 — phải sau artwork
    "test_pt01_buynow",         # 15 — Design BuyNow PT01
    "test_m21_cart",            # 16 — Design Cart M21 all sizes
    "test_pt01_mydesigns",      # 17 — Design My Designs PT01
    "test_multi_cart",          # 18 — Design Multi-Cart PT01 + M21
]


def pytest_collection_modifyitems(items):
    """Sắp xếp daily tests: artwork chạy trước print_tech và tryon."""
    def _sort_key(item):
        base = item.originalname.split("[")[0]  # bỏ phần [chromium-...]
        try:
            return _TEST_ORDER.index(base)
        except ValueError:
            return len(_TEST_ORDER)  # test không có trong list → chạy cuối

    items.sort(key=_sort_key)


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
    from production.daily.test_auth_login      import TestDailyAuthLogin
    from production.daily.test_forgot_password import TestDailyForgotPassword
    from production.daily.test_design_buynow_daily   import TestDailyDesignBuynow
    from production.daily.test_design_cart_m21_daily import TestDailyDesignCartM21
    from production.daily.test_design_mydesigns_daily import TestDailyDesignMydesigns
    from production.daily.test_design_multi_cart_daily import TestDailyDesignMultiCart

    _ALL_CLASSES = (
        TestDailyPriceCheckout, TestDailySizeGuide, TestDailyCheckoutSummary,
        TestDailyTryon, TestDailyPrintTech, TestDailyArtwork,
        TestDailyHeader, TestDailyFooter, TestDailyProfile,
        TestDailyLibraryDelete, TestDailyAuthLogin, TestDailyForgotPassword,
        TestDailyDesignBuynow, TestDailyDesignCartM21,
        TestDailyDesignMydesigns, TestDailyDesignMultiCart,
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

    # ── Lưu AI timings TRƯỚC (độc lập — luôn chạy dù gửi Chat có lỗi) ────────
    try:
        import json as _json, os as _os2
        from utils.google_chat_reporter import _extract_ai_timings
        _ai_times = _extract_ai_timings(suites)
        if _ai_times:
            _timings_dir = _os2.path.join(_os2.getcwd(), "reports")
            _os2.makedirs(_timings_dir, exist_ok=True)
            with open(_os2.path.join(_timings_dir, "ai_timings.json"), "w", encoding="utf-8") as _f:
                _json.dump(_ai_times, _f, ensure_ascii=False, indent=2)
            print(f"[AI Timings] saved: {_ai_times}")
        else:
            print("[AI Timings] nothing to save (no timing data found in results)")
    except Exception as _te:
        print(f"[AI Timings] save error: {_te}")

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
