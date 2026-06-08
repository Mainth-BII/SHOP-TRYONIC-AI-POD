"""AdminOrdersPage — màn Quản lý đơn hàng (list + chuyển trạng thái inline).

Chuyển trạng thái LUÔN scope theo đúng dòng đơn (chứa order code) → KHÔNG bao
giờ bấm nhầm đơn khác. Nút inline dạng '→ {label}':
  Chờ xác nhận → "Đã xác nhận" → "Đang in" → "Đang giao" → "Đã giao"
"""
from __future__ import annotations
from playwright.sync_api import Page


class AdminOrdersPage:
    def __init__(self, page: Page, admin_url: str):
        self.page = page
        self.base = admin_url.rstrip("/")

    def goto(self) -> None:
        self.page.goto(f"{self.base}/orders")
        self.page.wait_for_timeout(2_500)

    def _row_selectors(self, code: str) -> list[str]:
        # Container PHẢI chứa order code → an toàn, không trúng đơn khác.
        return [
            f"tr:has-text('{code}')",
            f"[role='row']:has-text('{code}')",
            f"li:has-text('{code}')",
            f"div[class*='row']:has-text('{code}')",
        ]

    def advance_status(self, code: str, next_label: str) -> bool:
        """Bấm '→ {next_label}' trong dòng đúng đơn → modal 'Xác nhận chuyển
        trạng thái?' → bấm 'Xác nhận' (modal React trong trang, KHÔNG phải
        browser dialog). Đây mới thực sự gọi updateStatus. False nếu không thấy."""
        self.goto()
        clicked = False
        for rsel in self._row_selectors(code):
            try:
                btn = self.page.locator(f"{rsel} button:has-text('{next_label}')").first
                if btn.is_visible(timeout=2_000):
                    btn.scroll_into_view_if_needed(timeout=1_500)
                    btn.click()
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            return False
        self.page.wait_for_timeout(800)
        # Modal xác nhận: 'Xác nhận chuyển trạng thái?' / 'Xác nhận hủy đơn?'
        try:
            confirm_btn = self.page.locator(
                "xpath=//*[contains(text(),'Xác nhận chuyển trạng thái') "
                "or contains(text(),'Xác nhận hủy')]"
                "/ancestor::div[.//button[contains(.,'Xác nhận')]][1]"
                "//button[contains(.,'Xác nhận')]"
            ).first
            if confirm_btn.is_visible(timeout=3_000):
                confirm_btn.click()
                self.page.wait_for_timeout(2_500)
                return True
        except Exception:
            pass
        # Fallback: nút 'Xác nhận' đang hiện (của modal)
        try:
            b = self.page.locator("button:has-text('Xác nhận'):visible").last
            if b.is_visible(timeout=2_000):
                b.click()
                self.page.wait_for_timeout(2_500)
                return True
        except Exception:
            pass
        return clicked

    def status_text(self, code: str) -> str:
        """Đọc text dòng đơn (chứa badge trạng thái) để verify."""
        self.goto()
        for rsel in self._row_selectors(code):
            try:
                row = self.page.locator(rsel).first
                if row.is_visible(timeout=2_000):
                    return row.inner_text().replace("\n", " ")
            except Exception:
                continue
        return ""

    def open_detail(self, code: str) -> bool:
        """Mở modal chi tiết đơn (bấm mã đơn)."""
        self.goto()
        try:
            el = self.page.locator(f"text={code}").first
            if el.is_visible(timeout=4_000):
                el.click()
                self.page.wait_for_timeout(2_000)
                return True
        except Exception:
            pass
        return False
