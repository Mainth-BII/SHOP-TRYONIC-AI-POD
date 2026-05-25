"""Daily smoke: AI Tạo Artwork — Studio → prompt → AI gen ≥ 1 ảnh mới → Hoàn tất thiết kế.

1 case duy nhất, tiết kiệm chi phí:
  Login → Studio → chọn sản phẩm → nhập prompt → chờ AI gen → click artwork → Hoàn tất.
Không test đổi màu / đổi áo / xoay — những tính năng đó có test case riêng.
"""
import json
import os
import time as _time
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

        # ── Fill prompt → chụp ảnh → submit ────────────────────────────────
        _inp = self.studio.prompt_input
        _input_visible = _inp.is_visible(timeout=5_000)

        if _input_visible:
            _inp.fill(prompt)
            self.page.wait_for_timeout(500)
            self._shot(TC, "2a", "prompt_filled")        # chụp lúc đang điền

            # Submit: thử click nút Tạo trước, fallback Enter
            try:
                _btn = self.studio.generate_button
                if _btn.is_visible(timeout=3_000):
                    _btn.click()
                else:
                    raise Exception("not visible")
            except Exception:
                _inp.press("Enter")

            self.page.wait_for_timeout(1_000)
            self._shot(TC, "2b", "prompt_submitted")     # chụp sau khi submit
        else:
            self.studio.generate(prompt)                 # fallback gọi như cũ
            self.page.wait_for_timeout(1_000)
            self._shot(TC, "2b", "prompt_submitted")

        self._record_check(TC, "S3: Gửi prompt",
                           "✅ PASS" if _input_visible else "⚠️ WARN",
                           f"{'Đã gửi' if _input_visible else 'Không tìm thấy input'}: \"{prompt[:80]}...\"")

        # ── S4: Chờ AI trả về ≥ 1 ảnh mới ───────────────────────────────────
        ok, elapsed, total, new_count = self.studio.wait_for_new_artworks(
            baseline=baseline, min_new=1, timeout=150
        )
        self._shot(TC, "3", f"artwork_result_{new_count}imgs_{elapsed}s")

        if ok and new_count > 0:
            self._record_check(TC, "S4: AI tạo artwork thành công", "✅ PASS",
                               f"{new_count} ảnh mới sau {elapsed}s")
        else:
            self._record_check(TC, "S4: AI tạo artwork thành công", "❌ FAIL",
                               f"timeout {elapsed}s — AI không trả kết quả ảnh",
                               "≥ 1 ảnh mới trong chat panel")
            self.__class__._results = self._results
            self._save_report()
            pytest.fail(f"AI không tạo được artwork mới sau {elapsed}s (baseline={baseline})")

        # ── S5: Click artwork từ chat → Hoàn tất thiết kế (đo thời gian load) ──
        # Click ảnh mới nhất trong chat panel (bên phải ≥ 65% viewport) để đặt lên canvas
        _clicked = self.page.evaluate("""() => {
            const vw = window.innerWidth;
            const threshold = vw * 0.65;
            const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.x > threshold && r.width >= 80 && r.height >= 80
                    && img.complete && img.naturalWidth > 0;
            });
            if (!imgs.length) return 0;
            imgs[imgs.length - 1].click();
            return imgs.length;
        }""")
        print(f"  [INFO] S5: click chat artwork ({_clicked} ảnh trong panel)")
        self.page.wait_for_timeout(2_500)
        self._shot(TC, "4", "artwork_on_canvas")

        # Click Hoàn tất thiết kế — bắt đầu đo thời gian TỪ LÚC CLICK
        _t5 = _time.time()
        try:
            _fb = self.studio.finish_button
            if _fb.is_visible(timeout=5_000):
                _fb.click(force=True)
            else:
                raise Exception("button not visible")
        except Exception:
            self.page.evaluate("""() => {
                const b = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất'));
                if (b) b.click();
            }""")

        # Chờ navigate tới /review hoặc rời khỏi /studio
        _nav_ok = False
        try:
            self.page.wait_for_url("**/review**", timeout=30_000)
            _nav_ok = True
        except Exception:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                _nav_ok = ("review" in self.page.url
                           or "/studio" not in self.page.url)
            except Exception:
                _nav_ok = False

        _e5 = round(_time.time() - _t5, 1)
        self._shot(TC, "5", f"after_finish_{_e5}s")

        _st5 = "✅ PASS" if _nav_ok else "⚠️ WARN"
        self._record_check(
            TC,
            "S5: Hoàn tất thiết kế → trang load",
            _st5,
            f"{_e5}s — {'trang load thành công' if _nav_ok else 'chưa xác nhận navigate'}",
        )
        self.__class__._results = self._results
        self._save_report()
