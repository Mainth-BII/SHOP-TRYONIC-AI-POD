"""Auth Modal Page Object — Login / Register / Forgot Password modal."""

from playwright.sync_api import Page, Locator
from .base_page import BasePage


class AuthModalPage(BasePage):
    """Quản lý modal đăng nhập, đăng ký, quên mật khẩu của Tryonic Shop."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Modal container ──────────────────────────────────────────────────────

    @property
    def modal(self) -> Locator:
        # Radix UI dialog content có role='dialog' và data-state='open'
        return self.page.locator(
            "[role='dialog'][data-state='open'], [role='dialog']:visible"
        ).first

    def is_open(self, timeout: int = 5000) -> bool:
        try:
            return self.modal.is_visible(timeout=timeout)
        except Exception:
            return False

    # ── Login form locators — query page directly (modal không dùng role=dialog) ──

    @property
    def email_input(self) -> Locator:
        return self.page.locator(
            "input[type='email'], input[name='email'], input[placeholder*='Email'], "
            "input[placeholder*='email'], input[placeholder*='name@']"
        ).first

    @property
    def password_input(self) -> Locator:
        return self.page.locator(
            "input[type='password'], input[name='password']"
        ).first

    @property
    def submit_button(self) -> Locator:
        # Tìm trong form hoặc role=dialog để tránh match vào nút header
        return self.page.locator(
            "form button[type='submit'], form button:has-text('Đăng nhập'), "
            "[role='dialog'] button[type='submit'], [role='dialog'] button:has-text('Đăng nhập')"
        ).first

    @property
    def google_button(self) -> Locator:
        return self.page.locator("button:has-text('Google'):visible").first

    @property
    def facebook_button(self) -> Locator:
        return self.page.locator("button:has-text('Facebook'):visible").first

    @property
    def register_link(self) -> Locator:
        return self.page.locator(
            "a:has-text('Đăng ký'), button:has-text('Đăng ký')"
        ).first

    @property
    def forgot_password_link(self) -> Locator:
        return self.page.locator(
            "a:has-text('Quên mật khẩu'), button:has-text('Quên mật khẩu')"
        ).first

    @property
    def error_message(self) -> Locator:
        return self.page.locator(
            ":text('Sai mật khẩu'), :text('Mật khẩu không đúng'), "
            ":text('incorrect'), :text('Invalid'), :text('Đăng nhập thất bại')"
        ).first

    # ── Register form locators ───────────────────────────────────────────────

    @property
    def register_name_input(self) -> Locator:
        return self.page.locator(
            "input[name='name'], input[placeholder*='Họ tên'], input[placeholder*='Ten']"
        ).first

    @property
    def register_email_input(self) -> Locator:
        return self.page.locator(
            "input[type='email'], input[name='email']"
        ).first

    @property
    def register_submit(self) -> Locator:
        return self.page.locator(
            "button[type='submit']:has-text('Đăng ký'), button:has-text('Tạo tài khoản')"
        ).first

    # ── Forgot password locators ─────────────────────────────────────────────

    @property
    def reset_email_input(self) -> Locator:
        return self.page.locator("input[type='email']").first

    @property
    def reset_submit(self) -> Locator:
        return self.page.locator(
            "button:has-text('Gửi'), button:has-text('Reset'), button[type='submit']"
        ).first

    # ── Actions ──────────────────────────────────────────────────────────────

    def fill_login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.page.wait_for_timeout(200)
        self.password_input.fill(password)
        self.page.wait_for_timeout(200)

    def submit_login(self) -> None:
        self.submit_button.click()
        self.page.wait_for_timeout(3000)

    def login(self, email: str, password: str) -> None:
        """Fill credentials và submit — toàn bộ luồng đăng nhập."""
        self.fill_login(email, password)
        self.submit_login()

    def click_register_link(self) -> None:
        self.register_link.click()
        self.page.wait_for_timeout(800)

    def click_forgot_password(self) -> None:
        self.forgot_password_link.click()
        self.page.wait_for_timeout(800)

    def click_google(self) -> None:
        self.google_button.click()

    def click_facebook(self) -> None:
        self.facebook_button.click()
