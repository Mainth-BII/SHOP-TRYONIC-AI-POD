"""
Daily Monitoring — Group 5: Order & Checkout
TC_DAILY_100 → TC_DAILY_115

Mục tiêu: Refactored Order tests using POM.
"""
import pytest
from playwright.sync_api import Page
from pages.studio_page import StudioPage
from pages.checkout_page import CheckoutPage

class TestDailyOrder:
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.studio = StudioPage(page, base_url)
        self.checkout = CheckoutPage(page, base_url)
        self.domain = "order"

    @pytest.mark.daily
    def test_TC_DAILY_100_add_to_cart_flow(self):
        """TC_DAILY_100 — Toàn bộ luồng thêm vào giỏ hàng."""
        self.studio.navigate()
        
        # S1: Mở modal đặt hàng
        self.studio.open_order_modal()
        self.studio.page.wait_for_timeout(2000)
        self.studio.shot("TC_DAILY_100", "1", "order_modal_opened", domain=self.domain)
        
        # S2: Trên trang /review — verify nút "Đặt hàng" tồn tại
        # (Flow mới: studio → /review với variant selector + Đặt hàng)
        order_btn = self.studio.page.locator("button:has-text('Đặt hàng')").first
        assert order_btn.is_visible(timeout=5000), \
            f"Nút 'Đặt hàng' không thấy trên trang review — URL: {self.studio.page.url}"

        self.studio.shot("TC_DAILY_100", "2", "review_page_with_order_btn", domain=self.domain)
        print("  [PASS] Review page với nút Đặt hàng verified")
