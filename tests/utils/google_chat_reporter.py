from __future__ import annotations
"""Google Chat reporter — sends daily smoke results to [Tryonic_notify]."""

import os
import re
import glob
import json
import base64
import requests
from datetime import datetime
from typing import Optional


WEBHOOK_URL   = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")   # https://imgbb.com → free API key

# ── Screenshot helpers ────────────────────────────────────────────────────────

def _find_failure_screenshot(suite_name: str, check_name: str, screenshots_base: str) -> str:
    """Tìm screenshot phù hợp nhất với check bị fail.

    Ưu tiên file có tên chứa nhiều keyword nhất từ check_name.
    Fallback: screenshot gần nhất trong suite directory.
    """
    pattern = os.path.join(screenshots_base, suite_name, "**", "*.png")
    all_files = glob.glob(pattern, recursive=True)
    if not all_files:
        return ""

    # Tách keyword từ tên check (bỏ từ ngắn/chung)
    _SKIP = {"verify", "pass", "fail", "click", "check", "ai", "của", "và", "→", "trên"}
    keywords = [
        w for w in re.split(r"[\s:→()\[\]/]+", check_name.lower())
        if len(w) >= 3 and w not in _SKIP
    ]

    def _score(path: str) -> int:
        fname = os.path.basename(path).lower()
        return sum(1 for kw in keywords if kw in fname)

    scored = [((_score(f), os.path.getmtime(f)), f) for f in all_files]
    best_score = max(s for (s, _), _ in scored)

    if best_score > 0:
        # Cao điểm nhất + mới nhất
        return max(
            (f for (s, _), f in scored if s == best_score),
            key=os.path.getmtime,
        )
    # Fallback: mới nhất
    return max(all_files, key=os.path.getmtime)


def _upload_to_imgbb(image_path: str, api_key: str, expiry_sec: int = 3600) -> str:
    """Upload ảnh lên imgbb.com → trả public URL (hoặc '' nếu lỗi).

    API key miễn phí tại https://imgbb.com/signup
    Set env: IMGBB_API_KEY=<your_key>
    """
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": api_key, "expiration": expiry_sec},
            data={"image": img_b64},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["data"]["url"]
        print(f"[GoogleChat] imgbb upload HTTP {resp.status_code}: {resp.text[:120]}")
    except Exception as exc:
        print(f"[GoogleChat] imgbb upload error: {exc}")
    return ""


