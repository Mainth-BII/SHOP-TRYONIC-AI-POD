from core.base_page import BasePage
from playwright.sync_api import Page, expect

class LoginPage(BasePage):
    """
    Page Object Model representing the Login Screen.
    """
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = "https://test.studio.tryonic.ai/sign-in"
        
        # Locators
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']"
        self.forgot_password_link = "text=Quên mật khẩu?"

    def navigate_to_login(self):
        self.navigate(self.url)

    def login(self, email: str, password: str):
        if email:
            self.fill(self.email_input, email)
        if password:
            self.fill(self.password_input, password)
        self.click(self.login_button)

    def verify_elements_visible(self):
        expect(self.find(self.email_input)).to_be_visible(timeout=5000)
        expect(self.find(self.password_input)).to_be_visible()
        expect(self.find(self.login_button)).to_be_visible()
        expect(self.find(self.forgot_password_link).first).to_be_visible()

    def verify_password_is_masked(self):
        expect(self.find(self.password_input)).to_have_attribute("type", "password")

    def verify_error_visible(self, error_type: str):
        if error_type == "required":
            expect(self.find("text=Required").or_(self.find("text=vui lòng nhập")).first).to_be_visible(timeout=2000)
        elif error_type == "invalid_format":
            expect(self.find("text=Invalid").or_(self.find("text=không hợp lệ")).first).to_be_visible(timeout=2000)
        elif error_type == "auth_failed":
            expect(self.find("text=sai").or_(self.find("text=không khớp")).or_(self.find("text=incorrect")).first).to_be_visible(timeout=3000)

    def verify_login_button_disabled(self):
        expect(self.find(self.login_button)).to_be_disabled()
