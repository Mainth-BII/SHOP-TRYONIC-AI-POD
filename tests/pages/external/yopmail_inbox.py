"""YopmailInbox — verify email khách nhận (TEST: tài khoản @yopmail.com).

Yopmail MASK chữ số trong list preview → KHÔNG match theo order code ở list.
Thay vào đó match theo SUBJECT (cụm chữ trạng thái, vẫn hiện rõ) + chỉ tính
email MỚI (so với baseline chụp lúc bắt đầu) → tránh trúng email cũ cùng cụm.

Subject theo trạng thái:
  CONFIRMED: 'Xác nhận đơn hàng'   PRINTING: 'đang được in'
  SHIPPING : 'đang được giao'      DELIVERED: 'đã được giao'
"""
from __future__ import annotations
from playwright.sync_api import Page


class YopmailInbox:
    BASE = "https://yopmail.com/en/"

    def __init__(self, page: Page):
        self.page = page
        self.seen: set[str] = set()
        self.login = ""

    def open(self, email: str) -> None:
        self.login = email.split("@")[0]
        self._reopen()

    def _reopen(self) -> None:
        """Vào lại inbox (làm tươi session — tránh stale sau run dài)."""
        self.page.goto(self.BASE)
        self.page.wait_for_timeout(1_500)
        try:
            self.page.fill("#login", self.login)
            self.page.keyboard.press("Enter")
        except Exception:
            pass
        self.page.wait_for_timeout(2_500)

    def _messages(self) -> list[str]:
        """Trả list text từng email trong inbox (subject + from + time)."""
        try:
            fin = self.page.frame(name="ifinbox")
            if not fin:
                return []
            return [t.strip() for t in fin.locator("div.m, button.m, .lm").all_inner_texts() if t.strip()]
        except Exception:
            return []

    def _refresh(self) -> None:
        for sel in ("#refresh", "button[title*='Check']"):
            try:
                b = self.page.locator(sel).first
                if b.is_visible(timeout=800):
                    b.click()
                    break
            except Exception:
                continue
        self.page.wait_for_timeout(1_500)

    def snapshot(self) -> None:
        """Chụp toàn bộ email hiện có làm baseline → chỉ verify email tới SAU đó."""
        self._refresh()
        self.seen = set(self._messages())

    def wait_for_new(self, subject_contains: str, retries: int = 10,
                     wait_ms: int = 4_000) -> tuple[bool, str]:
        """Chờ 1 email MỚI (không có trong baseline/seen) chứa cụm subject_contains.

        Đánh dấu đã match để lần sau không trúng lại. Email qua queue → retry.
        """
        kw = subject_contains.lower()
        self._reopen()  # làm tươi session trước khi poll (tránh stale sau run dài)
        for i in range(max(1, retries)):
            for m in self._messages():
                if m in self.seen:
                    continue
                if kw in m.lower():
                    self.seen.add(m)
                    return True, m[:140]
            # vài vòng không thấy → vào lại inbox phòng iframe/session hỏng
            if i and i % 4 == 0:
                self._reopen()
            else:
                self._refresh()
            self.page.wait_for_timeout(wait_ms)
        return False, ""
