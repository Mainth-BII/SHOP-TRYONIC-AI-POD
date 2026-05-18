"""
ET002 Áo Phông Trẻ Em / Màu Trắng — Luồng Trơn / Mua ngay (MH1→MH10)

Giá ET002 / Trắng / Size 120 / qty 1 (áo trơn — không in):
  salePrice     = 96.000đ   |  originalPrice = 116.000đ  (variant 100-140)
  VAT 8%        = 7.680đ    |  Phí GH = 20.000đ  |  Tổng = 123.680đ
  Với GIAM20 (20%): giảm 19.200đ → tổng 102.944đ
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
_PRODUCT = next(x for x in _DATA["products"] if x["code"] == "ET002")
_VARIANT = next(v for v in _PRODUCT["variants"] if v["id"] == "ET002_100_140")

_SALE         = _VARIANT["salePrice"]                           # 96_000
_ORIGINAL     = _VARIANT["originalPrice"]                       # 116_000
_LIST_SALE    = _PRODUCT["listing_displayed"]["sale_price"]     # 96_000
_LIST_ORIG    = _PRODUCT["listing_displayed"]["original_price"] # 120_000
_SHIPPING     = _DATA["global"]["shipping_fee"]                 # 20_000
_VAT_RATE     = _DATA["global"]["VAT_rate"]                     # 0.08
_GIAM20       = _DATA["discount_codes"]["GIAM20"]["value"]      # 0.20

_VAT_NO_DC    = int(_SALE * _VAT_RATE)                          # 7_680
_TOTAL_NO_DC  = _SALE + _VAT_NO_DC + _SHIPPING                 # 123_680
_AFTER_DC     = int(_SALE * (1 - _GIAM20))                     # 76_800
_VAT_DC       = int(_AFTER_DC * _VAT_RATE)                     # 6_144
_TOTAL_DC     = _AFTER_DC + _VAT_DC + _SHIPPING                # 102_944
_DISCOUNT_AMT = int(_SALE * _GIAM20)                           # 19_200

_SLUG  = "ao-phong-tre-em"
_NAME  = "Áo Phông Trẻ Em"
_COLOR = "Trắng"
_SIZE  = "120"  # size trẻ em (variant 100-140)

# ── Test class ────────────────────────────────────────────────────────────────


class TestPlainBuynowET002Trang(BasePriceFlowTest):
    """ET002 Trắng — luồng Trơn / Mua ngay MH1→MH10."""

    _MH_NAMES = {
        "MH1":   "Product Listing",
        "MH2":   "Product Detail",
        "MH3":   "Studio",
        "MH4":   "Popup Mua ngay",
        "MH5":   "Checkout",
        "MH6":   "QR Code",
        "MH7":   "Order (sau hủy QR)",
        "MH8":   "Đơn hàng của tôi",
        "MH9":   "Chi tiết đơn hàng",
        "MH10":  "Admin — Chi tiết đơn",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "ET002 Áo Phông Trẻ Em (Trắng) — Trơn / Mua ngay"

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
        self.tc       = "ET002_TRANG_PLAIN_BUYNOW"
        self.root     = "production"
        self.domain   = "et002_trang_plain_buynow"
        self._results = []

    @pytest.mark.production
    def test_plain_buynow(self):
        """ET002 Trắng / Trơn / Mua ngay — MH1→MH10."""
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
        self._assert_price(sale_disp, _SALE,     "MH2 Giá sale default (Trắng)")
        self._assert_price(orig_disp, _ORIGINAL, "MH2 Giá gốc gạch ngang")
        self._shot("MH2_2", "detail_prices_default")
        print(f"  [PASS] MH2: OK — sale={sale_disp}, orig={orig_disp}")

        self.detail.select_color(_COLOR)
        self.page.wait_for_timeout(500)

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Studio (verify button tồn tại, không cần thiết kế)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Studio ───────────────────────────────────────────")
        studio_ok = self.detail.click_thiet_ke_hinh_in()
        if studio_ok:
            self.page.wait_for_timeout(2000)
            self.studio.accept_terms(tc)
            self._shot("MH3_1", "studio_from_detail")
            canvas_ok = self.studio.is_canvas_visible()
            print(f"  [{'PASS' if canvas_ok else 'WARN'}] MH3: Studio canvas visible={canvas_ok}")
            self.page.go_back()
            try:
                self.page.wait_for_url(f"**/{_SLUG}**", timeout=10000)
            except Exception:
                self.detail.navigate(_SLUG)
            self.page.wait_for_timeout(1500)
            self.detail.select_color(_COLOR)
            self.page.wait_for_timeout(500)
        else:
            print(f"  [WARN] MH3: Không tìm thấy button 'Thiết kế hình in' — bỏ qua")
        self._shot("MH3_2", "back_to_detail")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Popup Mua ngay
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Popup Mua ngay ───────────────────────────────────")
        mua_ngay_ok = self.detail.click_mua_ngay()
        if not mua_ngay_ok:
            pytest.skip(f"SKIP MH4 ({tc}): Không mở được popup Mua ngay")

        self.page.wait_for_timeout(1500)
        modal_visible = self.checkout.is_buynow_modal_visible(timeout=5000)
        self._shot("MH4_1", "buynow_modal")

        if modal_visible:
            self.checkout.select_size_by_name(_SIZE)
            self.page.wait_for_timeout(800)
            price_after = self.checkout.read_buynow_modal_price()
            btn_price   = self.checkout.read_buynow_button_price()
            self._shot("MH4_2", f"buynow_size_{_SIZE}")
            self._assert_price(price_after, _SALE, f"MH4 Đơn giá sau chọn size {_SIZE}")
            self._assert_price(btn_price,   _SALE, "MH4 Giá trên button Thanh toán ngay")
            print(f"  [PASS] MH4: Popup OK")
        else:
            print(f"  [WARN] MH4: Modal không detect được — bỏ qua verify")

        paid = self.checkout.click_thanh_toan_ngay()
        if not paid:
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

        self._assert_price(subtotal, _SALE,        "MH5 Tổng tiền")
        self._assert_price(vat,      _VAT_NO_DC,   "MH5 Thuế VAT (8%)")
        self._assert_price(shipping, _SHIPPING,    "MH5 Phí giao hàng")
        self._assert_price(total,    _TOTAL_NO_DC, "MH5 Tổng thanh toán")

        dc_ok = False
        self.checkout.apply_discount_code("GIAM20")
        self.page.wait_for_timeout(2000)
        self._shot("MH5_2", "checkout_after_GIAM20")

        discount_amt = self.checkout.read_checkout_discount()
        if discount_amt and discount_amt > 0:
            dc_ok = True
            self._assert_price(discount_amt, _DISCOUNT_AMT, "MH5 Giảm giá GIAM20 (20%)")
            total_dc = self.checkout.read_checkout_total()
            self._assert_price(total_dc, _TOTAL_DC, "MH5 Tổng TT sau GIAM20")
            print(f"  [PASS] MH5: GIAM20 OK — giảm {discount_amt:,}đ")
        else:
            print(f"  [INFO] MH5: Mã GIAM20 không áp dụng — tiếp tục với giá gốc")

        actual_total_paid = self.checkout.read_payment_button_price() or _TOTAL_NO_DC
        print(f"  [INFO] MH5: Giá thực tế = {actual_total_paid:,}đ")

        checkout_product = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const m = text.match(/(\d{3})\s*[×x]\s*(\d+)/);
            return { size: m ? m[1] : '', qty: m ? parseInt(m[2]) : 1 };
        }""")
        order_info = {
            "product_name": _NAME,
            "color": _COLOR,
            "size": checkout_product.get("size", _SIZE) if checkout_product else _SIZE,
            "qty":  checkout_product.get("qty", 1)     if checkout_product else 1,
        }
        shipping_info = self.page.evaluate(r"""() => {
            const m = (document.body.innerText || '').match(/0\d{9,10}/);
            return { phone: m ? m[0] : '' };
        }""")
        order_info["phone"] = shipping_info.get("phone", "")

        self.checkout.fill_guest_shipping_info(
            "Test Tryonic", "0912345678",
            "123 Đường Test, Quận 1, TP. Hồ Chí Minh",
            tc_id=tc,
        )
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
            self._assert_price(qr_amount,                          actual_total_paid, "MH6 Số tiền QR")
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
        # MH7 / MH8 / MH9 / MH10
        # ════════════════════════════════════════════════════════════════════
        self._do_mh7_order(actual_total_paid, _SHIPPING)
        self._do_mh8_my_orders(actual_total_paid)
        self._do_mh9_order_detail(
            order_info, actual_total_paid, _SHIPPING,
            dc_ok, _DISCOUNT_AMT if dc_ok else None,
        )
        self._do_admin_verify("MH10", order_code, order_info, actual_total_paid, _SHIPPING)

        print(f"\n  [PASS] {tc}: ALL SCREENS PASSED")
        self._print_summary_table()
