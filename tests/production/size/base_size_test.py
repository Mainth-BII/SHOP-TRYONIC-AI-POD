"""Base class cho AI size recommendation tests.

Subclass khai báo:
  _PRODUCT_CODE = "PT01"
  _PRODUCT_NAME = "Áo Phông Cá Tính"
  _REPORT_SLUG  = "pt01"
  _results: list = []   # class-level, shared across all parametrized cases
"""
import glob as _glob
import os
from datetime import datetime
from typing import ClassVar


class BaseSizeTest:
    _PRODUCT_CODE: str = ""
    _PRODUCT_NAME: str = ""
    _REPORT_SLUG: str = ""
    _results: ClassVar[list] = []

    # ── Report helpers (copied from BasePriceFlowTest) ────────────────────────

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

    @classmethod
    def _pad_cell(cls, s: str, target_width: int) -> str:
        return s + " " * max(0, target_width - cls._text_width(s))

    @staticmethod
    def _clip(s: str, n: int = 38) -> str:
        return s if len(s) <= n else s[: n - 1] + "…"

    # ── Report save ───────────────────────────────────────────────────────────

    @classmethod
    def _save_report(cls) -> None:
        report_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "reports", "size_guide"
        )
        os.makedirs(report_dir, exist_ok=True)

        slug = cls._REPORT_SLUG or cls._PRODUCT_CODE.lower()
        for old in _glob.glob(os.path.join(report_dir, f"{slug}_size_guide_*.md")):
            try:
                os.remove(old)
            except OSError:
                pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(report_dir, f"{slug}_size_guide_{ts}.md")

        results = cls._results
        total   = len(results)
        passed  = sum(1 for r in results if "PASS" in r.get("status", ""))
        failed  = sum(1 for r in results if "FAIL" in r.get("status", ""))
        skipped = sum(1 for r in results if "SKIP" in r.get("status", ""))
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        headers = ("#", "Loại test", "Input", "Kỳ vọng", "Thực tế", "AI gợi ý", "Kết quả")

        rows = []
        for i, r in enumerate(results, 1):
            test_type  = _pretty_test_type(r.get("test_type", ""))
            label      = r.get("label", "")
            input_desc = r.get("input", "")
            # Ưu tiên label (ngắn gọn, mô tả đủ); fallback sang input_desc
            combined   = label if label else input_desc
            expected   = str(r.get("expected", "")) or "—"
            chart_size = str(r.get("chart_size", "")) or "—"
            actual     = cls._clip(str(r.get("actual", "")) or "—")
            status     = r.get("status", "—")
            rows.append((str(i), test_type, combined, expected, chart_size, actual, status))

        tw    = cls._text_width
        pad   = cls._pad_cell
        col_w = [
            max(tw(headers[ci]), max((tw(row[ci]) for row in rows), default=0)) + 1
            for ci in range(len(headers))
        ]

        def fmt_row(cells):
            return "| " + " | ".join(
                pad(c, col_w[ci]) for ci, c in enumerate(cells)
            ) + " |"

        sep = "|" + "|".join("-" * (w + 2) for w in col_w) + "|"

        if failed == 0 and skipped == 0:
            summary = "> ✅ **TẤT CẢ KIỂM TRA ĐỀU PASS!**"
        elif failed == 0:
            summary = f"> ⏭️ **PASS nhưng có {skipped} test bị skip**"
        else:
            summary = f"> ❌ **CÓ {failed} KIỂM TRA FAIL — CẦN XỬ LÝ!**"

        lines = [
            f"# 🎯 Gợi Ý Size Bằng AI — {cls._PRODUCT_CODE} {cls._PRODUCT_NAME}", "",
            f"| Ngày chạy  | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} |",
            "| ---------- | ------- |",
            "| Môi trường | TEST — `test.shop.tryonic.ai` |",
            f"| Kết quả    | {verdict} |",
            f"| Tổng       | {total} kiểm tra &nbsp; ✅ {passed} &nbsp; ❌ {failed} &nbsp; ⏭️ {skipped} |",
            "", "## Bảng chi tiết", "",
            fmt_row(headers), sep,
            *[fmt_row(r) for r in rows],
            "", "## Tóm tắt", "",
            summary, "",
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Báo cáo size guide đã lưu: {filepath}")


# ── Helpers ───────────────────────────────────────────────────────────────────

_TEST_TYPE_LABELS = {
    "test_popup_has_required_elements":  "UI Elements",
    "test_valid_recommendation":         "Valid",
    "test_invalid_no_result":            "Invalid",
    "test_recommendation_accuracy":      "Accuracy",
    "test_boundary_recommendation":      "Biên",
    "test_out_of_range_recommendation":  "Ngoài khoảng",
    "test_bang_size_accessible":         "UI Link",
    "test_small_group_recommendation":   "Nhóm nhỏ",
    "test_large_group_recommendation":   "Nhóm lớn",
    "test_chon_size_after_recommendation": "Chọn size",
    "test_form_limit_validation":          "Giới hạn form",
}


def _pretty_test_type(name: str) -> str:
    return _TEST_TYPE_LABELS.get(name, name.replace("test_", "").replace("_", " ").title())
