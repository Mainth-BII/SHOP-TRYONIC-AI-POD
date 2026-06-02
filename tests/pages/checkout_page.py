from __future__ import annotations
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
        """Match giá VN: 189.000đ, 732.000đ, 810.560₫, ... Trả về match đầu tiên."""
        try:
            return self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const match = text.match(/\d[\d,.]*\d[đ₫]/);
                return match ? match[0] : null;
            }""")
        except Exception:
            return None

    def read_address_from_checkout(self) -> str | None:
        """Đọc địa chỉ nhận hàng — chờ spinner biến mất trước khi đọc."""
        try:
            # Chờ "Đang tải địa chỉ" biến mất (tối đa 8s)
            try:
                self.page.wait_for_function(
                    "() => !document.body.innerText.includes('Đang tải địa chỉ')",
                    timeout=8000
                )
            except Exception:
                pass
            return self.page.evaluate("""() => {
                const skipLine = (l) =>
                    !l || l.length < 3
                    || l.includes('_')                      // snake_case codes
                    || /^[a-zA-Z]+$/.test(l)               // pure ASCII word (codes)
                    || l === 'Địa chỉ nhận hàng'
                    || l.includes('Đang tải');

                // 1. Input/textarea với value trông như địa chỉ thực
                const inps = document.querySelectorAll(
                    'input[name*="address"], textarea[name*="address"]'
                );
                for (const inp of inps) {
                    const v = (inp.value || '').trim();
                    if (v.length > 10 && v.includes(' ') && !v.includes('_')) return v;
                }
                // 2. Section "Địa chỉ nhận hàng": lọc dòng code, giữ text VN thực
                const all = Array.from(document.querySelectorAll('*'));
                for (const el of all) {
                    const t = (el.innerText || '').trim();
                    if (t === 'Địa chỉ nhận hàng' || t.startsWith('Địa chỉ nhận hàng')) {
                        const card = el.closest('div, section, article');
                        if (card) {
                            const lines = card.innerText.split('\\n')
                                .map(l => l.trim())
                                .filter(l => !skipLine(l));
                            const content = lines.join(', ').trim();
                            if (content.length > 5) return content.slice(0, 200);
                        }
                    }
                }
                // 3. Fallback: [class*="address"] section
                const section = document.querySelector('[class*="address"], [class*="Address"]');
                if (section) {
                    const lines = section.innerText.split('\\n')
                        .map(l => l.trim()).filter(l => !skipLine(l));
                    const content = lines.join(', ').trim();
                    if (content) return content.slice(0, 200);
                }
                return null;
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

    def select_color_on_order(self, color_name: str) -> bool:
        """Chọn màu áo trên order screen. Trả về True nếu thành công."""
        try:
            btn = self.page.locator(f"button:has-text('{color_name}')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                self.page.wait_for_timeout(500)
                return True
            btn = self.page.locator(
                f"button[aria-label*='{color_name}'], button[title*='{color_name}'], "
                f"[data-color*='{color_name}']"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                self.page.wait_for_timeout(500)
                return True
            if color_name.lower() in ("trắng", "trang", "white"):
                btn = self.page.locator(
                    "button[style*='#fff'], button[style*='white'], "
                    "[data-color='white'], [data-color='#ffffff'], "
                    "button[style*='rgb(255, 255, 255)']"
                ).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(500)
                    return True
        except Exception:
            pass
        return False

    def select_size_by_name(self, size_name: str) -> bool:
        """Chọn size bất kỳ theo tên trên order screen. Trả về True nếu thành công."""
        try:
            btn = self.page.locator(f"button:text-is('{size_name}')").first
            if btn.is_visible(timeout=3000):
                btn.click()
                self.page.wait_for_timeout(500)
                return True
            btn = self.page.locator(
                f"[data-size='{size_name}'], label:text-is('{size_name}')"
            ).first
            if btn.is_visible(timeout=2000):
                btn.click()
                self.page.wait_for_timeout(500)
                return True
        except Exception:
            pass
        return False

    def read_unit_price_as_int(self) -> int | None:
        """Đọc unit price trên order screen, parse ra số nguyên (VNĐ)."""
        raw = self.read_price_from_page()
        if not raw:
            return None
        import re
        digits = re.sub(r"[^\d]", "", raw)
        return int(digits) if digits else None

    # ── Buy-now modal helpers ──────────────────────────────────────────────────

    # Selector thực tế của buy-now popup (div max-w-md shadow, không có role=dialog)
    _BUYNOW_MODAL_SEL = "[class*='max-w-md'][class*='shadow']"

    def is_buynow_modal_visible(self, timeout: int = 5000) -> bool:
        """Kiểm tra popup 'Mua ngay' đang hiển thị."""
        try:
            modal = self.page.locator(self._BUYNOW_MODAL_SEL).first
            return modal.is_visible(timeout=timeout)
        except Exception:
            return False

    def read_buynow_modal_product_name(self) -> str:
        """Đọc tên sản phẩm trong popup Mua ngay."""
        try:
            return self.page.evaluate(f"""() => {{
                const dialog = document.querySelector("{self._BUYNOW_MODAL_SEL}");
                if (!dialog) return '';
                const h = dialog.querySelector('h1, h2, h3, [class*="name"], [class*="title"]');
                return h ? h.innerText.trim() : '';
            }}""") or ""
        except Exception:
            return ""

    def read_buynow_modal_price(self) -> int | None:
        """Đọc đơn giá trong popup Mua ngay."""
        import re
        try:
            raw = self.page.evaluate(f"""() => {{
                const dialog = document.querySelector("{self._BUYNOW_MODAL_SEL}");
                if (!dialog) return null;
                const els = dialog.querySelectorAll("[class*='price'], [class*='Price'], span");
                for (const el of els) {{
                    const t = el.innerText || '';
                    if (/\\d[\\d,.]*\\d[đ₫]/.test(t)) return t;
                }}
                return null;
            }}""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def read_buynow_button_price(self) -> int | None:
        """Đọc giá trên button 'Thanh toán ngay' trong popup."""
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    const t = b.innerText || '';
                    if (t.includes('Thanh toán') && /\d[\d,.]*\d[đ₫]/.test(t))
                        return t;
                }
                return null;
            }""")
            if raw:
                m = __import__('re').search(r'\d[\d,.]*\d', raw)
                if m:
                    digits = re.sub(r"[^\d]", "", m.group(0))
                    return int(digits) if digits else None
        except Exception:
            pass
        return None

    def click_thanh_toan_ngay(self) -> bool:
        """Click 'Thanh toán ngay' trong popup Mua ngay."""
        try:
            btn = self.page.locator(
                "button:has-text('Thanh toán ngay'), button:has-text('Thanh Toan Ngay')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    # ── Checkout screen price breakdown ───────────────────────────────────────

    def _read_price_label(self, label: str) -> int | None:
        """Đọc giá trên dòng có label cho trước (regex: label → số tiền).
        Chỉ match số có 4+ chữ số hoặc định dạng thousands (x,xxx / x.xxx)
        để tránh match số ngắn trong mã khuyến mãi (vd: GIAM20 → "20")."""
        import re
        try:
            raw = self.page.evaluate(f"""() => {{
                const text = document.body.innerText || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                // Regex chỉ match số thousands-formatted hoặc 4+ chữ số
                const priceRe = /(-?\\d{{1,3}}(?:[,.]\\d{{3}})+|-?\\d{{4,}})\\s*[đ₫]?/;
                for (let i = 0; i < lines.length; i++) {{
                    if (lines[i].includes('{label}')) {{
                        let m = lines[i].match(priceRe);
                        if (m) return m[1];
                        for (let j = 1; j <= 2; j++) {{
                            if (i + j < lines.length) {{
                                let m2 = lines[i+j].match(priceRe);
                                if (m2) return m2[1];
                            }}
                        }}
                    }}
                }}
                return null;
            }}""")
            if raw:
                digits = re.sub(r"[^\d]", "", str(raw))
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def read_checkout_subtotal(self) -> int | None:
        """Đọc 'Tổng tiền' trên checkout."""
        for label in ("Tổng tiền", "Tổng cộng", "Subtotal"):
            v = self._read_price_label(label)
            if v:
                return v
        return None

    def read_checkout_vat(self) -> int | None:
        """Đọc 'Thuế VAT' / 'VAT (8%)' trên checkout."""
        for label in ("Thuế VAT", "VAT", "Thuế"):
            v = self._read_price_label(label)
            if v:
                return v
        return None

    def read_checkout_shipping(self) -> int | None:
        """Đọc 'Phí giao hàng' trên checkout."""
        for label in ("Phí giao hàng", "Giao hàng", "Shipping"):
            v = self._read_price_label(label)
            if v:
                return v
        return None

    def read_checkout_discount(self) -> int | None:
        """Đọc số tiền giảm giá trên checkout."""
        for label in ("Khuyến mãi", "Giảm giá", "Discount"):
            v = self._read_price_label(label)
            if v:
                return v
        return None

    def read_checkout_total(self) -> int | None:
        """Đọc 'Tổng thanh toán' trên checkout — lấy số lớn nhất trên trang."""
        import re
        for label in ("Tổng thanh toán", "Tổng TT", "Tổng"):
            v = self._read_price_label(label)
            if v:
                return v
        # Fallback: lấy số tiền lớn nhất trên trang
        try:
            raw_list = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                return [...text.matchAll(/\d[\d,.]*\d[đ₫]/g)].map(m => m[0]);
            }""")
            candidates = []
            for r in (raw_list or []):
                d = re.sub(r"[^\d]", "", r)
                if d:
                    candidates.append(int(d))
            return max(candidates) if candidates else None
        except Exception:
            return None

    def read_payment_button_price(self) -> int | None:
        """Đọc giá trên button 'Thanh toán'."""
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    const t = b.innerText || '';
                    if ((t.includes('Thanh toán') || t.includes('Đặt hàng'))
                        && /\d[\d,.]*\d[đ₫]/.test(t))
                        return t;
                }
                return null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", __import__('re').search(r'\d[\d,.]*\d', raw).group(0))
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def apply_discount_code(self, code: str) -> bool:
        """Nhập mã giảm giá và apply. Trả về True nếu thành công."""
        try:
            inp = self.page.locator(
                "input[placeholder*='mã'], input[placeholder*='khuyến'], "
                "input[placeholder*='discount'], input[name*='coupon'], input[name*='voucher']"
            ).first
            if inp.is_visible(timeout=3000):
                inp.click()
                inp.fill(code)
                self.page.wait_for_timeout(300)
                apply_btn = self.page.locator(
                    "button:has-text('Áp dụng'), button:has-text('Apply'), "
                    "button:has-text('Dùng'), button[type='submit']:near(input)"
                ).first
                if apply_btn.is_visible(timeout=2000):
                    apply_btn.click()
                    self.page.wait_for_timeout(1500)
                    return True
                inp.press("Enter")
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    def click_checkout_payment(self) -> bool:
        """Click nút 'Thanh toán' / 'Đặt hàng' cuối checkout."""
        try:
            btn = self.page.locator(
                "button:has-text('Thanh toán'), button:has-text('Đặt hàng'), "
                "button:has-text('Xác nhận thanh toán'), button:has-text('Hoàn tất')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(3000)
                return True
        except Exception:
            pass
        return False

    # ── QR screen helpers ─────────────────────────────────────────────────────

    def read_qr_amount(self) -> int | None:
        """Đọc số tiền trên màn hình QR (Số tiền / Tổng thanh toán)."""
        import re
        for label in ("Số tiền", "Tổng thanh toán", "Thanh toán"):
            v = self._read_price_label(label)
            if v:
                return v
        # Fallback: số tiền trong text lưu ý
        try:
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const m = text.match(/thanh to[áa]n\s+(\d[\d,.]*\d)[đ₫₫]/i);
                return m ? m[1] : null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def read_qr_note_amount(self) -> int | None:
        """Đọc số tiền trong câu lưu ý 'Nhập chính xác số tiền X'.

        UI mẫu: 'Lưu ý : Nhập chính xác số tiền 183,296, nội dung ...'
        Số tiền không có ký hiệu đ ngay sau — chỉ có dấu phẩy hoặc khoảng trắng.
        """
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const m = text.match(/chính xác[^\d]*(\d[\d,.]*\d)/i)
                        || text.match(/Lưu ý[^:]*:[^\d]*(\d[\d,.]*\d)/i)
                        || text.match(/(\d[\d,.]*\d)\s*(?:vnd|đ|₫)[^\d]*nội dung/i);
                return m ? m[1] : null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def click_cancel_qr(self) -> bool:
        """Click 'Huỷ' trên màn hình QR. UI dùng chữ 'Huỷ' (dấu ỷ)."""
        try:
            # Text thật trên UI: 'Huỷ' (ỷ) — thử cả 2 variant
            btn = self.page.locator(
                "button:has-text('Huỷ'), button:has-text('Hủy'), "
                "button:has-text('Huy'), button:has-text('Cancel')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(1500)
                return True
            # Fallback: JS click bất kỳ button nào chứa 'hu' (case-insensitive)
            clicked = self.page.evaluate(r"""() => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    const t = (b.innerText || '').trim().toLowerCase();
                    if (t === 'huỷ' || t === 'hủy' || t === 'huy' || t === 'cancel') {
                        b.click();
                        return true;
                    }
                }
                return false;
            }""")
            if clicked:
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    def confirm_cancel_dialog(self) -> bool:
        """Xác nhận hộp thoại confirm hủy — handle cả browser dialog và custom modal."""
        # 1. Register handler cho browser native dialog (window.confirm)
        try:
            self.page.on("dialog", lambda d: d.accept())
        except Exception:
            pass
        # 2. Custom modal confirm button
        try:
            confirm_btn = self.page.locator(
                "button:has-text('Xác nhận'), button:has-text('Đồng ý'), "
                "button:has-text('OK'), button:has-text('Có'), "
                "button:has-text('Yes'), button:has-text('Confirm')"
            ).first
            if confirm_btn.is_visible(timeout=5000):
                confirm_btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        self.page.wait_for_timeout(2000)
        return False

    def click_view_order(self) -> bool:
        """Click 'Xem đơn hàng' sau khi hủy QR."""
        try:
            btn = self.page.locator(
                "button:has-text('Xem đơn hàng'), a:has-text('Xem đơn hàng'), "
                "button:has-text('Xem đơn'), a:has-text('Xem đơn')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    # ── Order page helpers (MH7) ──────────────────────────────────────────────

    def read_order_banner_amount(self) -> int | None:
        """Đọc số tiền trong banner 'Vui lòng thanh toán Xđ để đơn hàng được xử lý'."""
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const m = text.match(/thanh to[áa]n\s+(\d[\d,.]*\d)[đ₫]/i);
                return m ? m[0] : null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", __import__('re').search(r'\d[\d,.]*', raw).group(0))
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def click_my_orders(self) -> bool:
        """Click 'Đơn hàng của tôi' → navigate sang trang danh sách đơn hàng."""
        try:
            btn = self.page.locator(
                "button:has-text('Đơn hàng của tôi'), a:has-text('Đơn hàng của tôi'), "
                "button:has-text('Đơn hàng'), a:has-text('Đơn hàng')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    # ── My Orders page helpers (MH8) ─────────────────────────────────────────

    def read_first_order_price(self) -> int | None:
        """Đọc giá 'Tổng: Xđ' của đơn hàng đầu tiên trong danh sách."""
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const lines = text.split('\n');
                for (const line of lines) {
                    const trimmed = line.trim();
                    // Match "Tổng: 183.296đ" hoặc "Tổng 183,296đ"
                    if (/^Tổng[:\s]/i.test(trimmed) && !/Tổng (tiền|giá|cộng|thanh)/i.test(trimmed)) {
                        const m = trimmed.match(/[\d,.]+[đ₫]/);
                        return m ? m[0] : null;
                    }
                }
                return null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def click_order_chi_tiet(self, index: int = 0) -> bool:
        """Click nút 'Chi tiết' của đơn hàng (theo index, default = đầu tiên).
        UI: Nút 'Chi tiết' mở popup/modal chi tiết đơn hàng."""
        try:
            btns = self.page.locator(
                "button:has-text('Chi tiết'), a:has-text('Chi tiết'), "
                "button:has-text('Xem chi tiết'), a:has-text('Xem chi tiết')"
            )
            btn = btns.nth(index)
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    def read_order_detail_total(self) -> int | None:
        """Đọc 'Tổng cộng: Xđ' trong popup chi tiết đơn hàng (MH9).
        Cần scroll xuống trong popup để thấy phần THANH TOÁN."""
        import re
        try:
            # Scroll popup modal xuống cuối
            self._scroll_order_detail_popup()

            # Đọc "Tổng cộng: 183.296đ"
            raw = self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const lines = text.split('\n');
                for (const line of lines) {
                    if (/Tổng cộng/i.test(line)) {
                        const m = line.match(/[\d,.]+[đ₫]/);
                        return m ? m[0] : null;
                    }
                }
                return null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def _scroll_order_detail_popup(self) -> None:
        """Scroll popup chi tiết đơn hàng xuống cuối để hiển thị phần THANH TOÁN."""
        self.page.evaluate(r"""() => {
            const modal = document.querySelector(
                '[class*="modal"], [class*="dialog"], [class*="drawer"], '
                + '[class*="popup"], [role="dialog"]'
            );
            if (modal) {
                const scrollable = modal.querySelector('[class*="body"], [class*="content"]')
                    || modal;
                scrollable.scrollTop = scrollable.scrollHeight;
            }
        }""")
        self.page.wait_for_timeout(1000)

    def read_order_detail_prices(self) -> dict:
        """Đọc toàn bộ giá trong phần THANH TOÁN của popup chi tiết đơn hàng.

        Returns dict:
            tong_gia: int       — Tổng giá (189.000đ)
            phi_van_chuyen: int — Phí vận chuyển (20.000đ)
            giam_gia: int       — Giảm giá GIAM20 (37.800đ, dương)
            thue_vat: int       — Thuế VAT 8% (12.096đ)
            tong_cong: int      — Tổng cộng (183.296đ)
        """
        import re
        self._scroll_order_detail_popup()

        raw = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            const result = {};
            const patterns = [
                { key: 'tong_gia',        regex: /Tổng giá|Tiền hàng|Tiền sản phẩm/i },
                { key: 'phi_van_chuyen',  regex: /Phí vận chuyển|Phí giao hàng/i },
                { key: 'giam_gia',        regex: /Giảm giá|Khuyến mãi|Discount/i },
                { key: 'thue_vat',        regex: /Thuế VAT|VAT/i },
                { key: 'tong_cong',       regex: /Tổng cộng|Tổng thanh toán|Tổng tiền/i },
            ];
            
            for (const line of lines) {
                for (const p of patterns) {
                    if (p.regex.test(line)) {
                        // Thử tìm số tiền có dấu '-' phía trước (đặc trưng của giảm giá)
                        let m = line.match(/(-?\d[\d,.]*\d)\s*[đ₫VND]*/i);
                        
                        // Nếu là giam_gia, cố gắng tránh lấy số trong mã code (ví dụ 20 trong GIAM20)
                        if (p.key === 'giam_gia') {
                            const minusMatch = line.match(/(-\d[\d,.]*\d)\s*[đ₫VND]*/i);
                            if (minusMatch) {
                                result[p.key] = minusMatch[1];
                                continue;
                            }
                            // Nếu không có dấu trừ, tìm số có >=3 chữ số (tránh lấy 20 từ GIAM20)
                            const allNums = line.match(/\d[\d,.]*\d/g) || [];
                            const filtered = allNums.filter(n => n.replace(/[^\d]/g, '').length > 2);
                            if (filtered.length > 0) {
                                result[p.key] = filtered[0];
                                continue;
                            }
                            // Thử tìm trong các dòng tiếp theo (label và value có thể tách dòng)
                            const idx = lines.indexOf(line);
                            for (let j = 1; j <= 2; j++) {
                                if (idx + j < lines.length) {
                                    const nextMatch = lines[idx + j].match(/(-?\d[\d,.]*\d)\s*[đ₫VND]*/i);
                                    if (nextMatch && nextMatch[1].replace(/[^\d]/g, '').length > 2) {
                                        result[p.key] = nextMatch[1];
                                        break;
                                    }
                                }
                            }
                            continue;  // tránh fall-through vào generic match bên dưới
                        }

                        if (m) {
                            result[p.key] = m[1];
                        } else {
                            // Thử tìm trong các dòng tiếp theo (nếu label và value bị tách dòng)
                            const idx = lines.indexOf(line);
                            for (let j = 1; j <= 2; j++) {
                                if (idx + j < lines.length) {
                                    const nextMatch = lines[idx + j].match(/(-?\d[\d,.]*\d)\s*[đ₫VND]*/i);
                                    if (nextMatch) {
                                        result[p.key] = nextMatch[1];
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            return result;
        }""")

        prices = {}
        if raw:
            for key, val in raw.items():
                if val:
                    digits = re.sub(r"[^\d]", "", val)
                    prices[key] = int(digits) if digits else None
                else:
                    prices[key] = None
        return prices

    def read_order_detail_info(self) -> dict:
        """Đọc thông tin sản phẩm + giao hàng từ popup chi tiết đơn hàng.

        Returns dict:
            product_name: str   — Tên sản phẩm
            color: str          — Màu áo
            size: str           — Size (XS/S/M/L...)
            qty: int            — Số lượng
            receiver_name: str  — Tên người nhận
            phone: str          — SĐT
            address: str        — Địa chỉ
        """
        # Scroll lên đầu popup trước
        self.page.evaluate(r"""() => {
            const modal = document.querySelector(
                '[class*="modal"], [class*="dialog"], [class*="drawer"], '
                + '[class*="popup"], [role="dialog"]'
            );
            if (modal) {
                const scrollable = modal.querySelector('[class*="body"], [class*="content"]')
                    || modal;
                scrollable.scrollTop = 0;
            }
        }""")
        self.page.wait_for_timeout(500)

        raw = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const result = {};

            // Product name — tìm dòng chứa "Áo Phông" hoặc tên SP
            const nameMatch = text.match(/(Áo [^\n]+)/i);
            result.product_name = nameMatch ? nameMatch[1].trim() : '';

            // Color — tìm dòng ngay sau tên SP (thường là "Trắng", "Đen"...)
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            for (let i = 0; i < lines.length; i++) {
                if (/Áo Phông/i.test(lines[i])) {
                    // Dòng tiếp theo thường là màu
                    if (i + 1 < lines.length) {
                        const nextLine = lines[i + 1];
                        if (/^(Trắng|Đen|Xanh|Đỏ|Hồng|Vàng|Xám|Nâu|Cam|Tím)/i.test(nextLine)) {
                            result.color = nextLine;
                        }
                    }
                }
            }

            // Size + Qty — tìm line-by-line để tránh false cross-line match
            // Hỗ trợ size số (100-199 cho ET002 trẻ em) và size chữ (XS/S/M/L/XL/2XL)
            let sizeFound = null, qtyFound = null;
            for (let i = 0; i < lines.length; i++) {
                const ln = lines[i];
                const nextLn = i + 1 < lines.length ? lines[i + 1] : '';
                // Pattern 1: "(Màu, Size) × N" trên 1 dòng
                const m1 = ln.match(/\((?:[^,)]+),\s*([A-Z0-9]+)\)\s*[×x]\s*(\d+)/i);
                if (m1) { sizeFound = m1[1]; qtyFound = parseInt(m1[2]); break; }
                // Pattern 2a: "NNN × N" trên 1 dòng (size 3 chữ số: ET002 100-199)
                const m2a = ln.match(/\b(\d{3})\s*[×x]\s*(\d+)/);
                if (m2a) { sizeFound = m2a[1]; qtyFound = parseInt(m2a[2]); break; }
                // Pattern 2b: "NNN" dòng trên, "× N" dòng dưới
                if (/^\d{3}$/.test(ln)) {
                    const qm2 = nextLn.match(/^[×x]\s*(\d+)/);
                    if (qm2) { sizeFound = ln; qtyFound = parseInt(qm2[1]); break; }
                }
                // Pattern 3: size chữ chuẩn — phải đứng ngay trước "× N" (cùng dòng hoặc dòng sau)
                // Dùng word-boundary chặt: không match khi là tiền tố của từ (Số, Sản, shopping...)
                const m3 = ln.match(/(?:^|[\s,:])(2XL|3XL|4XL|XL|XS|[SML])$/i);
                if (m3) {
                    const qm = nextLn.match(/^[×x]\s*(\d+)/);
                    if (qm) { sizeFound = m3[1]; qtyFound = parseInt(qm[1]); break; }
                }
                // Pattern 3b: "SIZE × N" trên cùng 1 dòng (size chữ kế tiếp ngay ×)
                const m3b = ln.match(/(?:^|[\s,:])(2XL|3XL|4XL|XL|XS|[SML])\s*[×x]\s*(\d+)/i);
                if (m3b) { sizeFound = m3b[1]; qtyFound = parseInt(m3b[2]); break; }
            }
            if (sizeFound) { result.size = sizeFound; result.qty = qtyFound; }

            // THÔNG TIN GIAO HÀNG section
            const shipSection = text.split(/THÔNG TIN GIAO HÀNG/i)[1] || '';
            const shipLines = shipSection.split('\n').map(l => l.trim()).filter(Boolean);

            // Tên người nhận — dòng đầu tiên sau header
            for (const line of shipLines) {
                if (line.length > 2 && !/^[0-9]/.test(line) && !/Giao/.test(line)
                    && !/Phường|Quận|Thành|^Q\./.test(line)) {
                    result.receiver_name = line;
                    break;
                }
            }

            // SĐT — pattern 09/08/07/03/05...
            const phoneMatch = shipSection.match(/0\d{9,10}/);
            result.phone = phoneMatch ? phoneMatch[0] : '';

            // Địa chỉ — dòng dài nhất chứa "Phường" hoặc "Quận" hoặc ","
            for (const line of shipLines) {
                if (/Phường|Quận|phường|quận|,/.test(line) && line.length > 10) {
                    result.address = line;
                    break;
                }
            }

            return result;
        }""")

        return raw or {}


    def read_order_detail_product_image(self) -> dict:
        """Đọc thông tin hình ảnh sản phẩm trong popup chi tiết đơn hàng.

        Returns dict:
            src: str    — URL ảnh sản phẩm
            alt: str    — Alt text
            color_in_url: bool — URL chứa tên màu (trang/den/xanh...)
        """
        # Scroll lên đầu popup
        self.page.evaluate(r"""() => {
            const modal = document.querySelector(
                '[class*="modal"], [class*="dialog"], [class*="drawer"], '
                + '[class*="popup"], [role="dialog"]'
            );
            if (modal) {
                const scrollable = modal.querySelector('[class*="body"], [class*="content"]')
                    || modal;
                scrollable.scrollTop = 0;
            }
        }""")
        self.page.wait_for_timeout(500)

        return self.page.evaluate(r"""() => {
            // Tìm section SẢN PHẨM trong popup
            const modal = document.querySelector(
                '[class*="modal"], [class*="dialog"], [class*="drawer"], '
                + '[class*="popup"], [role="dialog"]'
            ) || document;

            // Tìm ảnh gần "Áo Phông" hoặc ảnh đầu tiên trong popup
            const imgs = modal.querySelectorAll('img');
            let productImg = null;

            for (const img of imgs) {
                const src = img.src || '';
                const alt = img.alt || '';
                // Bỏ qua icon/avatar nhỏ
                if (img.naturalWidth < 30 || img.naturalHeight < 30) continue;
                if (/logo|icon|avatar/i.test(src)) continue;
                // Ưu tiên ảnh chứa "product" hoặc gần text "Áo"
                if (/product|ao|shirt|phong/i.test(src) || /product|ao|shirt|phong/i.test(alt)) {
                    productImg = img;
                    break;
                }
                // Lấy ảnh đầu tiên có kích thước hợp lý
                if (!productImg && (img.width >= 40 || img.height >= 40)) {
                    productImg = img;
                }
            }

            if (!productImg) return { src: '', alt: '', found: false };

            return {
                src: productImg.src || '',
                alt: productImg.alt || '',
                width: productImg.width,
                height: productImg.height,
                found: true
            };
        }""") or {}



    # ── Cart page helpers (MH10) ──────────────────────────────────────────────

    def navigate_cart(self) -> None:
        self.goto("/cart")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    def read_cart_item_price(self) -> int | None:
        """Đọc giá item đầu tiên trong giỏ hàng."""
        import re
        try:
            raw = self.page.evaluate(r"""() => {
                const items = document.querySelectorAll(
                    "[class*='cart-item'], [class*='cartItem'], [class*='cart'] li"
                );
                const first = items[0];
                if (!first) return null;
                const m = first.innerText.match(/\d[\d,.]*\d[đ₫]/);
                return m ? m[0] : null;
            }""")
            if raw:
                digits = re.sub(r"[^\d]", "", raw)
                return int(digits) if digits else None
        except Exception:
            pass
        return None

    def read_cart_total(self) -> int | None:
        """Đọc tổng giỏ hàng."""
        for label in ("Tổng tiền", "Tổng cộng", "Total"):
            v = self._read_price_label(label)
            if v:
                return v
        return None

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

    # ── Cart / Studio popup helpers ────────────────────────────────────────────

    def is_size_in_qty_section(self, size: str) -> bool:
        """Kiểm tra size đã xuất hiện trong mục qty của modal buy-now."""
        modal = self.page.locator(self._BUYNOW_MODAL_SEL).first
        return modal.locator(f"text={size}").first.is_visible(timeout=3000)

    def select_all_sizes_in_modal(self, sizes: list, qty: int = 1) -> None:
        """Chọn từng size trong popup buy-now và đặt quantity."""
        modal = self.page.locator(self._BUYNOW_MODAL_SEL).first
        for size in sizes:
            btn = modal.locator(f"button:has-text('{size}')").first
            if btn.is_visible(timeout=3000):
                btn.click()
                self.page.wait_for_timeout(300)
            qty_input = modal.locator("input[type='number']").last
            if qty_input.is_visible(timeout=2000):
                qty_input.fill(str(qty))
                self.page.wait_for_timeout(200)

    def click_them_vao_gio(self) -> bool:
        """Nhấn nút 'Thêm vào giỏ' trong popup buy-now / cart panel. Trả về True nếu click được."""
        try:
            btn = self.page.locator(
                "button:has-text('Thêm vào giỏ'), button:has-text('Add to Cart')"
            ).first
            if btn.is_visible(timeout=5000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    # Panel giỏ hàng (CartDrawer): div.max-w-md.shadow-2xl chứa h2 "Giỏ hàng (N)"
    _CART_PANEL_SEL = "[class*='max-w-md'][class*='shadow']"
    # Nút giỏ hàng trên header: <button> chứa span material-symbol 'shopping_cart'
    # (kèm tooltip 'Giỏ hàng'). Không có data-testid/aria-label nên dò theo text.
    _CART_BTN_SEL = (
        "header button:has-text('shopping_cart'), "
        "header button:has-text('Giỏ hàng'), "
        "button:has-text('shopping_cart')"
    )

    def _cart_panel_open(self, timeout: int = 1_500) -> bool:
        try:
            if self.page.locator(self._CART_PANEL_SEL).first.is_visible(timeout=timeout):
                return True
        except Exception:
            pass
        try:
            return self.page.locator("h2:has-text('Giỏ hàng')").first.is_visible(timeout=600)
        except Exception:
            return False

    def open_cart_panel(self) -> bool:
        """Mở panel giỏ hàng robust (headed + CI headless). Trả về True nếu mở.

        Nút giỏ hàng dùng onClick (không phải hover) nên click là đủ; nhưng
        trên CI chậm cần: chờ header, scroll vào tầm nhìn, click thật, và
        fallback JS-click nếu click thật bị che/trượt.
        """
        if self._cart_panel_open(timeout=500):
            return True
        btn = self.page.locator(self._CART_BTN_SEL).first
        for _attempt in range(3):
            try:
                if btn.is_visible(timeout=3_000):
                    try:
                        btn.scroll_into_view_if_needed(timeout=2_000)
                    except Exception:
                        pass
                    try:
                        btn.click(timeout=3_000)
                    except Exception:
                        # Fallback: click qua JS (bỏ qua phần tử che)
                        try:
                            btn.evaluate("el => el.click()")
                        except Exception:
                            pass
                    self.page.wait_for_timeout(1_200)
                    if self._cart_panel_open():
                        return True
            except Exception:
                pass
            self.page.wait_for_timeout(600)
        return self._cart_panel_open()

    def read_cart_panel_total(self) -> int | None:
        """Đọc tổng tiền trong panel giỏ hàng (slide-in panel, trả về int VNĐ)."""
        import re as _re
        raw = self.page.evaluate(r"""() => {
            const panel = document.querySelector('[class*="max-w-md"][class*="shadow"]');
            if (!panel) return null;
            const text = panel.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            const priceRe = /(\d{1,3}(?:[,.]\d{3})+)/;
            for (let i = 0; i < lines.length; i++) {
                if (/Tổng tiền/i.test(lines[i])) {
                    let m = lines[i].match(priceRe);
                    if (m) return m[1];
                    if (i + 1 < lines.length) {
                        let m2 = lines[i + 1].match(priceRe);
                        if (m2) return m2[1];
                    }
                }
            }
            return null;
        }""")
        if not raw:
            return None
        digits = _re.sub(r"[^\d]", "", str(raw))
        return int(digits) if digits else None

    def click_checkout_from_cart(self) -> bool:
        """Nhấn nút 'Thanh toán ngay' / 'Thanh toán' trong panel giỏ hàng."""
        try:
            panel = self.page.locator(self._BUYNOW_MODAL_SEL).first
            if panel.is_visible(timeout=3000):
                btn = panel.locator(
                    "button:has-text('Thanh toán ngay'), button:has-text('Thanh toán')"
                ).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    self.page.wait_for_timeout(3000)
                    return True
        except Exception:
            pass
        try:
            btn = self.page.locator("button:has-text('Thanh toán ngay')").first
            if btn.is_visible(timeout=3000):
                btn.click()
                self.page.wait_for_timeout(3000)
                return True
        except Exception:
            pass
        return False
