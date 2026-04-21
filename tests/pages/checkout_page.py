"""Checkout / Order Modal Page Object."""

from playwright.sync_api import Page, Locator
from .base_page import BasePage


class CheckoutPage(BasePage):
    """Order modal, size selection, cart, checkout flow."""

    MH_DIR = "MH08_checkout"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Order modal locators ──────────────────────────────────────────────────

    @property
    def order_modal(self) -> Locator:
        return self.page.locator(
            "[role='dialog']:has-text('Đặt hàng'), "
            "[role='dialog']:has-text('hang'), "
            "[class*='order'], form:visible, aside:has-text('Size')"
        ).first

    @property
    def size_s_button(self) -> Locator:
        return self.page.locator(
            "[data-size='S'], button:has-text('S'), label:has-text('S'), "
            "[role='dialog'] button:has-text('S')"
        ).first

    @property
    def size_selector(self) -> Locator:
        return self.page.locator(
            "[role='dialog'] select[name*='size'], select[name*='Size']"
        ).first

    @property
    def price_element(self) -> Locator:
        return self.page.locator(
            "[class*='price'], [class*='Price'], [class*='total'], "
            ":text('VND'), :text('vnđ')"
        ).first

    @property
    def buy_now_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Mua ngay'), button:has-text('Thanh toán ngay'), "
            "button:has-text('Checkout'), button:has-text('Đặt hàng ngay')"
        ).first

    @property
    def finish_button(self) -> Locator:
        """Nút 'Hoàn tất thiết kế' / 'Đặt hàng' trên Studio canvas."""
        return self.page.locator(
            "button:has-text('Hoàn tất thiết kế'), button:has-text('Hoan tat thiet ke'), "
            "button:has-text('Đặt hàng'), button:has-text('Dat hang'), "
            "button:has-text('Order')"
        ).first

    # ── Cart locators ─────────────────────────────────────────────────────────

    @property
    def cart_page_indicator(self) -> Locator:
        return self.page.locator(
            ":text('Giỏ hàng'), :text('Gio hang'), h1:has-text('Cart'), "
            "[class*='cart-item'], [class*='CartItem']"
        ).first

    @property
    def cart_badge(self) -> Locator:
        return self.page.locator(
            "header [class*='badge'], header [class*='cart-count'], "
            "header [class*='CartCount'], a[href*='cart'] span"
        ).first

    @property
    def add_to_cart_toast(self) -> Locator:
        return self.page.locator(
            "[class*='toast']:has-text('giỏ'), [class*='toast']:has-text('cart'), "
            "[role='alert']:has-text('giỏ'), [class*='notification']"
        ).first

    # ── Actions ──────────────────────────────────────────────────────────────

    def navigate_cart(self) -> None:
        self.goto("/cart")

    def select_size_if_shown(self, tc_id: str = "") -> None:
        """Chọn size S trong order modal nếu có."""
        try:
            s_btn = self.size_s_button
            if s_btn.is_visible(timeout=3000):
                s_btn.click()
                self.page.wait_for_timeout(500)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã chọn size S")
                return
            sel = self.size_selector
            if sel.is_visible(timeout=2000):
                sel.select_option(index=1)
                self.page.wait_for_timeout(500)
        except Exception:
            pass

    def click_buy_now(self) -> None:
        self.buy_now_button.click()
        self.page.wait_for_timeout(2000)

    # ── AI generation helpers ─────────────────────────────────────────────────

    def enter_prompt_and_wait_for_generation(
        self, page: Page, prompt: str, tc_id: str = "", timeout_s: int = 60
    ) -> bool:
        """Studio: nhập prompt → click Tạo → poll cho 'Hoàn tất thiết kế' enabled.

        Returns True nếu gen xong trong timeout_s giây.
        """
        ai_input = page.locator(
            "textarea[placeholder*='Mô tả ý tưởng thiết kế'], "
            "textarea[placeholder*='thiết kế'], textarea[placeholder*='Mo ta']"
        ).first
        if not ai_input.is_visible(timeout=8000):
            if tc_id:
                print(f"  [WARN] {tc_id}: Không tìm thấy textarea AI input")
            return False

        ai_input.click()
        ai_input.fill(prompt)
        page.wait_for_timeout(300)

        gen_btn = page.locator(
            "button:has-text('Tạo'), button:has-text('Generate'), "
            "button:has-text('Tạo ảnh'), button:has-text('Tạo thiết kế')"
        ).first
        if gen_btn.is_visible(timeout=2000):
            gen_btn.click()
        else:
            ai_input.press("Enter")

        finish_btn = self.finish_button
        ticks = timeout_s // 5
        for attempt in range(ticks):
            try:
                if finish_btn.is_visible() and finish_btn.get_attribute("disabled") is None:
                    if tc_id:
                        print(f"  [INFO] {tc_id}: AI gen xong sau ~{(attempt + 1) * 5}s")
                    return True
            except Exception:
                pass
            page.wait_for_timeout(5000)
            if tc_id:
                print(f"  [INFO] {tc_id}: Đang đợi AI gen... {(attempt + 1) * 5}s")

        if tc_id:
            print(f"  [WARN] {tc_id}: AI gen timeout sau {timeout_s}s")
        return False
