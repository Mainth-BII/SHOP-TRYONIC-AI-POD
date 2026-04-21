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
        
        # S2: Chọn size và Thêm vào giỏ
        self.checkout.select_size_if_shown()
        
        add_btn = self.studio.page.locator("button:has-text('Thêm vào giỏ'), button:has-text('Add to cart')").first
        assert add_btn.is_visible(), "Add to cart button not found"
        add_btn.click()
        
        self.studio.page.wait_for_timeout(2000)
        self.studio.shot("TC_DAILY_100", "2", "after_add_to_cart", domain=self.domain)
        
        # Verify toast hoặc icon giỏ hàng
        assert self.checkout.add_to_cart_toast.is_visible(timeout=5000) or self.checkout.cart_badge.is_visible(), \
            "No feedback after adding to cart"
        print("  [PASS] Add to cart flow verified")
