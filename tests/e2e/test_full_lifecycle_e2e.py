"""E2E FULL LIFECYCLE — CHỈ chạy trên TEST (env khóa ở tests/e2e/conftest.py).

Khách đặt COD → Admin: Xác nhận → Lệnh in → Tạo+Duyệt vận đơn ViettelPost →
Đang giao → Đã giao. Verify mỗi bước đổi trạng thái có email gửi khách (Yopmail).
Dọn vận đơn cuối. Test mỏng — logic nằm trong flows/ + pages/admin/, pages/external/.

3 context tách biệt: khách (self.page), admin, yopmail.
"""
from __future__ import annotations
import pytest

from production.daily.base_daily_test import BaseDailyTest
from pages.admin.admin_login_page import AdminLoginPage
from pages.external.yopmail_inbox import YopmailInbox
from e2e.flows.customer_order_flow import place_cod_order
from e2e.flows.admin_fulfillment_flow import AdminFulfillmentFlow

TC = "e2e_lifecycle"


class TestE2ELifecycle(BaseDailyTest):
    _SUITE_NAME = "E2E_LIFECYCLE"
    _REPORT_TITLE = "E2E Full Lifecycle (TEST) — Order→Confirm→Print→Ship→Deliver + Email"
    _results = []

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_list_page, product_detail_page,
               studio_page, checkout_page, env, page, browser):
        self.home, self.listing, self.detail = home_page, product_list_page, product_detail_page
        self.studio, self.checkout = studio_page, checkout_page
        self.env, self.page, self.browser = env, page, browser
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
    def test_lifecycle(self):
        env = self.env
        assert env.name == "test", f"🚫 E2E chỉ chạy TEST, đang {env.name}"
        if not env.admin_email or not env.admin_password:
            # Ghi WARN vào report TRƯỚC khi skip → notify hiện rõ suite này bị bỏ
            # qua vì thiếu creds (thay vì biến mất lặng lẽ khỏi report).
            self._record_check(
                "L0", "Admin credentials", "⚠️ WARN",
                "Thiếu ADMIN_TEST_EMAIL/ADMIN_TEST_PASSWORD → BỎ QUA luồng Admin",
                "set 2 secret này trong CI (Settings → Secrets)",
            )
            self.__class__._results = list(self._results)
            self._save_report()
            pytest.skip("Thiếu admin credentials TEST (ADMIN_TEST_EMAIL/PASSWORD)")

        # L1 — khách đặt COD
        r = place_cod_order(self, TC)
        code = r["code"]
        self._record_check("L1", "Khách đặt đơn COD", "✅ PASS" if code else "❌ FAIL",
                           f"{code} / total={r['total']} / {r['payment_method']}")
        assert code, "Không tạo được đơn COD"

        # L2 — admin login (context riêng, auto-accept confirm())
        admin_page = self.browser.new_context(
            locale="vi-VN", viewport={"width": 1440, "height": 900}).new_page()
        admin_page.on("dialog", lambda d: d.accept())
        logged = AdminLoginPage(admin_page, env.admin_url).login(
            env.admin_email, env.admin_password)
        self._record_check("L2", "Login admin", "✅ PASS" if logged else "⚠️ WARN",
                           env.admin_email)

        # Yopmail (context riêng)
        yop = YopmailInbox(self.browser.new_context(
            locale="en-US", viewport={"width": 1280, "height": 900}).new_page())
        yop.open(env.login_email)

        # L3–L8 — admin fulfillment + verify email từng bước
        AdminFulfillmentFlow(admin_page, env.admin_url, yop, self._record_check).run(code)

        self.__class__._results.extend(self._results)
        self._save_report()
