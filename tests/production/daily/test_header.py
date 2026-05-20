"""Daily smoke: Header — logo, nav links, Đăng nhập button hiển thị đầy đủ."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "HEADER_SMOKE"


class TestDailyHeader(BaseDailyTest):
    _SUITE_NAME   = "HEADER_SMOKE"
    _REPORT_TITLE = "Daily Smoke: Header Navigation"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page

    def test_header_smoke(self):
        """Navigate Home → kiểm tra header: logo, nav links, Đăng nhập button."""
        # ── 1. Load trang chủ ────────────────────────────────────────────────
        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "1", "home_loaded")

        # ── 2. Header element hiển thị ───────────────────────────────────────
        header = self.page.locator("header").first
        header_ok = header.is_visible(timeout=10_000)
        self._record_check(TC, "Header element visible",
                           "✅ PASS" if header_ok else "❌ FAIL",
                           "header hiển thị" if header_ok else "không tìm thấy <header>")
        if not header_ok:
            pytest.fail("Header không hiển thị")

        # ── 3. Logo ──────────────────────────────────────────────────────────
        logo = header.locator(
            "a[href='/'], img[alt*='Tryonic'], img[alt*='logo'], "
            "a[href='/'] img, [class*='logo' i] img, [class*='logo' i] a"
        ).first
        logo_ok = logo.is_visible(timeout=5_000)
        self._record_check(TC, "Logo hiển thị trong header",
                           "✅ PASS" if logo_ok else "⚠️ WARN",
                           "logo visible" if logo_ok else "không tìm thấy logo")

        # ── 4. Nav links ─────────────────────────────────────────────────────
        nav_checks = [
            ("Sản phẩm",
             "button:has-text('Sản phẩm'), a:has-text('Sản phẩm')"),
            ("Chính sách",
             "button:has-text('Chính sách'), a:has-text('Chính sách')"),
            ("Hướng dẫn",
             "button:has-text('Hướng dẫn'), a:has-text('Hướng dẫn')"),
            ("Về Tryonic AI",
             "a:has-text('Về Tryonic AI'), a:has-text('Về Chúng tôi'), button:has-text('Về Tryonic AI')"),
        ]
        for label, selector in nav_checks:
            el = header.locator(selector).first
            ok = el.is_visible(timeout=5_000)
            self._record_check(TC, f"Nav link: {label}",
                               "✅ PASS" if ok else "❌ FAIL",
                               "visible" if ok else "không thấy trên header")
        self._shot(TC, "2", "header_nav_checked")

        # ── 5. Hover Chính sách → kiểm tra sub-links trong DOM ───────────────
        chinh_sach = header.locator(
            "button:has-text('Chính sách'), a:has-text('Chính sách')"
        ).first
        if chinh_sach.is_visible(timeout=3_000):
            chinh_sach.hover()
            self.page.wait_for_timeout(1_000)
        self._shot(TC, "3", "chinh_sach_hover")

        CHINH_SACH_SUB = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi trả"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
        ]
        missing_sub = [label for href, label in CHINH_SACH_SUB
                       if self.page.locator(f"a[href*='{href}']").count() == 0]
        self._record_check(TC, "Sub-links Chính sách trong DOM",
                           "✅ PASS" if not missing_sub else "❌ FAIL",
                           "đủ 4 sub-links" if not missing_sub
                           else f"thiếu: {', '.join(missing_sub)}")

        # ── 6. Nút Đăng nhập ────────────────────────────────────────────────
        self.page.mouse.move(0, 0)
        self.page.wait_for_timeout(500)
        login_btn = header.locator(
            ":text('Đăng nhập'), button:has-text('Đăng nhập')"
        ).first
        login_ok = login_btn.is_visible(timeout=5_000)
        self._record_check(TC, "Nút Đăng nhập visible",
                           "✅ PASS" if login_ok else "❌ FAIL",
                           "Đăng nhập button visible" if login_ok
                           else "không tìm thấy nút Đăng nhập")
        self._shot(TC, "4", "header_all_verified")

        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Header có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
