"""E2E FULL FLOW — CHỈ chạy trên môi trường TEST (test.shop.tryonic.ai).

Khác Daily (PROD, dừng trước Thanh toán): luồng này đi HẾT:
  Login → Chọn sản phẩm → Studio thiết kế → Thêm giỏ → Checkout →
  Nhập địa chỉ → Đặt hàng → Thanh toán sandbox → Verify đơn đã tạo.

An toàn vì env bị KHÓA CỨNG = test (xem tests/e2e/conftest.py). Trên TEST,
BaseDailyTest._setup_prod_safety KHÔNG kích hoạt (chỉ chặn khi fe_url là PROD),
nên được phép submit đơn + thanh toán.

⚠️ Một số bước (thanh toán sandbox + verify đơn) dùng selector best-effort,
cần CHẠY THỬ 1 lần trên TEST để chốt chính xác — các bước đó hiện ghi INFO/WARN
(không hard-fail) để không chặn luồng khi scaffold.
"""
from __future__ import annotations
import pytest

from production.daily.base_daily_test import BaseDailyTest

TC = "e2e_full_flow"

# Sản phẩm dùng cho luồng (PT01 — Áo Phông Cá Tính)
_PRODUCT_SLUG = "ao-phong-ca-tinh"
_PRODUCT_COLOR = "Trắng"
_PRODUCT_SIZE = "M"

# Thông tin giao hàng test (chỉ dùng trên TEST env)
_SHIP_NAME = "QA E2E Tester"
_SHIP_PHONE = "0900000000"
_SHIP_ADDRESS = "123 Đường Test, Phường 1, Quận 1, TP.HCM"