# ── Mapping check-name → nhãn hiển thị thời gian AI ─────────────────────────
# key: chuỗi con (lowercase) trong r["check"]
# value: nhãn hiển thị trong section "⚡ Thời gian AI"
_AI_TIMING_CHECKS = {
    "ai tạo artwork":       "Tạo Artwork",
    "tryon nam hoàn tất":   "AI Tryon (Nam)",
    "ai phân tích xong":    "Gợi ý công nghệ in",
    "size phù hợp":         "AI Size Guide",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_time(actual: str) -> str:
    """Trích xuất giá trị thời gian từ trường actual. VD: '(28.1s)' → '28.1s'."""
    m = re.search(r'\((\d+\.?\d*)s\)', actual)         # (28.1s)
    if not m:
        m = re.search(r'^(\d+\.?\d*)\s*s\b', actual.strip())  # 45.2s đầu chuỗi
    if not m:
        m = re.search(r'(\d+\.?\d*)\s*s\b', actual)   # bất kỳ vị trí nào
    return f"{m.group(1)}s" if m else ""


def _timing_extra(actual: str, label: str) -> str:
    """Thông tin bổ sung cho timing (số ảnh, tên công nghệ,...)."""
    if label == "Tạo Artwork":
        m = re.search(r'(\d+)\s*ảnh mới', actual)
        return f" ({m.group(1)} ảnh)" if m else ""
    if label == "Gợi ý công nghệ in":
        m = re.match(r'([A-Z][A-Z0-9]{1,10})\s', actual)
        return f" — {m.group(1)}" if m else ""
    return ""


def _extract_ai_timings(suites: dict) -> dict:
    """Quét tất cả results → trả {label: 'Xs (extra)'} cho các bước AI."""
    timings: dict = {}
    for data in suites.values():
        for r in data["results"]:
            chk_lower = r.get("check", "").lower()
            actual    = r.get("actual", "")
            for keyword, label in _AI_TIMING_CHECKS.items():
                if keyword in chk_lower and label not in timings:
                    t = _extract_time(actual)
                    if t:
                        timings[label] = t + _timing_extra(actual, label)
    return timings


def _collect_failures(suites: dict) -> list[dict]:
    """Trả danh sách {suite, check, actual} cho mọi check bị FAIL."""
    failures = []
    for suite_name, data in suites.items():
        for r in data["results"]:
            if "FAIL" in r.get("status", ""):
                failures.append({
                    "suite":  suite_name,
                    "check":  r.get("check", ""),
                    "actual": r.get("actual", ""),
                })
    return failures


def _suite_display(name: str) -> str:
    """ARTWORK_SMOKE → Artwork"""
    return name.replace("_SMOKE", "").replace("_", " ").title()


# ── Card builder ──────────────────────────────────────────────────────────────

def _build_daily_card(
    suites: dict,
    total_duration: float = 0,
    artifact_url: str = "",
    failure_screenshots: dict | None = None,
) -> dict:
    """
    Xây Google Chat Card v2 cho daily smoke report.

    suites: {suite_name: {"title": str, "results": list[dict]}}
    """
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Tổng hợp số liệu ─────────────────────────────────────────────────────
    total_passed = total_failed = total_warned = 0
    for data in suites.values():
        for r in data["results"]:
            st = r.get("status", "")
            if "PASS" in st: total_passed += 1
            elif "FAIL" in st: total_failed += 1
            elif "WARN" in st: total_warned += 1

    total_checks = total_passed + total_failed + total_warned
    pass_rate = (
        f"{round(total_passed / total_checks * 100)}%"
        if total_checks else "—"
    )
    header_icon  = "✅ ALL PASSED" if total_failed == 0 else f"❌ {total_failed} FAILED"
    dur_str      = f"{int(total_duration)}s" if total_duration else "—"

    # ── Section 1: Metrics ────────────────────────────────────────────────────
    section_metrics = {
        "header": "📊 Tổng kết",
        "collapsible": False,
        "widgets": [{
            "columns": {
                "columnItems": [
                    {
                        "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                        "widgets": [
                            {"decoratedText": {"topLabel": "✅ Passed",  "text": str(total_passed)}},
                            {"decoratedText": {"topLabel": "❌ Failed",  "text": str(total_failed)}},
                        ],
                    },
                    {
                        "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                        "widgets": [
                            {"decoratedText": {"topLabel": "Pass Rate",   "text": pass_rate}},
                            {"decoratedText": {"topLabel": "⏱ Duration",  "text": dur_str}},
                        ],
                    },
                ]
            }
        }],
    }

    # ── Section 2: Per-suite status ───────────────────────────────────────────
    suite_lines = []
    for suite_name, data in suites.items():
        results  = data["results"]
        s_fail   = sum(1 for r in results if "FAIL" in r.get("status", ""))
        s_warn   = sum(1 for r in results if "WARN" in r.get("status", ""))
        s_pass   = sum(1 for r in results if "PASS" in r.get("status", ""))
        icon     = "✅" if s_fail == 0 else "❌"
        label    = _suite_display(suite_name)
        detail   = f"  ({s_pass}✅ {s_fail}❌{(' ' + str(s_warn) + '⚠️') if s_warn else ''})"
        suite_lines.append(f"{icon} <b>{label}</b>{detail}")

    section_suites = {
        "header": "🔍 Kết quả từng Suite",
        "collapsible": False,
        "widgets": [
            {"textParagraph": {"text": "\n".join(suite_lines)}}
        ],
    }

    # ── Section 3: AI timings ────────────────────────────────────────────────
    sections = [section_metrics, section_suites]
    timings  = _extract_ai_timings(suites)
    if timings:
        timing_lines = [
            f"⏱ <b>{label}</b>: {val}"
            for label, val in timings.items()
        ]
        sections.append({
            "header": "⚡ Thời gian AI",
            "collapsible": False,
            "widgets": [
                {"textParagraph": {"text": "\n".join(timing_lines)}}
            ],
        })

    # ── Section 4: Bug detail + screenshot (chỉ khi có FAIL) ────────────────
    failures  = _collect_failures(suites)
    fshots    = failure_screenshots or {}
    if failures:
        bug_widgets = []
        for f in failures:
            suite_label = _suite_display(f["suite"])
            check       = f["check"][:90]
            actual      = f["actual"][:250].replace("\n", " ")
            # Text mô tả bug
            bug_widgets.append({
                "textParagraph": {
                    "text": (
                        f'❌ <b>[{suite_label}]</b> {check}\n'
                        f'   → <i>{actual}</i>'
                    )
                }
            })
            # Ảnh chụp màn hình (nếu đã upload thành công)
            img_url = fshots.get(f"{f['suite']}|{f['check']}", "")
            if img_url:
                bug_widgets.append({
                    "image": {
                        "imageUrl": img_url,
                        "altText":  f"Screenshot: {check[:60]}",
                        "onClick":  {"openLink": {"url": img_url}},
                    }
                })

        sections.append({
            "header":     f"🐛 Bug cần xử lý ({len(failures)})",
            "collapsible": False,
            "widgets":     bug_widgets,
        })

    # ── Section 5: Footer ─────────────────────────────────────────────────────
    footer_text = (
        f"*Run:* {now}  |  *Env:* TEST — test.shop.tryonic.ai  "
        f"|  *Tester:* Playwright CI"
    )
    if artifact_url:
        footer_text += f"\n📎 <{artifact_url}|Xem full report & screenshots>"

    sections.append({
        "widgets": [{"textParagraph": {"text": footer_text}}]
    })

    return {
        "cardsV2": [{
            "cardId": "tryonic-daily-report",
            "card": {
                "header": {
                    "title":    f"🤖 Tryonic Daily Smoke — {header_icon}",
                    "subtitle": f"test.shop.tryonic.ai  |  {now}",
                    "imageUrl": "https://tryonic.ai/favicon.ico",
                    "imageType": "CIRCLE",
                },
                "sections": sections,
            },
        }]
    }


