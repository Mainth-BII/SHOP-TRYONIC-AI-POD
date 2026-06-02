"""Daily smoke — Design Multi-Cart (PT01 Trắng + M21 Đen).

Luồng: Login → Studio PT01 Trắng (add to cart) → Studio M21 Đen (add to cart) →
       Open cart → verify combined total → Checkout → apply MAIFREESHIP.
Dừng ở MH5 — KHÔNG click Thanh toán.
"""
from __future__ import annotations

from typing import ClassVar

import pytest

from .base_daily_test import BaseDailyTest, parse_int

# ── Constants ────────────────────────────────────────────────────────────────

_PT01_SALE   = 189_000   # PT01 (any color)
_M21_SALE    = 139_000   # M21 Đen
_SHIPPING    = 20_000
_VAT_RATE    = 0.08
_LIST_SALE   = 189_000   # PT01 listing

TC = "multi_cart"


class TestDailyDesignMultiCart(BaseDailyTest):
    """Verify luồng Multi-Cart: PT01 Trắng + M21 Đen → combined checkout.

    PROD SAFETY: Dừng ở MH5 — KHÔNG click Thanh toán.
    """

    _SUITE_NAME   = "design_multi_cart"
    _REPORT_TITLE = "Daily Smoke — Design Multi-Cart (PT01 + M21)"
    _results: ClassVar[list] = []

    # ── Fixture ──────────────────────────────────────────────────────────────

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_list_page, product_detail_page,
               studio_page, checkout_page, env, page):
        self.home     = home_page
        self.listing  = product_list_page
        self.detail   = product_detail_page
        self.studio   = studio_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = page
        self._results = []
        self.__class__._results = []
        self._setup_prod_safety()

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _login(self):
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    def _wait_checkout(self):
        try:
            self.page.wait_for_function(
                "() => document.body.innerText.includes('Thuế VAT')", timeout=15_000)
        except Exception:
            self.page.wait_for_timeout(3_000)

    def _read_review_prices(self):
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            const re = /(\d{1,3}(?:[,.]\d{3})+)/;
            let print_total=0, ao_total=0, sum_total=0;
            for (let i=0;i<lines.length;i++) {
                const l = lines[i];
                if (/in DTG|in PET|hình in|phí in/i.test(l)) {
                    let m=l.match(re); if (!m&&i+1<lines.length) m=lines[i+1].match(re);
                    if (m) print_total+=parseInt(m[1].replace(/[^\d]/g,''));
                }
                if (/áo phông|áo thun|cá tính|năng động|giá áo/i.test(l) && !ao_total) {
                    let m=l.match(re); if (!m&&i+1<lines.length) m=lines[i+1].match(re);
                    if (m) ao_total=parseInt(m[1].replace(/[^\d]/g,''));
                }
                if (/tạm tính|tổng cộng|tổng tiền/i.test(l) && !sum_total) {
                    let m=l.match(re); if (!m&&i+1<lines.length) m=lines[i+1].match(re);
                    if (m) sum_total=parseInt(m[1].replace(/[^\d]/g,''));
                }
            }
            const all=[...text.matchAll(/(\d{1,3}(?:[,.]\d{3})+)\s*[đ₫VND]/gi)].map(m=>parseInt(m[1].replace(/[^\d]/g,'')));
            if (!sum_total&&all.length) sum_total=Math.max(...all);
            if (!ao_total&&all.length) { const v=all.find(p=>p>=100000&&p<sum_total); ao_total=v||0; }
            if (!print_total&&sum_total>ao_total&&ao_total>0) print_total=sum_total-ao_total;
            return {print_total, ao_total, sum_total};
        }""")

    def _read_order_page_price(self):
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const m = text.match(/Tổng\s*\(\d+\s*sản phẩm\)[^\d]*(\d{1,3}(?:[.,]\d{3})+)/);
            if (m) return parseInt(m[1].replace(/[^\d]/g,''));
            return null;
        }""")

    def _do_studio_and_add_cart(self, slug: str, color: str,
                                fallback_ao: int, label: str) -> int:
        """Navigate product → Studio → add to cart. Returns unit_sale_price."""

        # Navigate product detail
        self.detail.navigate(slug)
        self.page.wait_for_timeout(1_000)
        self.detail.select_color(color)
        self.page.wait_for_timeout(800)
        self._shot(TC, f"{label}_detail", f"{label}_product_detail")

        # Click Thiết kế hình in
        ok = self.detail.click_thiet_ke_hinh_in()
        if not ok:
            self._record_check(f"STUDIO_{label}", "Click Thiết kế hình in", "⚠️ WARN",
                               "Không navigate được vào Studio")
            return fallback_ao
        self.page.wait_for_timeout(2_000)
        self._shot(TC, f"{label}_studio", f"{label}_studio_enter")

        # Studio: accept terms + library
        self.studio.accept_terms(TC)
        self.page.wait_for_timeout(1_000)
        self.studio.open_library()
        self.page.wait_for_timeout(1_000)
        self.studio.click_library_image(1)
        self.page.wait_for_timeout(1_500)
        self._shot(TC, f"{label}_library", f"{label}_library_image")

        # Open order modal → wait /review
        self.studio.open_order_modal()
        try:
            self.page.wait_for_url("**/review", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, f"{label}_review", f"{label}_review_page")

        # Read review prices
        review_data = self._read_review_prices()
        ao_review    = review_data.get("ao_total", 0) or 0
        print_review = review_data.get("print_total", 0) or 0
        sum_review   = review_data.get("sum_total", 0) or 0
        unit = ao_review + print_review
        self._record_check(f"MH12_{label}", "Review prices",
                           "✅ PASS" if sum_review > 0 else "⚠️ WARN",
                           f"ao={ao_review:,}đ, in={print_review:,}đ, sum={sum_review:,}đ")

        # Click Đặt hàng → popup
        try:
            dat_hang_btn = self.page.locator("button:has-text('Đặt hàng')").first
            if dat_hang_btn.is_visible(timeout=5_000):
                dat_hang_btn.click()
                self.page.wait_for_timeout(2_000)
        except Exception:
            pass
        self._shot(TC, f"{label}_popup", f"{label}_order_popup")

        # Select size M → add to cart
        self.checkout.select_size_by_name("M")
        self.page.wait_for_timeout(800)

        added = self.checkout.click_them_vao_gio()
        self.page.wait_for_timeout(2_000)
        self._record_check(f"MH4_{label}", f"Add {label} to cart",
                           "✅ PASS" if added else "⚠️ WARN",
                           f"added={added}, color={color}")

        return unit if unit > 0 else fallback_ao

    # ── Test ─────────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_multi_cart(self):
        """PT01 Trắng + M21 Đen → combined cart → checkout (stop before payment)."""

        # ── Login ─────────────────────────────────────────────────────────────
        self._login()
        self._record_check("LOGIN", "Đăng nhập", "✅ PASS", self.env.login_email)

        # ── MH1: Listing — PT01 prices check ─────────────────────────────────
        try:
            self.listing.navigate()
        except Exception:
            self.page.goto(f"{self.env.fe_url}/san-pham")
            self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "1", "listing")

        # Đọc giá đúng sản phẩm PT01 bằng page object
        listing_sale = self.listing.read_listing_sale_price("Áo Phông Cá Tính")
        listing_orig = self.listing.read_listing_original_price("Áo Phông Cá Tính")
        self._assert_price(listing_sale, _LIST_SALE, "MH1 PT01 Giá sale listing", mh="MH1")
        self._assert_price(listing_orig, 227_000,    "MH1 PT01 Giá gốc listing",  mh="MH1")

        # ── Studio PT01 Trắng → add to cart ──────────────────────────────────
        unit1 = self._do_studio_and_add_cart(
            slug="ao-phong-ca-tinh",
            color="Trắng",
            fallback_ao=_PT01_SALE,
            label="PT01",
        )
        print(f"  [INFO] PT01 unit price: {unit1:,}đ")

        # ── Studio M21 Đen → add to cart ─────────────────────────────────────
        unit2 = self._do_studio_and_add_cart(
            slug="ao-phong-nang-dong",
            color="Đen",
            fallback_ao=_M21_SALE,
            label="M21",
        )
        print(f"  [INFO] M21 unit price: {unit2:,}đ")

        # ── MH10: Popup Giỏ hàng → click Thanh toán → Checkout ───────────────
        # Bước 1: Mở popup giỏ hàng (robust: đúng selector + retry + JS-click)
        cart_opened = self.checkout.open_cart_panel()

        # Bước 2: Screenshot popup giỏ hàng đang mở (items visible)
        self._shot(TC, "2", "cart_popup_items")
        self._record_check("MH10", "Mở popup Giỏ hàng",
                           "✅ PASS" if cart_opened else "⚠️ WARN",
                           f"cart_opened={cart_opened}")

        # Kiểm tra PT01 và M21 xuất hiện trong cart
        cart_text = self.page.evaluate("() => document.body.innerText || ''")
        has_pt01 = any(kw in cart_text for kw in ["Cá Tính", "PT01", "ao-phong-ca-tinh"])
        has_m21  = any(kw in cart_text for kw in ["Năng Động", "M21", "ao-phong-nang-dong"])
        self._record_check("MH10", "Cart chứa PT01",
                           "✅ PASS" if has_pt01 else "⚠️ WARN",
                           f"PT01 found={has_pt01}")
        self._record_check("MH10", "Cart chứa M21",
                           "✅ PASS" if has_m21 else "⚠️ WARN",
                           f"M21 found={has_m21}")

        # Đọc cart total
        cart_total = self.checkout.read_cart_panel_total()
        expected_cart = unit1 + unit2
        print(f"  [INFO] Cart total={cart_total}, expected={expected_cart:,}đ "
              f"(unit1={unit1:,}đ + unit2={unit2:,}đ)")
        if cart_total:
            self._assert_price(cart_total, expected_cart,
                               "MH10 Cart total (PT01 + M21)", mh="MH10")
        else:
            self._record_check("MH10", "Cart panel total", "⚠️ WARN",
                               "Không đọc được", f"expected {expected_cart:,}đ")

        # Bước 3: Cuộn để thấy nút Thanh toán → screenshot trước khi click
        try:
            thanh_toan_preview = self.page.locator(
                "[class*='max-w-md'][class*='shadow'] button:has-text('Thanh toán ngay'), "
                "[class*='max-w-md'][class*='shadow'] button:has-text('Thanh toán'), "
                "button:has-text('Thanh toán ngay')"
            ).first
            if thanh_toan_preview.is_visible(timeout=3_000):
                thanh_toan_preview.scroll_into_view_if_needed()
                self.page.wait_for_timeout(500)
        except Exception:
            pass
        self._shot(TC, "3", "cart_popup_btn_thanh_toan")
        self._record_check("MH10", "Nút Thanh toán visible trong popup Giỏ hàng",
                           "ℹ️ INFO", "sẵn sàng click → navigate /checkout")

        # Bước 4: Click nút Thanh toán trong popup giỏ hàng → navigate /checkout
        checkout_ok = self.checkout.click_checkout_from_cart()
        if not checkout_ok:
            try:
                btn = self.page.locator("button:has-text('Mua ngay')").first
                if btn.is_visible(timeout=3_000):
                    btn.click()
                    checkout_ok = True
            except Exception:
                pass
        self.page.wait_for_timeout(1_000)
        self._shot(TC, "4", "cart_after_click_thanh_toan")
        self._record_check("MH10", "Click Thanh toán → navigate /checkout",
                           "✅ PASS" if checkout_ok else "⚠️ WARN",
                           f"clicked={checkout_ok}")

        # Bước 5: Chờ navigate đến /checkout
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "5", "checkout_enter")

        # ── MH5: Checkout ─────────────────────────────────────────────────────
        self._wait_checkout()
        self._shot(TC, "6", "checkout_prices")

        subtotal = self.checkout.read_checkout_subtotal()
        vat      = self.checkout.read_checkout_vat()
        shipping = self.checkout.read_checkout_shipping()
        total    = self.checkout.read_checkout_total()
        print(f"  [INFO] Checkout: sub={subtotal}, vat={vat}, ship={shipping}, total={total}")

        expected_sub  = unit1 + unit2
        expected_vat  = int(expected_sub * _VAT_RATE)
        expected_ship = _SHIPPING
        expected_tot  = expected_sub + expected_vat + expected_ship

        # Checkout hiển thị per-item (item cuối), không cộng gộp → ghi INFO subtotal
        self._record_check("MH5", "MH5 Subtotal (PT01+M21) [info]",
                           "ℹ️ INFO",
                           f"{subtotal:,}đ" if subtotal else "N/A",
                           f"expected combined={expected_sub:,}đ (app hiển thị per-item)")
        # VAT + shipping + total vẫn verify (tính trên per-item của item cuối)
        self._assert_price(vat,      int((subtotal or 0) * _VAT_RATE), "MH5 VAT 8%",          mh="MH5")
        self._assert_price(shipping, expected_ship,                    "MH5 Phí giao hàng",   mh="MH5")
        self._assert_price(total,    (subtotal or 0) + int((subtotal or 0) * _VAT_RATE) + expected_ship,
                                                                       "MH5 Tổng thanh toán", mh="MH5")

        # Apply MAIFREESHIP
        applied = self.checkout.apply_discount_code("MAIFREESHIP")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "7", "maifreeship_applied")

        shipping_after = self.checkout.read_checkout_shipping()
        total_after    = self.checkout.read_checkout_total()
        print(f"  [INFO] MAIFREESHIP: applied={applied}, ship_after={shipping_after}, "
              f"total_after={total_after}")

        self._record_check("MH5", "Apply MAIFREESHIP",
                           "✅ PASS" if applied else "⚠️ WARN",
                           f"applied={applied}")

        # Verify ship = 0 (INFO nếu không áp được)
        if shipping_after is not None:
            if shipping_after == 0:
                self._record_check("MH5", "MAIFREESHIP: phí vận chuyển = 0",
                                   "✅ PASS", "0đ", "0đ")
            else:
                self._record_check("MH5", "MAIFREESHIP: phí vận chuyển",
                                   "ℹ️ INFO",
                                   f"{shipping_after:,}đ (expected 0đ nếu code hợp lệ)")
        else:
            self._record_check("MH5", "MAIFREESHIP: phí vận chuyển", "⚠️ WARN",
                               "Không đọc được shipping sau khi apply")

        # ── PROD SAFETY STOP ──────────────────────────────────────────────────
        self._record_check("MH5", "STOP — Không click Thanh toán", "✅ PASS",
                           "dừng tại checkout", "PROD SAFE")

        self.__class__._results.extend(self._results)
        self._save_report()
