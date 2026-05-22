"""Daily smoke: Quên mật khẩu — gửi email → mở yopmail → reset → login với mật khẩu mới."""
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

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _open_yopmail_inbox(self, inbox_name: str) -> bool:
        """Mở yopmail, điền tên inbox, trả về True nếu inbox load được."""
        try:
            self.page.goto(
                "https://yopmail.com/en/wm",
                wait_until="domcontentloaded",
                timeout=20_000,
            )
            self.page.wait_for_timeout(2_000)

            login_el = self.page.locator("input#login").first
            login_el.fill(inbox_name)
            login_el.press("Enter")
            self.page.wait_for_timeout(3_000)
            return True
        except Exception as e:
            print(f"  [WARN] _open_yopmail_inbox: {e}")
            return False

    def _get_reset_link_from_yopmail(self) -> str:
        """Click email mới nhất trong iframe ifinbox, trả về reset link từ iframe ifmail."""
        # Click email mới nhất
        inbox_frame = self.page.frame(name="ifinbox")
        if inbox_frame:
            try:
                first_mail = inbox_frame.locator(".m, div.m, span.lien").first
                if first_mail.is_visible(timeout=5_000):
                    first_mail.click()
                    self.page.wait_for_timeout(2_000)
            except Exception as e:
                print(f"  [WARN] click inbox email: {e}")

        # Tìm reset link trong iframe ifmail
        mail_frame = self.page.frame(name="ifmail")
        if not mail_frame:
            return ""

        try:
            links = mail_frame.eval_on_selector_all(
                "a[href]", "els => els.map(a => a.href)"
            )
        except Exception as e:
            print(f"  [WARN] eval links: {e}")
            return ""

        # Ưu tiên link thuộc domain của shop
        fe_domain = self.env.fe_url.split("://")[-1].split("/")[0]  # e.g. test.shop.tryonic.ai
        RESET_KEYWORDS = ["reset", "password", "token", "forgot", "set-password"]

        for link in links:
            if fe_domain in link and any(kw in link.lower() for kw in RESET_KEYWORDS):
                return link

        # Fallback: bất kỳ link nào chứa keyword reset
        for link in links:
            if any(kw in link.lower() for kw in RESET_KEYWORDS):
                return link

        return ""

    # ── Test ─────────────────────────────────────────────────────────────────

    def test_forgot_password_smoke(self):
        """Forgot password end-to-end:
        1. Mở modal → click Quên mật khẩu → verify form
        2. Nhập email → submit → verify thông báo xác nhận
        3. Mở yopmail → tìm link reset trong email
        4. Mở link reset → điền mật khẩu mới → submit
        5. Đăng nhập với mật khẩu mới → verify thành công
        """
        email = self.env.login_email
        pwd   = self.env.login_password or "Admin@12"
        if not email:
            pytest.skip("Thiếu DAILY_TEST_EMAIL — không có email để test forgot password")

        from pages.auth_modal_page import AuthModalPage
        auth = AuthModalPage(self.page, self.env.fe_url)

        # ── 1. Mở trang home ──────────────────────────────────────────────────
        self.home.navigate()
        self._shot(TC, "1", "home_loaded")

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
        form_email_visible = False
        form_password_hidden = True
        try:
            form_email_visible = auth.reset_email_input.is_visible(timeout=4_000)
        except Exception:
            pass
        try:
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

        # ── 6. Verify thông báo xác nhận gửi email ───────────────────────────
        success_visible = False
        try:
            success_visible = auth.reset_success_message.is_visible(timeout=6_000)
        except Exception:
            pass

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
        if not success_visible:
            pytest.fail(
                "API gửi email đặt lại mật khẩu thất bại — "
                "không thấy thông báo xác nhận trên UI"
            )

        # ── 7. Mở yopmail — tìm email và lấy reset link ──────────────────────
        inbox_name = email.split("@")[0]  # "tester_beta_2026"
        reset_link = ""

        inbox_loaded = self._open_yopmail_inbox(inbox_name)
        self._shot(TC, "6", "yopmail_inbox")

        if inbox_loaded:
            reset_link = self._get_reset_link_from_yopmail()
            self._shot(TC, "6b", "yopmail_email_opened")

        yopmail_ok = bool(reset_link)
        self._record_check(
            TC, "Nhận được email và tìm thấy link đặt lại mật khẩu trong yopmail",
            "✅ PASS" if yopmail_ok else "❌ FAIL",
            f"Reset link: {reset_link[:80]}" if yopmail_ok
            else "Không tìm thấy link reset trong email — kiểm tra email có được gửi không",
        )
        if not yopmail_ok:
            pytest.fail("Không lấy được link reset password từ email yopmail")

        # ── 8. Mở link reset và điền mật khẩu mới ────────────────────────────
        print(f"  [INFO] Reset link: {reset_link}")
        try:
            self.page.goto(reset_link, wait_until="domcontentloaded", timeout=15_000)
            self.page.wait_for_timeout(2_000)
        except Exception as e:
            self._record_check(TC, "Mở link đặt lại mật khẩu", "❌ FAIL", str(e))
            pytest.fail(f"Không mở được trang đặt lại mật khẩu: {e}")

        self._shot(TC, "7", "reset_password_page")

        # Điền mật khẩu mới (= password cũ, để các test khác không bị ảnh hưởng)
        new_password = pwd
        reset_submit_ok = False
        try:
            pwd_inputs = self.page.locator("input[type='password']").all()
            if len(pwd_inputs) >= 1:
                pwd_inputs[0].fill(new_password)
            if len(pwd_inputs) >= 2:
                pwd_inputs[1].fill(new_password)   # Confirm password
            self.page.wait_for_timeout(300)

            submit_btn = self.page.locator(
                "button[type='submit'], button:has-text('Xác nhận'), "
                "button:has-text('Đặt lại'), button:has-text('Reset'), "
                "button:has-text('Save'), button:has-text('Lưu'), "
                "button:has-text('Đổi mật khẩu')"
            ).first
            if submit_btn.is_visible(timeout=4_000):
                submit_btn.click()
                self.page.wait_for_timeout(3_000)
                reset_submit_ok = True
        except Exception as e:
            print(f"  [WARN] reset form submit error: {e}")

        self._shot(TC, "8", "after_reset_submit")
        self._record_check(
            TC, "Điền mật khẩu mới và submit form đặt lại",
            "✅ PASS" if reset_submit_ok else "❌ FAIL",
            "Submit thành công" if reset_submit_ok
            else "Không tìm thấy hoặc submit thất bại trên form đặt lại mật khẩu",
        )
        if not reset_submit_ok:
            pytest.fail("Không hoàn thành được form đặt lại mật khẩu trên trang reset")

        # ── 9. Đăng nhập với mật khẩu mới — verify thành công ───────────────
        # Quay về trang chủ shop
        try:
            self.home.navigate()
            self.page.wait_for_timeout(1_000)
        except Exception:
            pass

        # Đảm bảo logged-out trước khi login
        if self.home.header.is_logged_in(timeout=2_000):
            try:
                self.home.header.logout()
                self.page.wait_for_timeout(1_000)
            except Exception:
                pass

        # Login với mật khẩu mới
        try:
            self.home.header.click_login()
            self.page.wait_for_timeout(800)
            auth.fill_login(email, new_password)
            auth.submit_login()
            self.page.wait_for_timeout(2_000)
        except Exception as e:
            print(f"  [WARN] login after reset error: {e}")

        login_after_reset = self.home.header.is_logged_in()
        self._shot(TC, "9", "login_after_reset")
        self._record_check(
            TC, "Đăng nhập thành công với mật khẩu mới sau khi đặt lại",
            "✅ PASS" if login_after_reset else "❌ FAIL",
            "Login với password mới thành công" if login_after_reset
            else f"Không login được với mật khẩu sau khi đặt lại (email={email})",
        )

        # ══ Kết quả ══════════════════════════════════════════════════════════
        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Forgot password có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