# ── Public API ────────────────────────────────────────────────────────────────

def send_daily_report(
    suites: dict,
    total_duration: float = 0,
    artifact_url: str = "",
    webhook_url: str = "",
    screenshots_base: str = "",
) -> bool:
    """
    Gửi báo cáo daily smoke tổng hợp lên Google Chat.

    Args:
        suites:           {suite_name: {"title": str, "results": list[dict]}}
                          results mỗi item: {"mh", "check", "status", "actual", "expected"}
        total_duration:   tổng thời gian chạy session (giây)
        artifact_url:     link download full report (GitHub Actions artifacts, v.v.)
        webhook_url:      override GOOGLE_CHAT_WEBHOOK_URL env var
        screenshots_base: đường dẫn đến thư mục screenshots/daily/
                          Nếu để trống, không gửi ảnh.
    """
    url = webhook_url or WEBHOOK_URL
    if not url:
        print("[GoogleChat] GOOGLE_CHAT_WEBHOOK_URL not set — skipping notification.")
        return False

    if not suites:
        print("[GoogleChat] Không có kết quả để gửi.")
        return False

    # ── Tìm và upload screenshot cho từng check FAIL ──────────────────────
    failure_screenshots: dict = {}
    failures = _collect_failures(suites)
    if failures and screenshots_base and IMGBB_API_KEY:
        print(f"[GoogleChat] Uploading {len(failures)} failure screenshot(s) to imgbb…")
        for f in failures:
            key        = f"{f['suite']}|{f['check']}"
            shot_path  = _find_failure_screenshot(
                f["suite"], f["check"], screenshots_base
            )
            if shot_path:
                print(f"  → [{f['suite']}] {os.path.basename(shot_path)}")
                img_url = _upload_to_imgbb(shot_path, IMGBB_API_KEY)
                if img_url:
                    failure_screenshots[key] = img_url
    elif failures and screenshots_base and not IMGBB_API_KEY:
        print(
            "[GoogleChat] IMGBB_API_KEY chưa set — không upload ảnh.\n"
            "             Lấy free key tại https://imgbb.com/signup"
        )

    payload = _build_daily_card(
        suites, total_duration, artifact_url,
        failure_screenshots=failure_screenshots,
    )

    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )
        resp.raise_for_status()
        total_failed = sum(
            1 for data in suites.values()
            for r in data["results"]
            if "FAIL" in r.get("status", "")
        )
        print(
            f"[GoogleChat] Report sent ✅  "
            f"(suites={len(suites)}, failed={total_failed}, HTTP {resp.status_code})"
        )
        return True
    except requests.exceptions.RequestException as exc:
        print(f"[GoogleChat] Failed to send report: {exc}")
        return False


