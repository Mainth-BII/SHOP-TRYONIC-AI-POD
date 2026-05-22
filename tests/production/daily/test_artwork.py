"""Daily smoke: AI Tạo Artwork — Studio → prompt → AI gen ≥ 1 ảnh mới.

1 case duy nhất, tiết kiệm chi phí:
  Login → Studio → chọn sản phẩm → nhập prompt → chờ AI gen → verify ảnh xuất hiện.
Không test đổi màu / đổi áo / xoay — những tính năng đó có test case riêng.
"""
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
        self.page   = page
        self.env    = env
        self.home   = home_page
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

    @pytest.mark.daily
    def test_artwork_smoke(self):
        """Login → Studio → prompt → AI gen ≥ 1 ảnh → PASS."""

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC, "S1: Đăng nhập", "✅ PASS", self.env.login_email)

        # ── S2: Vào Studio, chọn sản phẩm ───────────────────────────────────
        prompt = _daily_prompt()
        self._record_check(TC, "S2: Load prompt hôm nay", "✅ PASS", f"{prompt[:60]}...")

        self.studio.navigate()          # goto /studio?category=t-shirts + ready()
        self._shot(TC, "1", "studio_ready")
        in_studio = "studio" in self.page.url

        self._record_check(TC, "S2: Vào Studio", "✅ PASS" if in_studio else "❌ FAIL",
                           self.page.url)
        if not in_studio:
            pytest.fail(f"Không navigate được vào Studio — URL: {self.page.url}")

        # ── S3: Nhập prompt → submit ─────────────────────────────────────────
        baseline = self.studio._count_chat_artworks()
        self._record_check(TC, "S3: Baseline artworks", "✅ PASS",
                           f"{baseline} ảnh cũ trong chat panel")

        self.studio.generate(prompt)
        self.page.wait_for_timeout(1_000)
        self._shot(TC, "2", "prompt_submitted")

        # ── S4: Chờ AI trả về ≥ 1 ảnh mới ───────────────────────────────────
        ok, elapsed, total, new_count = self.studio.wait_for_new_artworks(
            baseline=baseline, min_new=1, timeout=120
        )
        self._shot(TC, "3", f"artwork_result_{new_count}imgs_{elapsed}s")

        if ok and new_count > 0:
            self._record_check(TC, "S4: AI tạo artwork thành công", "✅ PASS",
                               f"{new_count} ảnh mới sau {elapsed}s")
        else:
            self._record_check(TC, "S4: AI tạo artwork thành công", "❌ FAIL",
                               f"timeout {elapsed}s — AI không trả kết quả ảnh",
                               "≥ 1 ảnh mới trong chat panel")
            pytest.fail(f"AI không tạo được artwork mới sau {elapsed}s (baseline={baseline})")
