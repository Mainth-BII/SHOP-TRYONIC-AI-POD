"""Daily smoke: AI Gợi ý Công nghệ in — 1 design, 1 lần gợi ý để verify end-to-end.

1 case duy nhất, tiết kiệm chi phí:
  Login → design đầu tiên có /review → click Gợi ý bằng AI → verify kết quả trả về.
"""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest

TC = "PRINT_TECH_SMOKE"


class TestDailyPrintTech(BaseDailyTest):
    _SUITE_NAME   = "PRINT_TECH_SMOKE"
    _REPORT_TITLE = "Daily Smoke: AI Gợi ý Công nghệ in"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page = page
        self.env  = env
        self.home = home_page
        from pages.print_tech_page import PrintTechPage
        self.pt = PrintTechPage(page, env.fe_url)

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

    def _start_network_capture(self) -> None:
        self._api_errors: list = []
        def _handler(response) -> None:
            try:
                if response.status >= 400:
                    url = response.url
                    if "api." in url or "/api/" in url:
                        self._api_errors.append(f"HTTP {response.status}: {url}")
            except Exception:
                pass
        self._net_handler = _handler
        self.page.on("response", _handler)

    def _stop_network_capture(self) -> list:
        if hasattr(self, "_net_handler"):
            try:
                self.page.remove_listener("response", self._net_handler)
            except Exception:
                pass
            del self._net_handler
        captured = list(getattr(self, "_api_errors", []))
        self._api_errors = []
        return captured

    @pytest.mark.daily
    def test_print_tech_smoke(self):
        """Login → design đầu tiên có /review → Gợi ý bằng AI → verify kết quả."""

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC, "S1: Đăng nhập", "✅ PASS", self.env.login_email)

        # ── S2: Lấy design URLs ──────────────────────────────────────────────
        studio_urls = self.pt.get_studio_urls(max_n=10)
        if not studio_urls:
            self._record_check(TC, "S2: Tìm design", "⚠️ SKIP",
                               "0 design — tài khoản chưa có thiết kế nào", "≥ 1")
            pytest.skip("Tài khoản test không có design nào — cần tạo test data")
        self._record_check(TC, "S2: Tìm design", "✅ PASS",
                           f"{len(studio_urls)} design tìm thấy", "≥ 1")

        # ── S3: Thử lần lượt đến design nào vào được /review ────────────────
        success = False
        for idx, url in enumerate(studio_urls):
            ok = self.pt.open_review(url)
            if not ok:
                print(f"  [SKIP] Không vào được /review: {url}")
                continue

            # Chờ page ổn định trước khi tương tác
            self.page.wait_for_timeout(1_500)

            self._record_check(TC, "S3: Vào /review", "✅ PASS",
                               f"design #{idx+1}: {self.page.url}")
            self._shot(TC, "1", "review_input")

            # Bắt API errors trước khi click
            self._start_network_capture()

            clicked = self.pt.click_ai_suggest()
            if not clicked:
                api_errs = self._stop_network_capture()
                error_detail = "Nút 'Gợi ý bằng AI' không khả dụng"
                if api_errs:
                    error_detail += " | API: " + "; ".join(api_errs[:2])
                print(f"  [SKIP] design #{idx+1}: {error_detail}")
                self._shot(TC, f"1b_skip{idx+1}", "disabled_state")
                continue

            success = True
            break

        if not success:
            self._record_check(TC, "S3: Click Gợi ý bằng AI", "❌ FAIL",
                               f"thử {len(studio_urls)} design đều không click được",
                               "ít nhất 1 design click được")
            pytest.fail(f"Không design nào click được 'Gợi ý bằng AI' (đã thử {len(studio_urls)})")

        self._record_check(TC, "S3: Click Gợi ý bằng AI", "✅ PASS")

        # ── S4: Chờ AI phân tích xong → verify kết quả ──────────────────────
        done, elapsed = self.pt.wait_ai_done()
        api_errs = self._stop_network_capture()

        if done:
            tech = self.pt.get_suggested_tech()
            self._shot(TC, "2", "ai_result")
            self._record_check(TC, "S4: AI gợi ý công nghệ in", "✅ PASS",
                               f"kết quả: {tech or '(đọc được)'} — {elapsed:.1f}s")

            # Expand danh sách công nghệ (bonus, không FAIL nếu không expand được)
            expanded = self.pt.expand_tech_list(tech)
            self._record_check(TC, "S4b: Expand danh sách", "✅ PASS" if expanded else "⚠️ WARN",
                               "danh sách đã mở" if expanded else "không click được expand")
            if expanded:
                self._shot(TC, "3", "tech_expanded")
        else:
            self._shot(TC, "2_fail", "ai_timeout_state")
            error_detail = f"timeout {elapsed:.1f}s — AI không trả kết quả"
            if api_errs:
                error_detail += " | API: " + "; ".join(api_errs[:3])
            self._record_check(TC, "S4: AI gợi ý công nghệ in", "❌ FAIL",
                               error_detail, "kết quả trong giới hạn thời gian")
            pytest.fail(f"AI Gợi ý Công nghệ in không trả kết quả: {error_detail}")
