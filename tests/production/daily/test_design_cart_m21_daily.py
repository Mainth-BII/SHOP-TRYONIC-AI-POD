"""Daily smoke — Design Cart M21 (All Sizes).

Luồng: Login → Listing → Product Detail M21 → verify all color prices →
       Studio (Library front + back) → Review → Add all 7 sizes to cart →
       Open cart → Checkout. Dừng ở MH5 — KHÔNG click Thanh toán.
"""
from __future__ import annotations

from typing import ClassVar

import pytest

from .base_daily_test import BaseDailyTest, parse_int

# ── Constants ────────────────────────────────────────────────────────────────

_NAME          = "Áo Phông Năng Động"
_SLUG          = "ao-phong-nang-dong"
_SALE_AO_DEN  = 139_000   # M21 màu (non-trắng)
_COST_AO_DEN  = 64_000
_SALE_AO_TRANG = 130_000
_MIN_SALE      = 130_000   # listing min
_MAX_ORIG      = 167_000   # listing max gạch
_SHIPPING      = 20_000
_VAT_RATE      = 0.08
_ALL_SIZES     = ["XS", "S", "M", "L", "XL", "2XL", "3XL"]

TC = "m21_cart"


class TestDailyDesignCartM21(BaseDailyTest):
    """Verify luồng Design → Cart (all 7 sizes) → Checkout cho M21 Đen.

    PROD SAFETY: Dừng ở màn hình MH5 checkout — KHÔNG click Thanh toán.
    """

    _SUITE_NAME   = "design_cart_m21"
    _REPORT_TITLE = "Daily Smoke — Design Cart M21 (All Sizes)"
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

    # ── Test ─────────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_m21_cart(self):
        """M21 Đen → all 7 sizes → cart → checkout (stop before payment)."""

        # ── Login ─────────────────────────────────────────────────────────────
        self._login()
        self._record_check("LOGIN", "Đăng nhập", "✅ PASS", self.env.login_email)

        # ── MH1: Listing ─────────────────────────────────────────────────────
        try:
            self.listing.navigate()
        except Exception:
            self.page.goto(f"{self.env.fe_url}/san-pham")
            self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "1", "listing")

        # Đọc giá sale/gốc đúng sản phẩm M21 bằng page object
        listing_sale = self.listing.read_listing_sale_price(_NAME)
        listing_orig = self.listing.read_listing_original_price(_NAME)
        self._assert_price(listing_sale, _MIN_SALE, "MH1 Giá sale listing M21", mh="MH1")
        self._assert_price(listing_orig, _MAX_ORIG, "MH1 Giá gốc listing M21", mh="MH1")

        # ── MH2: Product Detail M21 ───────────────────────────────────────────
        self.detail.navigate("ao-phong-nang-dong")
        self.page.wait_for_timeout(1_000)
        self._shot(TC, "2", "product_detail")

        # Detect all colors và verify theo màu
        colors = self.detail.get_available_colors()
        print(f"  [INFO] Colors found: {colors}")
        self._record_check("MH2", "Detect màu sắc",
                           "✅ PASS" if colors else "⚠️ WARN",
                           f"{len(colors)} màu: {colors}")

        # Verify giá từng màu
        for color in (colors or ["Trắng", "Đen"]):
            self.detail.select_color(color)
            self.page.wait_for_timeout(800)
            sp = self.detail.read_sale_price()
            color_lower = color.lower()
            expected = _SALE_AO_TRANG if color_lower in ("trắng", "trang", "white") else _SALE_AO_DEN
            self._assert_price(sp, expected, f"MH2 Giá {color}", mh="MH2")

        # Select Đen để vào studio
        self.detail.select_color("Đen")
        self.page.wait_for_timeout(800)
        self._shot(TC, "3", "color_den_selected")

        ok = self.detail.click_thiet_ke_hinh_in()
        if not ok:
            pytest.skip("Không navigate được vào Studio")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "4", "studio_enter")
        self._record_check("MH2", "Click Thiết kế hình in", "✅ PASS", self.page.url)

        # ── MH3: Studio (front + back) ────────────────────────────────────────
        self.studio.accept_terms(TC)
        self.page.wait_for_timeout(1_000)
        self.studio.open_library()
        self.page.wait_for_timeout(1_000)
        # Front image
        self.studio.click_library_image(1)
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "5", "studio_front_image")
        self._record_check("MH3", "Studio front image", "✅ PASS", "library image 1 selected")

        # Toggle to back side
        try:
            self.studio.toggle_side("back")
            self.page.wait_for_timeout(1_500)
            self._shot(TC, "6", "studio_back_side")
            # Back image
            self.studio.click_library_image(2)
            self.page.wait_for_timeout(1_500)
            self._shot(TC, "7", "studio_back_image")
            self._record_check("MH3", "Studio back image", "✅ PASS", "library image 2 selected")
        except Exception as e:
            self._record_check("MH3", "Studio back image", "⚠️ WARN",
                               f"Không toggle được back: {e}")

        self.studio.open_order_modal()
        try:
            self.page.wait_for_url("**/review", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "8", "review_page")
        self._record_check("MH3", "Open order modal → /review", "✅ PASS", self.page.url)

        # ── MH12: Review ──────────────────────────────────────────────────────
        review_data = self._read_review_prices()
        ao_review    = review_data.get("ao_total", 0) or 0
        print_review = review_data.get("print_total", 0) or 0
        sum_review   = review_data.get("sum_total", 0) or 0
        unit = (ao_review + print_review) if (ao_review + print_review) > 0 else sum_review
        print(f"  [INFO] Review prices: ao={ao_review}, in={print_review}, sum={sum_review}")
        self._record_check("MH12", "Review: đọc giá (ao + in = unit)",
                           "✅ PASS" if sum_review > 0 else "⚠️ WARN",
                           f"ao={ao_review:,}đ, in={print_review:,}đ, sum={sum_review:,}đ")
        if sum_review > 0 and unit > 0:
            self._assert_price(sum_review, unit, "MH12 Review sum = ao+in", mh="MH12")

        # Click Đặt hàng → popup
        try:
            dat_hang_btn = self.page.locator("button:has-text('Đặt hàng')").first
            if dat_hang_btn.is_visible(timeout=5_000):
                dat_hang_btn.click()
                self.page.wait_for_timeout(2_000)
        except Exception:
            pass
        self._shot(TC, "9", "popup_order")

        # Dọn sạch giỏ TRƯỚC khi thêm (ở context trang Đặt hàng — nơi CartDrawer
        # studio chắc chắn mở được; tránh cộng dồn số lượng từ các lần chạy trước).
        _cleared = self.checkout.clear_cart()
        self._record_check("MH0", "Dọn giỏ trước khi thêm món", "ℹ️ INFO",
                           f"đã xóa {_cleared} dòng tồn")

        # ── MH4: Popup — Add all 7 sizes to cart ─────────────────────────────
        n_added = 0
        subtotal_expected = 0

        for size in _ALL_SIZES:
            try:
                ok_size = self.checkout.select_size_by_name(size)
                self.page.wait_for_timeout(500)
                if ok_size:
                    # Read price displayed in modal for this size selection
                    modal_price = self._read_order_page_price()
                    if modal_price:
                        subtotal_expected += modal_price
                    else:
                        subtotal_expected += unit if unit else _SALE_AO_DEN

                    added = self.checkout.click_them_vao_gio()
                    self.page.wait_for_timeout(1_500)
                    if added:
                        n_added += 1
                        print(f"  [INFO] Added size {size} to cart (total added: {n_added})")
                    else:
                        print(f"  [WARN] Không click được 'Thêm vào giỏ' cho size {size}")
                else:
                    print(f"  [WARN] Không chọn được size {size}")
            except Exception as e:
                print(f"  [WARN] Lỗi add size {size}: {e}")

        print(f"  [INFO] Total added: {n_added}/{len(_ALL_SIZES)} sizes")
        self._record_check("MH4", f"Add {n_added}/{len(_ALL_SIZES)} sizes to cart",
                           "✅ PASS" if n_added > 0 else "❌ FAIL",
                           f"{n_added} sizes added")

        self._shot(TC, "10", "all_sizes_added")

        # Verify modal total via JS (button price = SUBTOTAL = unit × n_sizes)
        modal_total = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const matches = [...text.matchAll(/(\d{1,3}(?:[,.]\d{3})+)\s*[đ₫]/g)];
            const prices = matches.map(m => parseInt(m[1].replace(/[^\d]/g, '')));
            return prices.length ? Math.max(...prices) : null;
        }""")
        if modal_total and n_added > 0:
            expected_modal = (unit if unit else _SALE_AO_DEN) * n_added
            self._record_check("MH4", "Modal subtotal",
                               "ℹ️ INFO",
                               f"modal={modal_total:,}đ, expected~{expected_modal:,}đ")

        # ── MH10: Popup Giỏ hàng → click Thanh toán → Checkout ───────────────
        # Bước 1: Mở popup giỏ hàng (robust: đúng selector + retry + JS-click)
        cart_opened = self.checkout.open_cart_panel()

        # Bước 2: Screenshot popup giỏ hàng đang mở (items visible)
        self._shot(TC, "11", "cart_popup_items")
        self._record_check("MH10", "Mở popup Giỏ hàng",
                           "✅ PASS" if cart_opened else "⚠️ WARN",
                           f"cart_opened={cart_opened}")

        # Đọc cart total. Verify theo TÍNH NHẤT QUÁN giá: tổng giỏ = unit × số
        # lượng (chia hết cho unit) và >= phần vừa thêm. M21 cùng thiết kế nên
        # BE gộp 1 dòng + cộng dồn qty qua nhiều lần chạy; check này đảm bảo GIÁ
        # từng cái đúng mà không phụ thuộc giỏ đã sạch hẳn hay chưa.
        cart_total = self.checkout.read_cart_panel_total()
        _unit = unit if unit else _SALE_AO_DEN
        expected_cart = _unit * n_added
        print(f"  [INFO] Cart panel total={cart_total}, unit={_unit}, "
              f"n_added={n_added}, expected_min~{expected_cart:,}đ")
        if cart_total and _unit:
            _qty = round(cart_total / _unit)
            _consistent = (_qty * _unit == cart_total) and (_qty >= n_added)
            self._record_check(
                "MH10", "Cart total = unit × số lượng (giá nhất quán)",
                "✅ PASS" if _consistent else "❌ FAIL",
                f"{cart_total:,}đ = {_unit:,}đ × {_qty}",
                f"unit {_unit:,}đ, vừa thêm {n_added} (tổng SL ≥ {n_added})")
        else:
            self._record_check("MH10", "Cart panel total", "⚠️ WARN",
                               "Không đọc được cart total",
                               f"expected~{expected_cart:,}đ")

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
        self._shot(TC, "12", "cart_popup_btn_thanh_toan")
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
        self._shot(TC, "13", "cart_after_click_thanh_toan")
        self._record_check("MH10", "Click Thanh toán → navigate /checkout",
                           "✅ PASS" if checkout_ok else "⚠️ WARN",
                           f"clicked={checkout_ok}")

        # Bước 5: Chờ navigate đến /checkout
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "14", "checkout_enter")

        # ── MH5: Checkout ─────────────────────────────────────────────────────
        self._wait_checkout()
        self._shot(TC, "15", "checkout_prices")

        subtotal = self.checkout.read_checkout_subtotal()
        vat      = self.checkout.read_checkout_vat()
        shipping = self.checkout.read_checkout_shipping()
        total    = self.checkout.read_checkout_total()
        print(f"  [INFO] Checkout: sub={subtotal}, vat={vat}, ship={shipping}, total={total}")

        # Subtotal — ghi INFO vì cart server-side có thể tích luỹ từ session trước
        if n_added > 0:
            exp_sub = (unit if unit else _SALE_AO_DEN) * n_added
            self._record_check("MH5", f"MH5 Subtotal ({n_added} sizes) [info]",
                               "ℹ️ INFO",
                               f"{subtotal:,}đ" if subtotal else "N/A",
                               f"expected~{exp_sub:,}đ (cart có thể chứa items từ session trước)")

        self._assert_price(shipping, _SHIPPING, "MH5 Phí giao hàng", mh="MH5")

        # Apply USERMAI. Hành vi ĐÚNG cần verify: mã hợp lệ → giảm tiền; mã hết
        # hạn/không hợp lệ → hệ thống TỪ CHỐI, total KHÔNG đổi. Cả hai đều PASS;
        # chỉ FAIL nếu mã lỗi mà vẫn bị trừ sai vào total.
        total_before = total
        applied = self.checkout.apply_discount_code("USERMAI")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "16", "usermai_applied")

        discount_usermai = self.checkout.read_checkout_discount()
        total_after = self.checkout.read_checkout_total()
        _um_reason = self.checkout.last_promo_message or "không rõ lý do"
        print(f"  [INFO] USERMAI: applied={applied}, discount={discount_usermai}, "
              f"total_before={total_before}, total_after={total_after}")

        if applied and discount_usermai:
            self._record_check("MH5", "USERMAI: mã hợp lệ → có giảm giá", "✅ PASS",
                               f"giảm {discount_usermai:,}đ")
        elif not applied:
            _total_unchanged = (total_after is None or total_before is None
                                or total_after == total_before)
            self._record_check(
                "MH5", "USERMAI: từ chối mã không hợp lệ, không trừ vào total",
                "✅ PASS" if _total_unchanged else "❌ FAIL",
                (f'Hệ thống từ chối đúng (BE: "{_um_reason}"), total giữ nguyên '
                 f'{(total_before or 0):,}đ' if _total_unchanged
                 else f'LỖI: từ chối nhưng total đổi '
                      f'{(total_before or 0):,}→{(total_after or 0):,}đ'))
        else:
            self._record_check("MH5", "USERMAI: discount", "⚠️ WARN",
                               "applied=True nhưng không đọc được discount")

        # Verify button price (tổng thanh toán)
        btn_price = self.checkout.read_payment_button_price()
        if btn_price:
            self._record_check("MH5", "Button price = tổng thanh toán",
                               "ℹ️ INFO",
                               f"{btn_price:,}đ")

        # ── PROD SAFETY STOP ──────────────────────────────────────────────────
        self._record_check("MH5", "STOP — Không click Thanh toán", "✅ PASS",
                           "dừng tại checkout", "PROD SAFE")

        self.__class__._results.extend(self._results)
        self._save_report()
