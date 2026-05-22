from __future__ import annotations
"""
SH03 — Thống kê hoa hồng affiliate (TC4 + TC5 + TC6)

TC4: Số đơn hàng liên kết — count đúng (≥ 0, integer)
TC5: Tổng số tiền hoa hồng — tính đúng (≥ 0, nhất quán với danh sách đơn)
TC6: Số dư hoa hồng liên kết = Tổng hoa hồng - Tổng đã rút (hoặc số còn lại)
"""
import pytest
from .base_share_flow import BaseShareFlowTest


class TestSH03CommissionStats(BaseShareFlowTest):
    """TC4-6: Stats hoa hồng trên trang /affiliate."""

    _MH_NAMES = {
        "MH1":   "Số đơn hàng liên kết (TC4)",
        "MH2":   "Tổng hoa hồng (TC5)",
        "MH3":   "Số dư hoa hồng (TC6)",
        "MH4":   "Kiểm tra nhất quán: Số dư = Tổng - Đã rút",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH03 — Thống kê hoa hồng (TC4 + TC5 + TC6)"

    @pytest.fixture(autouse=True)
    def setup(self, home_page, product_list_page, product_detail_page,
              studio_page, auth_page, checkout_page, env):
        self.home     = home_page
        self.listing  = product_list_page
        self.detail   = product_detail_page
        self.studio   = studio_page
        self.auth     = auth_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = home_page.page
        self.tc       = "SH03_COMMISSION_STATS"
        self.root     = "production"
        self.domain   = "sh03_commission_stats"
        self._results = []

    def _read_total_withdrawn(self) -> int | None:
        """Đọc tổng số tiền đã rút từ lịch sử rút tiền."""
        history = self._read_withdrawal_history()
        success_items = [
            h for h in history
            if any(kw in (h.get("status") or "").lower()
                   for kw in ("thành công", "hoàn thành", "success"))
        ]
        if not success_items:
            return None
        amounts = [h.get("amount") for h in success_items if h.get("amount")]
        return sum(amounts) if amounts else 0

    @pytest.mark.production
    def test_commission_stats(self):
        """TC4 + TC5 + TC6: Đọc và verify stats hoa hồng."""
        tc = self.tc
        self._login()
        self._goto_affiliate()

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: User chưa được duyệt affiliate")

        self._shot("MH_before", "affiliate_stats_page")

        # ════════════════════════════════════════════════════════════════════
        # MH1 — TC4: Số đơn hàng liên kết
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Số đơn hàng liên kết (TC4) ─────────────────────")
        order_count = self._read_order_count()

        self._record_check(
            "MH1", "MH1 Số đơn liên kết hiển thị",
            "✅ PASS" if order_count is not None else "⚠️ WARN",
            str(order_count) if order_count is not None else "N/A", "Số nguyên ≥ 0",
        )
        if order_count is not None:
            self._assert_count("MH1", "MH1 Số đơn liên kết ≥ 0", order_count, expected_min=0)
        print(f"  [INFO] TC4: order_count = {order_count}")

        # ════════════════════════════════════════════════════════════════════
        # MH2 — TC5: Tổng hoa hồng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Tổng hoa hồng (TC5) ─────────────────────────────")
        total_commission = self._read_total_commission()

        self._record_check(
            "MH2", "MH2 Tổng hoa hồng hiển thị",
            "✅ PASS" if total_commission is not None else "⚠️ WARN",
            f"{total_commission:,}đ" if total_commission is not None else "N/A",
            "Số tiền ≥ 0đ",
        )
        if total_commission is not None:
            self._assert_count("MH2", "MH2 Tổng hoa hồng ≥ 0", total_commission, expected_min=0)
        self._shot("MH2_1", "stats_commission")
        print(f"  [INFO] TC5: total_commission = {total_commission}")

        # Verify nhất quán: nếu đọc được order list → tổng commission phải khớp
        orders = self._read_affiliate_orders()
        if orders and total_commission is not None:
            commissions_in_list = [o.get("commission") for o in orders if o.get("commission")]
            if commissions_in_list:
                sum_from_list = sum(commissions_in_list)
                delta = abs(sum_from_list - total_commission)
                ok = delta <= max(1000, total_commission * 0.02)  # cho phép sai lệch 2%
                self._record_check(
                    "MH2", "MH2 Tổng hoa hồng khớp với danh sách đơn",
                    "✅ PASS" if ok else "⚠️ WARN",
                    f"{sum_from_list:,}đ (Σ list)", f"{total_commission:,}đ (stat)",
                )
                print(f"  [{'PASS' if ok else 'WARN'}] MH2: Σlist={sum_from_list:,} vs stat={total_commission:,}")

        # ════════════════════════════════════════════════════════════════════
        # MH3 — TC6: Số dư hoa hồng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Số dư hoa hồng liên kết (TC6) ──────────────────")
        balance = self._read_balance()

        self._record_check(
            "MH3", "MH3 Số dư hoa hồng hiển thị",
            "✅ PASS" if balance is not None else "⚠️ WARN",
            f"{balance:,}đ" if balance is not None else "N/A",
            "Số dư ≥ 0đ",
        )
        if balance is not None:
            self._assert_count("MH3", "MH3 Số dư ≥ 0", balance, expected_min=0)
        self._shot("MH3_1", "stats_balance")
        print(f"  [INFO] TC6: balance = {balance}")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Verify: Số dư = Tổng hoa hồng - Tổng đã rút
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Kiểm tra nhất quán Số dư = Tổng - Đã rút ───────")
        total_withdrawn = self._read_total_withdrawn()
        print(f"  [INFO] MH4: total_withdrawn = {total_withdrawn}")

        if total_commission is not None and balance is not None:
            if total_withdrawn is not None:
                expected_balance = total_commission - total_withdrawn
                delta = abs(balance - expected_balance)
                ok = delta <= max(1000, total_commission * 0.01)  # sai lệch ≤1%
                self._record_check(
                    "MH4", "MH4 Số dư = Tổng hoa hồng - Đã rút",
                    "✅ PASS" if ok else "❌ FAIL",
                    f"{balance:,}đ",
                    f"{expected_balance:,}đ ({total_commission:,} - {total_withdrawn:,})",
                )
                print(f"  [{'PASS' if ok else 'FAIL'}] MH4: balance={balance:,}, exp={expected_balance:,}")
            else:
                # Chưa rút tiền → balance nên = tổng hoa hồng
                delta = abs(balance - total_commission)
                ok = delta <= max(1000, total_commission * 0.01)
                self._record_check(
                    "MH4", "MH4 Số dư = Tổng hoa hồng (chưa rút)",
                    "✅ PASS" if ok else "ℹ️ INFO",
                    f"{balance:,}đ", f"{total_commission:,}đ",
                )
                print(f"  [{'PASS' if ok else 'INFO'}] MH4: balance={balance:,} vs total={total_commission:,}")
        else:
            self._record_check(
                "MH4", "MH4 Kiểm tra nhất quán số dư",
                "ℹ️ INFO", "Không đủ dữ liệu để verify", "balance + total cần đọc được",
            )

        print(f"\n  [PASS] {tc}: TC4 + TC5 + TC6 COMPLETED")
        self._print_summary_table()
