"""Base class cho full price flow tests.

Chứa toàn bộ helpers dùng chung: assert giá, ghi kết quả, in báo cáo,
và các khối verify MH7→MH9 (Order / My Orders / Chi tiết) + Admin.

Subclass chỉ cần override:
  _MH_NAMES   : dict mapping MHxx → tên màn hình
  _REPORT_TITLE : tiêu đề báo cáo Markdown
  tc / root / domain : gán trong setup fixture
"""
import json
import os
import re

import pytest


# ── Shared price-parsing util ─────────────────────────────────────────────────

def parse_int(val) -> int | None:
    """Strip dấu phân cách và chuyển sang int. Trả về None nếu rỗng."""
    if not val:
        return None
    digits = re.sub(r"[^\d]", "", str(val))
    return int(digits) if digits else None


# ── Admin page text parser (dùng chung cho MH10/MH11) ────────────────────────

def parse_admin_page(text: str) -> dict:
    """Parse nội dung trang Admin detail. Trả về dict các field quan trọng."""
    import re as _re
    result: dict = {}
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Mã đơn hàng (POD-...)
    m = _re.search(r"(POD-[\w-]+)", text)
    result["order_code"] = m.group(1) if m else ""

    # Trạng thái đơn hàng
    for kw in ["Chờ xác nhận", "Đang xử lý", "Đã xác nhận",
               "Đang giao", "Hoàn thành", "Đã hủy"]:
        if kw in text:
            result["trang_thai"] = kw
            break

    # Trạng thái thanh toán
    for kw in ["Chưa thanh toán", "Đã thanh toán", "Hoàn tiền"]:
        if kw in text:
            result["thanh_toan"] = kw
            break

    # Tên sản phẩm — "ProductName (Màu, Size) × Qty" pattern
    m = _re.search(r"^([^\n(]+?)\s+\([^)]+\)\s*[×x]\s*\d+", text, _re.MULTILINE)
    if m:
        result["ten_sp"] = m.group(1).strip()
    else:
        for line in lines:
            if _re.search(r"Áo Phông|áo phông", line, _re.I):
                result["ten_sp"] = line
                break

    # Màu + Size + Qty — "(Màu, Size) × Qty" pattern, multi-item support
    _COLORS = r"Trắng|Đen|Xanh|Đỏ|Hồng|Vàng|Xám|Nâu|Cam|Tím"
    all_items = _re.findall(
        rf"\(({_COLORS}),\s*([A-Z0-9]+)\)\s*[×x]\s*(\d+)", text, _re.I
    )
    if all_items:
        result["mau"]   = all_items[0][0]
        result["sizes"] = [(item[1].upper(), int(item[2])) for item in all_items]
        result["size"]  = all_items[0][1].upper()
        result["qty"]   = int(all_items[0][2])
    else:
        mc = _re.search(rf"({_COLORS})", text, _re.I)
        result["mau"] = mc.group(1) if mc else ""
        ms = _re.search(r"\b(XS|S|M|L|XL|2XL|3XL)\b", text, _re.I)
        result["size"] = ms.group(1).upper() if ms else ""
        result["qty"]  = None
        result["sizes"] = []

    # Email, SĐT
    m = _re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    result["email"] = m.group(0) if m else ""
    m = _re.search(r"0\d{9,10}", text)
    result["phone"] = m.group(0) if m else ""

    # Tất cả số tiền ≥ 1000 trên trang
    amounts = _re.findall(r"(\d{1,3}(?:[.,]\d{3})+)\s*(?:đ|₫|vnd)?", text, _re.I)
    seen: set = set()
    unique: list = []
    for a in amounts:
        val = int(_re.sub(r"[^\d]", "", a))
        if val not in seen and val >= 1000:
            seen.add(val)
            unique.append(val)
    result["raw_amounts"] = unique
    return result


# ── Base test class ───────────────────────────────────────────────────────────

