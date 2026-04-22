"""Home Page Object — https://shop.tryonic.ai/"""

from playwright.sync_api import Page, Locator
from .base_page import BasePage
from .components.header import HeaderComponent


class HomePage(BasePage):
    """Trang chủ: AI prompt input, nút Tạo ngay, category filters."""

    MH_DIR = "MH01_home"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)
        self.header = HeaderComponent(page)

    # ── Locators ─────────────────────────────────────────────────────────────

    @property
    def prompt_input(self) -> Locator:
        return self.page.locator(
            "input[placeholder*='Bạn muốn'], input[placeholder*='Ban muon'], "
            "input[placeholder*='ý tưởng'], input[placeholder*='y tuong'], "
            "textarea[placeholder*='Bạn'], textarea[placeholder*='ý tưởng']"
        ).first

    @property
    def generate_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Tạo ngay'), button:has-text('Tao ngay'), "
            "button:has-text('Tạo'), button:has-text('Tao')"
        ).first

    @property
    def tao_ngay_button(self) -> Locator:
        """Nút 'Tạo ngay' / 'Bắt đầu thiết kế' để navigate vào Studio sau khi đã login."""
        return self.page.locator(
            "button:has-text('Tạo ngay'), a:has-text('Tạo ngay'), "
            "button:has-text('Bắt đầu tạo'), a:has-text('Bắt đầu thiết kế')"
        ).first

    # Category filter buttons
    @property
    def cat_anime(self) -> Locator:
        return self.page.locator('span:has-text("Anime")').last

    @property
    def cat_ink(self) -> Locator:
        return self.page.locator('span:has-text("Thủy mặc")').last

    @property
    def cat_shape(self) -> Locator:
        return self.page.locator('span:has-text("Hình khối")').last

    @property
    def cat_street(self) -> Locator:
        return self.page.locator('span:has-text("Đường phố")').last

    @property
    def cat_abstract(self) -> Locator:
        return self.page.locator('span:has-text("Trừu tượng")').last

    @property
    def cat_3d(self) -> Locator:
        return self.page.locator('span:has-text("Siêu thực/3D")').last

    # ── Actions ──────────────────────────────────────────────────────────────

    def navigate(self) -> None:
        self.goto("")

    def fill_prompt(self, text: str) -> None:
        self.prompt_input.click()
        self.prompt_input.fill(text)
        self.page.wait_for_timeout(300)

    def click_generate(self) -> None:
        self.generate_button.click()

    def generate(self, prompt: str) -> None:
        """Fill prompt và click Tạo ngay."""
        self.fill_prompt(prompt)
        self.click_generate()

    def click_tao_ngay_to_studio(self, tc_id: str = "") -> None:
        """Click Tạo ngay → chờ navigate vào /studio. Raise nếu thất bại."""
        if self.base_url and self.base_url not in self.page.url:
            self.navigate()

        assert self.tao_ngay_button.is_visible(timeout=10_000), (
            f"{tc_id} FAIL: Không tìm thấy nút 'Tạo ngay' sau khi đăng nhập"
        )
        self.tao_ngay_button.click()
        try:
            self.page.wait_for_url("**/studio**", timeout=15_000)
        except Exception:
            pass
        self.page.wait_for_timeout(3000)
        assert "studio" in self.page.url, (
            f"{tc_id} FAIL: Sau 'Tạo ngay' không navigate vào Studio. URL: {self.page.url}"
        )
        if tc_id:
            print(f"  [INFO] {tc_id}: Vào Studio thành công — {self.page.url}")

    def select_category(self, name: str) -> None:
        category_map = {
            "Anime": self.cat_anime,
            "Thủy mặc": self.cat_ink,
            "Hình khối": self.cat_shape,
            "Đường phố": self.cat_street,
            "Trừu tượng": self.cat_abstract,
            "3D": self.cat_3d,
        }
        if name not in category_map:
            raise ValueError(f"Category '{name}' không tồn tại.")
        # dispatch_event bypasses pointer-events:none trên overlay span
        category_map[name].dispatch_event("click")
