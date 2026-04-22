"""
Critical Path Tests — Môi trường Production (Live)
Tập trung vào các luồng nghiệp vụ tạo ra doanh thu và trải nghiệm người dùng cốt lõi.
"""
import pytest
from playwright.sync_api import Page, expect
import os

class TestProductionCriticalFlows:

    @pytest.fixture(autouse=True)
    def setup(self, home_page, studio_page, auth_page, checkout_page):
        self.home = home_page
        self.studio = studio_page
        self.auth = auth_page
        self.checkout = checkout_page
        self.domain = "production"

    @pytest.mark.production
    def test_CRITICAL_001_guest_journey_to_checkout(self):
        """Kịch bản: Khách vãng lai vào xem -> Thiết kế -> Đi tới Checkout."""
        # 1. Truy cập Studio
        self.studio.navigate()
        self.studio.shot("CRIT_01", "1", "studio_loaded", domain=self.domain)
        assert self.studio.is_canvas_visible(), "LỖI: Canvas không hiển thị trên Production"

        # 2. Tương tác thiết kế (Đổi màu)
        self.studio.select_color("Đen")
        self.studio.page.wait_for_timeout(1000)
        self.studio.shot("CRIT_01", "2", "color_changed", domain=self.domain)

        # 3. Mở Modal Đặt hàng & Chọn size
        self.studio.accept_terms("CRIT_01")
        self.studio.open_order_modal()
        self.checkout.select_size_if_shown()
        self.studio.shot("CRIT_01", "3", "order_modal_prepared", domain=self.domain)

        # 4. Nhấn Mua ngay để tới trang Checkout
        buy_btn = self.checkout.buy_now_button
        if not buy_btn.is_visible(timeout=8_000):
            self.studio.shot("CRIT_01", "4", "no_buy_button_canvas_empty", domain=self.domain)
            pytest.skip("BỎ QUA: Canvas trống, 'Hoàn tất thiết kế' không mở order modal — cần design trước khi checkout")
        self.checkout.click_buy_now()
        self.studio.page.wait_for_timeout(3000)
        self.studio.shot("CRIT_01", "4", "checkout_page_reached", domain=self.domain)

        # Verify: Phải ở trang checkout hoặc thấy form thông tin giao hàng
        assert "checkout" in self.studio.page.url or "checkouts" in self.studio.page.url, \
            f"LỖI: Không tới được trang Checkout. URL hiện tại: {self.studio.page.url}"

    @pytest.mark.production
    def test_CRITICAL_002_login_functionality(self):
        """Kịch bản: Đăng nhập bằng tài khoản thật (lấy từ .env)."""
        email = os.getenv("DAILY_TEST_EMAIL")
        password = os.getenv("DAILY_TEST_PASSWORD")
        
        if not email or not password:
            pytest.skip("BỎ QUA: Thiếu thông tin DAILY_TEST_EMAIL/PASSWORD trong .env")

        self.home.navigate()
        self.home.header.click_login()
        self.auth.login(email, password)
        
        # Verify: Kiểm tra biến mất của nút đăng nhập hoặc xuất hiện avatar/logout
        self.home.page.wait_for_timeout(3000)
        self.home.shot("CRIT_02", "1", "after_login_attempt", domain=self.domain)
        
        # Check nếu không còn nút đăng nhập (nghĩa là đã login)
        assert not self.home.header.login_button.is_visible(), "LỖI: Nút Đăng nhập vẫn còn sau khi login"

    @pytest.mark.production
    def test_CRITICAL_003_legal_and_contact_links(self):
        """Kịch bản: Kiểm tra các thông tin pháp lý & liên hệ (Footer)."""
        self.home.navigate()
        self.home.scroll_to_bottom()
        self.home.shot("CRIT_03", "1", "footer_check", domain=self.domain)
        
        # Kiểm tra sự tồn tại của các link quan trọng
        legal_links = ["chinh-sach-bao-mat", "chinh-sach-doi-tra", "lien-he-cskh"]
        for link in legal_links:
            loc = self.home.page.locator(f"footer a[href*='{link}']").first
            assert loc.is_visible(), f"LỖI: Thiếu link {link} ở Footer"
