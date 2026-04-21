"""Product Page Object — /product."""

from playwright.sync_api import Page, Locator
from .base_page import BasePage


class ProductPage(BasePage):
    """Trang sản phẩm: gallery ảnh, thêm giỏ hàng, mua ngay."""

    MH_DIR = "MH04_product"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Locators ─────────────────────────────────────────────────────────────

    @property
    def heading(self) -> Locator:
        return self.page.locator(
            "h1:has-text('Áo'), h2:has-text('Áo'), h1, h2"
        ).first

    @property
    def product_images(self) -> Locator:
        return self.page.locator(
            "img[src*='tryon'], img[alt*='product'], "
            "[class*='gallery'] img, [class*='product'] img"
        )

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Thêm vào giỏ'), button:has-text('Them vao gio'), "
            "button:has-text('Add to cart'), button:has-text('Thêm')"
        ).first

    @property
    def buy_now_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Mua ngay'), button:has-text('Mua Ngay'), "
            "button:has-text('Buy now')"
        ).first

    @property
    def cart_toast(self) -> Locator:
        return self.page.locator(
            "[class*='toast'], [class*='Toast'], [role='alert']:has-text('giỏ')"
        ).first

    @property
    def login_modal(self) -> Locator:
        return self.page.locator("div[role='dialog']").first

    # ── Actions ──────────────────────────────────────────────────────────────

    def navigate(self) -> None:
        self.goto("/product")

    def click_add_to_cart(self) -> None:
        self.add_to_cart_button.click()
        self.page.wait_for_timeout(2000)

    def click_buy_now(self) -> None:
        self.buy_now_button.click()
        self.page.wait_for_timeout(2000)

    def click_gallery_image(self, index: int = 1) -> None:
        try:
            self.product_images.nth(index).click()
            self.page.wait_for_timeout(1000)
        except Exception:
            pass

    # ── State checks ─────────────────────────────────────────────────────────

    def add_to_cart_feedback_visible(self, timeout: int = 5000) -> bool:
        """Trả về True nếu có toast, modal, hoặc URL chuyển sang cart."""
        return (
            "cart" in self.page.url
            or self.cart_toast.is_visible(timeout=timeout)
            or self.login_modal.is_visible(timeout=timeout)
        )
