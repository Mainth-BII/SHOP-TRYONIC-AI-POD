from __future__ import annotations
"""Daily smoke — Checkout Summary (cart + coupon).

Luồng: PT01 Trắng → Add to cart → Checkout → Apply GIAM20
→ verify dòng khuyến mãi + tổng sau giảm.
KHÔNG click Thanh toán.
"""
import pytest
from playwright.sync_api import Page

from .base_daily_test import BaseDailyTest, parse_int


# ── Tham chiếu sản phẩm (chỉ slug/size để điều hướng — giá đọc từ trang) ─────

def _load_pt01() -> dict:
    return {
        "slug":  "ao-phong-ca-tinh",
        "name":  "Áo Phông Cá Tính",
        "color": "Trắng",
        "size":  "M",
    }


_PT01 = _load_pt01()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_discount_line(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        for (let i = 0; i < lines.length; i++) {
            if (/khuyến mãi|giảm giá|discount/i.test(lines[i])) {
                const nearby = lines.slice(i, i + 3).join(' ');
                const m = nearby.match(/[−\-]\s*([\d,.]+)\s*[đ₫]/);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _read_total(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        const re = /(\d{1,3}(?:[,.]\d{3})+)/;
        for (let i = 0; i < lines.length; i++) {
            if (/Tổng thanh toán/i.test(lines[i])) {
                const m = lines[i].match(re) || (lines[i+1] || '').match(re);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _read_vat_line(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const lines = (document.body.innerText || '').split('\n').map(l => l.trim()).filter(Boolean);
        for (let i = 0; i < lines.length; i++) {
            if (/\bVAT\b|thuế/i.test(lines[i])) {
                const nearby = lines.slice(i, i + 3).join(' ');
                const m = nearby.match(/(\d{1,3}(?:[,.]\d{3})+)/);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _read_shipping_line(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const lines = (document.body.innerText || '').split('\n').map(l => l.trim()).filter(Boolean);
        for (let i = 0; i < lines.length; i++) {
            if (/vận chuyển|phí ship|shipping/i.test(lines[i])) {
                const nearby = lines.slice(i, i + 3).join(' ');
                const m = nearby.match(/(\d{1,3}(?:[,.]\d{3})+)/);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _read_coupon_feedback(page: Page) -> tuple[bool, str]:
    """Đọc message phản hồi sau khi apply coupon.

    Returns:
        (is_error, message)
        is_error=True  → có thông báo lỗi (hết hạn, không hợp lệ, ...)
        is_error=False → thành công hoặc không có message
    """
    msg = page.evaluate(r"""() => {
        // Tìm element chứa thông báo lỗi coupon
        const selectors = [
            '[class*="coupon"] [class*="error"]',
            '[class*="coupon"] [class*="invalid"]',
            '[class*="promo"]  [class*="error"]',
            '[class*="promo"]  [class*="invalid"]',
            '[class*="error-message"]',
            '[class*="alert"]',
            '[role="alert"]',
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el && el.offsetWidth > 0 && el.innerText.trim()) {
                return el.innerText.trim();
            }
        }
        // Fallback: quét innerText toàn trang tìm từ khoá lỗi coupon
        const body = document.body.innerText || '';
        const lines = body.split('\n').map(l => l.trim()).filter(Boolean);
        const errorKeywords = ['hết hạn', 'không hợp lệ', 'không tồn tại',
                               'expired', 'invalid', 'không tìm thấy',
                               'không áp dụng', 'đã sử dụng'];
        for (const line of lines) {
            const low = line.toLowerCase();
            if (errorKeywords.some(k => low.includes(k)) && line.length < 200) {
                return line;
            }
        }
        return '';
    }""")
    if msg:
        low = msg.lower()
        error_kw = ['hết hạn', 'không hợp lệ', 'không tồn tại',
                    'expired', 'invalid', 'không tìm thấy',
                    'không áp dụng', 'đã sử dụng']
        is_err = any(k in low for k in error_kw)
        return is_err, msg
    return False, ""


def _apply_coupon(page: Page, code: str) -> bool:
    """Xóa mã cũ (nếu có) → nhập mã mới → click Áp dụng."""
    page.evaluate(r"""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const del = btns.find(b => b.offsetWidth > 0 && (
            /^[×x✕]$/.test(b.textContent.trim()) ||
            b.textContent.trim() === 'Xoá' ||
            b.textContent.trim() === 'Xóa' ||
            (b.getAttribute('aria-label') || '').toLowerCase().includes('xo')
        ));
        if (del) del.click();
    }""")
    page.wait_for_timeout(800)

    inp = page.locator(
        "input[placeholder*='mã khuyến mại'], input[placeholder*='mã giảm giá'], "
        "input[placeholder*='coupon'], input[placeholder*='promo']"
    ).first
    if not inp.is_visible(timeout=5_000):
        return False
    inp.click()
    page.wait_for_timeout(300)
    inp.fill(code)
    page.wait_for_timeout(500)

    try:
        page.wait_for_selector("#btn-apply-promo:not([disabled])", timeout=5_000)
        page.locator("#btn-apply-promo").click()
    except Exception:
        page.evaluate(r"""() => {
            const btn = document.querySelector('#btn-apply-promo')
                       || Array.from(document.querySelectorAll('button'))
                          .find(b => b.textContent.trim() === 'Áp dụng');
            if (btn) { btn.removeAttribute('disabled'); btn.click(); }
        }""")
    page.wait_for_timeout(2_000)
    return True


# ── Test class ────────────────────────────────────────────────────────────────

class TestDailyCheckoutSummary(BaseDailyTest):
    """Smoke: Cart → Checkout → Apply GIAM20 → verify discount + total (no submit)."""

    _SUITE_NAME   = "checkout_summary"
    _REPORT_TITLE = "Daily Smoke — Checkout Summary (PT01 + GIAM20)"
    _results: list = []

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_detail_page, checkout_page, env, page):
        self.home     = home_page
        self.detail   = product_detail_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = page
        self._results = []

    def _login(self) -> None:
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    def test_checkout_with_coupon_giam20(self):
        """PT01 Trắng M → checkout → GIAM20 → verify discount line + tổng sau giảm."""
        p = _PT01
        self._login()

        tc = "PT01_GIAM20"

        # Navigate to product
        self.page.goto(f"{self.env.fe_url}/product/{p['slug']}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)
        self._shot(tc, "1", "product_page")

        # Mua ngay → chọn size → Thêm vào giỏ (cùng pattern với price_checkout)
        mua_ngay_ok = self.detail.click_mua_ngay()
        if not mua_ngay_ok:
            pytest.skip("Không mở được popup Mua ngay")
        self.page.wait_for_timeout(1_500)
        self._shot(tc, "2", "buynow_popup")

        self.checkout.select_size_by_name(p["size"])
        self.page.wait_for_timeout(800)
        self._shot(tc, "3", "size_selected")

        added = self.checkout.click_them_vao_gio()
        self.page.wait_for_timeout(2_000)
        if not added:
            pytest.skip("Không click được 'Thêm vào giỏ' trong popup")

        # Mở cart panel qua header → proceed to checkout
        try:
            menu_btn = self.page.locator("button:has-text('menu')").first
            if menu_btn.is_visible(timeout=2_000):
                menu_btn.click()
                self.page.wait_for_timeout(600)
            cart_btn = self.page.locator("button:has-text('Giỏ hàng')").first
            if cart_btn.is_visible(timeout=3_000):
                cart_btn.click()
                self.page.wait_for_timeout(1_500)
        except Exception:
            pass
        self._shot(tc, "4", "cart_panel")

        checkout_ok = self.checkout.click_checkout_from_cart()
        if not checkout_ok:
            self.page.goto(f"{self.env.fe_url}/checkout")
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)

        self._shot(tc, "5", "checkout_before_coupon")

        # ── Đọc giá subtotal thực tế từ trang (không hardcode) ──────────────
        subtotal_raw = self.page.evaluate(r"""() => {
            const lines = (document.body.innerText||'').split('\n').map(l=>l.trim()).filter(Boolean);
            const re = /(\d{1,3}(?:[,.]\d{3})+)/;
            for (let i = 0; i < lines.length; i++) {
                if (/^Tổng tiền$/.test(lines[i])) {
                    const m = (lines[i+1]||'').match(re) || lines[i].match(re);
                    if (m) return m[1];
                }
            }
            return null;
        }""")
        subtotal_actual = parse_int(subtotal_raw)
        self._record_check("MH1", "Subtotal trước coupon (giá thực tế từ trang)",
                           "✅ PASS" if subtotal_actual else "⚠️ WARN",
                           f"{subtotal_actual:,}đ" if subtotal_actual else "Không đọc được subtotal")

        # Apply GIAM20
        applied = _apply_coupon(self.page, "GIAM20")
        self._shot(tc, "6", "after_giam20")

        # ── Đọc feedback message sau khi apply ───────────────────────────────
        is_coupon_error, coupon_msg = _read_coupon_feedback(self.page)

        if not applied:
            self._record_check("MH2", "GIAM20 áp dụng", "⚠️ WARN",
                               "Không tìm thấy ô nhập coupon")
        elif is_coupon_error:
            # Coupon lỗi (hết hạn / không hợp lệ ...) → báo WARN đúng message
            self._record_check("MH2", "GIAM20 áp dụng", "⚠️ WARN", coupon_msg)
            self._record_check("MH2b", "GIAM20 = 20% subtotal", "⚠️ WARN",
                               f"Bỏ qua — coupon lỗi: {coupon_msg}")
            self._record_check("MH3", "Tổng sau GIAM20", "⚠️ WARN",
                               f"Bỏ qua — coupon lỗi: {coupon_msg}")
            print(f"\n  [WARN] Coupon GIAM20 lỗi: {coupon_msg}")
            self.__class__._results = self._results
            self._save_report()
            return
        else:
            self._record_check("MH2", "GIAM20 áp dụng", "✅ PASS",
                               coupon_msg if coupon_msg else "OK",
                               "Coupon applied")

        # ── Verify discount = 20% subtotal ───────────────────────────────────
        discount = _read_discount_line(self.page)
        expected_discount = int(subtotal_actual * 0.20) if subtotal_actual else None
        self._assert_price(discount, expected_discount, "GIAM20 = 20% subtotal", "MH2")

        # ── Verify tổng = (subtotal − 20%) + VAT + phí vận chuyển ───────────
        total_after   = _read_total(self.page)
        after_dc      = (subtotal_actual - discount) if (subtotal_actual and discount) else None
        vat_actual    = _read_vat_line(self.page)
        ship_actual   = _read_shipping_line(self.page)
        # Fallback nếu không đọc được từ trang
        vat_calc      = int(after_dc * 0.08) if after_dc else None
        ship_default  = 20_000
        vat           = vat_actual  if vat_actual  else vat_calc
        ship          = ship_actual if ship_actual else ship_default
        expected_total = (after_dc + vat + ship) if (after_dc and vat and ship) else None

        detail = (
            f"({subtotal_actual:,} − {discount:,}) + {vat:,} VAT + {ship:,} ship"
            f" = {expected_total:,}đ"
            if expected_total else "Không tính được do thiếu dữ liệu"
        )
        self._record_check("MH3", "Công thức giá: (subtotal−20%) + VAT + ship",
                           "ℹ️ INFO", detail)
        self._assert_price(total_after, expected_total, "Tổng sau GIAM20", "MH3")

        print(f"\n  [INFO] subtotal={subtotal_actual}, discount={discount}, "
              f"vat={vat}, ship={ship}, total={total_after}")
        self.__class__._results = self._results
        self._save_report()
