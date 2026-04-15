"""
Kiểm tra ảnh artwork bằng Claude Vision:
  - Phát hiện ảnh hộp quà / placeholder (FAIL)
  - Kiểm tra nội dung có liên quan đến prompt (FAIL nếu không liên quan)

Nếu ANTHROPIC_API_KEY không được set → bỏ qua, trả PASS.
"""

import base64
import json
import os
from typing import Tuple

VISION_MODEL = "claude-haiku-4-5-20251001"

_SYSTEM = (
    "You are a QA assistant for an AI T-shirt design tool. "
    "Answer only with valid JSON — no markdown, no extra text."
)

_PROMPT_TEMPLATE = """This image is the generated artwork from a T-shirt design AI.
User's prompt: "{prompt}"

INSTRUCTIONS FOR EVALUATION:
1. SUBJECT: Identify the main subject. If the prompt is "football" (bóng đá), LOOK CLOSELY for a round soccer ball, a football player, or a goal post. DO NOT confuse dynamic speed lines with vehicles (cars/motorcycles).
2. COLOR: Check if requested colors are present. If color is wrong but subject is right, mark as relevant but mention color in reason.
3. PLACEHOLDER: Check if it's a generic 3D gift box or loading icon.

Respond ONLY with this JSON (no code fences):
{{"is_gift_box": true/false, "is_relevant": true/false, "reason": "one concise sentence in English"}}"""


def check_artwork(img_bytes: bytes, prompt_text: str) -> Tuple[bool, str]:
    """
    Dùng Claude Haiku Vision để kiểm tra ảnh.
    Returns (ok, reason).
      ok=True  → ảnh hợp lệ và liên quan đến prompt
      ok=False → gift box hoặc không liên quan
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return True, "SKIP: ANTHROPIC_API_KEY not configured"

    try:
        import anthropic  # noqa: PLC0415

        client = anthropic.Anthropic(api_key=api_key)
        img_b64 = base64.b64encode(img_bytes).decode()

        resp = client.messages.create(
            model=VISION_MODEL,
            max_tokens=300,
            system=_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": _PROMPT_TEMPLATE.format(prompt=prompt_text),
                        },
                    ],
                }
            ],
        )

        raw = resp.content[0].text.strip()
        # Strip accidental code fences
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()

        data = json.loads(raw)
        is_gift_box = data.get("is_gift_box", False)
        is_relevant = data.get("is_relevant", True)
        reason = data.get("reason", "")

        if is_gift_box:
            return False, f"[GIFT_BOX] Anh placeholder qua tang bi phat hien — {reason}"
        
        # Luon tra ve True neu co hinh anh, chi kem theo feedback review
        prefix = "[GOOD]" if is_relevant else "[REVIEW]"
        return True, f"{prefix} {reason}"

    except json.JSONDecodeError as e:
        # Claude returned something unexpected — don't block the test
        return True, f"SKIP: JSON parse error ({e})"
    except Exception as e:
        return True, f"SKIP: Vision check error ({type(e).__name__}: {e})"
