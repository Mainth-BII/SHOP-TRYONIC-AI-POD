"""
Base class cho các test Tiếp thị liên kết (Affiliate / Share store).

URL gốc: /affiliate
Cấu trúc trang gồm:
  - Thông tin gian hàng (banner + danh sách sản phẩm)
  - Stats: lượt click, số đơn, tổng hoa hồng, số dư
  - Danh sách đơn hàng liên kết
  - Lịch sử rút tiền
"""
from __future__ import annotations

import json

from ..price.base_price_flow import BasePriceFlowTest  # tái sử dụng login, report, assert


class BaseShareFlowTest(BasePriceFlowTest):
    """Base class cho affiliate tests — kế thừa login, screenshot, report."""

    AFFILIATE_URL   = "/affiliate"
    TOLERANCE       = 500   # sai số chấp nhận cho số tiền nhỏ (đ)
    _REPORT_SUBDIR  = "share"  # lưu vào reports/share/ thay vì reports/price_flow/

    def _save_summary_report(self, passed: int, failed: int, warned: int, info_count: int) -> None:
        """Override để lưu vào reports/share/."""
        import os as _os, re as _re, glob as _glob
        from datetime import datetime

        report_dir = _os.path.join(
            _os.path.dirname(__file__), "..", "..", "..", "reports", self._REPORT_SUBDIR
        )
        _os.makedirs(report_dir, exist_ok=True)

        slug = _re.sub(r"[^a-zA-Z0-9_]", "_", self.tc)
        for old in _glob.glob(_os.path.join(report_dir, f"{slug}_*.md")):
            try:
                _os.remove(old)
            except OSError:
                pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = _os.path.join(report_dir, f"{slug}_{ts}.md")
        total = len(self._results)
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        ts_display = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        tong_str = f"{total} kiểm tra  ✅ {passed}  ❌ {failed}  ⚠️ {warned}  ℹ️ {info_count}"
        info_rows = [
            ("Ngày chạy",  ts_display),
            ("Môi trường", "TEST — `test.shop.tryonic.ai`"),
            ("Kết quả",    verdict),
            ("Tổng",       tong_str),
        ]
        iw1 = max(len(k) for k, _ in info_rows)
        iw2 = max(len(v) for _, v in info_rows)
        info_sep = f"| {'-' * iw1} | {'-' * iw2} |"
        info_header = f"| {'Trường':<{iw1}} | {'Giá trị':<{iw2}} |"
        info_lines = [info_header, info_sep] + [f"| {k:<{iw1}} | {v:<{iw2}} |" for k, v in info_rows]

        detail_items = []
        for i, r in enumerate(self._results, 1):
            _mh     = str(r["mh"]).replace("\n", " ").replace("\t", " ")
            _check  = str(r["check"]).replace("\n", " ").replace("\t", " ")
            _status = str(r["status"]).replace("\n", " ").replace("\t", " ")
            _actual = str(r["actual"]).replace("\n", " ").replace("\t", " / ") if r["actual"] else "—"
            _expected = str(r["expected"]).replace("\n", " ").replace("\t", " ") if r["expected"] else (
                "" if "INFO" in r.get("status", "") else "—"
            )
            # Icon theo kết quả
            icon = "✅" if "PASS" in _status else ("❌" if "FAIL" in _status else ("⚠️" if "WARN" in _status else "ℹ️"))
            line1 = f"{i}. {icon} **{_mh}** — {_check}"
            line2 = f"   → `{_actual}`"
            if _expected and _expected != "—":
                line2 += f"  *(mong đợi: {_expected})*"
            detail_items += [line1, line2, ""]

        lines = [
            f"# {self._REPORT_TITLE}", "",
            *info_lines,
            "", "## Bảng chi tiết", "",
            *detail_items,
            "## Tóm tắt", "",
            ("> ✅ **TẤT CẢ KIỂM TRA ĐỀU PASS!**" if failed == 0 and warned == 0
             else f"> ⚠️ **PASS nhưng có {warned} cảnh báo**" if failed == 0
             else f"> ❌ **CÓ {failed} KIỂM TRA FAIL — CẦN XỬ LÝ!**"),
            "",
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Báo cáo đã lưu: {filepath}")

    # ── Navigate ──────────────────────────────────────────────────────────────

    def _goto_affiliate(self) -> None:
        base = self.env.fe_url.rstrip("/")
        self.page.goto(f"{base}{self.AFFILIATE_URL}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    def _click_tiep_thi_lien_ket_menu(self) -> bool:
        """Mở menu header → click 'Tiếp thị liên kết' → đến /affiliate."""
        try:
            menu_btn = self.page.locator("button:has-text('Menu')").first
            if menu_btn.is_visible(timeout=3000):
                menu_btn.click()
                self.page.wait_for_timeout(800)
        except Exception:
            pass

        try:
            link = self.page.locator("a:has-text('Tiếp thị liên kết'), a[href*='affiliate']").first
            if link.is_visible(timeout=4000):
                link.click()
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    # ── Kiểm tra trạng thái phê duyệt ────────────────────────────────────────

    def _is_affiliate_approved(self) -> bool:
        """True nếu user đã được duyệt vào chương trình affiliate."""
        text = self.page.evaluate("() => document.body.innerText || ''")
        not_approved_kw = ["chưa được duyệt", "chưa đăng ký", "liên hệ", "đăng ký"]
        return not any(kw in text.lower() for kw in not_approved_kw)

    # ── Đọc thông tin gian hàng ───────────────────────────────────────────────

    def _get_store_url(self) -> str | None:
        """Lấy URL gian hàng từ button [Xem] hoặc link /store/ /gian-hang/."""
        try:
            link = self.page.locator("a[href*='/store/'], a[href*='/gian-hang/'], a[href*='/shop/']").first
            if link.is_visible(timeout=3000):
                return link.get_attribute("href")
        except Exception:
            pass

        # Fallback: button Xem → lấy href của parent
        try:
            btn = self.page.locator("button:has-text('Xem'), a:has-text('Xem gian hàng'), a:has-text('Xem')").first
            if btn.is_visible(timeout=3000):
                href = btn.get_attribute("href")
                if href:
                    return href
                # Nếu là button (không có href) → click và lấy URL mới
                btn.click()
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(1500)
                return self.page.url
        except Exception:
            pass
        return None

    def _read_store_page(self) -> dict:
        """Đọc thông tin từ trang gian hàng: banner, tên, số SP."""
        text = self.page.evaluate("() => document.body.innerText || ''")

        banner_visible = bool(self.page.locator("img[src*='banner'], [class*='banner'] img, .hero img").first.is_visible(timeout=3000))
        product_cards  = self.page.locator("a[href*='/product/'], [class*='product-card'], [class*='ProductCard']").count()

        return {
            "banner_visible": banner_visible,
            "product_count":  product_cards,
            "page_text":      text,
        }

    # ── Đọc thống kê affiliate ────────────────────────────────────────────────

    def _read_affiliate_stat(self, label_pattern: str) -> int | None:
        """Đọc số liệu thống kê theo nhãn (regex), trả về int hoặc None.

        Tìm số ở trước label (2 dòng) hoặc sau label (2 dòng).
        Ưu tiên số nhỏ (<= 10000) để tránh nhầm với số tiền (₫).
        """
        return self.page.evaluate(f"""() => {{
            const text = document.body.innerText || '';
            const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
            const re = new RegExp({json.dumps(label_pattern)}, 'i');
            const numRe = /^[\\d,.]+$/;
            for (let i = 0; i < lines.length; i++) {{
                if (re.test(lines[i])) {{
                    // Ưu tiên dòng TRƯỚC label (thường là số liệu thống kê)
                    for (let j = 1; j <= 2; j++) {{
                        if (i - j >= 0) {{
                            const m = lines[i - j].match(/^[\\d,.]+$/);
                            if (m) {{
                                const n = parseInt(m[0].replace(/[^\\d]/g, ''));
                                if (n <= 100000) return n;  // Tránh nhầm số tiền lớn
                            }}
                        }}
                    }}
                    // Fallback: tìm số ở dòng hiện tại hoặc 2 dòng kế
                    for (let j = 0; j <= 2; j++) {{
                        if (i + j < lines.length) {{
                            const m = lines[i + j].match(/^[\\d,.]+$/);
                            if (m) {{
                                const n = parseInt(m[0].replace(/[^\\d]/g, ''));
                                if (n <= 100000) return n;
                            }}
                        }}
                    }}
                }}
            }}
            return null;
        }}""")

    def _read_click_count(self) -> int | None:
        return self._read_affiliate_stat(r"lượt click|số lượt|lượt truy cập|click")

    def _read_order_count(self) -> int | None:
        return self._read_affiliate_stat(r"số đơn|đơn hàng liên kết|số đơn hàng|^đơn hàng$|Đơn hàng")

    def _read_total_commission(self) -> int | None:
        return self._read_affiliate_stat(r"tổng hoa hồng|tổng tiền hoa hồng|tổng commission")

    def _read_balance(self) -> int | None:
        return self._read_affiliate_stat(r"số dư|số dư hoa hồng|số dư liên kết")

    # ── Đọc danh sách đơn hàng liên kết ──────────────────────────────────────

    def _read_affiliate_orders(self) -> list[dict]:
        """Đọc danh sách đơn hàng liên kết.

        Trả về list[dict] với keys: order_code, commission_rate, commission, date.
        """
        return self.page.evaluate(r"""() => {
            const rows = [];
            // Tìm table rows hoặc list items chứa thông tin đơn
            const trs = document.querySelectorAll('tr, [class*="order-row"], [class*="OrderRow"]');
            const numRe = /[\d,.]+/;
            const pctRe = /(\d+(?:\.\d+)?)\s*%/;
            const dateRe = /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2}/;
            const codeRe = /POD-[\w\-]+|[A-Z0-9]{6,}/;

            for (const tr of trs) {
                const text = tr.innerText || '';
                if (!text.trim()) continue;

                const pctM   = text.match(pctRe);
                const dateM  = text.match(dateRe);
                const codeM  = text.match(codeRe);
                // Tìm số tiền có dấu + hoặc ₫/đ đi kèm (hoa hồng)
                const priceMatches = [...text.matchAll(/\+\s*([\d,.]+)\s*[₫đ]/g)];
                const prices = priceMatches.length
                    ? priceMatches.map(m => parseInt(m[1].replace(/[^\d]/g, ''))).filter(n => n > 0)
                    : [...text.matchAll(/[\d,.]{4,}/g)]
                        .map(m => parseInt(m[0].replace(/[^\d]/g, '')))
                        .filter(n => n > 0 && n < 10000000);  // Loại trừ số lớn như ngày

                if (pctM || dateM || codeM) {
                    rows.push({
                        order_code:      codeM  ? codeM[0]              : '',
                        commission_rate: pctM   ? parseFloat(pctM[1])   : null,
                        commission:      prices.length ? Math.max(...prices) : null,
                        date:            dateM  ? dateM[0]               : '',
                        raw:             text.substring(0, 120),
                    });
                }
            }
            return rows;
        }""") or []

    # ── Đọc lịch sử rút tiền ─────────────────────────────────────────────────

    def _read_withdrawal_history(self) -> list[dict]:
        """Đọc lịch sử rút tiền, trả về list[dict] với keys: amount, date, status."""
        return self.page.evaluate(r"""() => {
            const items = [];
            const containers = document.querySelectorAll(
                '[class*="withdraw"], [class*="Withdraw"], [class*="rut-tien"], tr'
            );
            const numRe  = /[\d,.]{4,}/g;
            const dateRe = /\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2}/;
            const statRe = /thành công|đang xử lý|hoàn thành|từ chối|pending|success|failed/i;

            for (const el of containers) {
                const text = el.innerText || '';
                if (!text.trim()) continue;

                const amounts = [...text.matchAll(numRe)].map(m =>
                    parseInt(m[0].replace(/[^\d]/g, ''))
                ).filter(n => n > 1000);
                const dateM  = text.match(dateRe);
                const statM  = text.match(statRe);

                if (amounts.length || dateM) {
                    items.push({
                        amount: amounts.length ? Math.max(...amounts) : null,
                        date:   dateM  ? dateM[0]   : '',
                        status: statM  ? statM[0]   : '',
                        raw:    text.substring(0, 120),
                    });
                }
            }
            return items;
        }""") or []

    # ── Commission calculator ─────────────────────────────────────────────────

    @staticmethod
    def calc_commission(order_subtotal: int, rate_pct: float) -> int:
        """Tính hoa hồng: subtotal (không gồm ship, không gồm VAT) × rate%.

        Args:
            order_subtotal: Tổng tiền hàng chưa VAT, chưa ship (đ)
            rate_pct: Tỷ lệ hoa hồng (%), ví dụ 5.0 = 5%
        Returns:
            Số tiền hoa hồng (làm tròn xuống)
        """
        return int(order_subtotal * rate_pct / 100)

    # ── Assert helpers ────────────────────────────────────────────────────────

    def _assert_count(self, mh: str, label: str, actual: int | None,
                      expected_min: int = 0) -> None:
        """Assert giá trị đếm ≥ expected_min."""
        if actual is None:
            self._record_check(mh, label, "⚠️ WARN", "N/A", f"≥{expected_min}")
            return
        ok = actual >= expected_min
        self._record_check(mh, label,
                           "✅ PASS" if ok else "❌ FAIL",
                           str(actual), f"≥{expected_min}")

    def _assert_commission_formula(self, mh: str, order_code: str,
                                   subtotal: int, rate_pct: float,
                                   actual_commission: int | None) -> None:
        """Verify: hoa hồng = subtotal × rate% (không gồm VAT/ship)."""
        expected = self.calc_commission(subtotal, rate_pct)
        self._assert_price(actual_commission, expected,
                           f"{mh} Hoa hồng đơn {order_code} ({rate_pct}% × {subtotal:,}đ)")
