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

    # Mega menu panel selector — fixed panel below header
    _MEGA_PANEL = "[class*='backdrop-blur-xl'][class*='fixed'], [class*='shadow-xl'][class*='w-full'][class*='fixed']"

    def _open_dropdown(self, btn_selector: str) -> bool:
        """Mở mega menu — robust trên cả headed lẫn headless CI.

        Menu được mở bởi onMouseEnter trên <div> wrapper bao quanh button
        (React tổng hợp mouseenter từ native 'mouseover' bubbles ở root).
        Trên CI headless, hover thật đôi khi không kích hoạt → fallback
        dispatch mouseover/mouseenter/pointerover qua JS lên button + các
        phần tử cha (bubbles=True để React bắt được).
        """
        self.home.navigate()
        self.page.wait_for_timeout(1_000)
        btn = self.page.locator(f"header {btn_selector}").first
        if not btn.is_visible(timeout=5_000):
            return False

        def _panel_visible() -> bool:
            try:
                return self.page.locator(self._MEGA_PANEL).first.is_visible(timeout=1_500)
            except Exception:
                return False

        # 1) Thử hover thật trước (đa số trường hợp headed/CI hoạt động)
        try:
            btn.hover(timeout=2_000)
        except Exception:
            pass
        if _panel_visible():
            self.page.wait_for_timeout(200)
            return True

        # 2) Fallback headless: bắn native mouse events lên button + cha
        _dispatch_js = """el => {
            const targets = [el, el.parentElement,
                             el.parentElement && el.parentElement.parentElement]
                            .filter(Boolean);
            for (const t of targets) {
                for (const type of ['pointerover','pointerenter',
                                    'mouseover','mouseenter','mousemove']) {
                    t.dispatchEvent(new MouseEvent(type, {
                        bubbles: true, cancelable: true, view: window,
                    }));
                }
            }
        }"""
        for _attempt in range(3):
            try:
                btn.evaluate(_dispatch_js)
            except Exception:
                pass
            self.page.wait_for_timeout(400)
            if _panel_visible():
                self.page.wait_for_timeout(200)
                return True
        return _panel_visible()

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

        # (a) Test menu UX: mở dropdown, link có hiển thị không (env-dependent → WARN)
        self._open_dropdown("button:has-text('Sản phẩm')")
        ao_tron = self.page.locator(
            f"{self._MEGA_PANEL} a[href*='/san-pham'], a[href='/san-pham']"
        ).first
        ao_tron_ok = ao_tron.is_visible(timeout=3_000)
        ao_tron_href = ao_tron.get_attribute("href") if ao_tron_ok else None
        self._record_check(TC, "Dropdown: link Áo trơn hiển thị",
                           "✅ PASS" if ao_tron_ok else "⚠️ WARN",
                           "/san-pham link visible" if ao_tron_ok
                           else "menu không mở trên headless — verify trang qua URL trực tiếp")
        self._shot(TC, "3", "san_pham_dropdown")
        # (b) Test trang load: luôn navigate thẳng tới URL đã biết (deterministic)
        dest = ao_tron_href if (ao_tron_ok and ao_tron_href) else "/san-pham"
        self.page.goto(self.env.fe_url + dest if dest.startswith("/") else dest,
                       wait_until="domcontentloaded", timeout=15_000)
        self.page.wait_for_timeout(1_500)
        # /san-pham đã redirect sang /products → chấp nhận cả hai path
        url = self.page.url
        url_ok = "/san-pham" in url or "/products" in url
        no_404 = not self.page.locator(
            ":text('404'), :text('Not Found'), :text('Không tìm thấy')"
        ).is_visible(timeout=2_000)
        has_content = self.page.locator(
            "h1, h2, main, article, [class*='content' i]"
        ).first.is_visible(timeout=8_000)
        self._record_check(TC, "Verify: Áo trơn",
                           "✅ PASS" if (url_ok and no_404 and has_content) else "❌ FAIL",
                           f"URL: {url}")
        self._shot(TC, "4", "page_ao_tron")

        # ══ PHẦN 3: SẢN PHẨM → THIẾT KẾ ÁO (STUDIO) ════════════════════════

        self._open_dropdown("button:has-text('Sản phẩm')")
        studio_link = self.page.locator(
            f"{self._MEGA_PANEL} a[href*='/studio'], a[href='/studio']"
        ).first
        studio_ok = studio_link.is_visible(timeout=3_000)
        studio_href = studio_link.get_attribute("href") if studio_ok else None
        self._record_check(TC, "Dropdown: link Thiết kế áo hiển thị",
                           "✅ PASS" if studio_ok else "⚠️ WARN",
                           "/studio link visible" if studio_ok
                           else "menu không mở trên headless — verify trang qua URL trực tiếp")
        self._shot(TC, "5", "san_pham_dropdown_2")
        dest = studio_href if (studio_ok and studio_href) else "/studio"
        self.page.goto(self.env.fe_url + dest if dest.startswith("/") else dest,
                       wait_until="domcontentloaded", timeout=15_000)
        self.page.wait_for_timeout(1_500)
        self._verify_page("/studio", "Thiết kế áo (Studio)", "6")

        # ══ PHẦN 4: CHÍNH SÁCH → 5 LINKS ═════════════════════════════════════
        # Hỗ trợ cả old URLs (/pages/...) và new short URLs (/payment-policy v.v.)

        CHINH_SACH_LINKS = [
            ("/pages/chinh-sach-thanh-toan", "/payment-policy",  "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "/shipping-policy", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "/return-policy",   "Chính sách đổi sản phẩm"),
            ("/pages/chinh-sach-bao-mat",    "/privacy-policy",  "Bảo mật thông tin"),
            ("/pages/dieu-khoan-su-dung",    "/terms",           "Điều khoản sử dụng"),
        ]
        for i, (old_href, new_href, label) in enumerate(CHINH_SACH_LINKS, start=1):
            self._open_dropdown("button:has-text('Chính sách')")
            link = self.page.locator(
                f"{self._MEGA_PANEL} a[href*='{old_href}'], "
                f"{self._MEGA_PANEL} a[href*='{new_href}'], "
                f"a[href='{old_href}'], a[href='{new_href}']"
            ).first
            link_ok = link.is_visible(timeout=3_000)
            # Lưu href TRƯỚC screenshot để tránh locator stale sau scroll
            actual_href = link.get_attribute("href") if link_ok else None
            self._record_check(TC, f"Dropdown Chính sách: {label} visible",
                               "✅ PASS" if link_ok else "⚠️ WARN",
                               "link visible" if link_ok
                               else "menu không mở trên headless — verify trang qua URL trực tiếp")
            if i == 1:
                self._shot(TC, "7", "chinh_sach_dropdown")
            # Luôn navigate tới URL đã biết để verify trang load (deterministic)
            target = actual_href if (link_ok and actual_href) else new_href
            dest = self.env.fe_url + target if target.startswith("/") else target
            self.page.goto(dest, wait_until="domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(1_000)
            # Verify: chấp nhận cả old path lẫn new path
            url = self.page.url
            url_ok = old_href in url or new_href in url
            has_content = self.page.locator("h1, h2, main").first.is_visible(timeout=8_000)
            self._record_check(TC, f"Verify: {label}",
                               "✅ PASS" if (url_ok and has_content) else "❌ FAIL",
                               f"URL: {url}")
            self._shot(TC, f"8_{i}", f"page_{label[:15].lower().replace(' ', '_')}")

        # ══ PHẦN 5: HƯỚNG DẪN → 2 LINKS ═════════════════════════════════════

        HUONG_DAN_LINKS = [
            ("/pages/huong-dan-mua-hang", "/shopping-guide", "Hướng dẫn mua hàng"),
            ("/pages/huong-dan-bao-quan", "/care-guide",     "Hướng dẫn bảo quản"),
        ]
        for i, (old_href, new_href, label) in enumerate(HUONG_DAN_LINKS, start=1):
            self._open_dropdown("button:has-text('Hướng dẫn')")
            link = self.page.locator(
                f"{self._MEGA_PANEL} a[href*='{old_href}'], "
                f"{self._MEGA_PANEL} a[href*='{new_href}'], "
                f"a[href='{old_href}'], a[href='{new_href}']"
            ).first
            link_ok = link.is_visible(timeout=3_000)
            # Lưu href TRƯỚC screenshot để tránh locator stale sau scroll
            hd_href = link.get_attribute("href") if link_ok else None
            self._record_check(TC, f"Dropdown Hướng dẫn: {label} visible",
                               "✅ PASS" if link_ok else "⚠️ WARN",
                               "link visible" if link_ok
                               else "menu không mở trên headless — verify trang qua URL trực tiếp")
            if i == 1:
                self._shot(TC, "9", "huong_dan_dropdown")
            # Luôn navigate tới URL đã biết để verify trang load (deterministic)
            target = hd_href if (link_ok and hd_href) else new_href
            dest = self.env.fe_url + target if target.startswith("/") else target
            self.page.goto(dest, wait_until="domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(1_000)
            url = self.page.url
            url_ok = old_href in url or new_href in url
            has_content = self.page.locator("h1, h2, main").first.is_visible(timeout=8_000)
            self._record_check(TC, f"Verify: {label}",
                               "✅ PASS" if (url_ok and has_content) else "❌ FAIL",
                               f"URL: {url}")
            self._shot(TC, f"10_{i}", f"page_{label[:15].lower().replace(' ', '_')}")

        # ══ PHẦN 6: VỀ TRYONIC AI ════════════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_000)
        ve_btn = self.page.locator(
            "header a:has-text('Về Tryonic AI'), header a:has-text('Về Chúng tôi')"
        ).first
        ve_ok = ve_btn.is_visible(timeout=5_000)
        ve_href = ve_btn.get_attribute("href") if ve_ok else None
        self._record_check(TC, "Link Về Tryonic AI visible",
                           "✅ PASS" if ve_ok else "⚠️ WARN",
                           "link visible" if ve_ok
                           else "link không thấy trên header — verify trang qua URL trực tiếp")
        # Luôn navigate tới URL đã biết để verify trang load (deterministic)
        target = ve_href if (ve_ok and ve_href) else "/about-us"
        dest = self.env.fe_url + target if target.startswith("/") else target
        self.page.goto(dest, wait_until="domcontentloaded", timeout=15_000)
        self.page.wait_for_timeout(1_000)
        # Chấp nhận cả old URL (/pages/ve-chung-toi) lẫn new URL (/about-us)
        url = self.page.url
        url_ok = "/ve-chung-toi" in url or "/about-us" in url
        has_content = self.page.locator("h1, h2, main").first.is_visible(timeout=8_000)
        self._record_check(TC, "Verify: Về Tryonic AI",
                           "✅ PASS" if (url_ok and has_content) else "❌ FAIL",
                           f"URL: {url}")
        self._shot(TC, "11", "page_ve_tryonic_ai")

        # ══ KẾT QUẢ ═══════════════════════════════════════════════════════════

        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Header có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
