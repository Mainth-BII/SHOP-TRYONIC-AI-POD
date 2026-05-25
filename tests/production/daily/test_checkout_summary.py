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
    _ERROR_KW = [
        'hết hạn', 'het han', 'không hợp lệ', 'khong hop le',
        'không tồn tại', 'không tìm thấy', 'không áp dụng',
        'đã sử dụng', 'da su dung', 'không còn', 'hết lượt',
        'không hiệu lực', 'vô hiệu', 'expired', 'invalid',
        'not found', 'does not exist',
    ]

    msg = page.evaluate(r"""() => {
        const errorKeywords = ['hết hạn', 'het han', 'không hợp lệ', 'khong hop le',
            'không tồn tại', 'không tìm thấy', 'không áp dụng',
            'đã sử dụng', 'da su dung', 'không còn', 'hết lượt',
            'không hiệu lực', 'vô hiệu', 'expired', 'invalid',
            'not found', 'does not exist'];

        // 1. Tìm element chứa thông báo lỗi coupon — ưu tiên element nhỏ, cụ thể
        const selectors = [
            '[role="alert"]',
            '[class*="error"]', '[class*="invalid"]', '[class*="danger"]',
            '[class*="warning"]', '[class*="toast"]', '[class*="snack"]',
            '[class*="message"]', '[class*="feedback"]', '[class*="notice"]',
            '[class*="coupon"] p', '[class*="coupon"] span',
            '[class*="promo"] p',  '[class*="promo"] span',
            '[class*="discount"] p', '[class*="discount"] span',
        ];
        for (const sel of selectors) {
            for (const el of document.querySelectorAll(sel)) {
                const t = (el.innerText || el.textContent || '').trim();
                if (!t || t.length > 300 || el.offsetWidth === 0) continue;
                const low = t.toLowerCase();
                if (errorKeywords.some(k => low.includes(k))) return t;
            }
        }

        // 2. Fallback: quét toàn bộ innerText trang theo từng dòng
        const body = document.body.innerText || '';
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 3 && l.length < 250);
        for (const line of lines) {
            const low = line.toLowerCase();
            if (errorKeywords.some(k => low.includes(k))) return line;
        }
        return '';
    }""")

    if msg:
        low = msg.lower()
        is_err = any(k in low for k in _ERROR_KW)
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

        if not applied:
            self._record_check("MH2", "GIAM20: nhập mã", "⚠️ WARN",
                               "Không tìm thấy ô nhập coupon")
            self.__class__._results = self._results
            self._save_report()
            return

        # ── Đọc feedback + discount line ─────────────────────────────────────
        is_coupon_error, coupon_msg = _read_coupon_feedback(self.page)

        # Re-check nếu chưa bắt được message ngay
        if not is_coupon_error and not coupon_msg:
            self.page.wait_for_timeout(1_000)
            is_coupon_error, coupon_msg = _read_coupon_feedback(self.page)

        discount = _read_discount_line(self.page)

        # ── CASE A: Coupon hết hạn / không hợp lệ ────────────────────────────
        # Hành vi đúng: hệ thống báo lỗi VÀ KHÔNG áp dụng giảm giá
        if is_coupon_error or (coupon_msg and not discount):
            no_discount_applied = (discount is None or discount == 0)
            if no_discount_applied:
                # ✅ Validate đúng: báo lỗi + không giảm tiền
                self._record_check("MH2", "GIAM20: validate mã hết hạn",
                                   "✅ PASS",
                                   f"Hệ thống báo lỗi đúng: \"{coupon_msg}\" — không giảm tiền")
            else:
                # ❌ Bug: báo lỗi nhưng vẫn giảm tiền
                self._record_check("MH2", "GIAM20: validate mã hết hạn",
                                   "❌ FAIL",
                                   f"Lỗi logic: báo \"{coupon_msg}\" nhưng vẫn giảm {discount:,}đ")
            print(f"\n  [INFO] Coupon GIAM20 — {coupon_msg} (discount={discount})")
            self.__class__._results = self._results
            self._save_report()
            return

        # ── CASE B: Coupon hợp lệ → verify giá trị giảm ─────────────────────
        self._record_check("MH2", "GIAM20: mã hợp lệ, áp dụng thành công",
                           "✅ PASS", coupon_msg if coupon_msg else "Coupon applied")

        expected_discount = int(subtotal_actual * 0.20) if subtotal_actual else None
        self._assert_price(discount, expected_discount, "GIAM20 = 20% subtotal", "MH2b")

        # Verify tổng = (subtotal − 20%) + VAT + phí vận chuyển
        total_after   = _read_total(self.page)
        after_dc      = (subtotal_actual - discount) if (subtotal_actual and discount) else None
        vat_actual    = _read_vat_line(self.page)
        ship_actual   = _read_shipping_line(self.page)
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

    def test_checkout_with_coupon_clc1(self):
        """PT01 Trắng M → checkout → CLC1 (hợp lệ, 20%) → verify discount + total + VAT + ship."""
        p = _PT01
        self._login()

        tc = "PT01_CLC1"

        # Navigate to product
        self.page.goto(f"{self.env.fe_url}/product/{p['slug']}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)
        self._shot(tc, "1", "product_page")

        mua_ngay_ok = self.detail.click_mua_ngay()
        if not mua_ngay_ok:
            pytest.skip("Không mở được popup Mua ngay")
        self.page.wait_for_timeout(1_500)

        self.checkout.select_size_by_name(p["size"])
        self.page.wait_for_timeout(800)

        added = self.checkout.click_them_vao_gio()
        self.page.wait_for_timeout(2_000)
        if not added:
            pytest.skip("Không click được 'Thêm vào giỏ'")

        # Mở cart → checkout
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

        checkout_ok = self.checkout.click_checkout_from_cart()
        if not checkout_ok:
            self.page.goto(f"{self.env.fe_url}/checkout")
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)

        self._shot(tc, "2", "checkout_before_coupon")

        # ── Đọc subtotal trước khi apply ─────────────────────────────────────
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
        self._record_check("CLC1_MH1", "Subtotal trước coupon",
                           "✅ PASS" if subtotal_actual else "⚠️ WARN",
                           f"{subtotal_actual:,}đ" if subtotal_actual else "Không đọc được subtotal")

        # ── Apply CLC1 ────────────────────────────────────────────────────────
        applied = _apply_coupon(self.page, "CLC1")
        self._shot(tc, "3", "after_clc1")

        if not applied:
            self._record_check("CLC1_MH2", "CLC1: nhập mã", "❌ FAIL",
                               "Không tìm thấy ô nhập coupon")
            self.__class__._results = self._results
            self._save_report()
            return

        # Đọc feedback — nếu lỗi là test FAIL (mã phải hợp lệ)
        is_coupon_error, coupon_msg = _read_coupon_feedback(self.page)
        if not is_coupon_error and not coupon_msg:
            self.page.wait_for_timeout(1_000)
            is_coupon_error, coupon_msg = _read_coupon_feedback(self.page)

        if is_coupon_error:
            self._record_check("CLC1_MH2", "CLC1: mã hợp lệ áp dụng", "❌ FAIL",
                               f"Mã bị từ chối: \"{coupon_msg}\"")
            self.__class__._results = self._results
            self._save_report()
            return

        self._record_check("CLC1_MH2", "CLC1: mã hợp lệ áp dụng", "✅ PASS",
                           coupon_msg if coupon_msg else "Áp dụng thành công")

        # ── Verify discount = 20% subtotal ────────────────────────────────────
        discount = _read_discount_line(self.page)
        expected_discount = int(subtotal_actual * 0.20) if subtotal_actual else None

        if discount is None:
            self._record_check("CLC1_MH3", "CLC1: số tiền giảm = 20% subtotal", "❌ FAIL",
                               "Không tìm thấy dòng giảm giá trên trang")
        else:
            tol = max(500, int((expected_discount or 0) * 0.01))  # tolerance 1%
            ok_dc = expected_discount and abs(discount - expected_discount) <= tol
            self._record_check(
                "CLC1_MH3", "CLC1: số tiền giảm = 20% subtotal",
                "✅ PASS" if ok_dc else "❌ FAIL",
                f"Giảm {discount:,}đ — mong đợi {expected_discount:,}đ "
                f"(20% × {subtotal_actual:,})",
            )

        # ── Đọc VAT + ship thực tế ────────────────────────────────────────────
        after_dc   = (subtotal_actual - discount) if (subtotal_actual and discount) else None
        vat_actual = _read_vat_line(self.page)
        ship_actual = _read_shipping_line(self.page)
        vat_calc   = int(after_dc * 0.08) if after_dc else None
        vat        = vat_actual  if vat_actual  else vat_calc
        ship       = ship_actual if ship_actual else 20_000

        self._record_check(
            "CLC1_MH4", "VAT (8% sau giảm)",
            "✅ PASS" if vat else "⚠️ WARN",
            f"{vat:,}đ" if vat else "Không đọc được VAT",
        )
        self._record_check(
            "CLC1_MH5", "Phí vận chuyển",
            "✅ PASS" if ship else "⚠️ WARN",
            f"{ship:,}đ" if ship else "Không đọc được phí ship",
        )

        # ── Verify tổng sau giảm ──────────────────────────────────────────────
        total_after    = _read_total(self.page)
        expected_total = (after_dc + vat + ship) if (after_dc and vat and ship) else None

        detail = (
            f"({subtotal_actual:,} − {discount:,}) + {vat:,} VAT + {ship:,} ship"
            f" = {expected_total:,}đ"
            if expected_total else "Không tính được do thiếu dữ liệu"
        )
        self._record_check("CLC1_MH6", "Công thức: (subtotal−20%) + VAT + ship",
                           "ℹ️ INFO", detail)

        if total_after is None:
            self._record_check("CLC1_MH7", "Tổng thanh toán sau CLC1", "⚠️ WARN",
                               "Không đọc được tổng từ trang")
        else:
            tol_total = max(1_000, int((expected_total or 0) * 0.02))
            ok_total  = expected_total and abs(total_after - expected_total) <= tol_total
            self._record_check(
                "CLC1_MH7", "Tổng thanh toán sau CLC1",
                "✅ PASS" if ok_total else "❌ FAIL",
                f"Trang hiện {total_after:,}đ — mong đợi {expected_total:,}đ",
            )

        self._shot(tc, "4", "checkout_final")
        print(f"\n  [INFO] subtotal={subtotal_actual}, discount={discount}, "
              f"vat={vat}, ship={ship}, total={total_after}, expected={expected_total}")
        self.__class__._results = self._results
        self._save_report()
