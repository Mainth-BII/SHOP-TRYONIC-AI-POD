"""Tryon flow — Thiết kế của tôi → AI Thử đồ.

Luồng:
1. Login → /my-designs → lấy tối đa 10 design URL
2. Mỗi design: vào /review → screenshot INPUT → thử 7 combination Nam/Nữ/Bé
3. Mỗi combination: set options → click Thử lại → chờ xong → screenshot RESULT

Screenshots lưu tại: screenshots/daily/tryon/{design_label}/
Report lưu tại:      reports/daily/tryon_<ts>.md
"""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.tryon.base_tryon_test import BaseTryonTest

_DOMAIN = "tryon"
_ROOT   = "daily"

# ── Combinations ──────────────────────────────────────────────────────────────

COMBINATIONS = [
    ("Nam",                 ["Nam"]),
    ("Nam_Nu",              ["Nam", "Nữ"]),
    ("Nam_Nu_BeTrai",       ["Nam", "Nữ", "Bé trai"]),
    ("Nam_Nu_BeGai",        ["Nam", "Nữ", "Bé gái"]),
    ("Nam_Nu_BeTrai_BeGai", ["Nam", "Nữ", "Bé trai", "Bé gái"]),
    ("Nam_BeTrai_BeGai",    ["Nam", "Bé trai", "Bé gái"]),
    ("Nu_BeTrai_BeGai",     ["Nữ", "Bé trai", "Bé gái"]),
]


class TestTryonFlow(BaseTryonTest):
    """AI Thử đồ — duyệt Thiết kế của tôi, thử 7 combination."""

    _SUITE_NAME  = "TRYON"
    _REPORT_TITLE = "Daily Tryon: AI Thử đồ"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page
        from pages.tryon_review_page import TryonReviewPage
        self.tryon = TryonReviewPage(page, env.fe_url)

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

    def test_tryon_my_designs(self):
        """Login → /my-designs → click từng design → AI Thử đồ 7 combinations."""

        # ── 1. Login ─────────────────────────────────────────────────────────
        self._login()

        # ── 2. Thu thập studio URLs ──────────────────────────────────────────
        studio_urls = self.tryon.get_studio_urls(max_n=10)
        assert len(studio_urls) > 0, "Không tìm thấy design nào trong Thiết kế của tôi"

        # ── 3. Duyệt từng design ─────────────────────────────────────────────
        for idx, studio_url in enumerate(studio_urls):
            design_label = f"design_{idx+1:02d}"
            print(f"\n  ── {design_label}: {studio_url}")

            ok = self.tryon.open_review(studio_url)
            if not ok:
                self._record(design_label, "ALL", "⏭️ SKIP", "không vào được /review")
                continue

            self.tryon.shot(design_label, "0", "input", domain=_DOMAIN, root=_ROOT)
            review_url = self.page.url

            # ── 4. Thử 7 combinations ─────────────────────────────────────
            for combo_name, combo_opts in COMBINATIONS:
                print(f"    [COMBO] {combo_name}: {combo_opts}")

                self.page.goto(review_url)
                self.page.wait_for_load_state("domcontentloaded")
                # Chờ page ổn định (có thể đang auto-load kết quả cũ) trước khi thao tác
                self.tryon._wait_image_rendered(timeout=15_000)
                self.page.wait_for_timeout(1_000)

                # Bắt đầu capture API errors trước khi thao tác
                self.tryon.start_network_capture()

                clicked = self.tryon.set_options_and_tryon(combo_opts)

                if not clicked:
                    api_errs = self.tryon.stop_network_capture()
                    error_detail = self.tryon.last_error or "không click được nút Thử lại / Thử đồ ngay"
                    if api_errs:
                        error_detail += " | API: " + "; ".join(api_errs[:2])
                    print(f"    [ISSUE] {design_label}/{combo_name}: {error_detail}")
                    # Chụp screenshot trạng thái lỗi để debug
                    self.tryon.shot(design_label, f"{combo_name}_fail", "disabled_state",
                                   domain=_DOMAIN, root=_ROOT)
                    self._record(design_label, combo_name, "❌ FAIL", error_detail)
                    continue

                loaded, elapsed = self.tryon.wait_tryon_done()
                api_errs = self.tryon.stop_network_capture()

                if loaded:
                    self.tryon.shot(design_label, combo_name, "result", domain=_DOMAIN, root=_ROOT)
                    self._record(design_label, combo_name, "✅ PASS", "", elapsed)
                else:
                    # Tryon không trả kết quả — luôn FAIL, không bao giờ WARN
                    self.tryon.shot(design_label, f"{combo_name}_fail", "timeout_state",
                                   domain=_DOMAIN, root=_ROOT)
                    error_detail = self.tryon.last_error or "tryon timeout"
                    if api_errs:
                        error_detail += " | API: " + "; ".join(api_errs[:2])
                    print(f"    [ISSUE] {design_label}/{combo_name}: {error_detail}")
                    self._record(design_label, combo_name, "❌ FAIL", error_detail, elapsed)

        print(f"\n  [DONE] Screenshots: screenshots/{_ROOT}/{_DOMAIN}/")
