"""Base class cho Tryon daily tests.

Tracking: mỗi (design, combo) ghi một dòng kết quả.
Report format: giống BaseDailyTest, lưu tại reports/daily/tryon_<ts>.md.
"""
import glob as _glob
import os
from datetime import datetime
from typing import ClassVar


class BaseTryonTest:
    _SUITE_NAME: str = "TRYON"
    _REPORT_TITLE: str = "Daily Tryon: AI Thử đồ"
    _results: ClassVar[list] = []

    def _record(self, design: str, combo: str, status: str,
                note: str = "", elapsed: float = 0.0) -> None:
        self._results.append({
            "design": design,
            "combo": combo,
            "status": status,
            "note": note,
            "elapsed": elapsed,
        })

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
        skipped = sum(1 for r in results if "SKIP" in r.get("status", ""))
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        tong_str = f"{total} lượt  ✅ {passed}  ❌ {failed}  ⚠️ {warned}  ⏭️ {skipped}"
        info_rows = [
            ("Ngày chạy",  ts_display),
            ("Môi trường", "TEST — `test.shop.tryonic.ai`"),
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
            _des = str(r["design"])
            _cmb = str(r["combo"])
            _sta = str(r["status"])
            _nt  = str(r.get("note", ""))
            _el   = r.get("elapsed", 0.0)
            icon = ("✅" if "PASS" in _sta else
                    "❌" if "FAIL" in _sta else
                    "⚠️" if "WARN" in _sta else "⏭️")
            line = f"{i}. {icon} **{_des}** / `{_cmb}`"
            if _el:
                line += f" ⏱ {_el}s"
            if _nt:
                line += f" — {_nt}"
            detail_items += [line, ""]

        if failed == 0 and warned == 0:
            summary_line = "> ✅ **TẤT CẢ TRYON ĐỀU PASS!**"
        elif failed == 0:
            summary_line = f"> ⚠️ **PASS nhưng có {warned} cảnh báo**"
        else:
            summary_line = f"> ❌ **CÓ {failed} TRYON FAIL — CẦN XỬ LÝ!**"

        lines = (
            [f"# {cls._REPORT_TITLE}", ""]
            + info_lines
            + ["", "## Bảng chi tiết", ""]
            + detail_items
            + ["## Tóm tắt", "", summary_line, ""]
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Tryon report: {filepath}")
