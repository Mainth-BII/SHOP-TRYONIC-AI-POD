"""E2E — Khách đặt đơn COD trên TEST (login→thiết kế→giỏ→checkout→COD→success).

Test mỏng: dùng flows/customer_order_flow. Env khóa = test (conftest).
"""
from __future__ import annotations
import re
import pytest

from production.daily.base_daily_test import BaseDailyTest
from e2e.flows.customer_order_flow import place_cod_order

TC = "e2e_full_flow"


class TestE2EFullFlow(BaseDailyTest):
    _SUITE_NAME = "E2E_FULL_FLOW"
    _REPORT_TITLE = "E2E Full Flow (TEST) — Design → COD Order"
    _results = []

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_list_page, product_detail_page,
               studio_page, checkout_page, env, page):
        self.home, self.listing, self.detail = home_page, product_list_page, product_detail_page
        self.studio, self.checkout = studio_page, checkout_page
        self.env, self.page = env, page
        self._results = []
        self.__class__._results = []
        self._setup_prod_safety()

    def _login(self):
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials TEST")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    @pytest.mark.e2e
    def test_full_flow(self):
        assert self.env.name == "test", f"🚫 E2E chỉ chạy TEST, đang {self.env.name}"

        r = place_cod_order(self, TC)
        code, total, pay, url = r["code"], r["total"], r["payment_method"], r["url"]

        self._record_check("E1", "Đặt hàng → /checkout/success",
                           "✅ PASS" if "/checkout/success" in (url or "") else "❌ FAIL", url)

        code_ok = bool(code and re.match(r"^POD-\d{8}-\d+$", code))
        self._record_check("E2", "Đơn hàng đã tạo (order code)",
                           "✅ PASS" if code_ok else "❌ FAIL", code or "N/A",
                           "POD-YYYYMMDD-NNN")
        assert code_ok, f"Order code không hợp lệ: {code}"

        self._record_check("E3", "Phương thức = COD",
                           "✅ PASS" if pay == "COD" else "❌ FAIL", str(pay), "COD")
        assert pay == "COD", f"paymentMethod != COD: {pay}"

        if total:
            self._record_check("E4", "Tổng tiền (success URL)", "ℹ️ INFO", f"{total:,}đ")

        self.__class__._results.extend(self._results)
        self._save_report()
