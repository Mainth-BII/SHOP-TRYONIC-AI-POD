"""Daily smoke: Authentication — Login thành công, Login sai, Logout."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "AUTH_SMOKE"


class TestDailyAuthLogin(BaseDailyTest):
    _SUITE_NAME   = "AUTH_SMOKE"
    _REPORT_TITLE = "Daily Smoke: Authentication (Login / Logout)"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _open_login_modal(self) -> bool:
        """Mở modal đăng nhập. Trả về True nếu thành công."""
        try:
            if self.home.header.is_logged_in(timeout=2_000):
                return False  # Đang login rồi, không cần mở
            self.home.header.click_login()
            self.page.wait_for_timeout(800)
            return True
        except Exception as e:
            print(f"  [WARN] Không mở được login modal: {e}")
            return False

    # ── Test ─────────────────────────────────────────────────────────────────

    def test_auth_smoke(self):
        """Login đúng → verify logged-in → Logout → verify logged-out → Login sai → verify lỗi."""
        email = self.env.login_email
        pwd   = self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")

        from pages.auth_modal_page import AuthModalPage
        auth = AuthModalPage(self.page, self.env.fe_url)

        # ── 1. Mở trang home ─────────────────────────────────────────────────
        self.home.navigate()
        self._shot(TC, "1", "home_loaded")

        # Logout nếu đang login sẵn (để test clean)
        if self.home.header.is_logged_in(timeout=2_000):
            print("  [INFO] Đang login sẵn → logout trước để test clean")
            try:
                self.home.header.logout()
                self.page.wait_for_timeout(1_000)
            except Exception:
                pass

        # ── 2. Login với credentials ĐÚNG ────────────────────────────────────
        self._open_login_modal()
        self._shot(TC, "2", "login_modal_opened")

        auth.fill_login(email, pwd)
        self._shot(TC, "2b", "login_filled")
        auth.submit_login()
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "3", "after_login_submit")

        logged_in = self.home.header.is_logged_in()
        self._record_check(
            TC, "Login đúng credentials → đăng nhập thành công",
            "✅ PASS" if logged_in else "❌ FAIL",
            "Header hiển thị profile/avatar" if logged_in
            else f"Vẫn thấy Login button — có thể API /auth/login lỗi (email={email})",
        )
        if not logged_in:
            pytest.fail("Đăng nhập thất bại — kiểm tra credentials hoặc API /auth/login")

        # ── 3. Verify profile button trên header ─────────────────────────────
        profile_ok = False
        try:
            profile_ok = self.home.header.profile_button.is_visible(timeout=3_000)
        except Exception:
            pass
        self._record_check(
            TC, "Header hiển thị profile button sau khi login",
            "✅ PASS" if profile_ok else "⚠️ WARN",
            "Profile button visible" if profile_ok else "Không thấy profile button",
        )
        self._shot(TC, "4", "header_after_login")

        # ── 4. Logout ─────────────────────────────────────────────────────────
        try:
            self.home.header.logout()
        except Exception as e:
            print(f"  [WARN] logout() error: {e}")
            # Thử cách khác: click trực tiếp vào logout button trong menu
            try:
                self.home.header.open_profile_menu()
                self.page.wait_for_timeout(500)
                self.page.locator(
                    "button:has-text('Đăng xuất'), a:has-text('Đăng xuất'), "
                    "[role='menuitem']:has-text('Đăng xuất')"
                ).first.click()
                self.page.wait_for_timeout(2_000)
            except Exception as e2:
                print(f"  [WARN] fallback logout error: {e2}")

        self._shot(TC, "5", "after_logout")

        still_logged_in = self.home.header.is_logged_in(timeout=2_000)
        logout_ok = not still_logged_in
        self._record_check(
            TC, "Logout → trở về trạng thái chưa đăng nhập",
            "✅ PASS" if logout_ok else "❌ FAIL",
            "Login button xuất hiện lại" if logout_ok
            else "Vẫn còn trạng thái logged-in sau logout",
        )

        # ── 5. Login với PASSWORD SAI → verify thông báo lỗi ─────────────────
        if not logout_ok:
            self._record_check(
                TC, "Login sai password → hiện thông báo lỗi",
                "⚠️ WARN", "Bỏ qua vì bước logout trước đó bị lỗi",
            )
        else:
            self._open_login_modal()
            auth.fill_login(email, "WrongPassword@999!")
            auth.submit_login()
            self._shot(TC, "6", "login_wrong_password")

            error_visible = False
            try:
                error_visible = auth.error_message.is_visible(timeout=6_000)
            except Exception:
                pass
            self._record_check(
                TC, "Login sai password → hiện thông báo lỗi",
                "✅ PASS" if error_visible else "❌ FAIL",
                "Error message visible" if error_visible
                else "Không thấy thông báo lỗi sau khi nhập sai password",
            )

            # Đóng modal sau khi test xong
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(500)
            except Exception:
                pass

        # ══ Kết quả ══════════════════════════════════════════════════════════
        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Auth có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
