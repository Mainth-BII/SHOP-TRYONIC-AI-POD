"""Flow: admin xử lý đơn COD hết vòng đời + verify email mỗi bước (sequence thật).

Đơn COD → đánh dấu đã thanh toán (POD policy) → Xác nhận → Lệnh in (chọn xưởng
Tuấn Hải → Đánh dấu đã gửi → order tự sang Đang in) → Đang giao → Đã giao.
Verify email khách (Yopmail) mỗi lần đổi trạng thái.

LƯU Ý (gap sản phẩm đã xác minh từ code): PRINTING đạt qua mark-sent đi qua
PrintJobService.maybeSyncOrderStatus → prisma.order.update TRỰC TIẾP, KHÔNG gọi
sendStatusChangeNotification → KHÔNG gửi email 'đang được in'. Test ghi WARN
trung thực (không phải lỗi test).

`record(mh, check, status, actual, expected="")` = callback ghi report.
"""
from __future__ import annotations

from pages.admin.admin_orders_page import AdminOrdersPage
from pages.admin.admin_order_detail_page import AdminOrderDetailPage
from pages.admin.admin_print_jobs_page import AdminPrintJobsPage
from pages.external.yopmail_inbox import YopmailInbox
from e2e._shots import shot

VENDOR = "Tuấn Hải"


class AdminFulfillmentFlow:
    def __init__(self, admin_page, admin_url, yopmail_page, record):
        self.page = admin_page
        self.orders = AdminOrdersPage(admin_page, admin_url)
        self.detail = AdminOrderDetailPage(admin_page)
        self.print_jobs = AdminPrintJobsPage(admin_page, admin_url)
        self.yop: YopmailInbox = yopmail_page
        self.record = record

    def _email(self, phrase, mh, soft=False, label=""):
        found, preview = self.yop.wait_for_new(phrase)
        shot(self.yop.page, f"email_{label or mh}")
        status = "✅ PASS" if found else ("⚠️ WARN" if soft else "❌ FAIL")
        self.record(mh, f"Email khách: '{phrase}'", status,
                    preview if found else "Không thấy email mới trong inbox",
                    f"subject chứa '{phrase}'")
        return found

    def run(self, code: str):
        self.yop.snapshot()  # baseline → chỉ tính email tới SAU đó

        # L2b — Đánh dấu đã thanh toán thủ công (COD bắt buộc PAID mới fulfill)
        self.orders.open_detail(code)
        shot(self.page, "adm_01_order_detail")
        paid = self.detail.mark_paid_manually()
        shot(self.page, "adm_02_after_force_pay")
        self.record("L2b", "Đánh dấu đã thanh toán thủ công (COD → PAID)",
                    "✅ PASS" if paid else "❌ FAIL", f"submitted={paid}")

        # L3 — Xác nhận đơn (trong modal, nay đã PAID) + email
        confirmed = self.detail.confirm_order()
        shot(self.page, "adm_03_confirmed")
        self.record("L3", "Xác nhận đơn hàng", "✅ PASS" if confirmed else "❌ FAIL",
                    f"clicked={confirmed}")
        self.detail.close()
        self._email("Xác nhận đơn hàng", "L3", label="L3_xac_nhan")

        # L4 — Lệnh in (coverage UI thật): chọn xưởng Tuấn Hải + thử Đánh dấu đã gửi
        opened = self.print_jobs.open_order_detail(code)
        self.record("L4", "Mở Lệnh in của đơn", "✅ PASS" if opened else "❌ FAIL",
                    f"opened={opened}")
        assigned = self.print_jobs.assign_vendor(VENDOR)
        shot(self.page, "adm_04_lenh_in_vendor_TuanHai")
        self.record("L4", f"Chọn xưởng in '{VENDOR}'",
                    "✅ PASS" if assigned else "⚠️ WARN", f"assigned={assigned}")
        sent, smsg = self.print_jobs.mark_sent_when_ready(code)
        shot(self.page, "adm_05_mark_sent")
        self.record("L4", "Đánh dấu đã gửi → Đang in (flow thật)",
                    "✅ PASS" if sent else "⚠️ WARN", smsg)

        # VERIFY EMAIL theo ĐÚNG path thật (mark-sent). Nếu mark-sent đã đẩy đơn
        # sang PRINTING mà KHÔNG có email → đó là GAP backend được xác nhận
        # (maybeSyncOrderStatus bỏ qua sendStatusChangeNotification) — khớp với
        # kiểm tra manual của QA. KHÔNG dùng path Orders updateStatus để làm xanh.
        if sent:
            # Verify email path thật. Gộp THÀNH 1 dòng: nếu không có mail → 1 FAIL
            # duy nhất nêu cả triệu chứng (khách không nhận) + nguyên nhân + hướng
            # sửa (tránh đếm 2 FAIL cho cùng 1 defect).
            found, preview = self.yop.wait_for_new("đang được in")
            shot(self.yop.page, "email_L4_dang_in")
            if found:
                self.record("L4", "Email khách: 'đang được in'", "✅ PASS",
                            preview, "subject chứa 'đang được in'")
            else:
                self.record(
                    "L4", "Email 'đang được in' KHÔNG được gửi (GAP backend)", "❌ FAIL",
                    "Khách KHÔNG nhận mail 'đang được in'. Nguyên nhân: nút 'Đánh dấu đã "
                    "gửi' chạy maybeSyncOrderStatus update thẳng DB sang PRINTING, bỏ qua "
                    "sendStatusChangeNotification (khớp check manual QA).",
                    "Backend cần gọi notification khi auto CONFIRMED→PRINTING")
        else:
            # mark-sent chưa READY (export chậm) → không verify được email qua flow thật
            self.record("L4", "Email 'đang được in' (flow thật)", "⚠️ WARN",
                        "Chưa đẩy được Đang in qua mark-sent (lệnh in chưa READY) → chưa verify được email theo path thật")
            # Progression-only: đưa đơn sang PRINTING để test tiếp Giao/Đã giao.
            prog = self.orders.advance_status(code, "Đang in", expect_next="Đang giao")
            shot(self.page, "adm_05b_dang_in_progression")
            self.record("L4", "[progression] → Đang in qua updateStatus (KHÔNG phải flow In thật)",
                        "ℹ️ INFO", f"clicked={prog} (path này có gửi mail nhưng admin dùng mark-sent)")

        # L6 — Đang giao (Orders, qua updateStatus → có email)
        ship = self.orders.advance_status(code, "Đang giao", expect_next="Đã giao")
        shot(self.page, "adm_06_dang_giao")
        _l6_detail = f"clicked={ship}"
        if not ship:
            _l6_detail += f" | trạng thái đơn hiện tại: {self.orders.status_text(code)[:90]}"
        self.record("L6", "Thao tác → Đang giao", "✅ PASS" if ship else "❌ FAIL", _l6_detail)
        self._email("đang được giao", "L6", label="L6_dang_giao")

        # L7 — Đã giao + email
        deliv = self.orders.advance_status(code, "Đã giao")  # expect_next=None (delivered)
        shot(self.page, "adm_07_da_giao")
        _l7_detail = f"clicked={deliv}"
        if not deliv:
            _l7_detail += f" | trạng thái đơn hiện tại: {self.orders.status_text(code)[:90]}"
        self.record("L7", "Thao tác → Đã giao", "✅ PASS" if deliv else "❌ FAIL", _l7_detail)
        self._email("đã được giao", "L7", label="L7_da_giao")