class BasePriceFlowTest:
    """Lớp cơ sở cho full price flow tests.

    Subclass phải:
      1. Gán tc, root, domain trong setup fixture
      2. Override _MH_NAMES và _REPORT_TITLE
      3. Gọi self.home/listing/detail/studio/auth/checkout/env/page từ setup
    """

    # ── Override trong subclass ───────────────────────────────────────────────
    _MH_NAMES: dict = {}
    _REPORT_TITLE: str = "Price Flow Test"

    # ── Core helpers ──────────────────────────────────────────────────────────

    def _login(self) -> None:
        email, password = self.env.login_email, self.env.login_password
        if not email or not password:
            pytest.skip(f"SKIP {self.tc}: Thiếu credentials trong .env")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1000)
        self.auth.login(email, password)
        self.page.wait_for_timeout(3000)
        ok = not self.home.header.login_button.is_visible(timeout=5000)
        assert ok, f"LỖI Login ({self.tc}): Đăng nhập thất bại"
        print(f"  [PASS] Login: OK")

    def _shot(self, step: str, label: str) -> None:
        self.detail.shot(self.tc, step, label, domain=self.domain, root=self.root)

    TOLERANCE: int = 1_000  # override trong subclass nếu cần

    def _assert_price(self, displayed: int | None, expected: int | None, label: str) -> None:
        """So sánh giá displayed vs expected, ghi kết quả, assert nếu fail."""
        if expected is None:
            val = f"{displayed:,}đ" if displayed else "N/A"
            self._record(label, "ℹ️ INFO", val, "")
            print(f"  [INFO] {label}: {val}")
            return
        if displayed is None:
            self._record(label, "⚠️ WARN", "N/A", f"expected={expected:,}đ")
            print(f"  [WARN] {label}: Không đọc được giá — bỏ qua assert")
            return
        tol = getattr(self, "TOLERANCE", 1_000)
        ok = abs(displayed - expected) <= tol
        symbol = "✅ PASS" if ok else "❌ FAIL"
        reason = ""
        if not ok:
            diff = displayed - expected
            reason = (
                f" → NGUYÊN NHÂN: expected={expected:,}đ, displayed={displayed:,}đ "
                f"(chênh lệch {diff:+,}đ). Kiểm tra lại giá trong config hoặc công thức tính."
            )
        self._record(label, symbol, f"{displayed:,}đ", f"{expected:,}đ")
        print(f"  [{symbol}] {label} | expected={expected:,}đ | displayed={displayed:,}đ{reason}")
        assert ok, f"LỖI GIÁ [{label}]:{reason}"

    def _record(self, check: str, status: str, actual: str, expected: str) -> None:
        mh = ""
        for part in ["MH11", "MH10", "MH1", "MH2", "MH3", "MH4", "MH5",
                     "MH6", "MH7", "MH8", "MH9", "Login"]:
            if part in check:
                mh = part
                break
        self._results.append({"mh": mh, "check": check, "status": status,
                               "actual": actual, "expected": expected})

    def _record_check(self, mh: str, check: str, status: str,
                      actual: str = "", expected: str = "") -> None:
        self._results.append({"mh": mh, "check": check, "status": status,
                               "actual": actual, "expected": expected})

    # ── Discount helper ───────────────────────────────────────────────────────

    @staticmethod
    def calculate_discount(
        code: str,
        subtotal: int = 0,
        shipping: int = 0,
        sale_ao: int = 0,
        cost_ao: int = 0,
        print_total: int = 0,
        total_items: int = 0,
        # ── tham số bổ sung cho maisize1 / maisizeall / maiallcart ───────────
        # variants: list[dict] — mỗi phần tử {"sale": int, "cost": int, "qty": int}
        # Dùng khi cần tính margin per-variant thay vì flat sale_ao/cost_ao
        variants: list | None = None,
    ) -> int:
        """Tính giá trị giảm giá theo mã KM.

        Tham số cơ bản (tương thích ngược):
          subtotal    — tổng giá trước VAT/ship
          shipping    — phí vận chuyển
          sale_ao     — giá bán áo (1 variant, flat)
          cost_ao     — giá vốn áo (1 variant, flat)
          print_total — tổng giá in (trước VAT, flat)
          total_items — tổng số sản phẩm (qty)

        Tham số mở rộng:
          variants    — list[{"sale": int, "cost": int, "qty": int}]
                        Dùng cho maisize1 / maisizeall / maiallcart khi đơn có
                        nhiều variant khác nhau. Nếu None, fallback về sale_ao/cost_ao.
        """
        code_upper = code.strip().upper()

        # ── Mã phần trăm / cố định ─────────────────────────────────────────
        if code_upper == "GIAM20":
            return int(subtotal * 0.20)

        if code_upper == "SAVE50K":
            return min(50_000, subtotal)

        if code_upper == "MAIFREESHIP":
            return shipping

        # ── Helper: margin hình in ─────────────────────────────────────────
        def _margin_in(pt: int) -> int:
            if pt == 0:
                return 0
            # Công thức: costPrice_in = salePrice_in / 1.20 → margin = sale - cost = sale/6
            return pt - int(pt / 1.20)

        # ── USERMAI: Σ margin × qty (flat variant) ────────────────────────
        if code_upper == "USERMAI":
            margin_ao = sale_ao - cost_ao
            margin_per_item = margin_ao + _margin_in(print_total)
            return margin_per_item * total_items

        # ── maisize1: margin của 1 item có giá cao nhất × 1 ───────────────
        # Áp dụng cho 1 size (qty=1) có salePrice cao nhất trong đơn.
        # Nếu variants được cung cấp → tìm variant có sale lớn nhất.
        # Nếu không → dùng sale_ao / cost_ao trực tiếp (đã là max).
        if code_upper == "MAISIZE1":
            if variants:
                max_v = max(variants, key=lambda v: v.get("sale", 0))
                margin_ao = max_v.get("sale", 0) - max_v.get("cost", 0)
            else:
                margin_ao = sale_ao - cost_ao
            return margin_ao + _margin_in(print_total)

        # ── maisizeall: margin của variant đắt nhất × tổng qty toàn đơn
        #    Variant có salePrice cao nhất → lấy margin đó × Σqty (không nhân per-variant)
        #    → Mức giảm cao nhất trong 1 đơn (all items hưởng rate của item đắt nhất)
        if code_upper == "MAISIZEALL":
            if variants:
                max_v      = max(variants, key=lambda v: v.get("sale", 0))
                max_margin = max_v.get("sale", 0) - max_v.get("cost", 0)
                total_qty  = sum(v.get("qty", 1) for v in variants)
                total_disc = max_margin * total_qty
            else:
                total_disc = (sale_ao - cost_ao) * total_items
            margin_in_total = _margin_in(print_total) * total_items
            return total_disc + margin_in_total

        # ── maiallcart: Σ margin × qty cho từng variant thực tế trong giỏ ─
        # Giống USERMAI nhưng variants là toàn bộ giỏ hàng (nhiều đơn khác nhau).
        if code_upper == "MAIALLCART":
            if variants:
                return sum(
                    (v.get("sale", 0) - v.get("cost", 0)) * v.get("qty", 1)
                    + _margin_in(v.get("print_total", 0)) * v.get("qty", 1)
                    for v in variants
                )
            else:
                margin_ao = sale_ao - cost_ao
                margin_per_item = margin_ao + _margin_in(print_total)
                return margin_per_item * total_items

        return 0

    # ── Report helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _text_width(s: str) -> int:
        w = 0
        for c in s:
            cp = ord(c)
            if 0xFE00 <= cp <= 0xFE0F or cp == 0x200D:
                continue
            elif cp > 0x2500:
                w += 2
            else:
                w += 1
        return w

    @staticmethod
    def _pad_cell(s: str, target_width: int) -> str:
        return s + " " * max(0, target_width - BasePriceFlowTest._text_width(s))

    def _print_summary_table(self) -> None:
        print("\n")
        print("═" * 140)
        print(f"  📋 BẢNG TỔNG HỢP KẾT QUẢ TEST — {self._REPORT_TITLE}")
        print("═" * 140)
        print(f"  {'#':<4} {'MH':<5} {'Màn hình':<22} {'Kiểm tra':<40} "
              f"{'Kết quả':<12} {'Thực tế':<20} {'Mong đợi':<20}")
        print("─" * 140)

        passed = failed = warned = info_count = 0
        for i, r in enumerate(self._results, 1):
            s = r["status"]
            if "PASS" in s:   passed    += 1
            elif "FAIL" in s: failed    += 1
            elif "WARN" in s: warned    += 1
            else:             info_count += 1
            mh = r["mh"]
            screen = self._MH_NAMES.get(mh, "")[:20]
            print(f"  {i:<4} {mh:<5} {screen:<22} {r['check'][:38]:<40} {s:<12} "
                  f"{str(r['actual'])[:18]:<20} {str(r['expected'])[:18]:<20}")

        print("─" * 140)
        total = len(self._results)
        print(f"  TỔNG: {total} | ✅ PASS: {passed} | ❌ FAIL: {failed} | "
              f"⚠️ WARN: {warned} | ℹ️ INFO: {info_count}")
        verdict = "🎉 TẤT CẢ KIỂM TRA ĐỀU PASS!" if failed == 0 else f"❌ CÓ {failed} KIỂM TRA FAIL!"
        print(f"\n  {verdict}")
        print("═" * 115)
        self._save_summary_report(passed, failed, warned, info_count)

    def _save_summary_report(self, passed: int, failed: int, warned: int, info_count: int) -> None:
        from datetime import datetime
        import glob as _glob

        report_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "price_flow")
        os.makedirs(report_dir, exist_ok=True)

        slug = re.sub(r"[^a-zA-Z0-9_]", "_", self.tc)
        for old in _glob.glob(os.path.join(report_dir, f"{slug}_price_flow_*.md")):
            try:
                os.remove(old)
            except OSError:
                pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(report_dir, f"{slug}_price_flow_{ts}.md")
        total = len(self._results)
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        rows = []
        for i, r in enumerate(self._results, 1):
            _mh = str(r["mh"]).replace("\n", " ")
            _screen = str(self._MH_NAMES.get(r["mh"], "")).replace("\n", " ")
            _check = str(r["check"]).replace("\n", " ")
            _status = str(r["status"]).replace("\n", " ")
            _actual = str(r["actual"]).replace("\n", " ") if r["actual"] else "—"
            _expected = str(r["expected"]).replace("\n", " ") if r["expected"] else ("" if "INFO" in r.get("status","") else "—")
            
            rows.append((str(i), _mh, _screen, _check, _status, _actual, _expected))

        headers = ("#", "MH", "Màn hình", "Kiểm tra", "Kết quả", "Thực tế", "Mong đợi")
        tw = self._text_width
        col_w = [max(tw(headers[ci]), max((tw(row[ci]) for row in rows), default=0)) + 1
                 for ci in range(len(headers))]

        def fmt_row(cells):
            return "| " + " | ".join(self._pad_cell(c, col_w[ci]) for ci, c in enumerate(cells)) + " |"
            
        sep = "|" + "|".join("-" * (w + 2) for w in col_w) + "|"

        lines = [
            f"# {self._REPORT_TITLE}", "",
            f"| Ngày chạy  | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} |",
            "| ---------- | ------- |",
            f"| Môi trường | TEST — `test.shop.tryonic.ai` |",
            f"| Kết quả    | {verdict} |",
            f"| Tổng       | {total} kiểm tra &nbsp; ✅ {passed} &nbsp; ❌ {failed} &nbsp; "
            f"⚠️ {warned} &nbsp; ℹ️ {info_count} |",
            "", "## Bảng chi tiết", "", fmt_row(headers), sep,
            *[fmt_row(r) for r in rows], "", "## Tóm tắt", "",
            ("> ✅ **TẤT CẢ KIỂM TRA ĐỀU PASS!**" if failed == 0 and warned == 0
             else f"> ⚠️ **PASS nhưng có {warned} cảnh báo**" if failed == 0
             else f"> ❌ **CÓ {failed} KIỂM TRA FAIL — CẦN XỬ LÝ!**"),
            "",
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Báo cáo đã lưu: {filepath}")

    # ── Shared MH blocks ──────────────────────────────────────────────────────

    def _do_mh7_order(self, actual_total_paid: int, shipping: int) -> None:
        """MH7 — Order page (sau hủy QR): verify banner amount + shipping."""
        print(f"\n  ── MH7: Order (sau hủy QR) ───────────────────────────────")
        self.page.wait_for_load_state("domcontentloaded")
        self._shot("MH7_1", "order_page")

        banner_amt = self.checkout.read_order_banner_amount()
        self._assert_price(banner_amt, actual_total_paid, "MH7 Banner 'Vui lòng thanh toán'")

        parsed = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            const result = {};
            const re4 = /(-?\d{1,3}(?:[,.]\d{3})+|-?\d{4,})\s*[đ₫]?/;
            for (let i = 0; i < lines.length; i++) {
                if (/Phí vận chuyển|Phí giao hàng/i.test(lines[i])) {
                    let m = lines[i].match(re4) || (i+1 < lines.length && lines[i+1].match(re4));
                    if (m) result.shipping = m[1] || m[0];
                }
                if (/Thuế VAT|VAT/i.test(lines[i])) {
                    let m = lines[i].match(re4) || (i+1 < lines.length && lines[i+1].match(re4));
                    if (m) result.vat = m[1] || m[0];
                }
            }
            return result;
        }""")
        ship = parse_int(parsed.get("shipping"))
        vat  = parse_int(parsed.get("vat"))
        self._assert_price(vat, None, "MH7 Thuế VAT (8%) [info only]")
        self._assert_price(ship, shipping, "MH7 Phí giao hàng")
        print(f"  [PASS] MH7: Order prices OK")

    def _do_mh8_my_orders(self, actual_total_paid: int) -> None:
        """MH8 — Đơn hàng của tôi: verify price + trạng thái."""
        print(f"\n  ── MH8: Đơn hàng của tôi ────────────────────────────────")
        my_ok = self.checkout.click_my_orders()
        self.page.wait_for_timeout(2000)
        self._shot("MH8_1", "my_orders_page")

        if not (my_ok or "order" in self.page.url):
            print(f"  [WARN] MH8: Không navigate được — URL: {self.page.url}")
            return

        first_price = parse_int(self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            for (let i = 0; i < lines.length; i++) {
                if (/Tổng[:\s]/i.test(lines[i]) && !/Tổng (tiền|giá|cộng|thanh)/i.test(lines[i])) {
                    let m = lines[i].match(/(\d[\d,.]*\d)\s*[đ₫]/i);
                    if (m) return m[1];
                    if (i + 1 < lines.length) {
                        let m2 = lines[i+1].match(/(\d[\d,.]*\d)\s*[đ₫]/i);
                        if (m2) return m2[1];
                    }
                }
            }
            return null;
        }"""))
        self._assert_price(first_price, actual_total_paid, "MH8 Giá đơn hàng đầu tiên")

        page_text = self.page.evaluate("() => document.body.innerText")
        assert "Chờ xác nhận" in page_text, "LỖI MH8: Không thấy 'Chờ xác nhận'"
        self._record_check("MH8", "MH8 Trạng thái đơn hàng", "✅ PASS", "Chờ xác nhận", "Chờ xác nhận")
        assert "Chưa thanh toán" in page_text, "LỖI MH8: Không thấy 'Chưa thanh toán'"
        self._record_check("MH8", "MH8 Thanh toán", "✅ PASS", "Chưa thanh toán", "Chưa thanh toán")
        print(f"  [PASS] MH8: Trạng thái + giá OK")

    def _do_mh9_order_detail(
        self, order_info: dict, actual_total_paid: int, shipping: int,
        dc_ok: bool, discount_amount: int | None
    ) -> None:
        """MH9 — Chi tiết đơn hàng (popup): verify status, info SP, giá."""
        print(f"\n  ── MH9: Chi tiết đơn hàng ───────────────────────────────")
        chi_tiet_ok = self.checkout.click_order_chi_tiet(index=0)
        print(f"  [INFO] MH9: click_chi_tiet = {chi_tiet_ok}")
        self.page.wait_for_timeout(2000)

        if not chi_tiet_ok:
            self._shot("MH9_1", "order_detail_fallback")
            print(f"  [WARN] MH9: Không click được Chi tiết — URL: {self.page.url}")
            return

        popup_text = self.page.evaluate("() => document.body.innerText")
        assert "Chờ xác nhận" in popup_text, "LỖI MH9: Không thấy 'Chờ xác nhận' trong popup"
        self._record_check("MH9", "MH9 Trạng thái đơn hàng", "✅ PASS", "Chờ xác nhận", "Chờ xác nhận")
        assert "Chưa thanh toán" in popup_text, "LỖI MH9: Không thấy 'Chưa thanh toán' trong popup"
        self._record_check("MH9", "MH9 Thanh toán", "✅ PASS", "Chưa thanh toán", "Chưa thanh toán")

        detail_info = self.checkout.read_order_detail_info()
        self._shot("MH9_1", "order_detail_popup")
        print(f"  [INFO] MH9: detail_info = {detail_info}")

        # Tên sản phẩm
        product_name = order_info.get("product_name", "")
        if detail_info.get("product_name"):
            ok = product_name.lower() in detail_info["product_name"].lower()
            status = "✅ PASS" if ok else "⚠️ WARN"
            self._record_check("MH9", "MH9 Tên sản phẩm", status,
                               detail_info["product_name"][:20], product_name)
            print(f"  [{status}] MH9 Tên SP: '{detail_info['product_name']}'")

        # Màu
        color = order_info.get("color", "")
        if detail_info.get("color"):
            ok = color.lower() in detail_info["color"].lower()
            status = "✅ PASS" if ok else "❌ FAIL"
            self._record_check("MH9", "MH9 Màu áo", status, detail_info["color"], color)
            print(f"  [{status}] MH9 Màu: '{detail_info['color']}'")
            if not ok:
                assert False, f"LỖI MH9: Màu không khớp — expected '{color}' in '{detail_info['color']}'"

        # Size — chấp nhận bất kỳ size nào thuộc danh sách order_info["sizes"]
        # (multi-size order popup có thể hiển thị sizes theo thứ tự khác)
        expected_size = order_info.get("size", "")
        if expected_size and detail_info.get("size"):
            all_sizes = order_info.get("sizes") or [expected_size]
            ok = (expected_size in detail_info["size"]
                  or detail_info["size"] in all_sizes)
            status = "✅ PASS" if ok else "❌ FAIL"
            self._record_check("MH9", "MH9 Size", status, detail_info["size"], str(all_sizes))
            print(f"  [{status}] MH9 Size: '{detail_info['size']}' (expected in {all_sizes})")
            if not ok:
                assert False, (
                    f"LỖI MH9: Size không khớp — "
                    f"expected one of {all_sizes} but got '{detail_info['size']}'"
                )

        # Qty (đơn hoặc per-size)
        expected_qty = order_info.get("qty", 0)
        if expected_qty and detail_info.get("qty") is not None:
            ok = detail_info["qty"] == expected_qty
            status = "✅ PASS" if ok else "❌ FAIL"
            self._record_check("MH9", "MH9 Số lượng", status,
                               str(detail_info["qty"]), str(expected_qty))
            print(f"  [{status}] MH9 Qty: {detail_info['qty']}")

        # SĐT
        if order_info.get("phone") and detail_info.get("phone"):
            ok = order_info["phone"] in detail_info["phone"]
            if ok:
                print(f"  [PASS] MH9 SĐT: '{detail_info['phone']}'")
            else:
                print(f"  [WARN] MH9 SĐT mismatch: expected {order_info['phone']}, got {detail_info['phone']}")

        # Giá trong phần THANH TOÁN
        detail_prices = self.checkout.read_order_detail_prices()
        self._shot("MH9_2", "order_detail_payment")
        print(f"  [INFO] MH9: detail_prices = {detail_prices}")

        self._assert_price(detail_prices.get("phi_van_chuyen"), shipping, "MH9 Phí vận chuyển")
        if dc_ok and discount_amount:
            self._assert_price(detail_prices.get("giam_gia"), discount_amount, "MH9 Giảm giá (mã)")
        else:
            self._assert_price(detail_prices.get("giam_gia"), None, "MH9 Giảm giá [info]")
        self._assert_price(detail_prices.get("thue_vat"), None, "MH9 Thuế VAT [info]")
        self._assert_price(detail_prices.get("tong_cong"), actual_total_paid, "MH9 Tổng cộng")
        print(f"  [PASS] MH9: Order detail prices verified")

    def _do_admin_verify(
        self, mh_label: str, order_code: str, order_info: dict,
        actual_total_paid: int, shipping: int
    ) -> None:
        """Admin verify block (MH10 hoặc MH11).

        order_info có thể chứa:
          product_name, color, size (đơn) | sizes (list, multi),
          qty (đơn) | qty_per_size (multi), phone, receiver_name
        """
        print(f"\n  ── {mh_label}: Admin — Verify đơn hàng ────────────────")
        try:
            admin_email    = self.env.admin_email
            admin_password = self.env.admin_password
            admin_url      = self.env.admin_url

            if not admin_email or not admin_password:
                self._record_check(mh_label, f"{mh_label} Admin login", "⚠️ WARN",
                                   "Thiếu credentials", "ADMIN_EMAIL / ADMIN_PASSWORD trong .env")
                print(f"  [WARN] {mh_label}: Thiếu admin credentials — bỏ qua")
                return

            if not order_code:
                self._record_check(mh_label, f"{mh_label} Admin — tìm đơn", "⚠️ WARN",
                                   "order_code rỗng", "orderCode từ URL MH6")
                print(f"  [WARN] {mh_label}: Không có order_code — bỏ qua")
                return

            # ── Bước 1: Login admin ───────────────────────────────────────
            self.page.goto(admin_url, wait_until="domcontentloaded", timeout=30_000)
            self.page.wait_for_timeout(2000)

            email_input = self.page.locator(
                "input[type='email'], input[name='email'], input[placeholder*='mail' i]"
            ).first
            if email_input.is_visible(timeout=5000):
                email_input.fill(admin_email)
                self.page.locator("input[type='password'], input[name='password']").first.fill(admin_password)
                self.page.locator(
                    "button[type='submit'], button:has-text('Đăng nhập'), button:has-text('Login')"
                ).first.click()
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(2000)

            still_login = self.page.locator(
                "input[type='email'], input[type='password']"
            ).first.is_visible(timeout=3000)
            if still_login:
                self._record_check(mh_label, f"{mh_label} Admin login", "⚠️ WARN",
                                   "Login thất bại", "Vẫn còn form login")
                print(f"  [WARN] {mh_label}: Admin login thất bại")
                return

            self._record_check(mh_label, f"{mh_label} Admin login", "✅ PASS", "OK", "Đăng nhập thành công")
            print(f"  [PASS] {mh_label}: Admin login OK")

            # ── Bước 2: Search đơn hàng ───────────────────────────────────
            orders_url = admin_url.rstrip("/") + "/orders"
            self.page.goto(orders_url, wait_until="domcontentloaded", timeout=30_000)
            self.page.wait_for_timeout(2000)

            search_box = self.page.locator(
                "input[placeholder*='tìm' i], input[placeholder*='Mã' i], "
                "input[placeholder*='search' i], input[type='search']"
            ).first
            if search_box.is_visible(timeout=5000):
                search_box.fill(order_code)
                search_box.press("Enter")
                self.page.wait_for_timeout(2000)
            self._shot(f"{mh_label}_1", "admin_order_list")

            # ── Bước 3: Click vào order row ───────────────────────────────
            order_btn = self.page.locator(f"button:has-text('{order_code}')").first
            clicked = False
            if order_btn.is_visible(timeout=5000):
                current_url = self.page.url
                order_btn.click()
                try:
                    self.page.wait_for_url(lambda url: url != current_url, timeout=10_000)
                except Exception:
                    pass
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                self.page.wait_for_timeout(2000)
                clicked = True
                self._shot(f"{mh_label}_2", "admin_order_detail")
            else:
                self._record_check(mh_label, f"{mh_label} Admin — tìm đơn", "⚠️ WARN",
                                   "Không tìm thấy", order_code)
                print(f"  [WARN] {mh_label}: Không tìm thấy {order_code} trên admin")
                return

            if not clicked:
                return

            # ── Bước 4: Parse + verify ────────────────────────────────────
            admin_text = self.page.evaluate("() => document.body.innerText || ''")
            d = parse_admin_page(admin_text)
            print(f"  [INFO] {mh_label}: admin_data = {d}")

            product_name = order_info.get("product_name", "")
            color = order_info.get("color", "")

            # Mã đơn hàng
            if d.get("order_code") and order_code in d["order_code"]:
                self._record_check(mh_label, f"{mh_label} Mã đơn hàng", "✅ PASS",
                                   d["order_code"], order_code)
                print(f"  [PASS] {mh_label} Mã đơn: '{d['order_code']}'")
            else:
                self._record_check(mh_label, f"{mh_label} Mã đơn hàng", "⚠️ WARN",
                                   d.get("order_code", "N/A"), order_code)

            # Trạng thái đơn
            if d.get("trang_thai"):
                ok = "xác nhận" in d["trang_thai"].lower()
                status = "✅ PASS" if ok else "❌ FAIL"
                self._record_check(mh_label, f"{mh_label} Trạng thái đơn", status,
                                   d["trang_thai"], "Chờ xác nhận")
                print(f"  [{status}] {mh_label} Trạng thái: '{d['trang_thai']}'")
                assert ok, f"LỖI {mh_label}: Trạng thái sai — got '{d['trang_thai']}'"

            # Trạng thái thanh toán
            if d.get("thanh_toan"):
                ok = "chưa" in d["thanh_toan"].lower()
                status = "✅ PASS" if ok else "❌ FAIL"
                self._record_check(mh_label, f"{mh_label} Trạng thái TT", status,
                                   d["thanh_toan"], "Chưa thanh toán")
                print(f"  [{status}] {mh_label} TT: '{d['thanh_toan']}'")
                assert ok, f"LỖI {mh_label}: Thanh toán sai — got '{d['thanh_toan']}'"

            # Tên sản phẩm
            if d.get("ten_sp") and product_name.lower() in d["ten_sp"].lower():
                self._record_check(mh_label, f"{mh_label} Tên sản phẩm", "✅ PASS",
                                   d["ten_sp"], product_name)
                print(f"  [PASS] {mh_label} Tên SP: '{d['ten_sp']}'")
            else:
                self._record_check(mh_label, f"{mh_label} Tên sản phẩm", "⚠️ WARN",
                                   d.get("ten_sp", "N/A"), product_name)

            # Màu áo
            if d.get("mau"):
                ok = color.lower() in d["mau"].lower()
                status = "✅ PASS" if ok else "❌ FAIL"
                self._record_check(mh_label, f"{mh_label} Màu áo", status, d["mau"], color)
                print(f"  [{status}] {mh_label} Màu: '{d['mau']}'")

            # Sizes (đơn hoặc multi)
            expected_sizes = order_info.get("sizes") or (
                [order_info["size"]] if order_info.get("size") else []
            )
            found_sizes = [s[0] for s in d.get("sizes", [])] if d.get("sizes") else (
                [d["size"]] if d.get("size") else []
            )
            if found_sizes:
                all_ok = all(s in found_sizes for s in expected_sizes)
                status = "✅ PASS" if all_ok else "⚠️ WARN"
                self._record_check(mh_label, f"{mh_label} Sizes ({len(found_sizes)})", status,
                                   str(found_sizes[:5]), str(expected_sizes[:5]))
                print(f"  [{status}] {mh_label} Sizes: {found_sizes}")

            # Email khách hàng
            if d.get("email"):
                ok = self.env.login_email.lower() in d["email"].lower()
                status = "✅ PASS" if ok else "❌ FAIL"
                self._record_check(mh_label, f"{mh_label} Email KH", status,
                                   d["email"], self.env.login_email)
                print(f"  [{status}] {mh_label} Email: '{d['email']}'")

            # SĐT
            if d.get("phone") and order_info.get("phone"):
                ok = order_info["phone"] in d["phone"]
                status = "✅ PASS" if ok else "❌ FAIL"
                self._record_check(mh_label, f"{mh_label} SĐT người nhận", status,
                                   d["phone"], order_info["phone"])
                print(f"  [{status}] {mh_label} SĐT: '{d['phone']}'")

            # Scroll xuống phần "Chi tiết giá" để chụp full thông tin
            self.page.evaluate("""() => {
                const el = [...document.querySelectorAll('*')].find(
                    e => e.textContent.includes('Chi tiết giá') && e.offsetHeight > 0
                );
                if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                else window.scrollTo(0, document.body.scrollHeight);
            }""")
            self.page.wait_for_timeout(1000)
            self._shot(f"{mh_label}_3", "admin_order_price_detail")

            # Scroll thêm xuống cuối để chụp phần tổng cộng nếu bị che
            self.page.evaluate("() => window.scrollBy(0, 400)")
            self.page.wait_for_timeout(500)
            self._shot(f"{mh_label}_4", "admin_order_price_total")

            # Kiểm tra giá tiền trong raw_amounts
            raw = d.get("raw_amounts", [])
            tol = getattr(self, "TOLERANCE", 1_000)

            total_found = next((v for v in raw if abs(v - actual_total_paid) <= tol), None)
            self._assert_price(total_found, actual_total_paid, f"{mh_label} Tổng cộng")

            ship_found = next((v for v in raw if abs(v - shipping) <= tol), None)
            self._assert_price(ship_found, shipping, f"{mh_label} Phí vận chuyển")

            print(f"  [PASS] {mh_label}: Admin verify OK")

        except AssertionError:
            raise
        except Exception as e:
            self._record_check(mh_label, f"{mh_label} Admin — unexpected error", "⚠️ WARN",
                               str(e)[:80], "")
            print(f"  [WARN] {mh_label}: Lỗi không mong đợi — {e}")

    # ── Checkout / QR shared helpers ─────────────────────────────────────────

    def _wait_checkout_breakdown(self) -> None:
        """Chờ checkout page render đủ phần Thuế VAT / Phí giao hàng."""
        try:
            self.page.wait_for_function(
                "() => document.body.innerText.includes('Thuế VAT')",
                timeout=15000
            )
        except Exception:
            self.page.wait_for_timeout(3000)

    def _read_order_page_price(self) -> int | None:
        """Đọc tổng giá trên trang đặt hàng Studio (step 3 — sau chọn size)."""
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            // Tìm "Tổng (N sản phẩm)\nX.XXXđ" hoặc inline "Tổng (N sản phẩm): X.XXXđ"
            const m = text.match(
                /Tổng\s*\(\d+\s*sản phẩm\)[^\d]*(\d{1,3}(?:[.,]\d{3})+)/
            );
            if (m) return parseInt(m[1].replace(/[^\d]/g, ''));

            // Fallback: tìm giá lớn nhất trong section Chi tiết giá
            const els = document.querySelectorAll('*');
            for (const el of els) {
                const t = (el.innerText || '').trim();
                if (/chi tiết giá/i.test(t) && el.children.length < 15) {
                    const amounts = [...t.matchAll(/(\d{1,3}(?:[.,]\d{3})+)\s*[đ₫]/g)]
                        .map(m => parseInt(m[1].replace(/[^\d]/g, '')))
                        .filter(n => n >= 10000);
                    if (amounts.length) return Math.max(...amounts);
                }
            }
            return null;
        }""")

    def _read_review_prices(self) -> dict:
        """Đọc giá in từ màn hình Review/Studio xác nhận thiết kế."""
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            let print_total = 0;
            let ao_total = 0;
            let sum_total = 0;
            const priceRe = /(\d{1,3}(?:[,.]\d{3})+)/;

            for (let i = 0; i < lines.length; i++) {
                if (/Giá in|Phí in|Công nghệ in/i.test(lines[i])) {
                    let m = lines[i].match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) print_total += parseInt(m[1].replace(/[^\d]/g, ''));
                }
                if (/Giá áo|Áo phông/i.test(lines[i]) && !ao_total) {
                    let m = lines[i].match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) ao_total = parseInt(m[1].replace(/[^\d]/g, ''));
                }
                if (/Tạm tính|Tổng cộng/i.test(lines[i])) {
                    let m = lines[i].match(priceRe);
                    if (!m && i+1 < lines.length) m = lines[i+1].match(priceRe);
                    if (m) sum_total = parseInt(m[1].replace(/[^\d]/g, ''));
                }
            }
            return { print_total, ao_total, sum_total };
        }""")

    def _do_mh6_qr(self, actual_total: int) -> None:
        """Xử lý màn hình QR: verify số tiền, hủy QR, navigate sang Order."""
        mh_label = "MH6"
        print(f"\n  ── {mh_label}: Mã QR Code ───────────────────────────────────────")
        self.page.wait_for_timeout(3000)
        self._shot(f"{mh_label}_1", "qr_code_page")

        qr_amt = self.checkout.read_qr_note_amount() or self.checkout.read_qr_amount()
        self._assert_price(qr_amt, actual_total, f"{mh_label} Số tiền thanh toán QR")

        ok_cancel = self.checkout.click_cancel_qr()
        if ok_cancel:
            self.checkout.confirm_cancel_dialog()
            self.page.wait_for_timeout(2000)
            self.checkout.click_view_order()
