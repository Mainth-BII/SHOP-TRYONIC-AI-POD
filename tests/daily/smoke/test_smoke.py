"""
Daily Monitoring — Group 1: Availability Checks
TC_DAILY_001 → TC_DAILY_010

Mục tiêu: Refactored smoke tests using POM.
"""
import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from pages.studio_page import StudioPage
from pages.auth_modal_page import AuthModalPage

class TestDailySmoke:
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.home = HomePage(page, base_url)
        self.studio = StudioPage(page, base_url)
        self.auth = AuthModalPage(page, base_url)
        self.domain = "smoke"

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_001_home_loads(self):
        """TC_DAILY_001 — Trang chủ load thành công."""
        self.home.navigate()
        self.home.shot("TC_DAILY_001", "1", "home_page_loaded", domain=self.domain)
        
        assert self.home.page.title() != "", "Home must have title"
        assert self.home.generate_button.is_visible(), "Generate button should be visible"
        print(f"  [PASS] Home page verified")

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_002_studio_loads(self):
        """TC_DAILY_002 — Studio page load, canvas hiển thị."""
        self.studio.navigate()
        self.studio.shot("TC_DAILY_002", "1", "studio_page_loaded", domain=self.domain)
        
        assert self.studio.is_canvas_visible(), "Canvas must be visible in Studio"
        print(f"  [PASS] Studio page verified")

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_003_login_modal_opens(self):
        """TC_DAILY_003 — Mở modal đăng nhập từ header."""
        self.home.navigate()
        
        # Action: Click Đăng nhập từ header
        self.home.header.login_button.click()
        self.home.page.wait_for_timeout(2000)
        self.home.shot("TC_DAILY_003", "1", "login_modal_opened", domain=self.domain)
        
        assert self.auth.is_open(), "Login modal should be open"
        assert self.auth.email_input.is_visible(), "Email input should be visible"
        print("  [PASS] Login modal verified")

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_007_order_modal_opens(self):
        """TC_DAILY_007 — Studio: Mở modal đặt hàng."""
        self.studio.navigate()
        self.studio.open_order_modal()
        self.studio.shot("TC_DAILY_007", "1", "order_modal_opened", domain=self.domain)

        # Flow mới: "Hoàn tất thiết kế" → navigate tới /review với nút "Đặt hàng"
        on_review = "/review" in self.studio.page.url
        has_order_btn = self.studio.page.locator("button:has-text('Đặt hàng')").is_visible(timeout=3000)
        assert on_review or has_order_btn, \
            f"Order flow không khởi động — URL: {self.studio.page.url}"
        print("  [PASS] Order flow verified")
