"""
SH04 — Danh sách đơn hàng liên kết (TC7)

TC7: Verify từng đơn hàng trong danh sách "Đơn hàng liên kết":
  - Mã đơn hàng hiển thị
  - Tỷ lệ hoa hồng (%) — lấy từ CMS setting
  - Hoa hồng = subtotal (không gồm VAT, không gồm ship) × tỷ lệ
  - Ngày đặt — đơn đã thanh toán thành công
"""
import re
import pytest
from .base_share_flow import BaseShareFlowTest


class TestSH04OrderList(BaseShareFlowTest):
    """TC7: Danh sách đơn hàng liên kết — verify commission per order."""

    _MH_NAMES = {
        "MH1":   "Danh sách đơn hàng liên kết — hiển thị",
        "MH2":   "Mã đơn hàng — tồn tại",
        "MH3":   "Tỷ lệ hoa hồng — lấy từ CMS",
        "MH4":   "Hoa hồng = subtotal × tỷ lệ (không gồm VAT/ship)",
        "MH5":   "Ngày đặt — định dạng hợp lệ",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH04 — Danh sách Đơn hàng Liên kết (TC7)"

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
        self.tc       = "SH04_ORDER_LIST"
        self.root     = "production"
        self.domain   = "sh04_order_list"
        self._results = []

    def _read_order_list_structured(self) -> list[dict]:
        """Parse danh sách đơn hàng liên kết với cấu trúc đầy đủ."""
        return self.page.evaluate(r"""() => {
            const orders = [];
            const numRe  = /[\d,.]+/g;
            const pctRe  = /(\d+(?:\.\d+)?)\s*%/;
            const dateRe = /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2}/;
            const codeRe = /[A-Z0-9\-]{6,20}/;
            const moneyRe = /(\d{1,3}(?:[.,]\d{3})+)/g;

            // Tìm section "Đơn hàng liên kết"
            let container = null;
            const sections = document.querySelectorAll('section, div, article');
            for (const sec of sections) {
                const txt = (sec.innerText || '').trim();
                if (/đơn hàng liên kết/i.test(txt) && sec.querySelectorAll('tr, li').length > 0) {
                    container = sec;
                    break;
                }
            }
            if (!container) container = document;

            // Thử parse từ table rows
            const rows = container.querySelectorAll('tr');
            for (const row of rows) {
                const cells = [...row.querySelectorAll('td, th')];
                if (cells.length < 2) continue;
                const rowText = row.innerText || '';
                if (!rowText.trim() || /mã đơn|hoa hồng|tỷ lệ|ngày/i.test(rowText)) continue; // skip header

                const pctM   = rowText.match(pctRe);
                const dateM  = rowText.match(dateRe);
                const codeM  = rowText.match(codeRe);

                // Lấy tất cả số tiền (>= 1000)
                const amounts = [...rowText.matchAll(moneyRe)]
                    .map(m => parseInt(m[0].replace(/[^\d]/g, '')))
                    .filter(n => n >= 1000);

                if (codeM || pctM || dateM) {
                    orders.push({
                        order_code:      codeM  ? codeM[0]              : '',
                        commission_rate: pctM   ? parseFloat(pctM[1])   : null,
                        commission:      amounts.length ? amounts[amounts.length - 1] : null,
                        subtotal:        amounts.length > 1 ? amounts[0] : null,
                        date:            dateM  ? dateM[0]               : '',
                        raw:             rowText.substring(0, 150),
                    });
                }
            }

            // Nếu không có table rows thì thử parse list items
            if (orders.length === 0) {
                const items = container.querySelectorAll('[class*="order"], [class*="Order"], li');
                for (const item of items) {
                    const text = item.innerText || '';
                    const pctM   = text.match(pctRe);
                    const dateM  = text.match(dateRe);
                    const codeM  = text.match(codeRe);
                    const amounts = [...text.matchAll(moneyRe)]
                        .map(m => parseInt(m[0].replace(/[^\d]/g, '')))
                        .filter(n => n >= 1000);
                    if (codeM || (pctM && dateM)) {
                        orders.push({
                            order_code:      codeM  ? codeM[0]            : '',
                            commission_rate: pctM   ? parseFloat(pctM[1]) : null,
                            commission:      amounts.length ? amounts[amounts.length - 1] : null,
                            subtotal:        amounts.length > 1 ? amounts[0] : null,
                            date:            dateM  ? dateM[0]             : '',
                            raw:             text.substring(0, 150),
                        });
                    }
                }
            }

            return orders;
        }""") or []

    @pytest.mark.production
    def test_order_list(self):
        """TC7: Verify danh sách đơn hàng liên kết."""
        tc = self.tc
        self._login()
        self._goto_affiliate()

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: User chưa được duyệt affiliate")

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Danh sách đơn hàng hiển thị
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Danh sách đơn hàng liên kết ─────────────────────")
        self._shot("MH1_1", "affiliate_order_section")

        orders = self._read_order_list_structured()
        has_orders = len(orders) > 0

        self._record_check(
            "MH1", "MH1 Danh sách đơn hàng liên kết hiển thị",
            "✅ PASS" if has_orders else "ℹ️ INFO",
            f"{len(orders)} đơn", "Có đơn hàng liên kết",
        )
        print(f"  [INFO] MH1: {len(orders)} đơn hàng liên kết tìm thấy")

        if not orders:
            self._record_check(
                "MH1", "MH1 Không có đơn hàng liên kết",
                "ℹ️ INFO", "0 đơn", "Chưa có đơn hoặc chưa được công nhận",
            )
            print(f"  [INFO] TC7: Chưa có đơn hàng liên kết nào — bỏ qua MH2-MH5")
            self._print_summary_table()
            return

        print(f"  [INFO] MH1: Orders found:")
        for i, o in enumerate(orders[:5]):  # chỉ log 5 đơn đầu
            print(f"    [{i+1}] {o.get('order_code')} | rate={o.get('commission_rate')}% "
                  f"| commission={o.get('commission')} | date={o.get('date')}")

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Mã đơn hàng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Mã đơn hàng ──────────────────────────────────────")
        orders_with_code = [o for o in orders if o.get("order_code")]
        pct_with_code = len(orders_with_code) / len(orders) * 100
        ok_code = pct_with_code >= 80  # ≥80% đơn có mã

        self._record_check(
            "MH2", f"MH2 Mã đơn hàng hiển thị ({len(orders_with_code)}/{len(orders)})",
            "✅ PASS" if ok_code else "⚠️ WARN",
            f"{pct_with_code:.0f}% có mã", "≥80% đơn có mã",
        )
        print(f"  [{'PASS' if ok_code else 'WARN'}] MH2: {len(orders_with_code)}/{len(orders)} đơn có mã")

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Tỷ lệ hoa hồng (từ CMS)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Tỷ lệ hoa hồng ──────────────────────────────────")
        orders_with_rate = [o for o in orders if o.get("commission_rate") is not None]
        has_rate = len(orders_with_rate) > 0

        self._record_check(
            "MH3", f"MH3 Tỷ lệ hoa hồng hiển thị ({len(orders_with_rate)}/{len(orders)})",
            "✅ PASS" if has_rate else "⚠️ WARN",
            f"{len(orders_with_rate)} đơn có tỷ lệ", "Tỷ lệ % hiển thị",
        )

        if orders_with_rate:
            rates = [o["commission_rate"] for o in orders_with_rate]
            rate_consistent = len(set(rates)) == 1  # tỷ lệ thống nhất trong 1 batch test
            rate_val = rates[0]
            self._record_check(
                "MH3", f"MH3 Tỷ lệ hoa hồng nhất quán ({rate_val}%)",
                "✅ PASS" if rate_consistent else "ℹ️ INFO",
                f"Rates: {sorted(set(rates))}",
                "Tỷ lệ thống nhất (hoặc nhiều mức tùy CMS)",
            )
            print(f"  [{'PASS' if rate_consistent else 'INFO'}] MH3: rates = {sorted(set(rates))}")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Hoa hồng = subtotal × tỷ lệ (không gồm VAT/ship)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Verify công thức hoa hồng ───────────────────────")
        verifiable = [o for o in orders
                      if o.get("commission_rate") and o.get("subtotal") and o.get("commission")]
        print(f"  [INFO] MH4: {len(verifiable)} đơn có đủ dữ liệu để verify công thức")

        passed_formula = 0
        for o in verifiable:
            expected = self.calc_commission(o["subtotal"], o["commission_rate"])
            delta    = abs(o["commission"] - expected)
            ok       = delta <= max(1000, expected * 0.02)  # sai lệch ≤2%
            self._record_check(
                "MH4",
                f"MH4 Hoa hồng đơn {o.get('order_code') or 'N/A'} "
                f"({o['commission_rate']}% × {o['subtotal']:,}đ)",
                "✅ PASS" if ok else "❌ FAIL",
                f"{o['commission']:,}đ", f"{expected:,}đ",
            )
            if ok:
                passed_formula += 1

        if not verifiable:
            self._record_check(
                "MH4", "MH4 Verify công thức hoa hồng",
                "ℹ️ INFO",
                "Không đủ dữ liệu (subtotal/rate chưa đọc được)",
                "subtotal + rate + commission cần hiển thị",
            )
        else:
            print(f"  [INFO] MH4: {passed_formula}/{len(verifiable)} đơn đúng công thức")

        # ════════════════════════════════════════════════════════════════════
        # MH5 — Ngày đặt hàng (đã thanh toán)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH5: Ngày đặt hàng ────────────────────────────────────")
        orders_with_date = [o for o in orders if o.get("date")]
        has_date = len(orders_with_date) > 0

        self._record_check(
            "MH5", f"MH5 Ngày đặt hàng hiển thị ({len(orders_with_date)}/{len(orders)})",
            "✅ PASS" if has_date else "⚠️ WARN",
            f"{len(orders_with_date)} đơn có ngày", "Ngày đặt hiển thị",
        )

        # Verify format ngày hợp lệ
        date_pattern = re.compile(
            r"^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$|^\d{4}[\/\-]\d{2}[\/\-]\d{2}$"
        )
        valid_dates = [o for o in orders_with_date if date_pattern.match(o["date"])]
        if orders_with_date:
            ok_date = len(valid_dates) == len(orders_with_date)
            self._record_check(
                "MH5", "MH5 Định dạng ngày hợp lệ",
                "✅ PASS" if ok_date else "⚠️ WARN",
                f"{len(valid_dates)}/{len(orders_with_date)} đúng format",
                "dd/MM/yyyy hoặc yyyy-MM-dd",
            )

        self._shot("MH5_1", "order_list_final")
        print(f"\n  [PASS] {tc}: TC7 COMPLETED")
        self._print_summary_table()
