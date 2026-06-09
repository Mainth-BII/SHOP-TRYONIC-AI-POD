"""Chụp screenshot từng bước cho E2E lifecycle → screenshots/e2e_lifecycle/NN_label.png

Tối ưu tốc độ:
- viewport screenshot (KHÔNG full_page) → nhanh hơn nhiều.
- Tắt được qua env E2E_SHOTS=0 (chạy CI siêu nhanh, không chụp).
"""
from __future__ import annotations
import os
from pathlib import Path

_DIR = Path("screenshots/e2e_lifecycle")
_n = {"i": 0}
_ENABLED = os.getenv("E2E_SHOTS", "1").lower() not in ("0", "false", "no")


def reset():
    _n["i"] = 0


def shot(page, label: str) -> None:
    if not _ENABLED:
        return
    _DIR.mkdir(parents=True, exist_ok=True)
    _n["i"] += 1
    try:
        page.screenshot(path=str(_DIR / f"{_n['i']:02d}_{label}.png"))
    except Exception:
        pass
