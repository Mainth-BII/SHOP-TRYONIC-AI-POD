"""Base class cho Print Tech daily tests.

Tracking: mỗi design ghi kết quả AI gợi ý công nghệ in.
Report format: giống BaseTryonTest, lưu tại reports/daily/print_tech_<ts>.md + .csv.
"""
import csv
import glob as _glob
import os
from datetime import datetime
from typing import ClassVar


def _clean_status(s: str) -> str:
    s = str(s)
    if "PASS" in s: return "PASS"
    if "FAIL" in s: return "FAIL"
    if "WARN" in s: return "WARN"
    if "SKIP" in s: return "SKIP"
    return s


class BasePrintTechTest:
    _SUITE_NAME: str = "PRINT_TECH"
    _REPORT_TITLE: str = "Daily Print Tech: AI Gợi ý Công nghệ in"
    _results: ClassVar[list] = []

    def _record(self, design: str, status: str,
                elapsed: float = 0.0, tech: str = "", note: str = "") -> None:
        self._results.append({
            "design": design,
            "status": status,
            "elapsed": elapsed,
            "tech": tech,
            "note": note,
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
            _des  = str(r["design"])
            _sta  = str(r["status"])
            _el   = r.get("elapsed", 0.0)
            _tech = str(r.get("tech", ""))
            _nt   = str(r.get("note", ""))
            icon  = ("✅" if "PASS" in _sta else
                     "❌" if "FAIL" in _sta else
                     "⚠️" if "WARN" in _sta else "⏭️")
            line = f"{i}. {icon} **{_des}**"
            if _tech:
                line += f" → `{_tech}`"
            if _el:
                line += f" ⏱ {_el}s"
            if _nt:
                line += f" — {_nt}"
            detail_items += [line, ""]

        if failed == 0 and warned == 0:
            summary_line = "> ✅ **TẤT CẢ PRINT TECH ĐỀU PASS!**"
        elif failed == 0:
            summary_line = f"> ⚠️ **PASS nhưng có {warned} cảnh báo**"
        else:
            summary_line = f"> ❌ **CÓ {failed} PRINT TECH FAIL — CẦN XỬ LÝ!**"

        lines = (
            [f"# {cls._REPORT_TITLE}", ""]
            + info_lines
            + ["", "## Bảng chi tiết", ""]
            + detail_items
            + ["## Tóm tắt", "", summary_line, ""]
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Print Tech report: {filepath}")

        # ── CSV report ───────────────────────────────────────────────────────
        csv_path = filepath.replace(".md", ".csv")
        fields = ["no", "tc_id", "step", "expected_result", "actual_result", "status", "duration"]
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for i, r in enumerate(results, 1):
                des  = str(r["design"])
                sta  = str(r["status"])
                tech = str(r.get("tech", ""))
                note = str(r.get("note", ""))
                el   = r.get("elapsed", 0.0)
                writer.writerow({
                    "no":              i,
                    "tc_id":           des,
                    "step":            "AI gợi ý công nghệ in",
                    "expected_result": "AI gợi ý thành công",
                    "actual_result":   tech or note,
                    "status":          _clean_status(sta),
                    "duration":        f"{el}s" if el else "",
                })