# ── Legacy: kept for backward compatibility ───────────────────────────────────

def _encode_image_base64(path: str) -> Optional[str]:
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            import base64
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def _status_icon(status: str) -> str:
    return {"PASS": "✅", "FAIL": "❌", "N/A": "⚠️"}.get(status.upper(), "❓")


def send_report(
    summary: dict,
    results: list[dict],
    screenshots: list[str] | None = None,
    artifact_url: str = "",
    webhook_url: str = "",
) -> bool:
    """Legacy: gửi báo cáo đơn lẻ (dùng cho các test ngoài daily suite)."""
    url = webhook_url or WEBHOOK_URL
    if not url:
        print("[GoogleChat] GOOGLE_CHAT_WEBHOOK_URL not set — skipping notification.")
        return False

    now        = datetime.now().strftime("%Y-%m-%d %H:%M")
    pass_rate  = summary.get("pass_rate", "0%")
    total      = summary.get("total", 0)
    passed     = summary.get("passed", 0)
    failed     = summary.get("failed", 0)

    header_color = "#0F9D58" if failed == 0 else "#DB4437"
    header_icon  = "✅ ALL PASSED" if failed == 0 else f"❌ {failed} FAILED"

    rows_text = ""
    for r in results[:20]:
        icon  = _status_icon(r.get("Result_R1", ""))
        tc    = r.get("TC_ID", "")
        title = r.get("Title", "")[:60]
        rows_text += f"{icon} `{tc}` — {title}\n"
    if len(results) > 20:
        rows_text += f"_... and {len(results) - 20} more_\n"

    footer = f"*Run:* {now} | *Tester:* Playwright CI"
    if artifact_url:
        footer += f"\n📎 <{artifact_url}|Download full report & screenshots>"

    card = {
        "cardsV2": [{
            "cardId": "tryonic-test-report",
            "card": {
                "header": {
                    "title":    f"Tryonic AI — Test Report {header_icon}",
                    "subtitle": f"pre-launch.tryonic.ai | {now}",
                    "imageUrl": "https://tryonic.ai/favicon.ico",
                    "imageType": "CIRCLE",
                },
                "sections": [
                    {
                        "header": "Summary",
                        "collapsible": False,
                        "widgets": [{
                            "columns": {
                                "columnItems": [
                                    {
                                        "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                                        "widgets": [
                                            {"decoratedText": {"topLabel": "Total",     "text": str(total)}},
                                            {"decoratedText": {"topLabel": "Pass Rate", "text": pass_rate}},
                                        ],
                                    },
                                    {
                                        "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                                        "widgets": [
                                            {"decoratedText": {"topLabel": "✅ Passed", "text": str(passed)}},
                                            {"decoratedText": {"topLabel": "❌ Failed", "text": str(failed)}},
                                        ],
                                    },
                                ]
                            }
                        }],
                    },
                    {
                        "header": "Test Results",
                        "collapsible": True,
                        "initialCollapseCount": 5,
                        "widgets": [
                            {"textParagraph": {"text": rows_text or "_No results_"}}
                        ],
                    },
                    {"widgets": [{"textParagraph": {"text": footer}}]},
                ],
            },
        }]
    }

    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(card),
            timeout=15,
        )
        resp.raise_for_status()
        print(f"[GoogleChat] Report sent successfully (HTTP {resp.status_code})")
        return True
    except requests.exceptions.RequestException as exc:
        print(f"[GoogleChat] Failed to send report: {exc}")
        return False


def send_simple_message(message: str, webhook_url: str = "") -> bool:
    """Gửi tin nhắn plain text lên Google Chat."""
    url = webhook_url or WEBHOOK_URL
    if not url:
        return False
    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"text": message}),
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except requests.exceptions.RequestException as exc:
        print(f"[GoogleChat] {exc}")
        return False
