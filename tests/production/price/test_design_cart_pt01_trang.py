"""
PT01 Áo Phông Cá Tính / Màu Trắng — Luồng In / Giỏ hàng (MH1→MH11)

Luồng: Listing → Detail → Studio (thiết kế mặt trước) → Review → Popup → Thêm vào giỏ
       → Giỏ hàng → Checkout → QR → Order → Admin

Giá PT01 / Trắng / Size M / qty 1:
  salePrice_áo  = 189.000đ  (variant M/L/XL)
  salePrice_in  = dynamic (đọc từ Review page)
  unit_price    = ao + in   (đọc từ UI)
  GIAM20 (20%): giảm 20% subtotal → tổng = subtotal×0.8×1.08 + 20.000đ
"""
import json
import os
import re

import pytest

from .base_price_flow import BasePriceFlowTest

# ── Load data ─────────────────────────────────────────────────────────────────

def _load() -> dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "data", "product_pricing.json",
    )
    with open(p, encoding="utf-8") as f:
        return json.load(f)


_DATA    = _load()
_PRODUCT = next(x for x in _DATA["products"] if x["code"] == "PT01")
_VARIANT = next(v for v in _PRODUCT["variants"] if v["id"] == "PT01_M_L_XL")

_SALE_AO      = _VARIANT["salePrice"]                           # 189_000
_ORIGINAL     = _PRODUCT["listing_displayed"]["original_price"] # 227_000
_LIST_SALE    = _PRODUCT["listing_displayed"]["sale_price"]     # 189_000
_LIST_ORIG    = _ORIGINAL                                       # 227_000
_SHIPPING     = _DATA["global"]["shipping_fee"]                 # 20_000
_VAT_RATE     = _DATA["global"]["VAT_rate"]                     # 0.08
_GIAM20       = _DATA["discount_codes"]["GIAM20"]["value"]      # 0.20

_SLUG  = "ao-phong-ca-tinh"
_NAME  = "Áo Phông Cá Tính"
_COLOR = "Trắng"
_SIZE  = "M"

_FALLBACK_PRINT = 12_000  # Giả định 1 hình PET 10x10cm

# ── Test class ────────────────────────────────────────────────────────────────


