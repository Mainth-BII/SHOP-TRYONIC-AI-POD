"""
Non-Functional Tests — Mobile Responsiveness & Performance baseline.
Kiểm tra hiệu năng và giao diện mobile trên môi trường Live.
"""
import pytest
import time
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.studio_page import StudioPage

class TestProductionNonFunctional:

    @pytest.mark.performance
    def test_PERF_001_page_load_timing(self, page: Page, base_url: str):
        """Kiểm tra thời gian tải trang (Performance Baseline)."""
        metrics = [
            ("/", "Home", 8),
            ("/studio", "Studio", 12),
            ("/pages/chinh-sach-bao-mat", "Policy", 6)
        ]
        
        for path, label, threshold in metrics:
            start_time = time.time()
            page.goto(f"{base_url}{path}", wait_until="load", timeout=30000)
            load_time = time.time() - start_time
            
            print(f"  [INFO] {label} load time: {load_time:.2f}s (Threshold: {threshold}s)")
            
            # Assert thời gian tải trang không quá ngưỡng quy định
            assert load_time <= threshold, f"LỖI: {label} tải quá chậm ({load_time:.2f}s > {threshold}s)"

    @pytest.mark.mobile
    def test_MOB_001_home_responsive(self, mobile_page: Page, base_url: str):
        """Kiểm tra giao diện trang chủ trên Mobile (iPhone 12 Pro)."""
        home = HomePage(mobile_page, base_url)
        home.navigate()
        home.shot("NON_FUNC", "MOB_01", "home_mobile_view", domain="production")
        
        # Kiểm tra sự xuất hiện của nút Menu Mobile (Hamburger)
        # Thường mobile sẽ ẩn menu ngang và hiện icon menu
        menu_btn = mobile_page.locator("header button[class*='menu'], header svg").first
        assert menu_btn.is_visible(), "LỖI: Không tìm thấy nút Menu Mobile (Hamburger)"
        print("  [PASS] Mobile Home response OK")

    @pytest.mark.mobile
    def test_MOB_002_studio_responsive(self, mobile_page: Page, base_url: str):
        """Kiểm tra giao diện Studio trên Mobile."""
        studio = StudioPage(mobile_page, base_url)
        studio.navigate()
        # Chờ studio load (mobile thường chậm hơn)
        mobile_page.wait_for_timeout(5000)
        studio.shot("NON_FUNC", "MOB_02", "studio_mobile_view", domain="production")
        
        # Kiểm tra canvas vẫn hiển thị trong không gian hẹp
        assert studio.is_canvas_visible(), "LỖI: Canvas Studio bị ẩn hoặc crash trên Mobile"
        print("  [PASS] Mobile Studio response OK")
