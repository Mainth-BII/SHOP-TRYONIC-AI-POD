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
            "[data-size='S'], button:text-is('S'), label:text-is('S')"
        ).first

    @property
    def size_m_button(self) -> Locator:
        return self.page.locator(
            "[data-size='M'], button:text-is('M'), label:text-is('M')"
        ).first

    @property
    def size_l_button(self) -> Locator:
        return self.page.locator(
            "[data-size='L'], button:text-is('L'), label:text-is('L')"
        ).first

    @property
    def quantity_input(self) -> Locator:
        return self.page.locator(
            "input[name='quantity'], input[name*='qty'], input[type='number'][min], "
            "[class*='quantity'] input, [class*='Quantity'] input"
        ).first

    @property
    def quantity_increment_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('+'), [aria-label*='tăng'], [aria-label*='increase'], "
            "[class*='increment'], [class*='plus']"
        ).first

    @property
    def recipient_name_input(self) -> Locator:
        return self.page.locator(
            "input[name='name'], input[name='fullName'], input[name='recipientName'], "
            "input[placeholder*='Họ tên'], input[placeholder*='họ và tên'], "
            "input[placeholder*='Tên người nhận']"
        ).first

    @property
    def recipient_phone_input(self) -> Locator:
        return self.page.locator(
            "input[name='phone'], input[name='phoneNumber'], input[type='tel'], "
            "input[placeholder*='Số điện thoại'], input[placeholder*='số điện thoại']"
        ).first

    @property
    def recipient_address_input(self) -> Locator:
        return self.page.locator(
            "input[name='address'], textarea[name='address'], "
            "input[placeholder*='Địa chỉ'], input[placeholder*='địa chỉ'], "
            "textarea[placeholder*='Địa chỉ']"
        ).first

    @property
    def payment_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Thanh toán'), button:has-text('Xác nhận thanh toán'), "
            "button:has-text('Đặt hàng'), button:has-text('Hoàn tất đặt hàng')"
        ).first

    @property
    def tax_code_input(self) -> Locator:
        """Field CCCD / Mã số thuế (bắt buộc để xuất hóa đơn)."""
        return self.page.locator(
            "input[name*='tax'], input[name*='cccd'], input[name*='mst'], "
            "input[placeholder*='CCCD'], input[placeholder*='MST'], "
            "input[placeholder*='cá nhân'], input[placeholder*='công ty']"
        ).first

    @property
    def qr_code_locator(self) -> Locator:
        return self.page.locator(
            "img[alt*='QR'], img[src*='qr'], img[src*='QR'], "
            "canvas[id*='qr'], [class*='qr-code'], [class*='QrCode'], "
            ":text('Quét mã'), :text('mã QR'), :text('QR Code')"
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
        # contains() để handle emoji prefix (vd: '🛒 Mua ngay')
        return self.page.locator(
            "xpath=//button[contains(normalize-space(), 'Mua ngay')]"
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

    def select_size_l(self, tc_id: str = "") -> bool:
        """Chọn size L. Trả về True nếu thành công."""
        try:
            btn = self.size_l_button
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(500)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã chọn size L")
                return True
        except Exception:
            pass
        if tc_id:
            print(f"  [WARN] {tc_id}: Không tìm thấy nút size L")
        return False

    def set_quantity(self, qty: int, tc_id: str = "") -> bool:
        """Đặt số lượng. Thử input trực tiếp, fallback sang nút +. Trả về True nếu thành công."""
        try:
            inp = self.quantity_input
            if inp.is_visible(timeout=3000):
                inp.triple_click()
                inp.fill(str(qty))
                self.page.wait_for_timeout(300)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã nhập số lượng = {qty}")
                return True
        except Exception:
            pass
        try:
            inc = self.quantity_increment_button
            if inc.is_visible(timeout=2000):
                for _ in range(qty - 1):
                    inc.click()
                    self.page.wait_for_timeout(200)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã tăng số lượng lên {qty} qua nút +")
                return True
        except Exception:
            pass
        if tc_id:
            print(f"  [WARN] {tc_id}: Không tìm thấy ô nhập số lượng")
        return False

    def fill_guest_shipping_info(self, name: str, phone: str, address: str, tc_id: str = "") -> None:
        """Điền thông tin nhận hàng cho guest checkout."""
        for field, locator, label in [
            (name, self.recipient_name_input, "Họ tên"),
            (phone, self.recipient_phone_input, "Số điện thoại"),
            (address, self.recipient_address_input, "Địa chỉ"),
        ]:
            try:
                if locator.is_visible(timeout=5000):
                    locator.click()
                    locator.fill(field)
                    self.page.wait_for_timeout(200)
                    if tc_id:
                        print(f"  [INFO] {tc_id}: Điền {label} = '{field[:20]}...' " if len(field) > 20 else f"  [INFO] {tc_id}: Điền {label}")
                else:
                    if tc_id:
                        print(f"  [WARN] {tc_id}: Không tìm thấy field {label}")
            except Exception as e:
                if tc_id:
                    print(f"  [WARN] {tc_id}: Lỗi điền {label}: {e}")

    def fill_tax_code(self, tax_code: str, tc_id: str = "") -> bool:
        """Nhập CCCD / Mã số thuế. Bắt buộc để enable nút Thanh toán."""
        try:
            inp = self.tax_code_input
            if inp.is_visible(timeout=5000):
                inp.click()
                inp.fill(tax_code)
                self.page.wait_for_timeout(300)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đủ Mã số thuế = '{tax_code}'")
                return True
        except Exception:
            pass
        if tc_id:
            print(f"  [WARN] {tc_id}: Không tìm thấy field Mã số thuế")
        return False

    def is_qr_visible(self, timeout: int = 15000) -> bool:
        """Kiểm tra màn hình QR code xuất hiện."""
        try:
            return self.qr_code_locator.is_visible(timeout=timeout)
        except Exception:
            return False

    def select_size_m(self, tc_id: str = "") -> bool:
        """Chọn size M. Trả về True nếu thành công."""
        try:
            btn = self.size_m_button
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(500)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã chọn size M")
                return True
        except Exception:
            pass
        if tc_id:
            print(f"  [WARN] {tc_id}: Không tìm thấy nút size M")
        return False

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

    # ── Order data capture ────────────────────────────────────────────────────

    def read_price_from_page(self) -> str | None:
        """Regex \\d+[,.]\\d+\\s*₫ trên document.body.innerText. Trả về match đầu tiên."""
        try:
            return self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const match = text.match(/\d+[,.]\d+\s*₫/);
                return match ? match[0] : null;
            }""")
        except Exception:
            return None

    def read_address_from_checkout(self) -> str | None:
        """Đọc input[name*='address'].value hoặc text từ [class*='address'] section."""
        try:
            return self.page.evaluate("""() => {
                const inp = document.querySelector(
                    'input[name*="address"], textarea[name*="address"]'
                );
                if (inp && inp.value) return inp.value;
                const section = document.querySelector('[class*="address"]');
                return section ? section.innerText.trim() : null;
            }""")
        except Exception:
            return None

    def read_order_code(self) -> str | None:
        """URL param ?orderCode=POD-... fallback regex POD-\\d{8}-\\d+ trong page text."""
        try:
            return self.page.evaluate(r"""() => {
                const params = new URLSearchParams(window.location.search);
                const fromUrl = params.get('orderCode');
                if (fromUrl && fromUrl.startsWith('POD-')) return fromUrl;
                const text = document.body.innerText || '';
                const match = text.match(/POD-\d{8}-\d+/);
                return match ? match[0] : null;
            }""")
        except Exception:
            return None

    def read_product_type(self) -> str | None:
        """Heading h1/h2/h3 chứa keyword áo|shirt|thun (case-insensitive)."""
        try:
            return self.page.evaluate(r"""() => {
                const headings = document.querySelectorAll('h1, h2, h3');
                for (const h of headings) {
                    if (/áo|shirt|thun/i.test(h.innerText)) return h.innerText.trim();
                }
                return null;
            }""")
        except Exception:
            return None

    def verify_order_data(self, order_data: dict, tc_id: str) -> None:
        """Verify từng field trong order_data trên trang chi tiết đơn hàng."""
        import re
        page_text = self.page.evaluate("() => document.body.innerText || ''")

        # order_code: exact string — FAIL nếu sai
        order_code = order_data.get("order_code")
        if order_code:
            assert order_code in page_text, \
                f"LỖI verify {tc_id}: Mã đơn '{order_code}' không tìm thấy trong trang chi tiết"

        # size: exact string — FAIL + format warning nếu sai
        size = order_data.get("size")
        if size:
            if size not in page_text:
                size_variants = [f"Size {size}", f"size {size}", f"SIZE {size}"]
                found_variant = next((v for v in size_variants if v in page_text), None)
                if found_variant:
                    print(f"  ⚠ Format size không nhất quán: captured `{size}`, "
                          f"page hiện `{found_variant}` — cần đồng nhất")
                assert False, \
                    f"LỖI verify {tc_id}: Size '{size}' không tìm thấy trong trang chi tiết"

        # unit_price: digits-only compare — WARN nếu sai
        unit_price = order_data.get("unit_price")
        if unit_price:
            digits_captured = re.sub(r"[^\d]", "", unit_price)
            page_digits = re.sub(r"[^\d]", "", page_text)
            if digits_captured and digits_captured not in page_digits:
                print(f"  [WARN] verify {tc_id}: unit_price mismatch — captured '{unit_price}'")

        # total_price: digits-only compare — WARN nếu sai
        total_price = order_data.get("total_price")
        if total_price:
            digits_captured = re.sub(r"[^\d]", "", total_price)
            page_digits = re.sub(r"[^\d]", "", page_text)
            if digits_captured and digits_captured not in page_digits:
                print(f"  [WARN] verify {tc_id}: total_price mismatch — captured '{total_price}'")

        # address, artwork_front_src, artwork_back_src, product_type: INFO log only
        for field in ("address", "artwork_front_src", "artwork_back_src", "product_type"):
            val = order_data.get(field)
            if val:
                print(f"  [INFO] verify {tc_id}: {field} = '{str(val)[:80]}'")

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
