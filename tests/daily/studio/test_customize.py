"""
Daily Monitoring — Group 4: Product Customization & UX
Refactored version with Data-Driven Testing (DDT).
"""
import json
import os
import pytest
from playwright.sync_api import Page
from pages.studio_page import StudioPage

# Load centralized test data
def load_test_data():
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_path, "data", "studio_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

test_data = load_test_data()

class TestDailyCustomize:

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.studio = StudioPage(page, base_url)
        self.domain = "customize"

    @pytest.mark.daily
    def test_TC_DAILY_070_color_change(self):
        """TC_DAILY_070 — Studio: Thay đổi màu sản phẩm."""
        self.studio.navigate()
        if self.studio.select_color("Đen"):
            self.studio.page.wait_for_timeout(1000)
            self.studio.shot("TC_DAILY_070", "1", "color_changed_to_black", domain=self.domain)
        else:
            self.studio.color_swatches.first.click()
            self.studio.shot("TC_DAILY_070", "1", "first_color_applied", domain=self.domain)

    @pytest.mark.daily
    def test_TC_DAILY_071_size_chart_modal(self):
        """TC_DAILY_071 — Studio -> Order Modal -> Size Chart."""
        self.studio.navigate()
        self.studio.open_order_modal()
        assert self.studio.size_chart_link.is_visible(timeout=5000)
        self.studio.size_chart_link.click()
        self.studio.shot("TC_DAILY_071", "1", "size_chart_modal_opened", domain=self.domain)
        self.studio.page.keyboard.press("Escape")

    @pytest.mark.daily
    @pytest.mark.parametrize("category", test_data["categories"])
    def test_switch_product_categories(self, category):
        """DDT: Kiểm tra việc chuyển đổi giữa nhiều loại sản phẩm từ file JSON."""
        self.studio.navigate(category["id"])
        self.studio.page.wait_for_timeout(2000)
        self.studio.shot("TC_DDT_01", category["id"], f"loaded_{category['id']}", domain=self.domain)
        assert self.studio.is_canvas_visible(), f"Canvas missing for {category['name']}"

    @pytest.mark.daily
    def test_TC_DAILY_073_front_back_toggle(self):
        """TC_DAILY_073 — Studio: Chuyển mặt trước/sau."""
        self.studio.navigate()
        self.studio.toggle_side("back")
        self.studio.page.wait_for_timeout(1500)
        self.studio.shot("TC_DAILY_073", "1", "back_view", domain=self.domain)
        self.studio.toggle_side("front")
        self.studio.shot("TC_DAILY_073", "2", "front_view", domain=self.domain)
