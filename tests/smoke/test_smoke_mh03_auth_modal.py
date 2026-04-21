"""
Smoke — MH03: Auth Modal (Đăng nhập / Đăng ký / Quên mật khẩu)
TC_DAILY_003 · TC_DAILY_014 · TC_DAILY_015 · TC_DAILY_016 · TC_DAILY_020
TC_DAILY_037 · TC_DAILY_044

Chay: pytest tests/smoke/test_smoke_mh03_auth_modal.py -v
Chi login: pytest tests/smoke/test_smoke_mh03_auth_modal.py -k "037 or 044" -v
"""
import sys
import os
import pytest
from playwright.sync_api import Page

from pages import HomePage, AuthModalPage, StudioPage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Credentials từ .env / CI env — không hardcode
_TEST_EMAIL    = os.environ.get("TEST_EMAIL",    "")
_TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "")


class TestSmokeMH03AuthModal(BaseSmokeTest):
    """MH03 — Auth Modal: Login modal, Register, Forgot password, Social login."""

    _MH_DIR = "MH03_auth_modal"
    _TC_IDS = [
        "TC_DAILY_003", "TC_DAILY_014", "TC_DAILY_015", "TC_DAILY_016",
        "TC_DAILY_020", "TC_DAILY_037", "TC_DAILY_044",
    ]

    # ── TC_DAILY_003 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_003_login_modal_opens(self, page: Page, base_url: str):
        """TC_DAILY_003 — Click nút Đăng nhập trên Header → Modal xuất hiện đầy đủ."""
        home = HomePage(page, base_url)
        auth = AuthModalPage(page, base_url)

        home.navigate()
        self.shot(home, "TC_DAILY_003", "1", "home_before_click")

        assert home.header.login_button.is_visible(timeout=10_000), \
            "TC_DAILY_003 FAIL: Không tìm thấy nút 'Đăng nhập' trên header"
        home.header.click_login()
        self.shot(home, "TC_DAILY_003", "2", "login_modal_opened")

        assert auth.is_open(timeout=8000), \
            "TC_DAILY_003 FAIL: Modal Đăng nhập không xuất hiện"

        title = auth.modal.locator(
            ":text('Chào mừng trở lại'), :text('Chao mung tro lai')"
        ).first
        assert title.is_visible(timeout=5000), \
            "TC_DAILY_003 FAIL: Tiêu đề modal không hiển thị"

        assert auth.email_input.is_visible(timeout=5000), \
            "TC_DAILY_003 FAIL: Email input không hiển thị"
        assert auth.password_input.is_visible(timeout=5000), \
            "TC_DAILY_003 FAIL: Password input không hiển thị"
        assert auth.submit_button.is_visible(timeout=5000), \
            "TC_DAILY_003 FAIL: Nút Submit không hiển thị"
        assert auth.google_button.is_visible(timeout=5000), \
            "TC_DAILY_003 FAIL: Nút Google không hiển thị"
        if not auth.facebook_button.is_visible(timeout=3000):
            print("  [WARN] TC_DAILY_003: Nút Facebook không hiển thị — có thể site đã bỏ")
        else:
            print("  [PASS] Facebook button có mặt")

        self.shot(home, "TC_DAILY_003", "3", "login_modal_full")
        print("  [PASS] Modal Đăng nhập hiển thị đầy đủ: Email, Password, Submit, Google")

    # ── TC_DAILY_014 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_014_register_form_opens(self, page: Page, base_url: str):
        """TC_DAILY_014 — Login modal → link 'Đăng ký' → form đăng ký hiển thị."""
        home = HomePage(page, base_url)
        auth = AuthModalPage(page, base_url)

        home.navigate()
        assert home.header.login_button.is_visible(timeout=10_000), \
            "TC_DAILY_014 FAIL: Không tìm thấy nút 'Đăng nhập' trên header"
        home.header.click_login()
        self.shot(home, "TC_DAILY_014", "1", "login_modal_opened")

        register_link = auth.modal.locator(
            "a:has-text('Đăng ký'), button:has-text('Đăng ký'), "
            "span:has-text('Đăng ký'), :text('Đăng ký')"
        ).first
        assert register_link.is_visible(timeout=8000), \
            "TC_DAILY_014 FAIL: Không tìm thấy link/nút 'Đăng ký' trong modal"

        register_link.click(force=True)
        page.wait_for_timeout(2000)
        self.shot(home, "TC_DAILY_014", "2", "register_form_opened")

        reg_form_visible = (
            page.locator("input[type='email'], input[placeholder*='email']").first.is_visible(timeout=5000)
            and page.locator("input[type='password']").first.is_visible(timeout=3000)
        )
        assert reg_form_visible, \
            "TC_DAILY_014 FAIL: Form Đăng ký không hiển thị đầy đủ"

        self.shot(home, "TC_DAILY_014", "3", "register_form_full")
        print("  [PASS] Form Đăng ký hiển thị đầy đủ")

    # ── TC_DAILY_015 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_015_forgot_password(self, page: Page, base_url: str):
        """TC_DAILY_015 — Login modal → 'Quên mật khẩu' → form reset password hiển thị."""
        home = HomePage(page, base_url)
        auth = AuthModalPage(page, base_url)

        home.navigate()
        assert home.header.login_button.is_visible(timeout=10_000), \
            "TC_DAILY_015 FAIL: Không tìm thấy nút 'Đăng nhập' trên header"
        home.header.click_login()
        self.shot(home, "TC_DAILY_015", "1", "login_modal_opened")

        assert auth.is_open(timeout=8000), "TC_DAILY_015 FAIL: Login modal không mở"

        forgot_link = auth.modal.locator(
            "a:has-text('Quên mật khẩu'), button:has-text('Quên mật khẩu'), "
            ":text('Quên mật khẩu'), a:has-text('Forgot'), :text('Forgot password')"
        ).first
        assert forgot_link.is_visible(timeout=8000), \
            "TC_DAILY_015 FAIL: Không tìm thấy link 'Quên mật khẩu'"

        forgot_link.click(force=True)
        page.wait_for_timeout(2000)
        self.shot(home, "TC_DAILY_015", "2", "forgot_password_form")

        reset_form_ok = (
            page.locator(
                "input[type='email'], input[placeholder*='email'], input[placeholder*='Email']"
            ).first.is_visible(timeout=5000)
            or page.locator(
                ":text('Đặt lại mật khẩu'), :text('Reset password'), :text('Lấy lại mật khẩu')"
            ).first.is_visible(timeout=3000)
        )
        assert reset_form_ok, \
            "TC_DAILY_015 FAIL: Form reset password không hiển thị"

        self.shot(home, "TC_DAILY_015", "3", "forgot_password_full")
        print("  [PASS] Form Quên mật khẩu hiển thị thành công")

    # ── TC_DAILY_016 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_016_social_login_popups(self, page: Page, base_url: str):
        """TC_DAILY_016 — Login modal: Google và Facebook buttons mở popup đúng domain."""
        home = HomePage(page, base_url)
        auth = AuthModalPage(page, base_url)

        # -- Google popup
        home.navigate()
        home.header.click_login()
        assert auth.is_open(timeout=8000), "TC_DAILY_016 FAIL: Login modal không mở"
        self.shot(home, "TC_DAILY_016", "1", "login_modal_for_social")

        assert auth.google_button.is_visible(timeout=5000), \
            "TC_DAILY_016 FAIL: Nút Google không hiển thị"

        with page.expect_popup(timeout=15000) as google_popup_info:
            auth.click_google()
        google_popup = google_popup_info.value
        google_popup.wait_for_load_state("domcontentloaded", timeout=15000)
        google_url = google_popup.url
        self.shot(google_popup, "TC_DAILY_016", "2", "google_popup")
        google_popup.close()

        assert "google" in google_url.lower() or "accounts" in google_url.lower(), \
            f"TC_DAILY_016 FAIL: Popup Google không phải domain Google. URL: {google_url}"
        print(f"  [PASS] Google popup OK — URL: {google_url[:60]}")

        # -- Facebook popup
        home.navigate()
        home.header.click_login()
        assert auth.is_open(timeout=8000), "TC_DAILY_016 FAIL: Login modal không mở lần 2"

        if not auth.facebook_button.is_visible(timeout=3000):
            print("  [WARN] TC_DAILY_016: Nút Facebook không hiển thị — có thể site đã bỏ Facebook login")
            print("  [PASS] TC_DAILY_016: Google popup OK — Facebook bị skip")
            return

        with page.expect_popup(timeout=15000) as fb_popup_info:
            auth.click_facebook()
        fb_popup = fb_popup_info.value
        fb_popup.wait_for_load_state("domcontentloaded", timeout=15000)
        fb_url = fb_popup.url
        self.shot(fb_popup, "TC_DAILY_016", "3", "facebook_popup")
        fb_popup.close()

        assert "facebook" in fb_url.lower(), \
            f"TC_DAILY_016 FAIL: Popup Facebook không phải domain Facebook. URL: {fb_url}"
        print(f"  [PASS] Facebook popup OK — URL: {fb_url[:60]}")

    # ── TC_DAILY_020 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_020_change_password_page_accessible(self, page: Page, base_url: str):
        """TC_DAILY_020 — Đổi mật khẩu: trang hoặc redirect hoạt động bình thường (không 404/500)."""
        candidate_urls = [
            f"{base_url}/profile",
            f"{base_url}/account",
            f"{base_url}/account/change-password",
            f"{base_url}/change-password",
        ]

        landed_url = None
        for url in candidate_urls:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                status = resp.status if resp else 0
                if status not in (404, 500):
                    landed_url = url
                    break
            except Exception:
                continue

        assert landed_url, \
            "TC_DAILY_020 FAIL: Tất cả URL đổi mật khẩu đều 404/500 hoặc không truy cập được"
        self.shot(page, "TC_DAILY_020", "1", "after_navigate")

        current_url = page.url.lower()
        has_change_pw_form = page.locator(
            "input[type='password'], :text('Đổi mật khẩu'), :text('Change password'), "
            ":text('Mật khẩu mới')"
        ).first.is_visible(timeout=5000)
        self.shot(page, "TC_DAILY_020", "2", "final_state")

        if "login" in current_url or "signin" in current_url:
            print(f"  [PASS] Redirect về Login (chưa xác thực) — URL: {page.url}")
        elif has_change_pw_form:
            print(f"  [PASS] Form đổi mật khẩu hiển thị — URL: {page.url}")
        else:
            print(f"  [PASS] Trang load bình thường (không 404/500) — URL: {page.url}")

        change_pw_link = page.locator(
            "a:has-text('Đổi mật khẩu'), button:has-text('Đổi mật khẩu')"
        ).first
        if change_pw_link.is_visible(timeout=3000):
            change_pw_link.click()
            page.wait_for_timeout(2000)
            self.shot(page, "TC_DAILY_020", "3", "change_pw_section")

    # ── TC_DAILY_037 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_037_login_email_password_tao_ngay_check_points(
        self, page: Page, base_url: str
    ):
        """TC_DAILY_037 — Đăng nhập email/pass → Tạo ngay → Studio → kiểm tra 50 điểm."""
        if not _TEST_EMAIL or not _TEST_PASSWORD:
            pytest.skip("TC_DAILY_037: Chưa set TEST_EMAIL / TEST_PASSWORD trong .env")

        home   = HomePage(page, base_url)
        auth   = AuthModalPage(page, base_url)
        studio = StudioPage(page, base_url)

        # S1: Vào trang chủ
        home.navigate()
        self.shot(home, "TC_DAILY_037", "1", "home_loaded")

        # S2: Logout nếu đang đăng nhập
        home.header.logout_if_needed("TC_DAILY_037")

        # S3: Mở modal đăng nhập
        assert home.header.login_button.is_visible(timeout=10_000), \
            "TC_DAILY_037 FAIL: Không tìm thấy nút 'Đăng nhập'"
        home.header.click_login()
        assert auth.is_open(timeout=8000), "TC_DAILY_037 FAIL: Login modal không mở"
        self.shot(home, "TC_DAILY_037", "2", "login_modal_opened")

        # S4: Nhập email + mật khẩu
        assert auth.email_input.is_visible(timeout=5000), \
            "TC_DAILY_037 FAIL: Không tìm thấy email input"
        assert auth.password_input.is_visible(timeout=5000), \
            "TC_DAILY_037 FAIL: Không tìm thấy password input"
        auth.fill_login(_TEST_EMAIL, _TEST_PASSWORD)
        self.shot(home, "TC_DAILY_037", "3", "credentials_filled")

        # S5: Submit
        auth.submit_login()
        self.shot(home, "TC_DAILY_037", "4", "after_submit")

        # S6: Kiểm tra đăng nhập thành công
        if auth.error_message.is_visible(timeout=2000):
            err_text = auth.error_message.inner_text().strip()[:100]
            pytest.fail(
                f"TC_DAILY_037 FAIL: Đăng nhập thất bại — '{err_text}'. "
                "Kiểm tra lại TEST_EMAIL / TEST_PASSWORD"
            )
        assert not auth.is_open(timeout=6000), \
            "TC_DAILY_037 FAIL: Login modal vẫn hiện sau submit"
        assert not home.header.login_button.is_visible(timeout=3000), \
            "TC_DAILY_037 FAIL: Nút 'Đăng nhập' vẫn còn trên header sau login"

        self.shot(home, "TC_DAILY_037", "5", "login_success")
        print(f"  [PASS] TC_DAILY_037: Đăng nhập thành công — email={_TEST_EMAIL}")

        # S7: Nhập prompt rồi click "Tạo ngay" → Studio (site yêu cầu có prompt trước)
        home.fill_prompt("con rồng Việt Nam phong cách cổ điển")
        page.wait_for_timeout(500)
        home.click_generate()
        try:
            page.wait_for_url("**/studio**", timeout=20_000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        assert "studio" in page.url, (
            f"TC_DAILY_037 FAIL: Sau 'Tạo ngay' không navigate vào Studio. URL: {page.url}"
        )
        print(f"  [INFO] TC_DAILY_037: Vào Studio — {page.url}")
        self.shot(studio, "TC_DAILY_037", "6", "studio_after_login")

        # S8: Kiểm tra 50 điểm
        studio.check_points(50, "TC_DAILY_037")
        self.shot(studio, "TC_DAILY_037", "7", "studio_points_check")
        print(f"  [PASS] TC_DAILY_037: Email login → Tạo ngay → Studio OK. URL: {page.url}")

    # ── TC_DAILY_044 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_044_login_gmail_tao_ngay_check_points(self, browser, base_url: str):
        """TC_DAILY_044 — Gmail session (storage_state JSON) → Tạo ngay → Studio → 50 điểm.

        Yêu cầu: chạy trước scripts/save_google_session.py để tạo auth_state/google_session.json
        """
        session_file = os.path.join(_BASE_DIR, "auth_state", "google_session.json")
        if not os.path.exists(session_file):
            pytest.skip(
                "TC_DAILY_044: Chưa có Google session. "
                "Chạy: python scripts/save_google_session.py để tạo session một lần"
            )

        # Dùng storage_state JSON qua browser fixture — tránh sync_playwright() conflict với asyncio
        context = browser.new_context(
            storage_state=session_file,
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
            viewport={"width": 1440, "height": 900},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()

        home   = HomePage(page, base_url)
        auth   = AuthModalPage(page, base_url)
        studio = StudioPage(page, base_url)

        try:
            # S1: Vào trang chủ — session đã có, site tự nhận diện đăng nhập
            home.navigate()
            self.shot(home, "TC_DAILY_044", "1", "home_with_google_session")

            # S2: Verify đang đăng nhập
            if home.header.login_button.is_visible(timeout=5000):
                print("  [INFO] TC_DAILY_044: Session hết hạn — thử Google OAuth lại")
                home.header.click_login()
                if auth.is_open(timeout=5000) and auth.google_button.is_visible(timeout=3000):
                    with page.expect_popup(timeout=15000) as popup_info:
                        auth.click_google()
                    google_popup = popup_info.value
                    google_popup.wait_for_load_state("domcontentloaded", timeout=15000)
                    self.shot(google_popup, "TC_DAILY_044", "1b", "google_popup_reauth")
                    try:
                        google_popup.wait_for_event("close", timeout=15000)
                    except Exception:
                        google_popup.close()
                    page.wait_for_timeout(3000)

                assert not home.header.login_button.is_visible(timeout=5000), (
                    "TC_DAILY_044 FAIL: Google session hết hạn và không thể re-auth. "
                    "Chạy lại: python scripts/save_google_session.py"
                )
            else:
                print("  [INFO] TC_DAILY_044: Google session hợp lệ — đã đăng nhập sẵn")

            self.shot(home, "TC_DAILY_044", "2", "google_login_verified")
            print("  [PASS] TC_DAILY_044: Google session OK")

            # S3: Fill prompt → Tạo ngay → Studio
            home.fill_prompt("con rồng Việt Nam phong cách cổ điển")
            page.wait_for_timeout(500)
            home.click_generate()
            try:
                page.wait_for_url("**/studio**", timeout=20_000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            assert "studio" in page.url, (
                f"TC_DAILY_044 FAIL: Sau 'Tạo ngay' không navigate vào Studio. URL: {page.url}"
            )
            self.shot(studio, "TC_DAILY_044", "3", "studio_after_gmail_login")

            # S4: Kiểm tra 50 điểm
            studio.check_points(50, "TC_DAILY_044")
            self.shot(studio, "TC_DAILY_044", "4", "studio_points_check")
            print(f"  [PASS] TC_DAILY_044: Gmail login → Tạo ngay → Studio OK. URL: {page.url}")

        finally:
            context.close()
