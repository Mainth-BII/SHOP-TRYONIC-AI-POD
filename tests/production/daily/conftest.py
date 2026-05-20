"""Session-scope autosave: sau khi session kết thúc → lưu report từng suite."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def _save_daily_reports():
    yield
    from production.daily.test_price_checkout import TestDailyPriceCheckout
    from production.daily.test_size_guide import TestDailySizeGuide
    from production.daily.test_checkout_summary import TestDailyCheckoutSummary
    from production.daily.test_tryon import TestDailyTryon
    from production.daily.test_print_tech import TestDailyPrintTech
    from production.daily.test_artwork import TestDailyArtwork
    from production.daily.test_header import TestDailyHeader
    from production.daily.test_footer import TestDailyFooter

    for cls in (TestDailyPriceCheckout, TestDailySizeGuide, TestDailyCheckoutSummary,
                TestDailyTryon, TestDailyPrintTech, TestDailyArtwork,
                TestDailyHeader, TestDailyFooter):
        if cls._results:
            cls._save_report()
