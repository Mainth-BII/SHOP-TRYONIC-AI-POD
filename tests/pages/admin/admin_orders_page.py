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
        # KHÔNG dùng networkidle (admin có polling → không idle, phí 10s mỗi goto).
        # Độ bền render chậm trên CI do _wait_next_button lo (poll + re-goto).

    def _row_selectors(self, code: str) -> list[str]:
        # Container PHẢI chứa order code → an toàn, không trúng đơn khác.
        return [
            f"tr:has-text('{code}')",
            f"[role='row']:has-text('{code}')",
            f"li:has-text('{code}')",
            f"div[class*='row']:has-text('{code}')",
        ]

    def _has_next_button(self, code: str, next_label: str) -> bool:
        """Nút '→ {next_label}' còn trong dòng đơn không (đang ở /orders sẵn)."""
        for rsel in self._row_selectors(code):
            try:
                b = self.page.locator(f"{rsel} button:has-text('{next_label}')").first
                if b.is_visible(timeout=1_500):
                    return True
            except Exception:
                continue
        return False

    def _row_found(self, code: str) -> bool:
        for rsel in self._row_selectors(code):
            try:
                if self.page.locator(rsel).first.is_visible(timeout=1_500):
                    return True
            except Exception:
                continue
        return False

    def _click_and_confirm(self, code: str, next_label: str) -> bool:
        """Bấm '→ {next_label}' trong dòng đơn + bấm 'Xác nhận' modal."""
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
        confirm_clicked = False
        try:
            cb = self.page.locator(
                "xpath=//*[contains(text(),'Xác nhận chuyển trạng thái') "
                "or contains(text(),'Xác nhận hủy')]"
                "/ancestor::div[.//button[contains(.,'Xác nhận')]][1]"
                "//button[contains(.,'Xác nhận')]"
            ).first
            if cb.is_visible(timeout=3_000):
                cb.click()
                confirm_clicked = True
        except Exception:
            pass
        if not confirm_clicked:
            try:
                b = self.page.locator("button:has-text('Xác nhận'):visible").last
                if b.is_visible(timeout=2_000):
                    b.click()
                    confirm_clicked = True
            except Exception:
                pass
        # QUAN TRỌNG: request updateStatus CHẬM (nút hiện 'Đang xử lý...'). Phải
        # CHỜ modal đóng (request xong) rồi mới reload — reload sớm sẽ ABORT
        # request đang chạy → transition không lưu (nguồn flaky chính).
        if confirm_clicked:
            try:
                self.page.wait_for_function(
                    "() => !document.body.innerText.includes('Xác nhận chuyển trạng thái') "
                    "&& !document.body.innerText.includes('Đang xử lý')",
                    timeout=20_000,
                )
            except Exception:
                pass
            self.page.wait_for_timeout(1_200)
        return True

    def advance_status(self, code: str, next_label: str,
                       expect_next: str | None = None, retries: int = 3) -> bool:
        """Chuyển trạng thái + VERIFY POSITIVE: sau khi chuyển, nút trạng thái
        KẾ TIẾP (`expect_next`) phải xuất hiện trong dòng đơn (tránh false-positive
        khi dòng không match). Với bước cuối (delivered) expect_next=None → verify
        dòng vẫn còn + nút '→ {next_label}' đã biến mất. Retry nếu chưa ăn."""
        self.goto()
        # Chờ-kiên-nhẫn nút xuất hiện (CI render chậm / trạng thái vừa đổi cần vài
        # giây mới hiện nút kế): poll + re-goto thay vì bỏ cuộc ngay sau goto đầu.
        if not self._wait_next_button(code, next_label):
            print(f"  [advance_status] '{next_label}' KHÔNG xuất hiện sau khi chờ. "
                  f"Trạng thái đơn hiện tại: {self.status_text(code)[:140]!r}")
            return False
        for _ in range(max(1, retries)):
            self._click_and_confirm(code, next_label)  # đã chờ modal đóng (request xong)
            self.page.wait_for_timeout(1_200)
            self.goto()  # reload + verify
            if expect_next:
                if self._has_next_button(code, expect_next):
                    return True  # POSITIVE: nút kế tiếp đã xuất hiện → chuyển thật
            else:
                if self._row_found(code) and not self._has_next_button(code, next_label):
                    return True
        print(f"  [advance_status] '{next_label}'→'{expect_next}' verify FAIL sau {retries} lần. "
              f"Trạng thái đơn: {self.status_text(code)[:140]!r}")
        return False

    def _wait_next_button(self, code: str, next_label: str, attempts: int = 4) -> bool:
        """Chờ nút '→ {next_label}' xuất hiện trong dòng đơn, poll + re-goto giữa
        các lần (CI headless render chậm / trạng thái vừa đổi)."""
        for i in range(max(1, attempts)):
            if self._has_next_button(code, next_label):
                return True
            self.page.wait_for_timeout(2_000)
            if i < attempts - 1:
                self.goto()
        return False

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
