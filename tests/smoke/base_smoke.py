"""Base class cho tất cả Smoke Test classes.

Cách dùng:
    class TestSmokeMH01Home(BaseSmokeTest):
        _MH_DIR = "MH01_home"
        _TC_IDS = ["TC_DAILY_001", ...]
"""

import os
import shutil
import datetime

from playwright.sync_api import Page

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseSmokeTest:
    """Cung cấp shot() và setup_class() dùng chung cho mọi smoke test module."""

    _MH_DIR: str = ""
    _TC_IDS: list = []

    @classmethod
    def setup_class(cls):
        if not cls._MH_DIR:
            return
        mh_dir = os.path.join(_BASE_DIR, "screenshots", "daily", "smoke", cls._MH_DIR)
        if os.path.exists(mh_dir):
            for tc_id in cls._TC_IDS:
                tc_dir = os.path.join(mh_dir, tc_id)
                if os.path.exists(tc_dir):
                    try:
                        shutil.rmtree(tc_dir)
                    except Exception:
                        pass

    def shot(self, page_or_obj, tc_id: str, step: str, label: str) -> None:
        """Chụp screenshot vào screenshots/daily/smoke/_MH_DIR/tc_id/."""
        pg: Page = page_or_obj.page if hasattr(page_or_obj, "page") else page_or_obj
        shot_dir = os.path.join(_BASE_DIR, "screenshots", "daily", "smoke", self._MH_DIR, tc_id)
        os.makedirs(shot_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%H%M%S")
        fpath = os.path.join(shot_dir, f"S{step}_{label}_{ts}.png")
        try:
            pg.screenshot(path=fpath, full_page=True)
            print(f"  [SHOT] {tc_id} S{step}: {label}")
        except Exception as e:
            print(f"  [SHOT FAIL] {tc_id} S{step}: {e}")
