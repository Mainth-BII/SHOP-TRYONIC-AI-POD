from .base_page import BasePage
from playwright.sync_api import Page, expect

class LoginPage(BasePage):
    """Page Object for the /sign-in screen."""

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # ── ALL locators defined here — NEVER in test files ──
        # Using name attributes (most stable for this app)
        self.email_input    = page.locator("input[name='email']")
        self.password_input = page.locator("input[name='password']")
        self.login_button   = page.locator("button[type='submit']")
        self.forgot_pw_link = page.locator("text=Quên mật khẩu?").first

        # Error message locators — verified against actual app output
        self.error_auth     = page.locator("text=Tài khoản hoặc mật khẩu không chính xác")
        self.error_format   = page.locator("text=Invalid").or_(
                              page.locator("text=không hợp lệ")).first

    # ── Navigation ──
    def goto(self):
        self.navigate("/sign-in")

    # ── Actions ──
    def fill_email(self, email: str):
        self.email_input.fill(email)

    def fill_password(self, password: str):
        self.password_input.fill(password)

    def click_login(self):
        self.login_button.click()

    def login(self, email: str, password: str):
        """Fills credentials and submits the login form."""
        self.fill_email(email)
        self.fill_password(password)
        self.click_login()
        self.page.wait_for_load_state("networkidle")

    # ── Assertions ──
    def assert_all_elements_visible(self):
        """Standard check + Viewport check to ensure no clipping on mobile."""
        elements = [self.email_input, self.password_input, self.login_button, self.forgot_pw_link]
        for el in elements:
            expect(el).to_be_visible(timeout=5000)
            # Stricter check: must be at least 80% in viewport to avoid cut-off text
            expect(el).to_be_in_viewport(ratio=0.8)

    def assert_password_is_masked(self):
        expect(self.password_input).to_have_attribute("type", "password")

    def assert_login_button_disabled(self):
        expect(self.login_button).to_be_disabled()

    def assert_auth_error(self):
        expect(self.error_auth).to_be_visible(timeout=3000)

    def assert_format_error(self):
        expect(self.error_format).to_be_visible(timeout=2000)

    def assert_redirected_after_login(self):
        self.page.wait_for_url(lambda url: "sign-in" not in url, timeout=8000)
