"""Daily smoke: AI Gợi ý Công nghệ in — 1 design để verify luồng end-to-end."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "PRINT_TECH_SMOKE"


class TestDailyPrintTech(BaseDailyTest):
    _SUITE_NAME   = "PRINT_TECH_SMOKE"
    _REPORT_TITLE = "Daily Smoke: AI Gợi ý Công nghệ in"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page
        from pages.print_tech_page import PrintTechPage
        self.pt = PrintTechPage(page, env.fe_url)

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

    def test_print_tech_smoke(self):
        """Login → thử lần lượt đến design đầu tiên vào được /review → AI gợi ý công nghệ in."""
        self._login()

        # ── 1. Lấy tối đa 10 URL, thử đến khi có 1 design vào được /review ──
        studio_urls = self.pt.get_studio_urls(max_n=10)
        if not studio_urls:
            self._record_check(TC, "Tìm design", "⚠️ SKIP",
                               "0 design — tài khoản chưa có thiết kế nào", "≥ 1")
            pytest.skip("Tài khoản test không có design nào trong Thiết kế của tôi — cần tạo test data")
        self._record_check(TC, "Tìm design", "✅ PASS", f"{len(studio_urls)} design", "≥ 1")

        # ── 2. Thử lần lượt đến design nào vào được /review VÀ click được AI ─
        success = False
        for url in studio_urls:
            ok = self.pt.open_review(url)
            if not ok:
                print(f"  [SKIP] Không vào được /review: {url}")
                continue

            self._record_check(TC, "Vào /review", "✅ PASS", self.page.url)
            self._shot(TC, "1", "review_input")

            clicked = self.pt.click_ai_suggest()
            if not clicked:
                print(f"  [SKIP] Gợi ý bằng AI không khả dụng: {url}")
                continue

            self._record_check(TC, "Click Gợi ý bằng AI", "✅ PASS")
            success = True
            break

        if not success:
            self._record_check(TC, "Vào /review + Gợi ý AI", "❌ FAIL",
                               f"thử {len(studio_urls)} design đều thất bại", "≥ 1 thành công")
            pytest.fail(f"Không design nào chạy được AI gợi ý công nghệ in (đã thử {len(studio_urls)})")

        # ── 3. Chờ AI xong → screenshot ──────────────────────────────────────
        done, elapsed = self.pt.wait_ai_done()
        tech = self.pt.get_suggested_tech()
        self._record_check(TC, "AI phân tích xong",
                           "✅ PASS" if done else "❌ FAIL",
                           f"{tech} ({elapsed}s)" if done else f"timeout {elapsed}s — AI không trả kết quả")

        self._shot(TC, "2", "ai_result")

        # ── 4. Click ^ expand danh sách công nghệ ────────────────────────────
        expanded = self.pt.expand_tech_list(tech)
        self._record_check(TC, "Expand danh sách công nghệ",
                           "✅ PASS" if expanded else "❌ FAIL",
                           "danh sách mở thành công" if expanded else "không click được nút expand")
        if expanded:
            self._shot(TC, "3", "tech_expanded")

        # ══ KẾT QUẢ ══════════════════════════════════════════════════════════
        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Print tech có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
