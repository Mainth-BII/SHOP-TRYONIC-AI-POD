"""Daily smoke: AI Tạo Artwork — Home → prompt → Studio → gen ≥ 1 ảnh mới → canvas render → xoay mặt sau."""
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
        """Login → Home → Studio (chọn sản phẩm) → nhập prompt → AI gen → đo thời gian → canvas."""
        self._login()

        # ── 1. Load prompt hôm nay ───────────────────────────────────────────
        prompt = _daily_prompt()
        self._record_check(TC, "Load prompt", "✅ PASS", f"{prompt[:60]}...")

        # ── 2. Navigate Home ─────────────────────────────────────────────────
        self.home.navigate()
        self._shot(TC, "1", "home_loaded")

        # Sau khi login: home có thể hiện prompt input hoặc không
        if self.home.prompt_input.is_visible(timeout=5_000):
            self.home.fill_prompt(prompt)
            self.page.wait_for_timeout(500)
            self._shot(TC, "2", "prompt_filled_home")
            self.home.click_generate()
            try:
                self.page.wait_for_url("**/studio**", timeout=20_000)
            except Exception:
                pass
            self.page.wait_for_timeout(2_000)
            in_studio = "studio" in self.page.url
            prompt_in_studio = False
        else:
            self._shot(TC, "2", "home_no_prompt_input")
            self.studio.navigate()
            self.page.wait_for_timeout(1_000)
            in_studio = "studio" in self.page.url
            prompt_in_studio = True

        self._record_check(TC, "Navigate tới Studio",
                           "✅ PASS" if in_studio else "❌ FAIL",
                           self.page.url)
        if not in_studio:
            self._shot(TC, "3", "studio_fail")
            pytest.fail(f"Không navigate được vào Studio — URL: {self.page.url}")

        # ── 3. Accept terms + chọn sản phẩm (double-click) ──────────────────
        # navigate() đã gọi ready() rồi; nếu vào từ home thì gọi thủ công
        if prompt_in_studio is False:
            self.studio.ready()
        self._shot(TC, "3", "studio_after_product_select")

        # Capture canvas baseline NGAY SAU KHI studio load (chưa có artwork)
        # → dùng để so sánh sau khi AI generate + click artwork
        _canvas_pre_shot = self.studio.get_canvas_screenshot()

        # ── 4. Nhập prompt trong Studio (nếu chưa nhập ở home) ───────────────
        # Ghi số ảnh hiện có TRONG CHAT PANEL (bên phải) trước khi gen → đo ảnh MỚI
        baseline = self.studio._count_chat_artworks()
        self._record_check(TC, "Baseline artworks (chat)", "✅ PASS",
                           f"{baseline} ảnh cũ trong chat panel")

        if prompt_in_studio:
            self.studio.generate(prompt)
            self.page.wait_for_timeout(1_000)
            self._shot(TC, "3b", "prompt_submitted_studio")
        else:
            # Prompt đã được gửi từ home → studio đang xử lý
            self._shot(TC, "3b", "studio_processing_home_prompt")

        # ── 5. Chờ AI tạo artwork MỚI, đo thời gian ─────────────────────────
        ok, elapsed, total, new_count = self.studio.wait_for_new_artworks(
            baseline=baseline, min_new=1, timeout=120
        )
        self._record_check(TC, "AI tạo artwork mới",
                           "✅ PASS" if ok else "❌ FAIL",
                           f"{new_count} ảnh mới ({elapsed}s) — tổng: {total}"
                           if ok else f"timeout {elapsed}s — AI không trả kết quả ảnh")
        self._shot(TC, "4", f"new_artworks_{new_count}imgs_{elapsed}s")

        if not ok or new_count == 0:
            pytest.fail(f"AI không tạo được artwork mới sau {elapsed}s (baseline={baseline})")

        # ── 6. Click artwork mới → chờ hiển thị lên canvas áo ───────────────
        # click_artwork dùng left library panel → index 0 là ảnh mới nhất (skip 'Thêm ảnh')
        clicked = self.studio.click_artwork(index=0)
        self._record_check(TC, "Click artwork variant",
                           "✅ PASS" if clicked else "❌ FAIL",
                           "đã click artwork mới" if clicked else "không click được artwork")
        self._shot(TC, "5", "after_click_artwork")

        if clicked:
            canvas_elapsed = self.studio.wait_for_canvas_artwork(
                pre_shot=_canvas_pre_shot, timeout=30, poll_ms=500
            )
            canvas_ok = canvas_elapsed >= 0
            self._record_check(TC, "Artwork render trên canvas áo",
                               "✅ PASS" if canvas_ok else "❌ FAIL",
                               f"hiện lên sau {canvas_elapsed}s" if canvas_ok
                               else "timeout — artwork không render được lên canvas")
            self._shot(TC, "6", "canvas_artwork_on_shirt")

        # ── 7. Đổi loại áo ──────────────────────────────────────────────────
        self.page.wait_for_timeout(1_000)
        old_name = self.studio.get_product_name()
        ok7, _, new_name = self.studio.change_product_type(index=1)
        changed_product = ok7 and new_name and new_name != old_name
        self._record_check(TC, "Đổi loại áo",
                           "✅ PASS" if changed_product else "⚠️ WARN",
                           f"{old_name!r} → {new_name!r}" if changed_product
                           else f"không đổi được (old={old_name!r})")
        self._shot(TC, "7", f"product_changed_{changed_product}")

        # ── 8. Đổi màu áo ───────────────────────────────────────────────────
        self._shot(TC, "8a", "before_color_change")

        ok8, chosen_color = self.studio.select_color_by_index(index=1)
        self._shot(TC, "8b", f"color_changed_{ok8}")

        # Lấy swatches sau khi chọn (panel đã mở) để log
        after_swatches = self.studio.get_color_swatches()
        self._record_check(TC, "Đổi màu áo",
                           "✅ PASS" if ok8 else "⚠️ WARN",
                           f"màu đã chọn: {chosen_color}" if ok8 else "không click được")
        if after_swatches:
            print(f"  [INFO] swatches sau khi chọn màu: {after_swatches[:3]}")

        # ── 9. Xoay áo → verify hiển thị "Mặt sau" ─────────────────────────
        self.page.wait_for_timeout(1_000)
        self._shot(TC, "9a", "before_rotate")
        ok9, elapsed9, label9 = self.studio.rotate_shirt(timeout=10)
        self._record_check(TC, "Xoay áo → Mặt sau",
                           "✅ PASS" if ok9 else "⚠️ WARN",
                           f"hiện 'Mặt sau' sau {elapsed9}s" if ok9 else f"không thấy 'Mặt sau' ({label9})")
        self._shot(TC, "9b", f"mat_sau_{ok9}")

        # ══ KẾT QUẢ ══════════════════════════════════════════════════════════
        failed_checks = [r for r in self._results if "FAIL" in r.get("status", "")]
        if failed_checks:
            pytest.fail(
                f"Artwork có {len(failed_checks)} check FAIL: "
                + ", ".join(r["check"] for r in failed_checks)
            )
