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
        
        # Đảm bảo base_url không có dấu gạch chéo ở cuối để tránh lỗi //
        clean_base = base_url.rstrip("/")
        
        for path, label, threshold in metrics:
            start_time = time.time()
            # Sử dụng wait_until='domcontentloaded' để tránh timeout nếu tracking script quá chậm
            page.goto(f"{clean_base}{path}", wait_until="domcontentloaded", timeout=30000)
            load_time = time.time() - start_time
            
            print(f"  [INFO] {label} load time: {load_time:.2f}s (Threshold: {threshold}s)")
            assert load_time <= threshold, f"LỖI: {label} tải quá chậm ({load_time:.2f}s > {threshold}s)"

    @pytest.mark.mobile
    def test_MOB_001_home_responsive(self, mobile_page: Page, base_url: str):
        """Kiểm tra giao diện trang chủ trên Mobile."""
        home = HomePage(mobile_page, base_url)
        home.navigate()
        home.shot("NON_FUNC", "MOB_01", "home_mobile_view", domain="production")
        
        # Selector linh hoạt hơn cho nút Menu Mobile
        menu_btn = mobile_page.locator("header button, header [class*='menu'], header i").first
        try:
            expect(menu_btn).to_be_visible(timeout=5000)
            print("  [PASS] Mobile Menu visible")
        except:
             # Nếu không thấy button, thử tìm SVG/Icon menu
             assert mobile_page.locator("header svg").first.is_visible(), "LỖI: Không tìm thấy UI menu mobile"

    @pytest.mark.mobile
    def test_MOB_002_studio_responsive(self, mobile_page: Page, base_url: str):
        """Kiểm tra giao diện Studio trên Mobile."""
        studio = StudioPage(mobile_page, base_url)
        studio.navigate()
        mobile_page.wait_for_timeout(5000)
        studio.shot("NON_FUNC", "MOB_02", "studio_mobile_view", domain="production")
        assert studio.is_canvas_visible(), "LỖI: Canvas Studio bị ẩn hoặc crash trên Mobile"
