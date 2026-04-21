"""Studio Page Object — /studio canvas, AI generation, điểm thưởng."""

from playwright.sync_api import Page, Locator
from .base_page import BasePage


class StudioPage(BasePage):
    """Trang Studio: AI gen artwork, chọn variant, đặt hàng, kiểm tra điểm."""

    MH_DIR = "MH09_ai_features"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Locators ─────────────────────────────────────────────────────────────
    @property
    def prompt_input(self) -> Locator:
        return self.page.locator(
            "input[placeholder*='Bạn muốn'], input[placeholder*='ý tưởng'], "
            "textarea[placeholder*='Bạn']"
        ).first

    @property
    def generate_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Tạo ngay'), button:has-text('Tạo'), "
            "button:has-text('Generate')"
        ).first

    @property
    def finish_button(self) -> Locator:
        """Nút 'Hoàn tất thiết kế' — xuất hiện sau khi gen xong."""
        return self.page.locator(
            "button:has-text('Hoàn tất thiết kế'), button:has-text('Hoan tat'), "
            "button:has-text('Finish')"
        ).first

    @property
    def order_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang'), "
            "button:has-text('Order')"
        ).first

    @property
    def variant_images(self) -> Locator:
        return self.page.locator("img[src*='generation'], img[class*='variant'], img[class*='result']")

    @property
    def color_swatches(self) -> Locator:
        return self.page.locator("[class*='color'], [class*='swatch'], button:has([style*='background-color'])")

    @property
    def size_chart_link(self) -> Locator:
        return self.page.locator("button:has-text('Bảng size'), a:has-text('Bảng size'), :text('Bảng size')").first

    @property
    def back_button(self) -> Locator:
        return self.page.locator("button:has-text('Mặt sau'), button:has-text('Mat sau')").first

    @property
    def front_button(self) -> Locator:
        return self.page.locator("button:has-text('Mặt trước'), button:has-text('Mat truoc')").first

    @property
    def category_selector(self) -> Locator:
        return self.page.locator(
            "button:has-text('Áo Thun'), button:has-text('T-Shirt'), "
            "button:has-text('T-shirt'), [class*='category']"
        ).first

    @property
    def library_button(self) -> Locator:
        return self.page.locator("button:has-text('Thư Viện'), button:has-text('Thu Vien')").first

    # ── Actions ──────────────────────────────────────────────────────────────

    def navigate(self, category_id: str = "t-shirts") -> None:
        self.goto(f"/studio?category={category_id}")

    def generate(self, prompt: str) -> None:
        self.prompt_input.fill(prompt)
        self.generate_button.click()

    def select_color(self, name: str) -> bool:
        """Tìm và click vào màu cụ thể theo text hoặc attribute."""
        btn = self.page.locator("button").filter(has_text=name).first
        if btn.is_visible(timeout=5000):
            btn.click()
            return True
        return False

    def toggle_side(self, side: str = "back") -> None:
        if side.lower() == "back":
            self.back_button.click()
        else:
            self.front_button.click()

    def open_library(self) -> None:
        self.library_button.click()

    def open_order_modal(self) -> None:
        self.order_button.click()

    # ── Assertions / Checks ──────────────────────────────────────────────────

    def is_canvas_visible(self) -> bool:
        return (
            self.page.locator(".canvas-container").is_visible(timeout=8000)
            or self.page.locator("canvas").first.is_visible(timeout=2000)
        )

    def check_points(self, expected: int = 50, tc_id: str = "") -> bool:
        """Kiểm tra số điểm hiển thị trong Studio DOM."""
        has_points = self.page.evaluate(f"""() => {{
            const body = document.body.innerText || "";
            if (/{expected}\\s*(điểm|points)/i.test(body)) return true;
            return Array.from(document.querySelectorAll(
                '[class*="point"], [class*="credit"], [class*="balance"]'
            )).some(el => el.innerText && /{expected}/.test(el.innerText));
        }}""")
        if has_points:
            if tc_id: print(f"  [PASS] {tc_id}: Tìm thấy {expected} điểm trong Studio")
        else:
            if tc_id: print(f"  [WARN] {tc_id}: Không tìm thấy {expected} điểm")
        return has_points

    def wait_for_generation(self, timeout: int = 90_000) -> bool:
        try:
            self.finish_button.wait_for(state="visible", timeout=timeout)
            return not self.finish_button.is_disabled()
        except Exception:
            return False

