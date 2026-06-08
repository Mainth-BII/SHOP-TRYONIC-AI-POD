"""AdminOrderDetailPage — modal chi tiết đơn: thao tác Vận đơn ViettelPost.

Quy trình thủ công VTP: Tạo vận đơn → Duyệt (VTP đến lấy) → Huỷ → Xoá.
Mỗi action đọc lại vùng thông báo/chi tiết vận đơn (ORDER_NUMBER, trạng thái).
Cần auto-accept confirm() (Duyệt/Huỷ/Xoá) — set ở AdminSession.
"""
from __future__ import annotations
from playwright.sync_api import Page


class AdminOrderDetailPage:
    def __init__(self, page: Page):
        self.page = page

    def _click(self, label: str) -> bool:
        try:
            btn = self.page.locator(f"button:has-text('{label}')").first
            if btn.is_visible(timeout=3_000):
                btn.click()
                self.page.wait_for_timeout(3_500)
                return True
        except Exception:
            pass
        return False

    def _vtp_text(self) -> str:
        """Đọc thông báo/chi tiết vận đơn (ORDER_NUMBER, trạng thái, msg)."""
        try:
            return self.page.evaluate(r"""() => {
                const kws = ['vận đơn','Mã vận đơn','ORDER_NUMBER','Đã tạo','Đã duyệt',
                             'Đã huỷ','Đã xoá','Không','VIETTELPOST','Trạng thái VTP'];
                const els = [...document.querySelectorAll('p,div,span')];
                for (const e of els) {
                    const t = (e.innerText||'').trim();
                    if (t && t.length < 200 && kws.some(k => t.includes(k))) return t;
                }
                return '';
            }""") or ""
        except Exception:
            return ""

    def mark_paid_manually(
        self,
        reason: str = "QA E2E TEST: COD đã đối chiếu, đánh dấu thanh toán tự động",
    ) -> bool:
        """Đánh dấu đã thanh toán thủ công (COD) — form 2 BƯỚC:
        1) bấm 'Đánh dấu đã thanh toán thủ công' → mở form,
        2) nhập lý do (>=10 ký tự) → bấm 'Xác nhận' (forceMarkPaid → PAID).
        POD policy yêu cầu PAID mới confirm/in/giao được.
        """
        if not self._click("Đánh dấu đã thanh toán"):
            return False
        try:
            ta = self.page.locator("textarea").last
            if ta.is_visible(timeout=3_000):
                ta.fill(reason)
                self.page.wait_for_timeout(500)
            # Nút 'Xác nhận' submit nằm TRONG modal chứa textarea (trang có nhiều
            # nút 'Xác nhận' khác) → scope theo ancestor của textarea.
            submit = self.page.locator(
                "xpath=//textarea/ancestor::div[.//button[contains(.,'Xác nhận')]][1]"
                "//button[contains(.,'Xác nhận')]"
            ).first
            if submit.is_visible(timeout=3_000):
                submit.click()
                self.page.wait_for_timeout(3_000)
                return True
        except Exception:
            pass
        return False

    def confirm_order(self) -> bool:
        """Bấm 'Xác nhận đơn hàng' trong modal (hiện khi đã PAID + đang pending).
        → order CONFIRMED + tự tạo print job + gửi email xác nhận."""
        return self._click("Xác nhận đơn hàng")

    def create_waybill(self) -> tuple[bool, str]:
        return self._click("Tạo vận đơn"), self._vtp_text()

    def approve_waybill(self) -> tuple[bool, str]:
        return self._click("Duyệt"), self._vtp_text()

    def cancel_waybill(self) -> tuple[bool, str]:
        return self._click("Huỷ vận đơn"), self._vtp_text()

    def delete_waybill(self) -> tuple[bool, str]:
        return self._click("Xoá vận đơn"), self._vtp_text()

    def close(self) -> None:
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        except Exception:
            pass
