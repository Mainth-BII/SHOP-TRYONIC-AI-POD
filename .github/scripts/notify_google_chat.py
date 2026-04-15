"""
CI/CD script: send test result notification to Google Chat [Tryonic_notify].

Called by GitHub Actions after each test run.
Reads result from environment variables set by the workflow.
"""

import os
import sys
import json
import glob
import base64
import requests
from datetime import datetime


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def build_payload(
    status: str,
    total: int,
    passed: int,
    failed: int,
    run_url: str,
    run_number: str,
    base_url: str,
) -> dict:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pass_rate = f"{(passed / total * 100):.0f}%" if total > 0 else "N/A"

    if failed == 0 and total > 0:
        header_icon = "✅"
        header_color = "#0F9D58"
        status_text = "ALL TESTS PASSED"
    elif total == 0:
        header_icon = "⚠️"
        status_text = "NO TESTS RAN"
    else:
        header_icon = "❌"
        status_text = f"{failed} TEST(S) FAILED"

    # Build failed test list from junit.xml if available
    failed_details = _parse_failures()
    failed_section = ""
    if failed_details:
        failed_section = "\n".join(f"❌ `{f}`" for f in failed_details[:10])
        if len(failed_details) > 10:
            failed_section += f"\n_...and {len(failed_details) - 10} more_"

    card = {
        "cardsV2": [
            {
                "cardId": "tryonic-ci-report",
                "card": {
                    "header": {
                        "title": f"{header_icon} Tryonic AI — {status_text}",
                        "subtitle": f"{base_url} | Run #{run_number} | {now}",
                    },
                    "sections": [
                        {
                            "header": "Test Summary",
                            "collapsible": False,
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": (
                                            f"<b>Total:</b> {total} &nbsp;&nbsp; "
                                            f"<b>✅ Passed:</b> {passed} &nbsp;&nbsp; "
                                            f"<b>❌ Failed:</b> {failed} &nbsp;&nbsp; "
                                            f"<b>Pass Rate:</b> {pass_rate}"
                                        )
                                    }
                                }
                            ],
                        },
                        *(
                            [
                                {
                                    "header": "Failed Tests",
                                    "collapsible": True,
                                    "widgets": [
                                        {"textParagraph": {"text": failed_section}}
                                    ],
                                }
                            ]
                            if failed_section
                            else []
                        ),
                        {
                            "widgets": [
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "View Full Report",
                                                "onClick": {
                                                    "openLink": {"url": run_url}
                                                },
                                            }
                                        ]
                                    }
                                }
                            ]
                        },
                    ],
                },
            }
        ]
    }
    return card


def _parse_failures() -> list[str]:
    """Parse failed test names from junit.xml if present."""
    junit_path = "tests/test_reports/junit.xml"
    if not os.path.exists(junit_path):
        return []
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(junit_path)
        root = tree.getroot()
        failures = []
        for tc in root.iter("testcase"):
            if tc.find("failure") is not None or tc.find("error") is not None:
                name = tc.get("name", "unknown")
                failures.append(name)
        return failures
    except Exception:
        return []


def collect_screenshots() -> list[str]:
    """Collect FAIL screenshots to mention in the message."""
    patterns = [
        "tests/screenshots/**/*FAIL*.png",
        "tests/screenshots/*FAIL*.png",
    ]
    shots = []
    for pattern in patterns:
        shots.extend(glob.glob(pattern, recursive=True))
    return shots[:5]  # max 5


def send(webhook_url: str, payload: dict) -> bool:
    try:
        resp = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )
        resp.raise_for_status()
        print(f"[notify] Google Chat notification sent (HTTP {resp.status_code})")
        return True
    except requests.exceptions.RequestException as exc:
        print(f"[notify] Failed to send: {exc}", file=sys.stderr)
        return False


def main() -> None:
    webhook_url = get_env("GOOGLE_CHAT_WEBHOOK_URL")
    if not webhook_url:
        print("[notify] GOOGLE_CHAT_WEBHOOK_URL not set — skipping.", file=sys.stderr)
        return

    status = get_env("STATUS", "UNKNOWN")
    total = int(get_env("TOTAL", "0"))
    passed = int(get_env("PASSED", "0"))
    failed = int(get_env("FAILED", "0"))
    run_url = get_env("RUN_URL", "https://github.com")
    run_number = get_env("RUN_NUMBER", "?")
    base_url = get_env("BASE_URL", "https://pre-launch.tryonic.ai")

    payload = build_payload(status, total, passed, failed, run_url, run_number, base_url)
    ok = send(webhook_url, payload)

    # Send screenshot filenames as a follow-up message if there are failures
    if failed > 0:
        shots = collect_screenshots()
        if shots:
            filenames = "\n".join(f"📸 {os.path.basename(s)}" for s in shots)
            followup = {
                "text": (
                    f"*Failed test screenshots* (download from Actions artifacts):\n"
                    f"{filenames}\n"
                    f"<{run_url}|📎 Download artifacts>"
                )
            }
            send(webhook_url, followup)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
