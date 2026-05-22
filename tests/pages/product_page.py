from __future__ import annotations
"""Product Page Object — /product và /san-pham-ao (listing)."""

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


class ProductListPage(BasePage):
    """Trang danh sách sản phẩm áo — /san-pham (Áo trơn)."""

    LIST_URL = "/san-pham"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    def navigate(self) -> None:
        """Điều hướng qua UI: Home → Menu → Sản phẩm áo → Áo trơn."""
        self.goto("/")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)
        # Mở menu
        try:
            menu_btn = self.page.locator("button:has-text('Menu')").first
            if menu_btn.is_visible(timeout=3000):
                menu_btn.click()
                self.page.wait_for_timeout(800)
        except Exception:
            pass
        # Click "Áo trơn"
        try:
            ao_tron = self.page.locator("a[href*='/san-pham']:has-text('Áo trơn')").first
            if ao_tron.is_visible(timeout=3000):
                ao_tron.click()
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(1500)
                return
        except Exception:
            pass
        # Fallback: navigate trực tiếp
        self.goto(self.LIST_URL)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    def _card_for(self, product_name: str) -> Locator:
        """Locator cho card sản phẩm dựa trên URL slug."""
        import unicodedata

        def remove_accents(s: str) -> str:
            return "".join(c for c in unicodedata.normalize("NFKD", s)
                           if not unicodedata.combining(c))

        slug = remove_accents(product_name).lower().replace(" ", "-").replace("đ", "d")
        return self.page.locator(f"a[href*='/product/{slug}']").first

    def read_listing_sale_price(self, product_name: str) -> int | None:
        """Đọc giá sale (màu hồng/đỏ) của card sản phẩm theo tên. Trả về số nguyên VNĐ."""
        import re
        card = self._card_for(product_name)
        if not card.is_visible(timeout=5000):
            return None
        # Thử đọc từ element có class sale/discount/price-sale trước
        for sel in (
            "span.font-black.tracking-tight, "
            "[class*='sale'] [class*='price'], [class*='price-sale'], "
            "[class*='discount'] [class*='price'], [class*='price--sale']"
        ).split(", "):
            try:
                el = card.locator(sel).first
                if el.is_visible(timeout=1000):
                    raw = el.inner_text()
                    digits = re.sub(r"[^\d]", "", raw)
                    if digits:
                        return int(digits)
            except Exception:
                pass
        # Fallback: lấy giá cuối cùng trong card (thường là giá sale)
        try:
            prices = card.locator("[class*='price'], span:has-text('đ'), span:has-text('₫')").all_inner_texts()
            candidates = []
            for p in prices:
                digits = re.sub(r"[^\d]", "", p)
                if digits and len(digits) >= 5:
                    candidates.append(int(digits))
            if candidates:
                return min(candidates)
        except Exception:
            pass
        return None

    def read_listing_original_price(self, product_name: str) -> int | None:
        """Đọc giá gốc bị gạch ngang của card sản phẩm. Trả về số nguyên VNĐ."""
        import re
        card = self._card_for(product_name)
        if not card.is_visible(timeout=5000):
            return None
        for sel in (
            "span.line-through, s, del, [class*='original'], [class*='old-price'], [class*='price-original']"
        ).split(", "):
            try:
                el = card.locator(sel).first
                if el.is_visible(timeout=1000):
                    raw = el.inner_text()
                    digits = re.sub(r"[^\d]", "", raw)
                    if digits:
                        return int(digits)
            except Exception:
                pass
        return None

    def is_product_card_visible(self, product_name: str) -> bool:
        card = self._card_for(product_name)
        try:
            card.scroll_into_view_if_needed(timeout=5000)
            return card.is_visible(timeout=2000)
        except Exception:
            return False

    def click_product_card(self, product_name: str) -> bool:
        """Click vào card sản phẩm → navigate MH2 Product Detail."""
        card = self._card_for(product_name)
        if not card.is_visible(timeout=5000):
            return False
        card.click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)
        return True

    def click_thiet_ke_on_card(self, product_name: str) -> bool:
        """Click nút 'Thiết kế' / 'Thiết kế ngay' trực tiếp trên card → vào Studio.

        Đây là luồng mới: Áo trơn listing → click Thiết kế trên card → Studio
        (không cần qua trang Product Detail).
        """
        card = self._card_for(product_name)
        if not card.is_visible(timeout=5000):
            return False
        # Tìm nút Thiết kế bên trong card
        design_btn = card.locator(
            "button:has-text('Thiết kế'), a:has-text('Thiết kế'), "
            "button:has-text('Thiet ke'), a:has-text('Thiet ke')"
        ).first
        if design_btn.is_visible(timeout=3000):
            design_btn.click()
            try:
                self.page.wait_for_url("**/studio**", timeout=15000)
            except Exception:
                self.page.wait_for_timeout(3000)
            return "studio" in self.page.url
        # Fallback: hover vào card để nút Thiết kế xuất hiện rồi click
        try:
            card.hover()
            self.page.wait_for_timeout(500)
            if design_btn.is_visible(timeout=2000):
                design_btn.click()
                try:
                    self.page.wait_for_url("**/studio**", timeout=15000)
                except Exception:
                    self.page.wait_for_timeout(3000)
                return "studio" in self.page.url
        except Exception:
            pass
        return False


