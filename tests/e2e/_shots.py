"""Chụp screenshot từng bước cho E2E lifecycle → screenshots/e2e_lifecycle/NN_label.png
Đánh số tăng dần theo thứ tự gọi (xem luồng theo đúng trình tự)."""
from __future__ import annotations
from pathlib import Path

_DIR = Path("screenshots/e2e_lifecycle")
_n = {"i": 0}


def reset():
    _n["i"] = 0


def shot(page, label: str) -> None:
    _DIR.mkdir(parents=True, exist_ok=True)
    _n["i"] += 1
    try:
        page.screenshot(path=str(_DIR / f"{_n['i']:02d}_{label}.png"), full_page=True)
    except Exception:
        try:
            page.screenshot(path=str(_DIR / f"{_n['i']:02d}_{label}.png"))
        except Exception:
            pass
