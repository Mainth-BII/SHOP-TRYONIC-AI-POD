"""Daily smoke: Profile menu — Thiết kế của tôi, Đơn hàng của tôi, Hồ sơ cá nhân, Đăng xuất."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "PROFILE_SMOKE"


class TestDailyProfile(BaseDailyTest):
    _SUITE_NAME   = "PROFILE_SMOKE"
    _REPORT_TITLE = "Daily Smoke: Profile Menu"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page

    # ── Helper ───────────────────────────────────────────────────────────────

    def _login(self) -> None:
        """Login và verify thành công. Skip nếu thiếu credentials, fail nếu API lỗi."""
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        from pages.auth_modal_page import AuthModalPage
        for attempt in range(1, 3):          # thử tối đa 2 lần (API /auth/login đôi khi 500)
            self.home.navigate()
            self.home.header.click_login()
            self.page.wait_for_timeout(1_000)
            AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
            self.page.wait_for_timeout(3_000)
            if self.home.header.is_logged_in():
                print(f"  [INFO] Đăng nhập thành công (lần {attempt})")
                return
            print(f"  [WARN] Đăng nhập thất bại lần {attempt} — thử lại..." if attempt < 2
                  else f"  [WARN] Đăng nhập thất bại cả 2 lần")
            self.page.wait_for_timeout(2_000)
        self._record_check(TC, "Login thành công", "❌ FAIL",
                           "API /auth/login có thể đang lỗi (HTTP 500)")
        pytest.fail("Đăng nhập thất bại sau 2 lần thử — kiểm tra API /auth/login")

    def _open_profile_dropdown(self) -> bool:
        """Click profile button → mở dropdown menu. Trả về True nếu thành công."""
        if not self.home.header.is_logged_in():
            print("  [WARN] Chưa đăng nhập — profile button không có trong header")
            return False
        try:
            self.home.header.open_profile_menu()
            print("  [INFO] profile dropdown mở thành công")
            return True
        except Exception as e:
            print(f"  [WARN] Không mở được profile dropdown: {e}")
            return False

    def _verify_page(self, expected_path: str, label: str, step: str) -> bool:
        """Verify trang load đúng: URL khớp, có content, không 404."""
        url_ok = expected_path in self.page.url
        no_404 = not self.page.locator(
            ":text('404'), :text('Not Found'), :text('Không tìm thấy')"
        ).is_visible(timeout=2_000)
        has_content = self.page.locator(
            "h1, h2, main, [class*='content' i], [class*='container' i]"
        ).first.is_visible(timeout=8_000)
        ok = url_ok and no_404 and has_content
        if not url_ok:
            detail = f"URL sai — expected '{expected_path}', got: {self.page.url}"
        elif not no_404:
            detail = f"Trang hiển thị lỗi 404 — {self.page.url}"
        elif not has_content:
            detail = f"Không có nội dung — {self.page.url}"
        else:
            detail = f"URL: {self.page.url}"
        self._record_check(TC, f"Verify: {label}",
                           "✅ PASS" if ok else "❌ FAIL", detail)
        self._shot(TC, step, f"page_{label[:20].lower().replace(' ', '_')}")
        return ok

    # ── Test ─────────────────────────────────────────────────────────────────

    def test_profile_smoke(self):
        """Login → kiểm tra profile menu: Thiết kế, Đơn hàng, Hồ sơ, Đăng xuất."""

        # ── 1. Login ──────────────────────────────────────────────────────────
        self._login()   # raises pytest.fail nếu API lỗi; raises pytest.skip nếu thiếu creds
        self._record_check(TC, "Login thành công", "✅ PASS", f"URL: {self.page.url}")
        self._shot(TC, "1", "home_after_login")

        # ── 2. Profile dropdown hiển thị ──────────────────────────────────────
        dropdown_opened = self._open_profile_dropdown()
        self._record_check(TC, "Mở profile dropdown",
                           "✅ PASS" if dropdown_opened else "❌ FAIL",
                           "dropdown mở" if dropdown_opened else "không click được profile btn")
        if not dropdown_opened:
            pytest.fail("Không mở được profile dropdown")
        self._shot(TC, "2", "profile_dropdown_open")

        # Verify các menu items visible trong dropdown
        MENU_ITEMS = [
            ("Thiết kế của tôi", "a[href*='/my-designs']"),
            ("Đơn hàng của tôi",  "a[href*='/my-orders']"),
            ("Hồ sơ cá nhân",    "a[href*='/profile']"),
            ("Đăng xuất",        "button:has-text('Đăng xuất'), a:has-text('Đăng xuất')"),
        ]
        for label, selector in MENU_ITEMS:
            el = self.page.locator(selector).first
            ok = el.is_visible(timeout=3_000)
            self._record_check(TC, f"Menu item visible: {label}",
                               "✅ PASS" if ok else "❌ FAIL",
                               "visible" if ok else "không thấy trong dropdown")

        # ══ LUỒNG 1: THIẾT KẾ CỦA TÔI ═══════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._open_profile_dropdown()
        self.page.wait_for_timeout(500)   # Chờ dropdown animation
        design_link = self.page.locator("a[href*='/my-designs']").first
        design_ok = design_link.is_visible(timeout=5_000)
        self._record_check(TC, "Click Thiết kế của tôi",
                           "✅ PASS" if design_ok else "❌ FAIL",
                           "link visible" if design_ok else "link không thấy")
        if design_ok:
            design_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=20_000)
            self.page.wait_for_timeout(2_000)
            self._verify_page("/my-designs", "Thiết kế của tôi", "3")
        else:
            self._record_check(TC, "Verify: Thiết kế của tôi", "⚠️ WARN", "skip")
            self._shot(TC, "3", "my_designs_skip")

        # ══ LUỒNG 2: ĐƠN HÀNG CỦA TÔI ═══════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._open_profile_dropdown()
        self.page.wait_for_timeout(500)
        order_link = self.page.locator("a[href*='/my-orders']").first
        order_ok = order_link.is_visible(timeout=5_000)
        self._record_check(TC, "Click Đơn hàng của tôi",
                           "✅ PASS" if order_ok else "❌ FAIL",
                           "link visible" if order_ok else "link không thấy")
        if order_ok:
            order_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=20_000)
            self.page.wait_for_timeout(2_000)
            self._verify_page("/my-orders", "Đơn hàng của tôi", "4")
        else:
            self._record_check(TC, "Verify: Đơn hàng của tôi", "⚠️ WARN", "skip")
            self._shot(TC, "4", "my_orders_skip")

        # ══ LUỒNG 3: HỒ SƠ CÁ NHÂN ═══════════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._open_profile_dropdown()
        self.page.wait_for_timeout(500)
        profile_link = self.page.locator("a[href*='/profile']").first
        profile_ok = profile_link.is_visible(timeout=5_000)
        self._record_check(TC, "Click Hồ sơ cá nhân",
                           "✅ PASS" if profile_ok else "❌ FAIL",
                           "link visible" if profile_ok else "link không thấy")
        if profile_ok:
            profile_link.click()
            self.page.wait_for_load_state("domcontentloaded", timeout=20_000)
            self.page.wait_for_timeout(2_000)
            self._verify_page("/profile", "Hồ sơ cá nhân", "5")

            # Verify có các field thông tin cá nhân
            profile_fields = self.page.evaluate("""() => {
                const fields = ['input[type=\"text\"]','input[type=\"email\"]',
                    'input[placeholder]','[class*=\"profile\" i]','[class*=\"account\" i]'];
                return fields.some(sel => document.querySelector(sel) !== null);
            }""")
            self._record_check(TC, "Hồ sơ cá nhân có form/fields",
                               "✅ PASS" if profile_fields else "⚠️ WARN",
                               "có input fields" if profile_fields else "không thấy fields")
        else:
            self._record_check(TC, "Verify: Hồ sơ cá nhân", "⚠️ WARN", "skip")
            self._shot(TC, "5", "profile_skip")

        # ══ LUỒNG 4: ĐĂNG XUẤT ═══════════════════════════════════════════════

        self.home.navigate()
        self.page.wait_for_timeout(1_500)
        self._open_profile_dropdown()
        self.page.wait_for_timeout(500)
        self._shot(TC, "6", "before_logout")

        logout_btn = self.page.locator(
            "button:has-text('Đăng xuất'), a:has-text('Đăng xuất')"
        ).first
        logout_visible = logout_btn.is_visible(timeout=5_000)
        self._record_check(TC, "Nút Đăng xuất visible",
                           "✅ PASS" if logout_visible else "❌ FAIL",
                           "visible trong dropdown" if logout_visible else "không thấy")
        if logout_visible:
            logout_btn.click()
            self.page.wait_for_timeout(2_500)
            self._shot(TC, "7", "after_logout")

            # Verify đã logout: login button xuất hiện, profile button biến mất
            login_visible = self.page.locator(
                "header button:has-text('Đăng nhập'), header :text('Đăng nhập')"
            ).first.is_visible(timeout=8_000)
            self._record_check(TC, "Đăng xuất thành công — nút Đăng nhập xuất hiện",
                               "✅ PASS" if login_visible else "❌ FAIL",
                               "Đăng nhập button visible" if login_visible
                               else f"Đăng nhập không xuất hiện — URL: {self.page.url}")
        else:
            self._record_check(TC, "Đăng xuất", "⚠️ WARN", "skip — nút không thấy")
            self._shot(TC, "7", "logout_skip")

        # ══ KẾT QUẢ ══════════════════════════════════════════════════════════

        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Profile có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
