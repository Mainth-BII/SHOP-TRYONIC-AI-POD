"""
Production Smoke Tests — Kiểm tra các tính năng trọng yếu trên môi trường Live.
"""
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage

class TestProductionSmoke:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.home = HomePage(page, base_url)
        self.domain = "production"

    @pytest.mark.smoke
    def test_homepage_elements(self):
        """Kiểm tra các thành phần cốt lõi của trang chủ Production."""
        self.home.navigate()
        self.home.shot("PROD_001", "1", "homepage_check", domain=self.domain)
        
        # Sử dụng HeaderComponent từ POM mới
        expect(self.home.header.login_button).to_be_visible()
        expect(self.home.prompt_input).to_be_visible()
        expect(self.home.generate_button).to_be_visible()
        
        print("  [PASS] Production Home elements are OK")

    @pytest.mark.artwork
    def test_category_selection(self):
        """Kiểm tra khả năng tương tác với các Style nghệ thuật."""
        self.home.navigate()
        
        categories = ["Anime", "Thủy mặc", "Hình khối"]
        for i, cat in enumerate(categories):
            self.home.select_category(cat)
            self.home.page.wait_for_timeout(500)
            # Chụp ảnh verify mỗi category
            self.home.shot("PROD_002", str(i+1), f"category_{cat}_selected", domain=self.domain)
            
        print("  [PASS] Production Category selection interaction OK")
