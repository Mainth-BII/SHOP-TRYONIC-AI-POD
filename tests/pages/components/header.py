"""Header Component — thanh điều hướng và trạng thái đăng nhập."""

from playwright.sync_api import Page, Locator


class HeaderComponent:
    """Đại diện cho header của shop.tryonic.ai — login state, nav, profile menu."""

    def __init__(self, page: Page):
        self.page = page

    # ── Locators ─────────────────────────────────────────────────────────────

    @property
    def login_button(self) -> Locator:
        return self.page.locator(
            "header :text('Đăng nhập'), header button:has-text('Đăng nhập')"
        ).first

    @property
    def profile_button(self) -> Locator:
        return self.page.locator(
            "header button:has-text('Tryonic'), "
            "header [class*='avatar'], "
            "header button[class*='rounded-full']"
        ).first

    @property
    def logout_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Đăng xuất'), a:has-text('Đăng xuất')"
        ).first

    @property
    def logo(self) -> Locator:
        return self.page.locator("header a[href='/'], header img[alt*='tryonic' i]").first

    @property
    def nav_product(self) -> Locator:
        return self.page.locator(
            "header a:has-text('Sản phẩm'), header a:has-text('San pham')"
        ).first

    # ── State ────────────────────────────────────────────────────────────────

    def is_logged_in(self, timeout: int = 3000) -> bool:
        try:
            return not self.login_button.is_visible(timeout=timeout)
        except Exception:
            return False

    # ── Actions ──────────────────────────────────────────────────────────────

    def click_login(self) -> None:
        self.login_button.click()
        self.page.wait_for_timeout(1000)

    def open_profile_menu(self) -> None:
        self.profile_button.click()
        self.page.wait_for_timeout(800)

    def logout(self) -> None:
        self.open_profile_menu()
        self.logout_button.click()
        self.page.wait_for_timeout(2000)

    def logout_if_needed(self, tc_id: str = "") -> bool:
        """Logout nếu đang đăng nhập. Trả về True nếu đã logout."""
        if self.login_button.is_visible(timeout=3000):
            return False
        if tc_id:
            print(f"  [INFO] {tc_id}: Đang đăng nhập → tự động logout trước")
        try:
            self.logout()
            if tc_id:
                print(f"  [INFO] {tc_id}: Logout thành công")
            return True
        except Exception as e:
            if tc_id:
                print(f"  [WARN] {tc_id}: Không thể logout — {e}")
            return False