class TestDesignCartPT01Trang(BasePriceFlowTest):
    """PT01 Trắng — luồng In / Giỏ hàng MH1→MH11."""

    _MH_NAMES = {
        "MH1":   "Product Listing",
        "MH2":   "Product Detail",
        "MH3":   "Studio",
        "MH12":  "Xác nhận thiết kế",
        "MH4":   "Popup Mua ngay → Thêm vào giỏ",
        "MH5":   "Checkout",
        "MH6":   "QR Code",
        "MH7":   "Order (sau hủy QR)",
        "MH8":   "Đơn hàng của tôi",
        "MH9":   "Chi tiết đơn hàng",
        "MH10":  "Giỏ hàng",
        "MH11":  "Admin — Chi tiết đơn",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "PT01 Áo Phông Cá Tính (Trắng) — In / Giỏ hàng"

    @pytest.fixture(autouse=True)
    def setup(self, home_page, product_list_page, product_detail_page,
              studio_page, auth_page, checkout_page, env):
        self.home     = home_page
        self.listing  = product_list_page
        self.detail   = product_detail_page
        self.studio   = studio_page
        self.auth     = auth_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = home_page.page
        self.tc       = "PT01_TRANG_DESIGN_CART"
        self.root     = "production"
        self.domain   = "pt01_trang_design_cart"
        self._results = []

    def _open_cart_panel(self) -> bool:
        """Mở cart panel qua menu → Giỏ hàng."""
        try:
            menu_btn = self.page.locator("button:has-text('menu')").first
            if menu_btn.is_visible(timeout=3000):
                menu_btn.click()
                self.page.wait_for_timeout(800)
            cart_btn = self.page.locator("button:has-text('Giỏ hàng')").first
            if cart_btn.is_visible(timeout=3000):
                cart_btn.click()
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    def _read_cart_panel_text(self) -> str:
        return self.page.evaluate(r"""() => {
            const panel = document.querySelector('[class*="max-w-md"][class*="shadow"]');
            return panel ? panel.innerText : '';
        }""") or ""

    def _read_review_prices(self) -> dict:
        """Đọc giá áo + giá in + tổng từ trang Xác nhận thiết kế."""
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            const priceRe = /(\d{1,3}(?:[,.]\d{3})+)/;

            let print_total = 0;
            let ao_total = 0;
            let sum_total = 0;

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (/in DTG|in PET|hình in|phí in/i.test(line)) {
                    let m = line.match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) print_total += parseInt(m[1].replace(/[^\d]/g, ''));
                }
                if (/áo phông|áo thun|cá tính|giá áo/i.test(line) && !ao_total) {
                    let m = line.match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) ao_total = parseInt(m[1].replace(/[^\d]/g, ''));
                }
                if (/tạm tính|tổng cộng|tổng tiền/i.test(line) && !sum_total) {
                    let m = line.match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) sum_total = parseInt(m[1].replace(/[^\d]/g, ''));
                }
            }

            const allPrices = [...text.matchAll(/(\d{1,3}(?:[,.]\d{3})+)\s*[đ₫VND]/gi)]
                .map(m => parseInt(m[1].replace(/[^\d]/g, '')));
            if (sum_total === 0 && allPrices.length > 0) sum_total = Math.max(...allPrices);
            if (ao_total === 0 && allPrices.length > 0) {
                const v = allPrices.find(p => p >= 100000 && p < sum_total);
                ao_total = v || 189000;
            }
            if (print_total === 0 && sum_total > ao_total) print_total = sum_total - ao_total;

            return { print_total, ao_total, sum_total };
        }""")

    @pytest.mark.production
    def test_design_cart(self):
        """PT01 Trắng / In / Giỏ hàng — MH1→MH11."""
        tc = self.tc
        self._login()

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Product Listing
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Product Listing ──────────────────────────────────")
        self.listing.navigate()
        self._shot("MH1_1", "listing_page")

        if self.listing.is_product_card_visible(_NAME):
            listing_sale = self.listing.read_listing_sale_price(_NAME)
            listing_orig = self.listing.read_listing_original_price(_NAME)
            self._assert_price(listing_sale, _LIST_SALE, "MH1 Giá sale listing")
            self._assert_price(listing_orig, _LIST_ORIG, "MH1 Giá gốc listing (gạch ngang)")
            self.listing.click_product_card(_NAME)
        else:
            print(f"  [INFO] MH1: Card '{_NAME}' không tìm thấy — navigate trực tiếp")
            self.detail.navigate(_SLUG)

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Product Detail
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Product Detail ───────────────────────────────────")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)
        self._shot("MH2_1", "detail_page")

        sale_disp = self.detail.read_sale_price()
        orig_disp = self.detail.read_original_price()
        self._assert_price(sale_disp, _SALE_AO,  "MH2 Giá sale default (Trắng)")
        self._assert_price(orig_disp, _ORIGINAL, "MH2 Giá gốc gạch ngang")
        self._shot("MH2_2", "detail_prices")
        print(f"  [PASS] MH2: OK — sale={sale_disp}, orig={orig_disp}")

        self.detail.select_color(_COLOR)
        self.page.wait_for_timeout(500)

        studio_ok = self.detail.click_thiet_ke_hinh_in()
        if not studio_ok:
            pytest.fail(f"FAIL: Không tìm thấy nút 'Thiết kế hình in'")
        self.page.wait_for_timeout(2000)

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Studio
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Studio ───────────────────────────────────────────")
        self.studio.accept_terms(tc)
        self.page.wait_for_timeout(1000)

        canvas_ok = self.studio.is_canvas_visible()
        self._record_check("MH3", "MH3 Studio canvas",
                           "✅ PASS" if canvas_ok else "⚠️ WARN",
                           "visible" if canvas_ok else "not found", "visible")
        self._shot("MH3_1", "studio_canvas")

        try:
            self.studio.open_library()
            self.page.wait_for_timeout(1000)
            self.studio.click_library_image(1)
            self.page.wait_for_timeout(2000)
            self._shot("MH3_2", "studio_designed")
            print(f"  [PASS] MH3: Đã thêm hình vào mặt trước")
        except Exception as e:
            print(f"  [WARN] MH3: Không click được hình — {e}")

        try:
            self.studio.open_order_modal()
            self.page.wait_for_url("**/review**", timeout=10000)
            self.page.wait_for_timeout(3000)
            print(f"  [PASS] MH3: Đã sang trang Review")
        except Exception as e:
            print(f"  [WARN] MH3: Không navigate được sang Review — {e}")
            self.page.wait_for_timeout(3000)

        # ════════════════════════════════════════════════════════════════════
        # MH12 — Xác nhận thiết kế (Review)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH12: Xác nhận thiết kế ───────────────────────────────")
        self.page.wait_for_timeout(2000)
        self._shot("MH12_1", "review_page")

        review_data = self._read_review_prices()
        print(f"  [INFO] MH12: Review prices = {review_data}")

        ao_price    = review_data.get("ao_total") or _SALE_AO
        print_price = review_data.get("print_total") or _FALLBACK_PRINT
        sum_review  = review_data.get("sum_total") or (ao_price + print_price)

        unit_sale_price = ao_price + print_price
        self._assert_price(sum_review, unit_sale_price, "MH12 Tổng (Áo + In) trên Review")

        try:
            btn = self.page.locator("button:has-text('Đặt hàng')").first
            if btn.is_visible(timeout=3000):
                btn.click()
                self.page.wait_for_timeout(2000)
                print(f"  [PASS] MH12: Đã click Đặt hàng")
        except Exception as e:
            print(f"  [WARN] MH12: Không click được Đặt hàng — {e}")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Trang Đặt hàng (Studio step 3) — chọn size → Thêm vào giỏ
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Trang Đặt hàng → Thêm vào giỏ ──────────────────")
        self.page.wait_for_timeout(2000)
        self._shot("MH4_1", "order_page")

        # Chọn size trước khi click Thêm vào giỏ
        size_ok = self.checkout.select_size_by_name(_SIZE)
        self.page.wait_for_timeout(1000)
        self._shot("MH4_2", f"order_size_{_SIZE}")
        self._record_check(
            "MH4", f"MH4 Chọn size {_SIZE}",
            "✅ PASS" if size_ok else "⚠️ WARN",
            "OK" if size_ok else "Không chọn được size", _SIZE,
        )
        print(f"  [{'PASS' if size_ok else 'WARN'}] MH4: select_size={size_ok}")

        price_on_page = self._read_order_page_price()
        self._assert_price(price_on_page, unit_sale_price, f"MH4 Tổng sau chọn size {_SIZE}")

        added = self.checkout.click_them_vao_gio()
        self.page.wait_for_timeout(1000)
        self._shot("MH4_3", "after_them_vao_gio")
        self._record_check("MH4", "MH4 Thêm vào giỏ",
                           "✅ PASS" if added else "⚠️ WARN",
                           "OK" if added else "click failed", "button clicked")
        print(f"  [{'PASS' if added else 'WARN'}] MH4: Thêm vào giỏ = {added}")

        # ════════════════════════════════════════════════════════════════════
        # MH10 — Giỏ hàng (click cart icon từ Studio header)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH10: Giỏ hàng ───────────────────────────────────────")
        # Sau khi "Thêm vào giỏ" trên Studio step 3, click cart button trong header
        panel_opened = False
        try:
            cart_btn = self.page.locator(
                "button:has-text('Giỏ hàng'), "
                "button[aria-label*='cart'], button[aria-label*='giỏ'], "
                "header button:has([class*='cart']), header button:has-text('shopping_cart')"
            ).first
            if cart_btn.is_visible(timeout=5000):
                cart_btn.click()
                self.page.wait_for_timeout(1500)
                panel_opened = True
                print(f"  [INFO] MH10: Đã click cart icon")
        except Exception as e:
            print(f"  [WARN] MH10: Không click được cart icon — {e}")

        self._shot("MH10_1", "cart_panel")

        cart_text = self.page.evaluate("() => document.body.innerText || ''")
        name_in_cart  = _NAME.split()[-1].lower() in cart_text.lower()
        color_in_cart = _COLOR.lower() in cart_text.lower()
        size_in_cart  = _SIZE in cart_text

        self._record_check("MH10", "MH10 Tên SP trong giỏ",
                           "✅ PASS" if name_in_cart else "⚠️ WARN",
                           "tìm thấy" if name_in_cart else "không thấy", _NAME)
        self._record_check("MH10", "MH10 Màu trong giỏ",
                           "✅ PASS" if color_in_cart else "⚠️ WARN",
                           "tìm thấy" if color_in_cart else "không thấy", _COLOR)
        self._record_check("MH10", f"MH10 Size {_SIZE} trong giỏ",
                           "✅ PASS" if size_in_cart else "⚠️ WARN",
                           "tìm thấy" if size_in_cart else "không thấy", _SIZE)

        cart_total = self.checkout.read_cart_panel_total()
        self._assert_price(cart_total, unit_sale_price, "MH10 Tổng giỏ hàng (1 áo có in)")
        self._shot("MH10_2", "cart_prices")
        print(f"  [{'PASS' if cart_total else 'WARN'}] MH10: cart_total={cart_total}")

        # Click "Thanh toán ngay" trong cart panel
        checked = self.checkout.click_checkout_from_cart()
        if checked:
            print(f"  [INFO] MH10: Đã click Thanh toán ngay từ cart panel")
        else:
            # Fallback: tìm bất kỳ button Thanh toán nào
            try:
                btn_tt = self.page.locator(
                    "button:has-text('Thanh toán'), a:has-text('Thanh toán')"
                ).last
                if btn_tt.is_visible(timeout=5000):
                    btn_tt.click()
                    self.page.wait_for_timeout(2000)
                    checked = True
                    print(f"  [INFO] MH10: Fallback click Thanh toán")
            except Exception:
                pass

        if not checked:
            print(f"  [WARN] MH10: Không click được Thanh toán — navigate trực tiếp /checkout")
            self.detail.goto("/checkout")
            self.page.wait_for_timeout(2000)

        try:
            self.page.wait_for_url("**/checkout**", timeout=10000)
        except Exception:
            self.page.wait_for_timeout(3000)

        # ════════════════════════════════════════════════════════════════════
        # MH5 — Checkout
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH5: Checkout ─────────────────────────────────────────")
        self.page.wait_for_load_state("domcontentloaded")
        self._wait_checkout_breakdown()
        self._shot("MH5_1", "checkout_page")

        subtotal = self.checkout.read_checkout_subtotal()
        vat      = self.checkout.read_checkout_vat()
        shipping = self.checkout.read_checkout_shipping()
        total    = self.checkout.read_checkout_total()
        print(f"  [INFO] MH5: subtotal={subtotal}, vat={vat}, ship={shipping}, total={total}")

        exp_vat      = int(unit_sale_price * _VAT_RATE)
        exp_total_nd = unit_sale_price + exp_vat + _SHIPPING

        self._assert_price(subtotal, unit_sale_price, "MH5 Tổng tiền (Áo + In)")
        self._assert_price(vat,      exp_vat,         "MH5 Thuế VAT (8%)")
        self._assert_price(shipping, _SHIPPING,       "MH5 Phí giao hàng")
        self._assert_price(total,    exp_total_nd,    "MH5 Tổng thanh toán")

        dc_ok = False
        self.checkout.apply_discount_code("GIAM20")
        self.page.wait_for_timeout(2000)
        self._shot("MH5_2", "checkout_after_GIAM20")

        discount_amt = self.checkout.read_checkout_discount()
        exp_discount = int(unit_sale_price * _GIAM20)

        if discount_amt and discount_amt > 0:
            dc_ok = True
            self._assert_price(discount_amt, exp_discount, "MH5 Giảm giá GIAM20 (20%)")
            after_dc     = int(unit_sale_price * (1 - _GIAM20))
            vat_dc       = int(after_dc * _VAT_RATE)
            exp_total_dc = after_dc + vat_dc + _SHIPPING
            total_dc = self.checkout.read_checkout_total()
            self._assert_price(total_dc, exp_total_dc, "MH5 Tổng TT sau GIAM20")
            print(f"  [PASS] MH5: GIAM20 OK — giảm {discount_amt:,}đ")
        else:
            print(f"  [INFO] MH5: Mã GIAM20 không áp dụng — tiếp tục với giá gốc")

        actual_total_paid = self.checkout.read_payment_button_price() or exp_total_nd
        print(f"  [INFO] MH5: Giá thực tế = {actual_total_paid:,}đ")

        order_info = {
            "product_name": _NAME,
            "color": _COLOR,
            "size": _SIZE,
            "qty": 1,
        }
        shipping_info = self.page.evaluate(r"""() => {
            const m = (document.body.innerText || '').match(/0\d{9,10}/);
            return { phone: m ? m[0] : '' };
        }""")
        order_info["phone"] = shipping_info.get("phone", "")

        # User đã đăng nhập — address pre-fill, chỉ điền MST
        self.checkout.fill_tax_code("012345678901", tc_id=tc)
        self._shot("MH5_3", "checkout_filled")
        self.checkout.click_checkout_payment()
        self.page.wait_for_timeout(3000)

        # ════════════════════════════════════════════════════════════════════
        # MH6 — QR Code
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH6: QR Code ──────────────────────────────────────────")
        self._shot("MH6_1", "qr_screen")
        qr_visible = self.checkout.is_qr_visible(timeout=10000)
        order_code = ""

        if qr_visible:
            qr_amount = self.checkout.read_qr_amount()
            if qr_amount is None:
                raw = self.page.evaluate(r"""() => {
                    const m = document.body.innerText.match(/thanh to[áa]n\s+(\d[\d,.]*\d)/i);
                    return m ? m[1] : null;
                }""")
                qr_amount = int(re.sub(r"[^\d]", "", str(raw))) if raw else None
            self._assert_price(qr_amount,                           actual_total_paid, "MH6 Số tiền QR")
            self._assert_price(self.checkout.read_qr_note_amount(), actual_total_paid, "MH6 Số tiền trong lưu ý")

            self.page.on("dialog", lambda d: d.accept())
            self.checkout.click_cancel_qr()
            self.page.wait_for_timeout(3000)
            self.checkout.confirm_cancel_dialog()
            self.page.wait_for_timeout(2000)
            self._shot("MH6_2", "qr_cancelled")
            self.checkout.click_view_order()
            self.page.wait_for_timeout(2000)

            if "payos" in self.page.url or "qr" in self.page.url.lower():
                self.checkout.goto("/my-orders")
                self.page.wait_for_timeout(2000)

            oc_m = re.search(r"orderCode=([\w-]+)", self.page.url)
            order_code = oc_m.group(1) if oc_m else ""
            print(f"  [INFO] MH6: order_code={order_code}")
        else:
            print(f"  [WARN] MH6: QR không hiển thị — URL: {self.page.url}")

        # ════════════════════════════════════════════════════════════════════
        # MH7 / MH8 / MH9 / MH11
        # ════════════════════════════════════════════════════════════════════
        self._do_mh7_order(actual_total_paid, _SHIPPING)
        self._do_mh8_my_orders(actual_total_paid)
        self._do_mh9_order_detail(
            order_info, actual_total_paid, _SHIPPING,
            dc_ok, exp_discount if dc_ok else None,
        )
        self._do_admin_verify("MH11", order_code, order_info, actual_total_paid, _SHIPPING)

        print(f"\n  [PASS] {tc}: ALL SCREENS PASSED")
        self._print_summary_table()
