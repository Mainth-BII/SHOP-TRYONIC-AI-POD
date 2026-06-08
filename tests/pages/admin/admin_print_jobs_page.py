"""AdminPrintJobsPage — màn Lệnh in ('Đơn hàng đang in').

Quy trình thật: mở chi tiết đơn → chọn Xưởng in (Tuấn Hải) → chờ mọi lệnh in
READY (export async sau confirm) → 'Đánh dấu đã gửi' → backend tự đẩy order
CONFIRMED→PRINTING. Cần auto-accept alert() (set ở context).
"""
from __future__ import annotations
from playwright.sync_api import Page


class AdminPrintJobsPage:
    def __init__(self, page: Page, admin_url: str):
        self.page = page
        self.base = admin_url.rstrip("/")

    def goto(self) -> None:
        self.page.goto(f"{self.base}/print-jobs")
        self.page.wait_for_timeout(2_500)

    def job_exists(self, code: str, retries: int = 6, wait_ms: int = 3_000) -> bool:
        for _ in range(max(1, retries)):
            self.goto()
            try:
                if self.page.locator(f"text={code}").first.is_visible(timeout=2_500):
                    return True
            except Exception:
                pass
            self.page.wait_for_timeout(wait_ms)
        return False

    def open_order_detail(self, code: str) -> bool:
        self.goto()
        try:
            el = self.page.locator(f"text={code}").first
            if el.is_visible(timeout=4_000):
                el.click()
                self.page.wait_for_timeout(2_500)
                return True
        except Exception:
            pass
        return False

    def assign_vendor(self, vendor_name: str) -> bool:
        """Chọn Xưởng in trong <select> chứa option tên xưởng (vd 'Tuấn Hải')."""
        try:
            sel = self.page.locator(
                f"select:has(option:has-text('{vendor_name}'))").first
            if sel.is_visible(timeout=3_000):
                sel.select_option(label=vendor_name)
                self.page.wait_for_timeout(2_500)
                return True
        except Exception:
            pass
        return False

    def mark_sent_when_ready(self, retries: int = 40, wait_ms: int = 20_000) -> tuple[bool, str]:
        """Chờ 'Đánh dấu đã gửi' bật (mọi lệnh in READY) rồi bấm.

        Export async sau confirm RẤT CHẬM trên TEST (có thể >10 phút) → poll tới
        ~13 phút, thoát sớm ngay khi READY.
        Thúc 'Chạy lại tất cả' MỘT lần (vòng 4) nếu chưa nhúc nhích; còn lại chỉ
        'Làm mới' + chờ (tránh re-trigger export làm reset về PROCESSING). Trả (ok, msg).
        """
        for i in range(max(1, retries)):
            btn = self.page.locator("button:has-text('Đánh dấu đã gửi')").first
            try:
                if btn.is_visible(timeout=2_000) and not btn.is_disabled():
                    btn.click()
                    self.page.wait_for_timeout(3_000)
                    return True, f"đã bấm 'Đánh dấu đã gửi' sau ~{i * wait_ms // 1000}s chờ READY"
            except Exception:
                pass
            if i == 4:  # thúc pipeline 1 lần duy nhất
                for lbl in ("Chạy lại tất cả", "Chạy tất cả"):
                    try:
                        rb = self.page.locator(f"button:has-text('{lbl}')").first
                        if rb.is_visible(timeout=1_500) and not rb.is_disabled():
                            rb.click()
                            self.page.wait_for_timeout(3_000)
                            break
                    except Exception:
                        continue
            try:
                r = self.page.locator("button:has-text('Làm mới')").first
                if r.is_visible(timeout=1_000):
                    r.click()
            except Exception:
                pass
            self.page.wait_for_timeout(wait_ms)
        return False, f"'Đánh dấu đã gửi' vẫn disabled sau ~{retries * wait_ms // 1000}s (lệnh in chưa READY)"
