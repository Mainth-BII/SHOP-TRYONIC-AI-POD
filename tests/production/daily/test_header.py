"""Daily smoke: Header — logo, nav links, click-through và verify data từng page."""
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

    # ── Helper ───────────────────────────────────────────────────────────────

    def _verify_page(self, expected_path: str, page_label: str, step: str) -> bool:
        """Verify trang đã load đúng: URL đúng, có content, không 404."""
        url_ok = expected_path in self.page.url
        no_404 = not self.page.locator(
            ":text('404'), :text('Not Found'), :text('Không tìm thấy')"
        ).is_visible(timeout=2_000)
        has_content = self.page.locator("h1, h2, main, article, [class*='content' i]").first \
                          .is_visible(timeout=8_000)
        ok = url_ok and no_404 and has_content
        detail = f"URL: {self.page.url}"
        if not url_ok:
            detail = f"URL sai — expected '{expected_path}', got: {self.page.url}"
        elif not no_404:
            detail = f"Trang hiển thị lỗi 404 — {self.page.url}"
        elif not has_content:
            detail = f"Không có nội dung (h1/main) — {self.page.url}"
        self._record_check(TC, f"Verify: {page_label}",
                           "✅ PASS" if ok else "❌ FAIL", detail)
        self._shot(TC, step, f"page_{page_label.lower().replace(' ', '_')[:20]}")
        return ok

    def _open_dropdown(self, btn_selector: str) -> bool:
        """Hover lên nav button → mở dropdown."""
        self.home.navigate()
        self.page.wait_for_timeout(1_000)
        btn = self.page.locator(f"header {btn_selector}").first
        if not btn.is_visible(timeout=5_000):
            return False
        btn.hover()
        self.page.wait_for_timeout(800)
        return True

    # ── Test ─────────────────────────────────────────────────────────────────

    def test_header_smoke(self):
        """Header elements + click-through từng menu item → verify data."""

        # ══ PHẦN 1: KIỂM TRA HEADER ELEMENTS ════════════════════════════════

        # 1. Load home
        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "1", "home_loaded")

        # 2. Header visible
        header = self.page.locator("header").first
        header_ok = header.is_visible(timeout=10_000)
        self._record_check(TC, "Header element visible",
                           "✅ PASS" if header_ok else "❌ FAIL",
                           "header hiển thị" if header_ok else "không tìm thấy <header>")
        if not header_ok:
            pytest.fail("Header không hiển thị")

        # 3. Logo
        logo = header.locator(
            "a[href='/'], img[alt*='Tryonic'], img[alt*='logo'], "
            "[class*='logo' i] img, [class*='logo' i] a"
        ).first
        self._record_check(TC, "Logo hiển thị trong header",
                           "✅ PASS" if logo.is_visible(timeout=5_000) else "⚠️ WARN",
                           "logo visible")

        # 4. Nav links tồn tại
        for label, selector in [
            ("Sản phẩm",     "button:has-text('Sản phẩm'), a:has-text('Sản phẩm')"),
            ("Chính sách",   "button:has-text('Chính sách'), a:has-text('Chính sách')"),
            ("Hướng dẫn",   "button:has-text('Hướng dẫn'), a:has-text('Hướng dẫn')"),
            ("Về Tryonic AI", "a:has-text('Về Tryonic AI'), a:has-text('Về Chúng tôi')"),
        ]:
            el = header.locator(selector).first
            ok = el.is_visible(timeout=5_000)
            self._record_check(TC, f"Nav link hiển thị: {label}",
                               "✅ PASS" if ok else "❌ FAIL",
                               "visible" if ok else "không thấy trên header")

        # 5. Nút Đăng nhập
        login_ok = header.locator("button:has-text('Đăng nhập'), :text('Đăng nhập')") \
                         .first.is_visible(timeout=5_000)
        self._record_check(TC, "Nút Đăng nhập visible",
                           "✅ PASS" if login_ok else "❌ FAIL",
                           "Đăng nhập button visible")
        self._shot(TC, "2", "header_elements_checked")

        # ══ PHẦN 2: SẢN PHẨM → ÁO TRƠN ═════════════════════════════════════

        self._open_dropdown("button:has-text('Sản phẩm')")
        self._shot(TC, "3", "san_pham_dropdown")

        ao_tron = self.page.locator("a[href*='/san-pham']").first
        ao_tron_ok = ao_tron.is_visible(timeout=5_000)
        self._record_check(TC, "Dropdown: link Áo trơn hiển thị",
                           "✅ PASS" if ao_tron_ok else "❌ FAIL",
                           "/san-pham link visible")
        if ao_tron_ok:
            ao_tron.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(1_500)
            self._verify_page("/san-pham", "Áo trơn", "4")
        else:
            self._record_check(TC, "Verify: Áo trơn", "⚠️ WARN", "skip — link không thấy")

        # ══ PHẦN 3: SẢN PHẨM → THIẾT KẾ ÁO (STUDIO) ════════════════════════

        self._open_dropdown("button:has-text('Sản phẩm')")
        self._shot(TC, "5", "san_pham_dropdown_2")

        studio_link = self.page.locator("a[href*='/studio']").first
        studio_ok = studio_link.is_visible(timeout=5_000)
        self._record_check(TC, "Dropdown: link Thiết kế áo hiển thị",
                           "✅ PASS" if studio_ok else "❌ FAIL",
                           "/studio link visible")
        if studio_ok:
            studio_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(1_500)
            self._verify_page("/studio", "Thiết kế áo (Studio)", "6")
        else:
            self._record_check(TC, "Verify: Thiết kế áo (Studio)", "⚠️ WARN", "skip — link không thấy")

        # ══ PHẦN 4: CHÍNH SÁCH → 5 LINKS ═════════════════════════════════════

        CHINH_SACH_LINKS = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi sản phẩm"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
            ("/pages/dieu-khoan-su-dung",    "Điều khoản sử dụng"),
        ]
        for i, (href, label) in enumerate(CHINH_SACH_LINKS, start=1):
            self._open_dropdown("button:has-text('Chính sách')")
            if i == 1:
                self._shot(TC, "7", "chinh_sach_dropdown")
            link = self.page.locator(f"a[href*='{href}']").first
            link_ok = link.is_visible(timeout=5_000)
            self._record_check(TC, f"Dropdown Chính sách: {label} visible",
                               "✅ PASS" if link_ok else "❌ FAIL",
                               f"{href} link visible" if link_ok else "link không thấy")
            if link_ok:
                link.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(1_000)
                self._verify_page(href, label, f"8_{i}")
            else:
                self._record_check(TC, f"Verify: {label}", "⚠️ WARN", "skip")

        # ══ PHẦN 5: HƯỚNG DẪN → 2 LINKS ═════════════════════════════════════

        HUONG_DAN_LINKS = [
            ("/pages/huong-dan-mua-hang", "Hướng dẫn mua hàng"),
            ("/pages/huong-dan-bao-quan", "Hướng dẫn bảo quản"),
        ]
        for i, (href, label) in enumerate(HUONG_DAN_LINKS, start=1):
            self._open_dropdown("button:has-text('Hướng dẫn')")
            if i == 1:
                self._shot(TC, "9", "huong_dan_dropdown")
            link = self.page.locator(f"a[href*='{href}']").first
            link_ok = link.is_visible(timeout=5_000)
            self._record_check(TC, f"Dropdown Hướng dẫn: {label} visible",
                               "✅ PASS" if link_ok else "❌ FAIL",
                               f"{href} link visible" if link_ok else "link không thấy")
            if link_ok:
                link.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(1_000)
                self._verify_page(href, label, f"10_{i}")
            else:
                self._record_check(TC, f"Verify: {label}", "⚠️ WARN", "skip")

        # ══ PHẦN 6: VỀ TRYONIC AI ════════════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_000)
        ve_btn = self.page.locator(
            "header a:has-text('Về Tryonic AI'), header a:has-text('Về Chúng tôi')"
        ).first
        ve_ok = ve_btn.is_visible(timeout=5_000)
        self._record_check(TC, "Link Về Tryonic AI visible",
                           "✅ PASS" if ve_ok else "❌ FAIL",
                           "link visible" if ve_ok else "link không thấy")
        if ve_ok:
            ve_btn.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(1_000)
            self._verify_page("/pages/ve-chung-toi", "Về Tryonic AI", "11")
        else:
            self._record_check(TC, "Verify: Về Tryonic AI", "⚠️ WARN", "skip")

        # ══ KẾT QUẢ ═══════════════════════════════════════════════════════════

        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Header có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
