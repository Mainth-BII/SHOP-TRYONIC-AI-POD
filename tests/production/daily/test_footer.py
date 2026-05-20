"""Daily smoke: Footer — thông tin công ty, Chính sách (5 links), Hướng dẫn (3 links)."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "FOOTER_SMOKE"


class TestDailyFooter(BaseDailyTest):
    _SUITE_NAME   = "FOOTER_SMOKE"
    _REPORT_TITLE = "Daily Smoke: Footer"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page

    # ── Helper ───────────────────────────────────────────────────────────────

    def _verify_page(self, expected_path: str, label: str, step: str) -> bool:
        """Verify trang load đúng: URL khớp, có content, không 404."""
        url_ok = expected_path in self.page.url
        no_404 = not self.page.locator(
            ":text('404'), :text('Not Found'), :text('Không tìm thấy')"
        ).is_visible(timeout=2_000)
        has_content = self.page.locator(
            "h1, h2, main, article, [class*='content' i]"
        ).first.is_visible(timeout=8_000)
        ok = url_ok and no_404 and has_content
        if not url_ok:
            detail = f"URL sai — expected '{expected_path}', got: {self.page.url}"
        elif not no_404:
            detail = f"Trang hiển thị lỗi 404 — {self.page.url}"
        elif not has_content:
            detail = f"Không có nội dung (h1/main) — {self.page.url}"
        else:
            detail = f"URL: {self.page.url}"
        self._record_check(TC, f"Verify: {label}",
                           "✅ PASS" if ok else "❌ FAIL", detail)
        self._shot(TC, step, f"page_{label[:20].lower().replace(' ', '_')}")
        return ok

    def _go_home_and_scroll_footer(self) -> None:
        self.home.navigate()
        self.page.wait_for_timeout(1_000)
        footer = self.page.locator("footer").first
        footer.scroll_into_view_if_needed()
        self.page.wait_for_timeout(800)

    # ── Test ─────────────────────────────────────────────────────────────────

    def test_footer_smoke(self):
        """Footer: thông tin công ty + click-through Chính sách (5) + Hướng dẫn (3)."""

        # ══ PHẦN 1: FOOTER VISIBLE + THÔNG TIN CÔNG TY ══════════════════════

        self._go_home_and_scroll_footer()
        self._shot(TC, "1", "footer_visible")

        footer = self.page.locator("footer").first
        footer_ok = footer.is_visible(timeout=10_000)
        self._record_check(TC, "Footer element visible",
                           "✅ PASS" if footer_ok else "❌ FAIL",
                           "footer hiển thị" if footer_ok else "không tìm thấy <footer>")
        if not footer_ok:
            pytest.fail("Footer không hiển thị")

        # Thông tin công ty
        COMPANY_CHECKS = [
            ("Tên công ty",   "TRYONIC"),
            ("Mã số thuế",    "0109678435"),
            ("Địa chỉ",       "Cầu Giấy"),
            ("Số điện thoại", "098"),
            ("Email",         "tryonicai"),
        ]
        footer_text = footer.inner_text()
        for label, keyword in COMPANY_CHECKS:
            found = keyword.lower() in footer_text.lower()
            self._record_check(TC, f"Thông tin công ty: {label}",
                               "✅ PASS" if found else "❌ FAIL",
                               f"tìm thấy '{keyword}'" if found
                               else f"không tìm thấy '{keyword}' trong footer")
        self._shot(TC, "2", "footer_company_info")

        # ══ PHẦN 2: CHÍNH SÁCH — 5 LINKS ════════════════════════════════════

        CHINH_SACH_LINKS = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi sản phẩm"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
            ("/pages/dieu-khoan-su-dung",    "Điều khoản sử dụng"),
        ]
        for i, (href, label) in enumerate(CHINH_SACH_LINKS, start=1):
            self._go_home_and_scroll_footer()
            footer = self.page.locator("footer").first
            link = footer.locator(f"a[href*='{href}']").first
            link_ok = link.is_visible(timeout=5_000)
            self._record_check(TC, f"Footer Chính sách: {label} visible",
                               "✅ PASS" if link_ok else "❌ FAIL",
                               f"link hiển thị trong footer" if link_ok
                               else "link không thấy trong footer")
            if i == 1:
                self._shot(TC, "3", "footer_chinh_sach_links")
            if link_ok:
                link.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(1_000)
                self._verify_page(href, label, f"4_{i}")
            else:
                self._record_check(TC, f"Verify: {label}", "⚠️ WARN", "skip — link không thấy")

        # ══ PHẦN 3: HƯỚNG DẪN — 3 LINKS ═════════════════════════════════════

        HUONG_DAN_LINKS = [
            ("/pages/huong-dan-mua-hang", "Hướng dẫn mua hàng"),
            ("/pages/huong-dan-bao-quan", "Hướng dẫn bảo quản"),
            ("/pages/lien-he-cskh",       "Liên hệ CSKH"),
        ]
        for i, (href, label) in enumerate(HUONG_DAN_LINKS, start=1):
            self._go_home_and_scroll_footer()
            footer = self.page.locator("footer").first
            link = footer.locator(f"a[href*='{href}']").first
            link_ok = link.is_visible(timeout=5_000)
            self._record_check(TC, f"Footer Hướng dẫn: {label} visible",
                               "✅ PASS" if link_ok else "❌ FAIL",
                               f"link hiển thị trong footer" if link_ok
                               else "link không thấy trong footer")
            if i == 1:
                self._shot(TC, "5", "footer_huong_dan_links")
            if link_ok:
                link.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(1_000)
                self._verify_page(href, label, f"6_{i}")
            else:
                self._record_check(TC, f"Verify: {label}", "⚠️ WARN", "skip — link không thấy")

        # ══ PHẦN 4: ICON BỘ CÔNG THƯƠNG ═════════════════════════════════════

        self._go_home_and_scroll_footer()
        footer = self.page.locator("footer").first

        # Tìm link/image Bộ Công Thương trong footer
        bct_link = footer.locator(
            "a[href*='online.gov.vn'], a[href*='bocongthuong'], "
            "a:has(img[alt*='Công Thương']), a:has(img[alt*='cong thuong']), "
            "a:has(img[src*='bocongthuong']), a:has(img[src*='gov'])"
        ).first
        bct_ok = bct_link.is_visible(timeout=5_000)
        self._record_check(TC, "Icon Bộ Công Thương visible trong footer",
                           "✅ PASS" if bct_ok else "❌ FAIL",
                           "icon hiển thị" if bct_ok else "không tìm thấy icon BCT")
        self._shot(TC, "7", "footer_bct_icon")

        if bct_ok:
            bct_href = bct_link.get_attribute("href") or ""
            self._record_check(TC, "Icon BCT có href link",
                               "✅ PASS" if bct_href else "❌ FAIL",
                               f"href: {bct_href}" if bct_href else "href rỗng")
            if bct_href:
                # Mở link trong tab mới để tránh rời khỏi trang test
                with self.page.context.expect_page() as new_page_info:
                    bct_link.click()
                try:
                    new_page = new_page_info.value
                    new_page.wait_for_load_state("domcontentloaded", timeout=15_000)
                    new_page.wait_for_timeout(1_500)
                    bct_url = new_page.url
                    bct_loaded = (
                        "online.gov.vn" in bct_url
                        or "bocongthuong" in bct_url
                        or "gov.vn" in bct_url
                        or new_page.locator("h1, main, body").first.is_visible(timeout=5_000)
                    )
                    self._record_check(TC, "Verify: Trang Bộ Công Thương load",
                                       "✅ PASS" if bct_loaded else "⚠️ WARN",
                                       f"URL: {bct_url}")
                    new_page.screenshot(
                        path=f"screenshots/daily/FOOTER_SMOKE/FOOTER_SMOKE/S8_bct_page.png",
                        full_page=False
                    )
                    self._shot(TC, "8", "bct_page_loaded")
                    new_page.close()
                except Exception as e:
                    self._record_check(TC, "Verify: Trang Bộ Công Thương load",
                                       "⚠️ WARN", f"Không mở được tab: {e}")
        else:
            # Fallback: tìm bằng JS nếu locator không khớp
            bct_info = self.page.evaluate("""() => {
                const footer = document.querySelector('footer');
                if (!footer) return null;
                const link = Array.from(footer.querySelectorAll('a[href]')).find(a =>
                    (a.href || '').includes('gov') || (a.href || '').includes('bocongthuong') ||
                    Array.from(a.querySelectorAll('img')).some(img =>
                        (img.alt || '').toLowerCase().includes('cong thuong') ||
                        (img.src || '').includes('gov')
                    )
                );
                return link ? {href: link.href, text: link.innerText.trim()} : null;
            }""")
            if bct_info:
                self._record_check(TC, "Icon BCT (fallback JS)",
                                   "⚠️ WARN",
                                   f"href={bct_info.get('href')} — locator không match nhưng link tồn tại")

        # ══ KẾT QUẢ ══════════════════════════════════════════════════════════

        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Footer có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
