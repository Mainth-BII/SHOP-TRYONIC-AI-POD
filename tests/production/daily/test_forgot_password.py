"""Daily smoke: Quên mật khẩu — mở form → nhập email → verify gửi thành công."""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "FORGOT_PWD_SMOKE"


class TestDailyForgotPassword(BaseDailyTest):
    _SUITE_NAME   = "FORGOT_PWD_SMOKE"
    _REPORT_TITLE = "Daily Smoke: Quên mật khẩu"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page

    def test_forgot_password_smoke(self):
        """Kiểm tra luồng Quên mật khẩu:
        1. Mở login modal → click Quên mật khẩu → verify form thay đổi
        2. Nhập email đăng ký → submit
        3. Verify thông báo xác nhận gửi email
        4. Verify link quay lại Đăng nhập
        """
        email = self.env.login_email
        if not email:
            pytest.skip("Thiếu DAILY_TEST_EMAIL — không có email để test forgot password")

        from pages.auth_modal_page import AuthModalPage
        auth = AuthModalPage(self.page, self.env.fe_url)

        # ── 1. Mở trang home ──────────────────────────────────────────────────
        self.home.navigate()
        self._shot(TC, "1", "home_loaded")

        # Đảm bảo chưa login (test phải ở trạng thái logged-out)
        if self.home.header.is_logged_in(timeout=2_000):
            try:
                self.home.header.logout()
                self.page.wait_for_timeout(1_000)
            except Exception:
                pass

        # ── 2. Mở login modal ─────────────────────────────────────────────────
        try:
            self.home.header.click_login()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self._record_check(TC, "Mở login modal", "❌ FAIL", str(e))
            pytest.fail(f"Không click được Login button: {e}")

        modal_open = auth.is_open(timeout=5_000)
        self._record_check(
            TC, "Mở login modal",
            "✅ PASS" if modal_open else "❌ FAIL",
            "Modal đăng nhập visible" if modal_open else "Modal không xuất hiện",
        )
        self._shot(TC, "2", "login_modal_opened")
        if not modal_open:
            pytest.fail("Login modal không mở được")

        # ── 3. Click "Quên mật khẩu" ─────────────────────────────────────────
        forgot_link_ok = False
        try:
            forgot_link_ok = auth.forgot_password_link.is_visible(timeout=3_000)
        except Exception:
            pass

        self._record_check(
            TC, "Link 'Quên mật khẩu' hiển thị trong modal",
            "✅ PASS" if forgot_link_ok else "❌ FAIL",
            "Link visible" if forgot_link_ok else "Không thấy link Quên mật khẩu",
        )
        if not forgot_link_ok:
            pytest.fail("Không tìm thấy link 'Quên mật khẩu' trong modal")

        auth.click_forgot_password()
        self._shot(TC, "3", "forgot_password_form")

        # ── 4. Verify form quên mật khẩu hiển thị ────────────────────────────
        # Form phải: có email input, KHÔNG có password input, có tiêu đề phù hợp
        form_email_visible = False
        form_password_hidden = True
        try:
            form_email_visible = auth.reset_email_input.is_visible(timeout=4_000)
        except Exception:
            pass
        try:
            # Password input không được visible trên form quên mật khẩu
            form_password_hidden = not auth.password_input.is_visible(timeout=1_500)
        except Exception:
            form_password_hidden = True  # Không thấy = đúng

        form_ok = form_email_visible and form_password_hidden
        self._record_check(
            TC, "Form Quên mật khẩu hiển thị (có email input, không có password)",
            "✅ PASS" if form_ok else "❌ FAIL",
            f"email_input={form_email_visible}, password_hidden={form_password_hidden}",
        )
        if not form_ok:
            pytest.fail("Form quên mật khẩu không hiển thị đúng")

        # ── 5. Nhập email và submit ───────────────────────────────────────────
        try:
            auth.reset_email_input.fill(email)
            self.page.wait_for_timeout(300)
        except Exception as e:
            self._record_check(TC, "Nhập email vào form", "❌ FAIL", str(e))
            pytest.fail(f"Không nhập được email: {e}")

        self._shot(TC, "4", "email_filled")

        submit_ok = False
        try:
            submit_ok = auth.reset_submit.is_visible(timeout=3_000)
        except Exception:
            pass
        self._record_check(
            TC, "Nút Gửi hiển thị và có thể click",
            "✅ PASS" if submit_ok else "❌ FAIL",
            "Nút Gửi visible" if submit_ok else "Không thấy nút Gửi",
        )
        if not submit_ok:
            pytest.fail("Không tìm thấy nút Gửi trên form quên mật khẩu")

        auth.reset_submit.click()
        self.page.wait_for_timeout(4_000)   # Chờ API call + UI update
        self._shot(TC, "5", "after_submit")

        # ── 6. Verify thông báo xác nhận ─────────────────────────────────────
        success_visible = False
        try:
            success_visible = auth.reset_success_message.is_visible(timeout=6_000)
        except Exception:
            pass

        # Fallback: scan body text cho các từ khoá thành công
        if not success_visible:
            try:
                body = self.page.evaluate("() => document.body.innerText.toLowerCase()")
                SUCCESS_KEYWORDS = [
                    "đã gửi", "kiểm tra email", "hộp thư", "gửi thành công",
                    "check your email", "successfully", "liên kết", "inbox",
                ]
                success_visible = any(kw in body for kw in SUCCESS_KEYWORDS)
                if success_visible:
                    print("  [INFO] Tìm thấy success keyword trong body text")
            except Exception:
                pass

        self._record_check(
            TC, "Thông báo xác nhận gửi email đặt lại mật khẩu",
            "✅ PASS" if success_visible else "❌ FAIL",
            "Hiển thị thông báo xác nhận" if success_visible
            else f"Không thấy thông báo xác nhận sau khi submit (email={email})",
        )

        # ── 7. Verify có thể quay lại trang Đăng nhập ────────────────────────
        back_to_login_ok = False
        try:
            back_btn = self.page.locator(
                ":text('Đăng nhập'), :text('Quay lại'), :text('Back'), "
                "a:has-text('đăng nhập'), button:has-text('Đăng nhập')"
            ).first
            back_to_login_ok = back_btn.is_visible(timeout=3_000)
        except Exception:
            pass

        self._record_check(
            TC, "Có link/button quay lại trang Đăng nhập",
            "✅ PASS" if back_to_login_ok else "⚠️ WARN",
            "Link quay lại visible" if back_to_login_ok
            else "Không thấy link quay lại (có thể modal đã đóng)",
        )
        self._shot(TC, "6", "final_state")

        # ══ Kết quả ══════════════════════════════════════════════════════════
        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Forgot password có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
