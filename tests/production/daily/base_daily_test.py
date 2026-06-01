from __future__ import annotations
"""Base class cho daily smoke tests.

Dừng ở màn hình checkout — không submit đơn, không tạo rác trên production.
Report format: numbered list (giống SH07), lưu tại reports/daily/.

PROD SAFETY RULE: Test chỉ verify đến màn checkout — KHÔNG click nút Thanh toán.
"""
import csv
import glob as _glob
import os
import re
from datetime import datetime
from typing import ClassVar


def parse_int(val) -> int | None:
    if not val:
        return None
    digits = re.sub(r"[^\d]", "", str(val))
    return int(digits) if digits else None


def _clean_status(s: str) -> str:
    s = str(s)
    if "PASS" in s: return "PASS"
    if "FAIL" in s: return "FAIL"
    if "WARN" in s: return "WARN"
    if "SKIP" in s: return "SKIP"
    return s


def _extract_duration(s: str) -> str:
    m = re.search(r"(\d+\.?\d*)\s*s\b", str(s))
    return m.group(0) if m else ""


class BaseDailyTest:
    """Subclass phải khai báo:
      _SUITE_NAME  = "PRICE_CHECKOUT"     # dùng trong tên file report
      _REPORT_TITLE = "Daily Smoke: ..."  # tiêu đề H1
      _results: ClassVar[list] = []       # class-level
    """

    _SUITE_NAME: str = "DAILY"
    _REPORT_TITLE: str = "Daily Smoke Test"
    _results: ClassVar[list] = []

    # ── PROD Safety ──────────────────────────────────────────────────────────

    @property
    def _is_prod(self) -> bool:
        """True nếu đang chạy trên môi trường PROD."""
        fe_url = getattr(getattr(self, "env", None), "fe_url", "")
        return bool(fe_url) and "test." not in fe_url

    def _setup_prod_safety(self) -> None:
        """PROD safety: chặn tạo đơn hàng trên PROD bằng 2 lớp.

        Lớp 1 — Block API: abort mọi request tạo đơn → đơn không bao giờ được tạo
        Lớp 2 — Click guard: nếu click Thanh toán → pytest.fail ngay với message rõ ràng
        """
        if not self._is_prod:
            return

        # ── Lớp 1: Block API tạo đơn (abort request) ─────────────────────────
        _ORDER_PATTERNS = [
            "**/orders**",
            "**/checkout/submit**",
            "**/checkout/confirm**",
            "**/payment**",
            "**/place-order**",
        ]
        for pattern in _ORDER_PATTERNS:
            try:
                self.page.route(
                    pattern,
                    lambda route, *_args: route.fulfill(
                        status=403,
                        body='{"error":"PROD_SAFETY: Không được đặt đơn trên môi trường PROD"}',
                    )
                )
            except Exception:
                pass

        # ── Lớp 2: Click guard → pytest.fail ngay ────────────────────────────
        import pytest as _pytest

        def _on_payment_click():
            _pytest.fail("🚫 Không được đặt đơn trên môi trường PROD")

        try:
            self.page.expose_function("__prodSafetyViolation__", _on_payment_click)
        except Exception:
            pass  # đã expose ở lần trước

        self.page.add_init_script("""() => {
            const BLOCKED = ['Thanh toán', 'Đặt hàng', 'Xác nhận đơn',
                             'Place order', 'Submit order'];
            document.addEventListener('click', function(e) {
                const el = e.target.closest('button, [role="button"], a[href]');
                if (!el) return;
                const text = (el.innerText || el.textContent || '').trim();
                if (BLOCKED.some(b => text.includes(b))) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    if (window.__prodSafetyViolation__) {
                        window.__prodSafetyViolation__();
                    }
                }
            }, true);
        }""")
        print("  [PROD SAFETY] Đã kích hoạt: block API order + click guard Thanh toán")
    # ── Screenshot ───────────────────────────────────────────────────────────

    def _shot(self, tc_id: str, step: str, label: str) -> None:
        """Chụp screenshot vào screenshots/daily/<suite>/<tc_id>/."""
        shot_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "screenshots",
            "daily", self._SUITE_NAME, tc_id.replace(" ", "_"),
        )
        os.makedirs(shot_dir, exist_ok=True)
        ts = datetime.now().strftime("%H%M%S")
        fpath = os.path.join(shot_dir, f"S{step}_{label}_{ts}.png")
        try:
            self.page.screenshot(path=fpath, full_page=True)
            print(f"  [SHOT] {tc_id} S{step}: {label}")
        except Exception as e:
            print(f"  [SHOT FAIL] {tc_id} S{step}: {e}")

    # ── Ghi kết quả ──────────────────────────────────────────────────────────

    def _record_check(self, mh: str, check: str, status: str,
                      actual: str = "", expected: str = "") -> None:
        self._results.append({
            "mh": mh, "check": check, "status": status,
            "actual": actual, "expected": expected,
        })

    # ── Assert giá ───────────────────────────────────────────────────────────

    TOLERANCE: int = 1_000

    def _assert_price(self, displayed: int | None, expected: int | None,
                      label: str, mh: str = "CHECK") -> None:
        if displayed is None:
            self._record_check(mh, label, "⚠️ WARN", "N/A",
                               f"expected={expected:,}đ" if expected else "")
            return
        if expected is None:
            self._record_check(mh, label, "ℹ️ INFO",
                               f"{displayed:,}đ", "")
            return
        ok = abs(displayed - expected) <= self.TOLERANCE
        status = "✅ PASS" if ok else "❌ FAIL"
        self._record_check(mh, label, status,
                           f"{displayed:,}đ", f"{expected:,}đ")
        assert ok, (
            f"{label}: expected={expected:,}đ, got={displayed:,}đ "
            f"(chênh {displayed - expected:+,}đ)"
        )

    # ── Save report ───────────────────────────────────────────────────────────

    @classmethod
    def _save_report(cls) -> None:
        report_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "reports", "daily"
        )
        os.makedirs(report_dir, exist_ok=True)

        slug = cls._SUITE_NAME.lower()
        for old in _glob.glob(os.path.join(report_dir, f"{slug}_*.md")):
            try:
                os.remove(old)
            except OSError:
                pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ts_display = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        filepath = os.path.join(report_dir, f"{slug}_{ts}.md")

        results = cls._results
        total   = len(results)
        passed  = sum(1 for r in results if "PASS" in r.get("status", ""))
        failed  = sum(1 for r in results if "FAIL" in r.get("status", ""))
        warned  = sum(1 for r in results if "WARN" in r.get("status", ""))
        info_c  = sum(1 for r in results if "INFO" in r.get("status", ""))
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        tong_str = (
            f"{total} kiểm tra  ✅ {passed}  ❌ {failed}  ⚠️ {warned}  ℹ️ {info_c}"
        )
        import os as _os
        _test_env = _os.getenv("TEST_ENV", "test").lower()
        _env_label = (
            "PROD — `shop.tryonic.ai`"
            if _test_env == "prod"
            else "TEST — `test.shop.tryonic.ai`"
        )
        info_rows = [
            ("Ngày chạy",  ts_display),
            ("Môi trường", _env_label),
            ("Kết quả",    verdict),
            ("Tổng",       tong_str),
        ]
        iw1 = max(len(k) for k, _ in info_rows)
        iw2 = max(len(v) for _, v in info_rows)
        info_sep    = f"| {'-' * iw1} | {'-' * iw2} |"
        info_header = f"| {'Trường':<{iw1}} | {'Giá trị':<{iw2}} |"
        info_lines  = [info_header, info_sep] + [
            f"| {k:<{iw1}} | {v:<{iw2}} |" for k, v in info_rows
        ]

        detail_items: list[str] = []
        for i, r in enumerate(results, 1):
            _mh   = str(r["mh"]).replace("\n", " ")
            _chk  = str(r["check"]).replace("\n", " ")
            _sta  = str(r["status"]).replace("\n", " ")
            _act  = (str(r["actual"]).replace("\n", " / ")
                     if r.get("actual") else "—")
            _exp  = (str(r["expected"]).replace("\n", " ")
                     if r.get("expected") else (
                         "" if "INFO" in r.get("status", "") else "—"))
            icon = ("✅" if "PASS" in _sta else
                    "❌" if "FAIL" in _sta else
                    "⚠️" if "WARN" in _sta else "ℹ️")
            line1 = f"{i}. {icon} **{_mh}** — {_chk}"
            line2 = f"   → `{_act}`"
            if _exp and _exp != "—":
                line2 += f"  *(mong đợi: {_exp})*"
            detail_items += [line1, line2, ""]

        if failed == 0 and warned == 0:
            summary_line = "> ✅ **TẤT CẢ KIỂM TRA ĐỀU PASS!**"
        elif failed == 0:
            summary_line = f"> ⚠️ **PASS nhưng có {warned} cảnh báo**"
        else:
            summary_line = f"> ❌ **CÓ {failed} KIỂM TRA FAIL — CẦN XỬ LÝ!**"

        lines = (
            [f"# {cls._REPORT_TITLE}", ""]
            + info_lines
            + ["", "## Bảng chi tiết", ""]
            + detail_items
            + ["## Tóm tắt", "", summary_line, ""]
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Daily report: {filepath}")

        # ── CSV report ───────────────────────────────────────────────────────
        csv_path = filepath.replace(".md", ".csv")
        fields = ["no", "tc_id", "step", "expected_result", "actual_result", "status", "duration"]
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for i, r in enumerate(results, 1):
                mh  = str(r["mh"]).replace("\n", " ")
                chk = str(r["check"]).replace("\n", " ")
                sta = str(r["status"]).replace("\n", " ")
                act = str(r.get("actual", "")).replace("\n", " / ")
                exp = str(r.get("expected", "")).replace("\n", " ")
                writer.writerow({
                    "no":              i,
                    "tc_id":           mh,
                    "step":            chk,
                    "expected_result": exp,
                    "actual_result":   act,
                    "status":          _clean_status(sta),
                    "duration":        _extract_duration(act),
                })
