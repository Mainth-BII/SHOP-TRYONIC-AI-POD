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

    # JS: thao tác trong ĐÚNG row của đơn (scope theo code) — tránh chạm nút
    # 'Làm mới'/'Đánh dấu đã gửi' của đơn khác (list nhiều đơn) hoặc nút global.
    _ROW_JS = r"""(args) => {
        const [code, action] = args;
        // tìm element lá chứa code → leo lên row chứa nút 'Đánh dấu đã gửi'
        let el = [...document.querySelectorAll('*')].find(
            e => e.childElementCount===0 && (e.textContent||'').trim().includes(code));
        if (!el) return {found:false};
        let row = el;
        for (let i=0;i<10 && row;i++){
            const bs=[...row.querySelectorAll('button')];
            if (bs.some(b=>(b.innerText||'').includes('Đánh dấu đã gửi'))) break;
            row=row.parentElement;
        }
        if (!row) return {found:false, expandedNeeded:true};
        const bs=[...row.querySelectorAll('button')];
        const mark = bs.find(b=>(b.innerText||'').includes('Đánh dấu đã gửi'));
        const refresh = bs.find(b=>(b.innerText||'').trim()==='Làm mới');
        const state = {found:true, hasMark:!!mark,
                       markEnabled: mark? !mark.disabled : false, hasRefresh:!!refresh};
        if (action==='mark' && mark && !mark.disabled) { mark.click(); state.acted='mark'; }
        if (action==='refresh' && refresh && !refresh.disabled) { refresh.click(); state.acted='refresh'; }
        return state;
    }"""

    def _row_action(self, code: str, action: str = "state") -> dict:
        try:
            return self.page.evaluate(self._ROW_JS, [code, action]) or {"found": False}
        except Exception as e:
            return {"found": False, "err": str(e)}

    def mark_sent_when_ready(self, code: str = "", max_wait_s: int = 1_080,
                             poll_ms: int = 20_000) -> tuple[bool, str]:
        """Bấm 'Làm mới' (trong ĐÚNG row của đơn) lặp lại để refresh trạng thái
        lệnh in CHO ĐẾN KHI READY (nút 'Đánh dấu đã gửi' bật) rồi bấm — path THẬT.

        UI: màn /print-jobs là LIST nhiều đơn; mỗi đơn (sau khi mở rộng) có nút
        'Làm mới' + 'Đánh dấu đã gửi' (disabled với title 'Phải đợi tất cả lệnh in
        về READY' khi chưa xong export). Thao tác qua JS scope theo `code` để KHÔNG
        chạm đơn khác. Export async TEST có thể >13 phút → poll tới max_wait_s; hết
        giờ → (False) để flow fallback (progression). Trả (ok, msg).
        """
        import time, os
        max_wait_s = int(os.getenv("MARK_SENT_MAX_WAIT_S", max_wait_s))
        start = time.time()
        deadline = start + max_wait_s
        refreshes = 0
        while True:
            st = self._row_action(code, "mark")  # check + click nếu đã bật
            if st.get("acted") == "mark":
                self.page.wait_for_timeout(3_000)
                el = int(time.time() - start)
                return True, f"đã bấm 'Đánh dấu đã gửi' sau ~{el}s ({refreshes} lần Làm mới)"
            if not st.get("found"):
                # row chưa mở rộng / chưa thấy → mở lại chi tiết đơn rồi thử tiếp
                self.open_order_detail(code)
            if time.time() >= deadline:
                el = int(time.time() - start)
                return False, (f"'Đánh dấu đã gửi' vẫn disabled sau ~{el}s / {refreshes} lần "
                               f"Làm mới (row found={st.get('found')}, mark={st.get('hasMark')}, "
                               f"enabled={st.get('markEnabled')}) — lệnh in chưa READY")
            rf = self._row_action(code, "refresh")
            if rf.get("acted") == "refresh":
                refreshes += 1
            self.page.wait_for_timeout(poll_ms)
