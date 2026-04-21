"""
Smoke — MH05: Tài khoản & Đơn hàng (Smoke)
TC_DAILY_012 · TC_DAILY_013

Chay: pytest tests/smoke/test_smoke_mh05_profile.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH05Profile(BaseSmokeTest):
    """MH05 — Profile / Orders (Smoke): /profile va /my-orders khong 404/500."""

    _MH_DIR = "MH05_profile"
    _TC_IDS = ["TC_DAILY_012", "TC_DAILY_013"]

    # ── TC_DAILY_012 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_012_profile_page(self, page: Page, base_url: str):
        """TC_DAILY_012 — Trang Profile: load duoc hoac redirect ve login (khong 404/500)."""
        page.goto(f"{base_url}/profile", wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_012", "1", "profile_page")

        assert not page.locator(
            ":text('404'), :text('Not Found'), :text('500'), :text('Internal Server Error')"
        ).is_visible(), \
            f"TC_DAILY_012 FAIL: Trang /profile tra ve loi. URL: {page.url}"

        profile_or_redirect = (
            page.locator(
                ":text('Hồ sơ'), :text('Ho so'), :text('Profile'), "
                ":text('Tài khoản'), :text('Tai khoan')"
            ).first.is_visible(timeout=3000)
            or page.locator("div[role='dialog'], input[type='email']").first.is_visible(timeout=3000)
            or page.url in (base_url, base_url + "/", f"{base_url}/login")
            or "login" in page.url or "auth" in page.url
        )
        assert profile_or_redirect, \
            f"TC_DAILY_012 FAIL: Trang /profile khong load duoc va khong redirect. URL: {page.url}"
        print(f"  [PASS] /profile: URL={page.url} (profile hien thi hoac redirect dung)")

    # ── TC_DAILY_013 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_013_my_orders_page(self, page: Page, base_url: str):
        """TC_DAILY_013 — Trang My Orders: load duoc hoac redirect ve login (khong 404/500)."""
        page.goto(f"{base_url}/my-orders", wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_013", "1", "my_orders_page")

        assert not page.locator(
            ":text('404'), :text('Not Found'), :text('500'), :text('Internal Server Error')"
        ).is_visible(), \
            f"TC_DAILY_013 FAIL: Trang /my-orders tra ve loi. URL: {page.url}"

        orders_or_redirect = (
            page.locator(
                ":text('Đơn hàng'), :text('Don hang'), :text('Orders'), "
                ":text('Lịch sử'), :text('Lich su')"
            ).first.is_visible(timeout=3000)
            or page.locator("div[role='dialog'], input[type='email']").first.is_visible(timeout=3000)
            or page.url in (base_url, base_url + "/", f"{base_url}/login")
            or "login" in page.url or "auth" in page.url
        )
        assert orders_or_redirect, \
            f"TC_DAILY_013 FAIL: Trang /my-orders khong load va khong redirect. URL: {page.url}"
        print(f"  [PASS] /my-orders: URL={page.url} (orders hien thi hoac redirect dung)")
