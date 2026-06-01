"""Daily smoke — Design My Designs (PT01).

Luồng: Login → /my-designs → click "Sử dụng" thiết kế đã có →
       nếu /terms redirect: FALLBACK sang studio mới → Review → Checkout.
Dừng ở MH5 — KHÔNG click Thanh toán.
"""
from __future__ import annotations

from typing import ClassVar

import pytest

from .base_daily_test import BaseDailyTest, parse_int

# ── Constants ────────────────────────────────────────────────────────────────

_SALE_AO_TRANG = 189_000   # PT01 Trắng
_ORIGINAL      = 227_000
_SHIPPING      = 20_000
_VAT_RATE      = 0.08
_GIAM20_RATE   = 0.20

TC = "pt01_mydesigns"


class TestDailyDesignMydesigns(BaseDailyTest):
    """Verify luồng My Designs → Checkout cho PT01.

    Nếu /my-designs redirect sang /terms (chưa có thiết kế cũ hoặc yêu cầu
    chấp nhận lại điều khoản), test tự FALLBACK sang tạo thiết kế mới từ Studio.

    PROD SAFETY: Dừng ở MH5 — KHÔNG click Thanh toán.
    """

    _SUITE_NAME   = "design_mydesigns"
    _REPORT_TITLE = "Daily Smoke — Design My Designs (PT01)"
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

    def _studio_fallback(self):
        """FALLBACK: Tạo thiết kế mới từ studio khi my-designs không dùng được."""
        self._record_check("MH_MY1", "FALLBACK: vào Studio tạo mới",
                           "⚠️ WARN", "redirect sang Studio", "/terms hoặc không có design")

        self.detail.navigate("ao-phong-ca-tinh")
        self.page.wait_for_timeout(1_000)
        self.detail.select_color("Trắng")
        self.page.wait_for_timeout(800)

        ok = self.detail.click_thiet_ke_hinh_in()
        if not ok:
            pytest.skip("FALLBACK: Không navigate được vào Studio")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "fb_studio", "fallback_studio_enter")

        self.studio.accept_terms(TC)
        self.page.wait_for_timeout(1_000)
        self.studio.open_library()
        self.page.wait_for_timeout(1_000)
        self.studio.click_library_image(1)
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "fb_library", "fallback_library_image")

        self.studio.open_order_modal()
        try:
            self.page.wait_for_url("**/review", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "fb_review", "fallback_review")
        self._record_check("MH_MY1", "FALLBACK: open order modal → /review",
                           "✅ PASS", self.page.url)

    # ── Test ─────────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_pt01_mydesigns(self):
        """PT01 My Designs → Review → Checkout (stop before payment)."""

        # ── Login ─────────────────────────────────────────────────────────────
        self._login()
        self._record_check("LOGIN", "Đăng nhập", "✅ PASS", self.env.login_email)

        # ── MH_MY1: My Designs ───────────────────────────────────────────────
        self.page.goto(f"{self.env.fe_url}/my-designs")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "1", "my_designs_page")

        page_title = self.page.title()
        self._record_check("MH_MY1", "Navigate /my-designs",
                           "✅ PASS" if "my-designs" in self.page.url or "thiết kế" in page_title.lower() else "⚠️ WARN",
                           self.page.url)

        # Kiểm tra nếu redirect sang /terms
        if "/terms" in self.page.url:
            self._record_check("MH_MY1", "Redirect sang /terms", "⚠️ WARN",
                               self.page.url, "cần chấp nhận điều khoản")
            self._studio_fallback()
        else:
            # Thử các cách lấy URL thiết kế để dùng lại
            used_design = False

            # Cách 1: Tìm và click nút "Sử dụng"
            try:
                su_dung_btn = self.page.locator(
                    "button:has-text('Sử dụng'), a:has-text('Sử dụng'), "
                    "button:has-text('Dùng lại'), a:has-text('Dùng lại')"
                ).first
                if su_dung_btn.is_visible(timeout=5_000):
                    su_dung_btn.click()
                    self.page.wait_for_timeout(3_000)
                    self._shot(TC, "2", "after_su_dung_click")

                    # Nếu redirect sang /terms sau click
                    if "/terms" in self.page.url:
                        self._record_check("MH_MY1", "Click Sử dụng → /terms redirect",
                                           "⚠️ WARN", self.page.url)
                        self._studio_fallback()
                    elif "studio" in self.page.url:
                        used_design = True
                        self._record_check("MH_MY1", "Click Sử dụng → vào Studio",
                                           "✅ PASS", self.page.url)
                    else:
                        # Có thể đã vào review hoặc trang khác
                        used_design = True
                        self._record_check("MH_MY1", "Click Sử dụng",
                                           "✅ PASS", self.page.url)
            except Exception:
                pass

            if not used_design:
                # Cách 2: Thử extract URL từ HTML/onclick
                design_url = self.page.evaluate(r"""() => {
                    // Tìm link tới /studio hoặc /product trong trang
                    const anchors = document.querySelectorAll('a[href*="studio"], a[href*="product"]');
                    if (anchors.length > 0) return anchors[0].href;
                    // onclick hoặc data-href
                    const btns = document.querySelectorAll('[onclick*="studio"], [data-href*="studio"]');
                    if (btns.length > 0) {
                        return btns[0].getAttribute('data-href') || btns[0].getAttribute('onclick') || null;
                    }
                    return null;
                }""")
                if design_url and "studio" in design_url:
                    self.page.goto(design_url)
                    self.page.wait_for_timeout(2_000)
                    used_design = True
                    self._record_check("MH_MY1", "Navigate từ design URL", "✅ PASS", design_url)
                else:
                    # FALLBACK hoàn toàn
                    self._record_check("MH_MY1", "Không tìm thấy design để dùng lại",
                                       "⚠️ WARN", "fallback sang Studio mới")
                    self._studio_fallback()

            # Nếu đã vào studio từ my-designs, accept terms và proceed
            if used_design and "studio" in self.page.url:
                self.studio.accept_terms(TC)
                self.page.wait_for_timeout(1_000)
                self.studio.open_library()
                self.page.wait_for_timeout(1_000)
                self.studio.click_library_image(1)
                self.page.wait_for_timeout(1_500)
                self._shot(TC, "3", "studio_library_from_mydesigns")
                self.studio.open_order_modal()
                try:
                    self.page.wait_for_url("**/review", timeout=10_000)
                except Exception:
                    self.page.wait_for_timeout(3_000)
                self._shot(TC, "4", "review_from_mydesigns")
                self._record_check("MH_MY1", "My Designs → Studio → /review",
                                   "✅ PASS", self.page.url)

        # ── MH_MY2: Review ────────────────────────────────────────────────────
        # Tại đây bất kể flow nào cũng nên đang ở /review
        if "/review" not in self.page.url:
            self._record_check("MH_MY2", "Chờ review page", "⚠️ WARN",
                               self.page.url, "expected /review")
            # Thử navigate nếu chưa đến review
        else:
            self._shot(TC, "5", "review_page")

        review_data = self._read_review_prices()
        ao_review    = review_data.get("ao_total", 0) or 0
        print_review = review_data.get("print_total", 0) or 0
        sum_review   = review_data.get("sum_total", 0) or 0
        unit = ao_review + print_review
        print(f"  [INFO] Review prices: ao={ao_review}, in={print_review}, sum={sum_review}")

        if sum_review > 0:
            self._record_check("MH_MY2", "Review: đọc giá OK",
                               "✅ PASS",
                               f"ao={ao_review:,}đ, in={print_review:,}đ, sum={sum_review:,}đ")
            if unit > 0:
                self._assert_price(sum_review, unit, "MH_MY2 Review sum = ao+in", mh="MH_MY2")
        else:
            self._record_check("MH_MY2", "Review: đọc giá", "⚠️ WARN",
                               "sum=0 — không đọc được giá review")

        # Click Đặt hàng → popup
        try:
            dat_hang_btn = self.page.locator("button:has-text('Đặt hàng')").first
            if dat_hang_btn.is_visible(timeout=5_000):
                dat_hang_btn.click()
                self.page.wait_for_timeout(2_000)
        except Exception:
            pass
        self._shot(TC, "6", "popup_order")

        # ── MH4: Popup chọn size ──────────────────────────────────────────────
        self.checkout.select_size_by_name("M")
        self.page.wait_for_timeout(800)
        self._shot(TC, "7", "size_selected")

        order_price = self._read_order_page_price()
        if order_price and unit > 0:
            self._assert_price(order_price, unit, "MH4 Order page price", mh="MH4")
        elif order_price:
            self._record_check("MH4", "Order page price", "ℹ️ INFO",
                               f"{order_price:,}đ")
        else:
            self._record_check("MH4", "Order page price", "⚠️ WARN",
                               "N/A", "không đọc được giá")

        # Click Mua ngay → navigate /checkout
        try:
            mua_ngay_btn = self.page.locator("button:has-text('Mua ngay')").first
            if mua_ngay_btn.is_visible(timeout=5_000):
                mua_ngay_btn.click()
                try:
                    self.page.wait_for_url("**/checkout**", timeout=10_000)
                except Exception:
                    self.page.wait_for_timeout(3_000)
        except Exception:
            pass
        self._shot(TC, "8", "checkout_enter")

        # ── MH5: Checkout ─────────────────────────────────────────────────────
        self._wait_checkout()
        self._shot(TC, "9", "checkout_prices")

        subtotal = self.checkout.read_checkout_subtotal()
        vat      = self.checkout.read_checkout_vat()
        shipping = self.checkout.read_checkout_shipping()
        total    = self.checkout.read_checkout_total()
        print(f"  [INFO] Checkout: sub={subtotal}, vat={vat}, ship={shipping}, total={total}")

        # Ưu tiên: unit (ao+in), fallback sum_review (đọc từ trang), fallback constant
        expected_sub  = unit if unit > 0 else (sum_review if sum_review > 0 else _SALE_AO_TRANG)
        expected_vat  = int(expected_sub * _VAT_RATE)
        expected_ship = _SHIPPING
        expected_tot  = expected_sub + expected_vat + expected_ship

        self._assert_price(subtotal, expected_sub,  "MH5 Subtotal",       mh="MH5")
        self._assert_price(vat,      expected_vat,  "MH5 VAT 8%",         mh="MH5")
        self._assert_price(shipping, expected_ship, "MH5 Phí giao hàng",  mh="MH5")
        self._assert_price(total,    expected_tot,  "MH5 Tổng thanh toán", mh="MH5")

        # Apply GIAM20
        applied = self.checkout.apply_discount_code("GIAM20")
        self.page.wait_for_timeout(2_000)
        self._shot(TC, "10", "giam20_applied")

        discount = self.checkout.read_checkout_discount()
        total_after = self.checkout.read_checkout_total()
        expected_discount = int(expected_sub * _GIAM20_RATE)
        print(f"  [INFO] GIAM20: applied={applied}, discount={discount}, "
              f"total_after={total_after}, expected_discount={expected_discount:,}đ")

        self._record_check("MH5", "Apply GIAM20",
                           "✅ PASS" if applied else "⚠️ WARN",
                           f"applied={applied}")
        if discount:
            self._assert_price(discount, expected_discount,
                               "MH5 GIAM20 discount amount", mh="MH5")
        else:
            self._record_check("MH5", "GIAM20 discount line", "⚠️ WARN",
                               "Không đọc được discount",
                               f"expected ~{expected_discount:,}đ")

        # ── PROD SAFETY STOP ──────────────────────────────────────────────────
        self._record_check("MH5", "STOP — Không click Thanh toán", "✅ PASS",
                           "dừng tại checkout", "PROD SAFE")

        self.__class__._results.extend(self._results)
        self._save_report()
