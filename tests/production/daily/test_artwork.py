"""Daily smoke: AI Tạo Artwork — Home → prompt → Studio → gen ≥ 1 ảnh → canvas render."""
import json
import os
from datetime import date
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "ARTWORK_SMOKE"


def _daily_prompt() -> str:
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "genz_prompts.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)["daily_prompts"]
    return prompts[date.today().timetuple().tm_yday % len(prompts)]


class TestDailyArtwork(BaseDailyTest):
    _SUITE_NAME   = "ARTWORK_SMOKE"
    _REPORT_TITLE = "Daily Smoke: AI Tạo Artwork"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page
        from pages.studio_page import StudioPage
        self.studio = StudioPage(page, env.fe_url)

    def _login(self) -> None:
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    def test_artwork_smoke(self):
        """Login → Home → nhập prompt ngày hôm nay → AI gen → ≥ 1 ảnh → click variant → canvas."""
        self._login()

        # ── 1. Load prompt hôm nay ───────────────────────────────────────────
        prompt = _daily_prompt()
        self._record_check(TC, "Load prompt", "✅ PASS", f"{prompt[:60]}...")

        # ── 2. Navigate Home ─────────────────────────────────────────────────
        self.home.navigate()
        self._shot(TC, "1", "home_loaded")

        # Sau khi login: home có thể hiện prompt input (guest flow)
        # hoặc nút "Tạo ngay"/"Bắt đầu thiết kế" → navigate thẳng vào Studio
        if self.home.prompt_input.is_visible(timeout=5_000):
            # Luồng có prompt input trên home
            self.home.fill_prompt(prompt)
            self.page.wait_for_timeout(500)
            self._shot(TC, "2", "prompt_filled")
            self.home.click_generate()
            try:
                self.page.wait_for_url("**/studio**", timeout=20_000)
            except Exception:
                pass
            self.page.wait_for_timeout(2_000)
            in_studio = "studio" in self.page.url
            prompt_in_studio = False
        else:
            # Luồng logged-in: không có prompt input trên home → navigate thẳng vào Studio
            self._shot(TC, "2", "home_no_prompt_input")
            self.studio.navigate()
            self.page.wait_for_timeout(2_000)
            in_studio = "studio" in self.page.url
            prompt_in_studio = True

        self._record_check(TC, "Navigate tới Studio",
                           "✅ PASS" if in_studio else "❌ FAIL",
                           self.page.url)
        if not in_studio:
            self._shot(TC, "3", "studio_fail")
            pytest.fail(f"Không navigate được vào Studio — URL: {self.page.url}")

        self.studio.accept_terms()
        self._shot(TC, "3", "studio_loaded")

        # Nếu chưa nhập prompt (vào studio qua nút Tạo ngay) → nhập tại Studio
        if prompt_in_studio:
            self.studio.generate(prompt)
            self.page.wait_for_timeout(1_000)
            self._shot(TC, "3b", "prompt_in_studio")

        # ── 3. Chờ AI tạo artwork, đo thời gian ─────────────────────────────
        ok, elapsed, found = self.studio.wait_for_artworks(count=1, timeout=120)
        self._record_check(TC, "AI tạo artwork",
                           "✅ PASS" if ok else "⚠️ WARN",
                           f"{found} ảnh ({elapsed}s)")
        self._shot(TC, "4", f"artworks_{found}imgs")

        if not ok or found == 0:
            pytest.fail(f"AI không tạo được artwork sau {elapsed}s")

        # ── 4. Click variant → chờ canvas render ────────────────────────────
        clicked = self.studio.click_artwork(index=0)
        self._record_check(TC, "Click artwork variant",
                           "✅ PASS" if clicked else "⚠️ WARN",
                           "đã click variant" if clicked else "không click được")

        if clicked:
            canvas_elapsed = self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
            canvas_ok = canvas_elapsed >= 0
            self._record_check(TC, "Artwork render trên canvas",
                               "✅ PASS" if canvas_ok else "⚠️ WARN",
                               f"{canvas_elapsed}s" if canvas_ok else "timeout")
            self._shot(TC, "5", "canvas_render")
