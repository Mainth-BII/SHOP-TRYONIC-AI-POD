"""AdminLoginPage — đăng nhập cms-admin (TEST only)."""
from __future__ import annotations
from playwright.sync_api import Page


class AdminLoginPage:
    def __init__(self, page: Page, admin_url: str):
        self.page = page
        self.base = admin_url.rstrip("/")

    def login(self, email: str, pwd: str) -> bool:
        self.page.goto(self.base)
        self.page.wait_for_timeout(2_500)
        try:
            em = self.page.locator(
                "input[type='email'], input[name*='email'], input[placeholder*='mail']"
            ).first
            if em.is_visible(timeout=5_000):
                em.fill(email)
                self.page.locator("input[type='password']").first.fill(pwd)
                self.page.locator(
                    "button[type='submit'], button:has-text('Đăng nhập'), button:has-text('Login')"
                ).first.click()
                self.page.wait_for_timeout(4_000)
        except Exception:
            pass
        # Coi là OK nếu mở được /orders thấy dữ liệu đơn
        self.page.goto(f"{self.base}/orders")
        self.page.wait_for_timeout(2_500)
        return "POD-" in (self.page.content() or "")