class ProductDetailPage(BasePage):
    """Trang chi tiết sản phẩm — /product/<slug>.

    Verify: tên, màu default, giá gạch/giá sale, đổi màu, Mua ngay, Thiết kế hình in.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    def navigate(self, slug: str) -> None:
        self.goto(f"/product/{slug}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    # ── Locators ─────────────────────────────────────────────────────────────

    @property
    def product_name_heading(self) -> Locator:
        return self.page.locator("h1, h2").first

    @property
    def sale_price_el(self) -> Locator:
        return self.page.locator(
            ".text-lg.font-black, [class*='price-sale'], [class*='salePrice'], "
            "[class*='sale-price'], [class*='price--sale'], [class*='currentPrice']"
        ).first

    @property
    def original_price_el(self) -> Locator:
        return self.page.locator(
            ".line-through, s, del, [class*='original-price'], [class*='oldPrice'], "
            "[class*='price-origin'], [class*='price--origin']"
        ).first

    @property
    def color_swatches(self) -> Locator:
        return self.page.locator(
            "[class*='color'] button, [class*='swatch'] button, "
            "button[aria-label*='màu'], button[title*='màu'], "
            "[class*='colorSelector'] button"
        )

    @property
    def buy_now_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Mua ngay'), button:has-text('Mua Ngay'), "
            "button:has-text('Buy now'), button:has-text('MUA NGAY')"
        ).first

    @property
    def design_button(self) -> Locator:
        """Nút 'Thiết kế hình in' / 'Thiết kế ngay'."""
        return self.page.locator(
            "button:has-text('Thiết kế hình in'), button:has-text('Thiết kế ngay'), "
            "a:has-text('Thiết kế hình in'), a:has-text('Thiết kế ngay')"
        ).first

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Thêm vào giỏ'), button:has-text('Thêm'), "
            "button:has-text('Add to cart')"
        ).first

    # ── Actions ──────────────────────────────────────────────────────────────

    def read_product_name(self) -> str:
        try:
            return self.product_name_heading.inner_text(timeout=5000).strip()
        except Exception:
            return ""

    def read_sale_price(self) -> int | None:
        import re
        try:
            raw = self.sale_price_el.inner_text(timeout=3000)
            digits = re.sub(r"[^\d]", "", raw)
            return int(digits) if len(digits) >= 3 else None
        except Exception:
            pass
        # Fallback: đọc tất cả giá → lấy min (không phải giá gạch)
        return self._read_min_price_on_page()

    def read_original_price(self) -> int | None:
        import re
        try:
            raw = self.original_price_el.inner_text(timeout=3000)
            digits = re.sub(r"[^\d]", "", raw)
            return int(digits) if len(digits) >= 3 else None
        except Exception:
            return None

    def _read_min_price_on_page(self) -> int | None:
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const matches = [...text.matchAll(/\d[\d,.]*\d[đ₫]/g)];
                return matches.map(m => m[0]);
            }""")
            candidates = []
            for r in (raw or []):
                d = re.sub(r"[^\d]", "", r)
                if d and len(d) >= 3:
                    candidates.append(int(d))
            return min(candidates) if candidates else None
        except Exception:
            return None

    def get_selected_color_label(self) -> str:
        """Đọc tên màu đang được active/selected (aria-pressed, class active…)."""
        try:
            active = self.page.locator(
                "[class*='color'] button[aria-pressed='true'], "
                "[class*='swatch'] button.active, "
                "[class*='colorSelector'] button[class*='active'], "
                "[class*='colorSelector'] button[class*='selected']"
            ).first
            if active.is_visible(timeout=2000):
                label = (
                    active.get_attribute("aria-label")
                    or active.get_attribute("title")
                    or active.inner_text()
                )
                return (label or "").strip()
        except Exception:
            pass
        return ""

    def select_color(self, color_name: str) -> bool:
        """Click swatch theo tên màu. Trả về True nếu thành công."""
        try:
            for sel in [
                f"button[title='{color_name}']",
                f"button[title*='{color_name}']",
                f"button[aria-label*='{color_name}']",
                f"button:has-text('{color_name}')",
            ]:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    btn.click()
                    self.page.wait_for_timeout(800)
                    return True
            # White fallback by style
            if color_name.lower() in ("trắng", "white", "trang"):
                for style_sel in [
                    "button[style*='#fff']", "button[style*='white']",
                    "button[style*='rgb(255, 255, 255)']", "button[data-color='white']",
                    "button[data-color='#ffffff']",
                ]:
                    btn = self.page.locator(style_sel).first
                    if btn.is_visible(timeout=1000):
                        btn.click()
                        self.page.wait_for_timeout(800)
                        return True
        except Exception:
            pass
        return False

    def click_mua_ngay(self) -> bool:
        """Click 'Mua ngay' → chờ popup/modal xuất hiện."""
        try:
            btn = self.buy_now_button
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    def click_thiet_ke_hinh_in(self) -> bool:
        """Click 'Thiết kế hình in' → chờ navigate sang /studio."""
        try:
            btn = self.design_button
            if btn.is_visible(timeout=5000):
                btn.click()
                try:
                    self.page.wait_for_url("**/studio**", timeout=15000)
                except Exception:
                    self.page.wait_for_timeout(3000)
                return "studio" in self.page.url
        except Exception:
            pass
        return False

    def get_available_colors(self) -> list[str]:
        """Lấy danh sách tên màu từ tất cả color swatches hiển thị trên trang.

        Color swatches trên shop là button[title][class*='rounded-full'] (w-7 h-7).
        """
        try:
            labels = self.page.evaluate("""() => {
                const seen = new Set();
                const result = [];
                // Swatch là button tròn nhỏ với title chứa tên màu
                for (const el of document.querySelectorAll('button[title]')) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    // Lọc đúng swatch: nhỏ (≤40px) và tròn (rounded-full)
                    if (rect.width > 40 || rect.height > 40) continue;
                    if (!el.className.includes('rounded-full')) continue;
                    const label = el.getAttribute('title').trim();
                    if (label && !seen.has(label)) {
                        seen.add(label);
                        result.push(label);
                    }
                }
                return result;
            }""")
            return labels or []
        except Exception:
            return []

    def click_add_to_cart(self) -> bool:
        """Click 'Thêm vào giỏ'. Trả về True nếu thành công (toast hoặc dialog)."""
        try:
            btn = self.add_to_cart_button
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False
