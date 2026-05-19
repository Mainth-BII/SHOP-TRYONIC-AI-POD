"""Print Tech flow — Thiết kế của tôi → AI Gợi ý Công nghệ in.

Luồng:
1. Login → /my-designs → lấy tối đa 10 design URL
2. Mỗi design: vào /review → screenshot INPUT → click 'Gợi ý bằng AI'
3. Chờ AI xong → screenshot RESULT → click ^ → screenshot EXPANDED

Screenshots lưu tại: screenshots/daily/print_tech/{design_label}/
Report lưu tại:      reports/daily/print_tech_<ts>.md + .csv
"""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.print_tech.base_print_tech_test import BasePrintTechTest

_DOMAIN = "print_tech"
_ROOT   = "daily"


class TestPrintTechFlow(BasePrintTechTest):
    """AI Gợi ý Công nghệ in — duyệt Thiết kế của tôi."""

    _SUITE_NAME   = "PRINT_TECH"
    _REPORT_TITLE = "Daily Print Tech: AI Gợi ý Công nghệ in"
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

    def test_print_tech_my_designs(self):
        """Login → /my-designs → mỗi design: AI gợi ý công nghệ in → expand list."""

        # ── 1. Login ─────────────────────────────────────────────────────────
        self._login()

        # ── 2. Thu thập studio URLs ──────────────────────────────────────────
        studio_urls = self.pt.get_studio_urls(max_n=10)
        assert len(studio_urls) > 0, "Không tìm thấy design nào trong Thiết kế của tôi"

        # ── 3. Duyệt từng design ─────────────────────────────────────────────
        for idx, studio_url in enumerate(studio_urls):
            design_label = f"design_{idx+1:02d}"
            print(f"\n  ── {design_label}: {studio_url}")

            ok = self.pt.open_review(studio_url)
            if not ok:
                self._record(design_label, "⏭️ SKIP", note="không vào được /review")
                continue

            # Screenshot INPUT (trang review trước khi chạy AI)
            self.pt.shot(design_label, "0", "input", domain=_DOMAIN, root=_ROOT)
            review_url = self.page.url

            # ── Click Gợi ý bằng AI ──────────────────────────────────────────
            clicked = self.pt.click_ai_suggest()
            if not clicked:
                self._record(design_label, "❌ FAIL", note="không click được Gợi ý bằng AI")
                continue

            # ── Chờ AI xong → ghi thời gian ──────────────────────────────────
            done, elapsed = self.pt.wait_ai_done()
            tech = self.pt.get_suggested_tech()
            if not done:
                self.pt.shot(design_label, "1", "ai_timeout", domain=_DOMAIN, root=_ROOT)
                self._record(design_label, "⚠️ WARN", elapsed=elapsed, tech=tech,
                             note="AI timeout")
                continue

            # Screenshot RESULT (sau khi AI gợi ý xong)
            self.pt.shot(design_label, "1", "ai_result", domain=_DOMAIN, root=_ROOT)

            # ── Click ^ để expand danh sách công nghệ ────────────────────────
            expanded = self.pt.expand_tech_list(tech)
            if expanded:
                self.page.wait_for_timeout(500)
                self.pt.shot(design_label, "2", "tech_expanded", domain=_DOMAIN, root=_ROOT)

            status = "✅ PASS" if done else "⚠️ WARN"
            note   = "" if expanded else "expand không thành công"
            self._record(design_label, status, elapsed=elapsed, tech=tech, note=note)

        print(f"\n  [DONE] Screenshots: screenshots/{_ROOT}/{_DOMAIN}/")
