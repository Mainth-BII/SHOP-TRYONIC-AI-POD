"""Google Chat reporter — sends test results with screenshots to [Tryonic_notify]."""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Optional


WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")


def _encode_image_base64(path: str) -> Optional[str]:
    """Return base64-encoded PNG string, or None if file missing."""
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None


def _status_icon(status: str) -> str:
    return {"PASS": "✅", "FAIL": "❌", "N/A": "⚠️"}.get(status.upper(), "❓")


def _build_card(summary: dict, results: list[dict], artifact_url: str = "") -> dict:
    """Build Google Chat Card v2 payload."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    pass_rate = summary.get("pass_rate", "0%")
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)

    # Status banner color
    header_color = "#0F9D58" if failed == 0 else "#DB4437"
    header_icon = "✅ ALL PASSED" if failed == 0 else f"❌ {failed} FAILED"

    # Build result rows (max 20 to avoid payload limits)
    rows_text = ""
    for r in results[:20]:
        icon = _status_icon(r.get("Result_R1", ""))
        tc = r.get("TC_ID", "")
        title = r.get("Title", "")[:60]
        rows_text += f"{icon} `{tc}` — {title}\n"

    if len(results) > 20:
        rows_text += f"_... and {len(results) - 20} more_\n"

    # Build footer with artifact link
    footer = f"*Run:* {now} | *Tester:* Playwright CI"
    if artifact_url:
        footer += f"\n📎 <{artifact_url}|Download full report & screenshots>"

    card = {
        "cardsV2": [
            {
                "cardId": "tryonic-test-report",
                "card": {
                    "header": {
                        "title": f"Tryonic AI — Test Report {header_icon}",
                        "subtitle": f"pre-launch.tryonic.ai | {now}",
                        "imageUrl": "https://tryonic.ai/favicon.ico",
                        "imageType": "CIRCLE",
                    },
                    "sections": [
                        {
                            "header": "Summary",
                            "collapsible": False,
                            "widgets": [
                                {
                                    "columns": {
                                        "columnItems": [
                                            {
                                                "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                                                "widgets": [
                                                    {"decoratedText": {"topLabel": "Total", "text": str(total)}},
                                                    {"decoratedText": {"topLabel": "Pass Rate", "text": pass_rate}},
                                                ]
                                            },
                                            {
                                                "horizontalSizeStyle": "FILL_AVAILABLE_SPACE",
                                                "widgets": [
                                                    {"decoratedText": {"topLabel": "✅ Passed", "text": str(passed), "startIcon": {"knownIcon": "CONFIRMATION_NUMBER_ICON"}}},
                                                    {"decoratedText": {"topLabel": "❌ Failed", "text": str(failed), "startIcon": {"knownIcon": "DESCRIPTION"}}},
                                                ]
                                            },
                                        ]
                                    }
                                }
                            ],
                        },
                        {
                            "header": "Test Results",
                            "collapsible": True,
                            "initialCollapseCount": 5,
                            "widgets": [
                                {"textParagraph": {"text": rows_text or "_No results_"}}
                            ],
                        },
                        {
                            "widgets": [
                                {"textParagraph": {"text": footer}}
                            ]
                        },
                    ],
                },
            }
        ]
    }
    return card


def send_report(
    summary: dict,
    results: list[dict],
    screenshots: list[str] | None = None,
    artifact_url: str = "",
    webhook_url: str = "",
) -> bool:
    """
    Send test report card to Google Chat.

    Args:
        summary: dict from ReportWriter.summary()
        results: list of result dicts from ReportWriter.results
        screenshots: list of screenshot file paths to attach
        artifact_url: public URL to full report (e.g. GitHub Actions artifacts)
        webhook_url: override env var GOOGLE_CHAT_WEBHOOK_URL

    Returns:
        True if message delivered successfully, False otherwise.
    """
    url = webhook_url or WEBHOOK_URL
    if not url:
        print("[GoogleChat] GOOGLE_CHAT_WEBHOOK_URL not set — skipping notification.")
        return False

    payload = _build_card(summary, results, artifact_url)

    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )
        resp.raise_for_status()
        print(f"[GoogleChat] Report sent successfully (HTTP {resp.status_code})")
    except requests.exceptions.RequestException as exc:
        print(f"[GoogleChat] Failed to send report: {exc}")
        return False

    # ── Upload screenshots as separate image messages ────────────────────
    if screenshots:
        _send_screenshots(url, screenshots, summary)

    return True


def _send_screenshots(url: str, screenshots: list[str], summary: dict) -> None:
    """Upload each screenshot as a separate text+image message."""
    failed_shots = []
    for path in screenshots:
        if not os.path.exists(path):
            continue
        basename = os.path.basename(path)
        if "FAIL" in basename.upper():
            failed_shots.append(path)

    # Only send failed screenshots to keep chat clean
    target = failed_shots if failed_shots else screenshots[:3]

    for path in target:
        basename = os.path.basename(path)
        # Read and encode to base64 for inline image
        b64 = _encode_image_base64(path)
        if not b64:
            continue

        # Google Chat does not support inline base64 images via webhook;
        # we send the filename as text instead. For full image support,
        # configure artifact_url pointing to uploaded screenshots.
        simple_payload = {
            "text": f"📸 Screenshot: `{basename}`\n_(attach full report for images — see artifact link above)_"
        }
        try:
            requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(simple_payload),
                timeout=10,
            )
        except requests.exceptions.RequestException:
            pass


def send_simple_message(message: str, webhook_url: str = "") -> bool:
    """Send a plain text message to the Google Chat space."""
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
