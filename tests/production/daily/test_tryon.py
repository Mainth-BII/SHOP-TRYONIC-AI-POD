"""Daily smoke: AI Thử đồ — 1 design, 1 combo Nam để verify luồng end-to-end.

Chi phí thấp nhất: chỉ chạy 1 tryon request duy nhất.
Nếu tryon trả ảnh → PASS. Nếu timeout / API lỗi → FAIL + in error chi tiết.
"""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "TRYON_SMOKE"
SMOKE_COMBO = ["Nam"]   # 1 combo duy nhất để tiết kiệm chi phí


class TestDailyTryon(BaseDailyTest):
    _SUITE_NAME   = "TRYON_SMOKE"
    _REPORT_TITLE = "Daily Smoke: AI Thử đồ"
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

    @pytest.mark.daily
    def test_tryon_smoke(self):
        """Login → design đầu tiên có /review → combo Nam → verify ảnh trả về."""

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC, "S1: Đăng nhập", "✅ PASS", self.env.login_email)

        # ── S2: Lấy design URLs ──────────────────────────────────────────────
        studio_urls = self.tryon.get_studio_urls(max_n=10)
        if not studio_urls:
            self._record_check(TC, "S2: Tìm design", "⚠️ SKIP",
                               "0 design — tài khoản chưa có thiết kế nào", "≥ 1")
            pytest.skip("Tài khoản test không có design nào — cần tạo test data")
        self._record_check(TC, "S2: Tìm design", "✅ PASS",
                           f"{len(studio_urls)} design tìm thấy", "≥ 1")

        # ── S3: Thử lần lượt đến design nào vào được /review ────────────────
        success = False
        for idx, url in enumerate(studio_urls):
            ok = self.tryon.open_review(url)
            if not ok:
                print(f"  [SKIP] Không vào được /review: {url}")
                continue

            # Chờ page ổn định trước khi thao tác
            self.tryon._wait_image_rendered(timeout=15_000)
            self.page.wait_for_timeout(1_000)

            self._record_check(TC, "S3: Vào /review", "✅ PASS",
                               f"design #{idx+1}: {self.page.url}")
            self._shot(TC, "1", "review_input")

            # Bắt API errors trước khi click
            self.tryon.start_network_capture()

            clicked = self.tryon.set_options_and_tryon(SMOKE_COMBO)
            if not clicked:
                api_errs = self.tryon.stop_network_capture()
                error_detail = self.tryon.last_error or "Thử lại không khả dụng"
                if api_errs:
                    error_detail += " | API: " + "; ".join(api_errs[:2])
                print(f"  [SKIP] design #{idx+1}: {error_detail}")
                self._shot(TC, f"1b_skip{idx+1}", "disabled_state")
                continue

            success = True
            break

        if not success:
            self._record_check(TC, "S3: Click Thử lại (Nam)", "❌ FAIL",
                               f"thử {len(studio_urls)} design đều không click được Thử lại",
                               "ít nhất 1 design click được")
            pytest.fail(f"Không design nào chạy được tryon (đã thử {len(studio_urls)})")

        self._record_check(TC, "S3: Click Thử lại (Nam)", "✅ PASS",
                           f"combo: {SMOKE_COMBO}")

        # ── S4: Chờ tryon xong → kiểm tra kết quả ───────────────────────────
        loaded, elapsed = self.tryon.wait_tryon_done()
        api_errs = self.tryon.stop_network_capture()

        if loaded:
            self._shot(TC, "2", "tryon_nam_result")
            self._record_check(TC, "S4: Tryon Nam hoàn tất", "✅ PASS",
                               f"{elapsed:.1f}s — ảnh trả về thành công")
        else:
            self._shot(TC, "2_fail", "tryon_timeout_state")
            error_detail = self.tryon.last_error or f"timeout {elapsed:.1f}s"
            if api_errs:
                error_detail += " | API: " + "; ".join(api_errs[:3])
            self._record_check(TC, "S4: Tryon Nam hoàn tất", "❌ FAIL",
                               error_detail, "ảnh trả về trong giới hạn thời gian")
            pytest.fail(f"Tryon không trả kết quả: {error_detail}")
