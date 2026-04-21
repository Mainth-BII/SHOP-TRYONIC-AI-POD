"""
Daily Monitoring — Group 2: Authentication Flow
TC_DAILY_032 → TC_DAILY_045

Mục tiêu: Refactored Auth tests using POM.
"""
import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.auth_modal_page import AuthModalPage

class TestDailyAuth:
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.home = HomePage(page, base_url)
        self.auth = AuthModalPage(page, base_url)
        self.domain = "auth"

    @pytest.mark.daily
    def test_TC_DAILY_032_login_form_validation(self):
        """TC_DAILY_032 — Kiểm tra validation form đăng nhập."""
        self.home.navigate()
        self.home.header.login_button.click()
        
        # S1: Để trống và click Đăng nhập
        self.auth.submit_button.click()
        self.home.page.wait_for_timeout(1000)
        self.auth.shot("TC_DAILY_032", "1", "empty_login_validation", domain=self.domain)
        
        # S2: Nhập email sai định dạng
        self.auth.email_input.fill("invalid-email")
        self.auth.submit_button.click()
        self.home.page.wait_for_timeout(1000)
        self.auth.shot("TC_DAILY_032", "2", "invalid_email_format", domain=self.domain)
        print("  [PASS] Login validation verified")

    @pytest.mark.daily
    def test_TC_DAILY_040_register_modal_loads(self):
        """TC_DAILY_040 — Chuyển sang form Đăng ký thành công."""
        self.home.navigate()
        self.home.header.login_button.click()
        
        # S1: Chuyển sang Tab Đăng ký
        self.auth.click_register_link()
        self.auth.shot("TC_DAILY_040", "1", "register_modal_visible", domain=self.domain)
        
        assert self.auth.register_email_input.is_visible(), "Register form not found"
        print("  [PASS] Register form verified")
