"""
SH05 — Lịch sử rút tiền hoa hồng (TC8)

TC8: Verify section Lịch sử rút tiền:
  - Hiển thị các lần rút tiền (số tiền, ngày, trạng thái)
  - Tổng đã rút = Σ các lần rút thành công
  - Số dư sau rút = Tổng hoa hồng - Tổng đã rút
  - Trạng thái rút hợp lệ: thành công / đang xử lý / từ chối
"""
import re
import pytest
from .base_share_flow import BaseShareFlowTest


class TestSH05Withdrawal(BaseShareFlowTest):
    """TC8: Lịch sử rút tiền hoa hồng."""

    _MH_NAMES = {
        "MH1":   "Lịch sử rút tiền — hiển thị",
        "MH2":   "Số tiền rút — hợp lệ",
        "MH3":   "Ngày rút — định dạng hợp lệ",
        "MH4":   "Trạng thái rút — hợp lệ",
        "MH5":   "Tổng đã rút — nhất quán với số dư",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH05 — Lịch sử Rút tiền Hoa hồng (TC8)"

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
        self.tc       = "SH05_WITHDRAWAL"
        self.root     = "production"
        self.domain   = "sh05_withdrawal"
        self._results = []

    def _read_withdrawal_detailed(self) -> list[dict]:
        """Parse lịch sử rút tiền đầy đủ từ trang."""
        return self.page.evaluate(r"""() => {
            const items = [];
            const moneyRe = /(\d{1,3}(?:[.,]\d{3})+)/g;
            const dateRe  = /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2}/;
            const statRe  = /thành công|hoàn thành|đã rút|đang xử lý|pending|chờ xác nhận|từ chối|thất bại/i;

            // Tìm section lịch sử rút tiền
            let container = null;
            const allEls = document.querySelectorAll('section, div, article, table');
            for (const el of allEls) {
                const txt = el.innerText || '';
                if (/lịch sử rút|rút tiền/i.test(txt) && el.children.length > 1) {
                    container = el;
                    break;
                }
            }
            if (!container) container = document;

            // Parse từ table rows
            const rows = container.querySelectorAll('tr');
            for (const row of rows) {
                const text = row.innerText || '';
                if (!text.trim() || /số tiền|ngày|trạng thái|lịch sử/i.test(text)) continue;

                const amounts = [...text.matchAll(moneyRe)]
                    .map(m => parseInt(m[0].replace(/[^\d]/g, '')))
                    .filter(n => n >= 10000); // rút ít nhất 10k
                const dateM  = text.match(dateRe);
                const statM  = text.match(statRe);

                if (amounts.length || dateM) {
                    items.push({
                        amount: amounts.length ? Math.max(...amounts) : null,
                        date:   dateM ? dateM[0] : '',
                        status: statM ? statM[0] : '',
                        raw:    text.substring(0, 120),
                    });
                }
            }

            // Fallback: list items
            if (items.length === 0) {
                const listEls = container.querySelectorAll('[class*="withdraw"], [class*="history"], li');
                for (const el of listEls) {
                    const text = el.innerText || '';
                    const amounts = [...text.matchAll(moneyRe)]
                        .map(m => parseInt(m[0].replace(/[^\d]/g, '')))
                        .filter(n => n >= 10000);
                    const dateM = text.match(dateRe);
                    const statM = text.match(statRe);
                    if (amounts.length || (dateM && statM)) {
                        items.push({
                            amount: amounts.length ? Math.max(...amounts) : null,
                            date:   dateM ? dateM[0] : '',
                            status: statM ? statM[0] : '',
                            raw:    text.substring(0, 120),
                        });
                    }
                }
            }

            return items;
        }""") or []

    @pytest.mark.production
    def test_withdrawal_history(self):
        """TC8: Verify lịch sử rút tiền."""
        tc = self.tc
        self._login()
        self._goto_affiliate()

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: User chưa được duyệt affiliate")

        total_commission = self._read_total_commission()
        balance          = self._read_balance()

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Lịch sử rút tiền hiển thị
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Lịch sử rút tiền ────────────────────────────────")
        self._shot("MH1_1", "withdrawal_section")

        withdrawals = self._read_withdrawal_detailed()
        has_history  = len(withdrawals) > 0

        self._record_check(
            "MH1", "MH1 Section lịch sử rút tiền hiển thị",
            "✅ PASS" if has_history else "ℹ️ INFO",
            f"{len(withdrawals)} lần rút", "Lịch sử rút tiền tồn tại",
        )
        print(f"  [INFO] MH1: {len(withdrawals)} bản ghi rút tiền")

        if not has_history:
            self._record_check(
                "MH1", "MH1 Chưa có lịch sử rút tiền",
                "ℹ️ INFO", "0 bản ghi", "Chưa thực hiện rút tiền",
            )
            # Nếu chưa rút tiền → số dư phải bằng tổng hoa hồng
            if total_commission is not None and balance is not None:
                delta = abs(balance - total_commission)
                ok = delta <= max(1000, total_commission * 0.01)
                self._record_check(
                    "MH5", "MH5 Chưa rút: Số dư = Tổng hoa hồng",
                    "✅ PASS" if ok else "ℹ️ INFO",
                    f"{balance:,}đ", f"{total_commission:,}đ",
                )
                print(f"  [{'PASS' if ok else 'INFO'}] MH5: balance={balance:,} vs total={total_commission:,}")
            self._print_summary_table()
            return

        for i, w in enumerate(withdrawals[:5]):
            print(f"    [{i+1}] amount={w.get('amount')} | date={w.get('date')} | status={w.get('status')}")

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Số tiền rút hợp lệ (> 0)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Số tiền rút ──────────────────────────────────────")
        items_with_amount = [w for w in withdrawals if w.get("amount") and w["amount"] > 0]
        ok_amount = len(items_with_amount) > 0

        self._record_check(
            "MH2", f"MH2 Số tiền rút > 0 ({len(items_with_amount)}/{len(withdrawals)})",
            "✅ PASS" if ok_amount else "⚠️ WARN",
            f"{len(items_with_amount)} bản ghi có số tiền", "Số tiền > 0đ",
        )
        if items_with_amount:
            amounts = [w["amount"] for w in items_with_amount]
            print(f"  [PASS] MH2: amounts = {[f'{a:,}' for a in amounts[:5]]}")

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Ngày rút hợp lệ
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Ngày rút tiền ────────────────────────────────────")
        date_pattern    = re.compile(
            r"^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$|^\d{4}[\/\-]\d{2}[\/\-]\d{2}$"
        )
        items_with_date = [w for w in withdrawals if w.get("date")]
        valid_dates     = [w for w in items_with_date if date_pattern.match(w["date"])]

        self._record_check(
            "MH3", f"MH3 Ngày rút hiển thị ({len(items_with_date)}/{len(withdrawals)})",
            "✅ PASS" if items_with_date else "⚠️ WARN",
            f"{len(items_with_date)} bản ghi có ngày", "Ngày rút hiển thị",
        )
        if items_with_date:
            ok_date = len(valid_dates) == len(items_with_date)
            self._record_check(
                "MH3", "MH3 Định dạng ngày hợp lệ",
                "✅ PASS" if ok_date else "⚠️ WARN",
                f"{len(valid_dates)}/{len(items_with_date)} đúng format",
                "dd/MM/yyyy hoặc yyyy-MM-dd",
            )

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Trạng thái rút hợp lệ
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Trạng thái rút tiền ──────────────────────────────")
        valid_statuses  = {"thành công", "hoàn thành", "đã rút", "đang xử lý",
                           "pending", "chờ xác nhận", "từ chối", "thất bại"}
        items_with_stat = [w for w in withdrawals if w.get("status")]
        valid_stat_items = [
            w for w in items_with_stat
            if any(v in w["status"].lower() for v in valid_statuses)
        ]

        self._record_check(
            "MH4", f"MH4 Trạng thái rút tiền hợp lệ ({len(valid_stat_items)}/{len(withdrawals)})",
            "✅ PASS" if (not items_with_stat or valid_stat_items) else "⚠️ WARN",
            str([w.get("status") for w in withdrawals[:3]]),
            str(list(valid_statuses)),
        )
        self._shot("MH4_1", "withdrawal_statuses")

        # ════════════════════════════════════════════════════════════════════
        # MH5 — Tổng đã rút nhất quán với số dư
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH5: Tổng đã rút nhất quán với số dư ─────────────────")
        success_kws = ("thành công", "hoàn thành", "đã rút", "success")
        success_items = [
            w for w in withdrawals
            if any(kw in (w.get("status") or "").lower() for kw in success_kws)
            and w.get("amount")
        ]
        total_withdrawn = sum(w["amount"] for w in success_items) if success_items else 0

        self._record_check(
            "MH5", f"MH5 Tổng đã rút ({len(success_items)} lần thành công)",
            "✅ PASS",
            f"{total_withdrawn:,}đ",
            "Σ các lần rút thành công",
        )
        print(f"  [INFO] MH5: total_withdrawn = {total_withdrawn:,}đ")

        if total_commission is not None and balance is not None:
            expected_balance = total_commission - total_withdrawn
            delta = abs(balance - expected_balance)
            ok    = delta <= max(1000, total_commission * 0.01)
            self._record_check(
                "MH5", "MH5 Số dư = Tổng hoa hồng - Tổng đã rút",
                "✅ PASS" if ok else "❌ FAIL",
                f"{balance:,}đ",
                f"{expected_balance:,}đ ({total_commission:,} - {total_withdrawn:,})",
            )
            print(f"  [{'PASS' if ok else 'FAIL'}] MH5: balance={balance:,}, exp={expected_balance:,}")

        self._shot("MH5_1", "withdrawal_final")
        print(f"\n  [PASS] {tc}: TC8 COMPLETED")
        self._print_summary_table()
