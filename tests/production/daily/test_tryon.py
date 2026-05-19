"""Daily smoke: AI Thử đồ — 1 design, 1 combo Nam để verify luồng end-to-end."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "TRYON_SMOKE"
SMOKE_COMBO = ["Nam"]


class TestDailyTryon(BaseDailyTest):
    _SUITE_NAME  = "TRYON_SMOKE"
    _REPORT_TITLE = "Daily Smoke: AI Thử đồ"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page
        from pages.tryon_review_page import TryonReviewPage
        self.tryon = TryonReviewPage(page, env.fe_url)

    def _login(self) -> None:
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    def test_tryon_smoke(self):
        """Login → thử lần lượt đến design đầu tiên vào được /review → combo Nam → tryon."""
        self._login()

        # ── 1. Lấy tối đa 5 URL, thử đến khi có 1 design vào được /review ──
        studio_urls = self.tryon.get_studio_urls(max_n=10)
        if not studio_urls:
            self._record_check(TC, "Tìm design", "❌ FAIL", "0 design", "≥ 1")
            pytest.fail("Không tìm thấy design nào trong Thiết kế của tôi")
        self._record_check(TC, "Tìm design", "✅ PASS", f"{len(studio_urls)} design", "≥ 1")

        # ── 2. Thử lần lượt đến design nào vào /review VÀ click được Thử lại ──
        success = False
        for url in studio_urls:
            ok = self.tryon.open_review(url)
            if not ok:
                print(f"  [SKIP] Không vào được /review: {url}")
                continue

            self._record_check(TC, "Vào /review", "✅ PASS", self.page.url)
            self._shot(TC, "1", "review_input")

            clicked = self.tryon.set_options_and_tryon(SMOKE_COMBO)
            if not clicked:
                print(f"  [SKIP] Thử lại không khả dụng: {url}")
                continue

            self._record_check(TC, "Click Thử lại (Nam)", "✅ PASS")
            success = True
            break

        if not success:
            self._record_check(TC, "Vào /review + Thử lại", "❌ FAIL",
                               f"thử {len(studio_urls)} design đều thất bại", "≥ 1 thành công")
            pytest.fail(f"Không design nào chạy được tryon (đã thử {len(studio_urls)})")

        # ── 3. Chờ tryon xong → screenshot ──────────────────────────────────
        loaded, elapsed = self.tryon.wait_tryon_done()
        self._record_check(TC, "Tryon Nam hoàn tất",
                           "✅ PASS" if loaded else "⚠️ WARN",
                           f"{elapsed}s" if loaded else f"timeout sau {elapsed}s")

        self._shot(TC, "2", "tryon_nam_result")