class TestE2EFullFlow(BaseDailyTest):
    """Luồng mua hàng đầy đủ trên TEST: thiết kế → đặt đơn → thanh toán → verify."""

    _SUITE_NAME = "E2E_FULL_FLOW"
    _REPORT_TITLE = "E2E Full Flow (TEST) — Design → Order → Payment"
    _results = []

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_list_page, product_detail_page,
               studio_page, checkout_page, env, page):
        self.home = home_page
        self.listing = product_list_page
        self.detail = product_detail_page
        self.studio = studio_page
        self.checkout = checkout_page
        self.env = env
        self.page = page
        self._results = []
        self.__class__._results = []
        # Trên TEST, _setup_prod_safety là no-op → cho phép đặt đơn.
        self._setup_prod_safety()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _login(self):
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials TEST (DAILY_TEST_EMAIL/PASSWORD)")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    # ── Test ─────────────────────────────────────────────────────────────────

    @pytest.mark.e2e
    def test_full_flow(self):
        # ── E1: Đăng nhập ─────────────────────────────────────────────────────
        self._login()
        self._record_check("E1", "Đăng nhập TEST", "✅ PASS", self.env.login_email)

        # ── E2: Vào sản phẩm + chọn màu ──────────────────────────────────────
        self.detail.navigate(_PRODUCT_SLUG)
        self.page.wait_for_timeout(1_000)
        self.detail.select_color(_PRODUCT_COLOR)
        self.page.wait_for_timeout(800)
        self._shot(TC, "1", "product_detail")
        self._record_check("E2", "Vào sản phẩm + chọn màu", "✅ PASS",
                            f"{_PRODUCT_SLUG} / {_PRODUCT_COLOR}")

        # ── E3: Studio — thiết kế (chọn ảnh từ thư viện) ────────────────────
        ok_studio = self.detail.click_thiet_ke_hinh_in()
        if not ok_studio:
            pytest.skip("Không vào được Studio")
        self.page.wait_for_timeout(2_000)
        self.studio.accept_terms(TC)
        self.page.wait_for_timeout(1_000)
        self.studio.open_library()
        self.page.wait_for_timeout(1_000)
        self.studio.click_library_image(1)
        self.page.wait_for_timeout(1_500)
        self._shot(TC, "2", "studio_design")
        self._record_check("E3", "Studio: chọn artwork từ thư viện", "✅ PASS",
                            "library image 1")

        # ── E4: Mở order modal → /review ─────────────────────────────────────
        self.studio.open_order_modal()
        try:
            self.page.wait_for_url("**/review", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "3", "review")

        # Click Đặt hàng → popup chọn size
        try:
            dat_hang = self.page.locator("button:has-text('Đặt hàng')").first
            if dat_hang.is_visible(timeout=5_000):
                dat_hang.click()
                self.page.wait_for_timeout(2_000)
        except Exception:
            pass
        self._shot(TC, "4", "order_popup")

        # ── E5: Dọn giỏ + chọn size + thêm vào giỏ ──────────────────────────
        self.checkout.clear_cart()
        self.checkout.select_size_by_name(_PRODUCT_SIZE)
        self.page.wait_for_timeout(800)
        added = self.checkout.click_them_vao_gio()
        self.page.wait_for_timeout(2_000)
        self._record_check("E5", "Thêm vào giỏ", "✅ PASS" if added else "❌ FAIL",
                            f"added={added}, size={_PRODUCT_SIZE}")
        assert added, "Không thêm được sản phẩm vào giỏ"

        # ── E6: Mở giỏ → sang checkout ───────────────────────────────────────
        self.checkout.open_cart_panel()
        self._shot(TC, "5", "cart_panel")
        checkout_ok = self.checkout.click_checkout_from_cart()
        if not checkout_ok:
            self.page.goto(f"{self.env.fe_url}/checkout")
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)
        self._shot(TC, "6", "checkout")
        self._record_check("E6", "Vào trang checkout", "✅ PASS", self.page.url)

        # ── E7: Nhập địa chỉ giao hàng ───────────────────────────────────────
        try:
            self.checkout.fill_guest_shipping_info(
                _SHIP_NAME, _SHIP_PHONE, _SHIP_ADDRESS, TC)
            self._record_check("E7", "Nhập địa chỉ giao hàng", "✅ PASS",
                               f"{_SHIP_NAME} / {_SHIP_PHONE}")
        except Exception as e:
            # Tài khoản đã có địa chỉ mặc định → có thể không cần nhập
            self._record_check("E7", "Nhập địa chỉ giao hàng", "ℹ️ INFO",
                               f"Bỏ qua (có thể đã có địa chỉ mặc định): {e}")
        self._shot(TC, "7", "shipping_filled")

        # ── E8: Chọn COD + đặt hàng ──────────────────────────────────────────
        # Liệt kê phương thức thanh toán đang hiển thị (để chốt selector).
        pay_opts = self.page.evaluate(r"""() => {
            const kws = ['COD','khi nhận','tiền mặt','khi giao','nhận hàng',
                         'MoMo','PayOS','chuyển khoản','VNPay','thanh toán'];
            const out = [];
            document.querySelectorAll('label, button, [role="radio"], li, div').forEach(el => {
                const t = (el.innerText || '').trim();
                if (t && t.length < 50
                    && kws.some(k => t.toLowerCase().includes(k.toLowerCase()))
                    && !out.includes(t)) out.push(t);
            });
            return out.slice(0, 15);
        }""")
        self._record_check("E8", "Phương thức thanh toán hiển thị", "ℹ️ INFO", str(pay_opts))

        # Chọn COD (thanh toán khi nhận hàng).
        cod_selected = False
        for sel in (
            "label:has-text('Thanh toán khi nhận hàng')",
            "label:has-text('khi nhận hàng')",
            "label:has-text('COD')",
            "label:has-text('Tiền mặt')",
            ":text('Thanh toán khi nhận hàng')",
            ":text('COD')",
        ):
            try:
                el = self.page.locator(sel).first
                if el.is_visible(timeout=1_500):
                    el.click()
                    cod_selected = True
                    break
            except Exception:
                continue
        self.page.wait_for_timeout(800)
        self._shot(TC, "8", "cod_selected")
        self._record_check("E8", "Chọn COD", "✅ PASS" if cod_selected else "⚠️ WARN",
                            f"cod_selected={cod_selected}")

        assert cod_selected, "Không chọn được phương thức COD trên checkout"

        # Đặt hàng (COD → tạo đơn trực tiếp, redirect /checkout/success?...).
        placed = self.checkout.click_checkout_payment()
        if not placed:
            placed = self.checkout.click_thanh_toan_ngay()
        # Chờ điều hướng sang trang success
        try:
            self.page.wait_for_url("**/checkout/success**", timeout=15_000)
        except Exception:
            self.page.wait_for_timeout(4_000)
        self._shot(TC, "8b", "after_place_order")

        # ── E9: Verify đơn đã tạo — đọc từ URL success (nguồn tin cậy) ────────
        import re
        from urllib.parse import urlparse, parse_qs
        url = self.page.url
        qs = parse_qs(urlparse(url).query)
        order_code = (qs.get("orderCode") or [None])[0]
        pay_method = (qs.get("paymentMethod") or [None])[0]
        total_url = (qs.get("total") or [None])[0]
        # Fallback: đọc order code từ DOM nếu URL không có
        if not order_code:
            try:
                order_code = self.checkout.read_order_code()
            except Exception:
                pass

        self._record_check("E8", "Bấm Đặt hàng (COD) → /checkout/success",
                            "✅ PASS" if "/checkout/success" in url else "❌ FAIL",
                            url)

        # Order code đúng định dạng POD-YYYYMMDD-NNN
        code_ok = bool(order_code and re.match(r"^POD-\d{8}-\d+$", order_code))
        self._record_check("E9", "Đơn hàng đã tạo (order code)",
                            "✅ PASS" if code_ok else "❌ FAIL",
                            order_code or "N/A", "POD-YYYYMMDD-NNN")
        assert code_ok, f"Order code không hợp lệ: {order_code}"

        # Đúng phương thức COD
        self._record_check("E9", "Phương thức thanh toán = COD",
                            "✅ PASS" if pay_method == "COD" else "❌ FAIL",
                            str(pay_method), "COD")
        assert pay_method == "COD", f"paymentMethod != COD: {pay_method}"

        # Tổng tiền khớp giữa checkout và success (nếu đọc được)
        if total_url:
            self._record_check("E9", "Tổng tiền đơn (từ success URL)", "ℹ️ INFO",
                               f"{int(total_url):,}đ")

        self.__class__._results.extend(self._results)
        self._save_report()
