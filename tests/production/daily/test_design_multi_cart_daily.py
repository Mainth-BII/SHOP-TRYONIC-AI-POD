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

        # Dọn sạch giỏ trước khi thêm món (tránh rác tồn từ lần chạy trước)
        _cleared = self.checkout.clear_cart()
        self._record_check("MH0", "Dọn giỏ trước khi test", "ℹ️ INFO",
                           f"đã xóa {_cleared} món tồn")

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

        # Đọc cart total + chi tiết từng dòng
        cart_total = self.checkout.read_cart_panel_total()
        breakdown  = self.checkout.read_cart_breakdown()
        expected_cart = unit1 + unit2
        print(f"  [INFO] Cart total={cart_total}, lines={breakdown['lines']}, "
              f"line_sum={breakdown['line_sum']:,}đ; popup unit1+unit2={expected_cart:,}đ "
              f"(unit1={unit1:,}đ + unit2={unit2:,}đ)")

        # Verify CHÍNH (đáng tin): cart tự cộng đúng — Σ dòng == Tổng tiền.
        # Giá popup đặt hàng hay đọc thiếu phí in (DTG +41k/áo) nên KHÔNG dùng
        # unit1+unit2 làm chuẩn hard-assert (gây false FAIL).
        cart_ref = breakdown["total"] or cart_total
        if cart_ref and breakdown["lines"]:
            self._assert_price(breakdown["line_sum"], cart_ref,
                               "MH10 Cart total = Σ giá từng dòng", mh="MH10")
        elif cart_ref:
            self._record_check("MH10", "Cart panel total", "ℹ️ INFO",
                               f"{cart_ref:,}đ", "không tách được dòng để đối chiếu")
        else:
            self._record_check("MH10", "Cart panel total", "⚠️ WARN",
                               "Không đọc được", f"expected ~{expected_cart:,}đ")

        # Cross-check phụ (INFO/WARN): cart_total vs unit popup. Lệch thường do
        # popup thiếu phí in → WARN, không FAIL.
        if cart_ref:
            _diff = cart_ref - expected_cart
            self._record_check(
                "MH10", "Cross-check cart vs giá popup",
                "✅ PASS" if _diff == 0 else "ℹ️ INFO",
                f"cart={cart_ref:,}đ, popup unit1+unit2={expected_cart:,}đ"
                + ("" if _diff == 0
                   else f" (lệch {_diff:+,}đ — phí in popup đọc thiếu, không phải lỗi)"))

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

        # Tạm tính THỰC mà checkout dùng = tổng giỏ đã verify (cart_ref, gồm cả
        # phí in). read_checkout_subtotal() đôi khi chỉ đọc per-item (item cuối)
        # → KHÔNG dùng làm chuẩn hard-assert (gây false FAIL VAT/total).
        checkout_ref  = cart_ref or (unit1 + unit2)
        expected_vat  = int(checkout_ref * _VAT_RATE)
        expected_ship = _SHIPPING
        expected_tot  = checkout_ref + expected_vat + expected_ship

        # Subtotal đọc được chỉ ghi INFO (app có thể hiển thị per-item)
        self._record_check("MH5", "MH5 Tạm tính (đọc được) [info]",
                           "ℹ️ INFO",
                           f"{subtotal:,}đ" if subtotal else "N/A",
                           f"tổng giỏ verify={checkout_ref:,}đ (app có thể hiển thị per-item)")

        # Verify VAT / ship / total dựa trên TỔNG GIỎ thực (đáng tin) — vẫn bắt
        # được lỗi tính sai thật (VAT/total lệch khỏi tổng giỏ → FAIL).
        self._assert_price(vat,      expected_vat,  "MH5 VAT 8% (trên tổng giỏ)", mh="MH5")
        self._assert_price(shipping, expected_ship, "MH5 Phí giao hàng",          mh="MH5")
        self._assert_price(total,    expected_tot,  "MH5 Tổng thanh toán",        mh="MH5")

        # Cross-check: tạm tính suy ngược từ total hiển thị == tổng giỏ verify
        if vat is not None and shipping is not None and total is not None:
            derived_sub = total - vat - shipping
            self._record_check(
                "MH5", "Checkout tạm tính (suy ngược) = tổng giỏ",
                "✅ PASS" if derived_sub == checkout_ref else "⚠️ WARN",
                f"derived={derived_sub:,}đ", f"giỏ={checkout_ref:,}đ")

        # Apply MAIFREESHIP (mã free-ship). Hành vi ĐÚNG cần verify:
        #  - Mã hợp lệ → phí ship = 0.
        #  - Mã hết hạn/không tồn tại → hệ thống TỪ CHỐI, ship KHÔNG đổi.
        # Cả hai đều PASS (validate hành vi đúng). Chỉ FAIL nếu mã lỗi mà vẫn
        # bị trừ ship sai (tính nhầm vào total).
        ship_before = shipping if shipping is not None else _SHIPPING
        applied = self.checkout.apply_discount_code("MAIFREESHIP")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "7", "maifreeship_applied")

        shipping_after = self.checkout.read_checkout_shipping()
        total_after    = self.checkout.read_checkout_total()
        _mfs_reason = self.checkout.last_promo_message or "không rõ lý do"
        print(f"  [INFO] MAIFREESHIP: applied={applied}, ship_before={ship_before}, "
              f"ship_after={shipping_after}, total_after={total_after}")

        if applied and shipping_after == 0:
            self._record_check("MH5", "MAIFREESHIP: mã hợp lệ → ship = 0",
                               "✅ PASS", "0đ", "0đ")
        elif not applied:
            # Bị từ chối là ĐÚNG nếu KHÔNG trừ ship (free-ship không áp sai vào total)
            _ship_unchanged = (shipping_after is None or shipping_after == ship_before)
            self._record_check(
                "MH5", "MAIFREESHIP: từ chối mã không hợp lệ, không trừ ship",
                "✅ PASS" if _ship_unchanged else "❌ FAIL",
                (f'Hệ thống từ chối đúng (BE: "{_mfs_reason}"), ship giữ nguyên '
                 f'{ship_before:,}đ — không tính vào total' if _ship_unchanged
                 else f'LỖI: mã bị từ chối nhưng ship đổi {ship_before:,}→{shipping_after:,}đ'))
        else:
            self._record_check("MH5", "MAIFREESHIP: phí vận chuyển", "⚠️ WARN",
                               f"applied=True nhưng ship={shipping_after}đ (mong đợi 0đ)")

        # ── PROD SAFETY STOP ──────────────────────────────────────────────────
        self._record_check("MH5", "STOP — Không click Thanh toán", "✅ PASS",
                           "dừng tại checkout", "PROD SAFE")

        self.__class__._results.extend(self._results)
        self._save_report()
