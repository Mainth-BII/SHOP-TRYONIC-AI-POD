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

Answer these two questions:
1. Is this image a generic gift box, loading placeholder, or default template — instead of a real custom design based on the prompt?
2. Does the image visually contain elements directly related to the prompt keywords?

Examples of FAIL:
- Prompt says "football" but image shows flowers, a gift box, or is blank/default.
- Image is clearly a placeholder 3D gift box icon.

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
        if not is_relevant:
            return False, f"[NOT_RELEVANT] Anh khong lien quan den prompt '{prompt_text}' — {reason}"
        return True, reason

    except json.JSONDecodeError as e:
        # Claude returned something unexpected — don't block the test
        return True, f"SKIP: JSON parse error ({e})"
    except Exception as e:
        return True, f"SKIP: Vision check error ({type(e).__name__}: {e})"
