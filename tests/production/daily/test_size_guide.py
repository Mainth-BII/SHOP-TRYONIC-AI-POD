"""Daily smoke — AI Size Guide.

1 valid input / sản phẩm → AI phải trả size hợp lệ.
Không tạo đơn, không navigate khỏi popup.
"""
import pytest
from playwright.sync_api import Page

from .base_daily_test import BaseDailyTest

# Import helpers từ size module (tái dùng, không duplicate)
from production.size._helpers import (
    open_ai_size_popup,
    submit_recommendation,
    read_recommended_size,
)

# ── Smoke cases: 1 input rõ ràng / sản phẩm ─────────────────────────────────
# (slug, product_code, gender, height, weight, valid_sizes)

_CASES = [
    ("ao-phong-ca-tinh",  "PT01",  "Nam", 170, 65, {"XS","S","M","L","XL","2XL","3XL"}),
    ("ao-phong-nang-dong","M21",   "Nam", 170, 65, {"XS","S","M","L","XL","2XL","3XL"}),
    ("ao-phong-co-ban",   "M22",   "Nam", 170, 65, {"XS","S","M","L","XL","2XL","3XL"}),
    ("ao-phong-tre-em",   "ET002", "Nam", 120, 22, {"100","110","120","130","140","150","160"}),
]


class TestDailySizeGuide(BaseDailyTest):
    """Smoke: AI size recommendation trả size hợp lệ cho 4 sản phẩm."""

    _SUITE_NAME   = "size_guide_smoke"
    _REPORT_TITLE = "Daily Smoke — AI Size Guide (4 SP)"
    _results: list = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, base_url: str):
        self.page     = page
        self.base_url = base_url
        self._results = []

    @pytest.mark.parametrize(
        "slug,code,gender,height,weight,valid_sizes", _CASES,
        ids=[c[1] for c in _CASES]
    )
    def test_ai_size_smoke(self, slug, code, gender, height, weight, valid_sizes):
        """Mở popup → submit valid input → AI trả size thuộc bộ size hợp lệ."""
        opened = open_ai_size_popup(self.page, self.base_url, slug)
        if not opened:
            self._record_check(code, f"{code} AI popup mở được", "⚠️ WARN",
                               "Không mở được popup", "Popup visible")
            pytest.skip(f"{code}: Không mở được popup AI size guide")

        self._record_check(code, f"{code} AI popup mở được", "✅ PASS",
                           "Popup visible", "Popup visible")
        self._shot(code, "1", "size_popup_open")

        submit_recommendation(self.page, gender, height, weight)
        self._shot(code, "2", "ai_result")
        result = read_recommended_size(self.page)

        if result is None:
            self._record_check(code, f"{code} AI gợi ý size ({height}cm/{weight}kg)",
                               "❌ FAIL", "Không trả kết quả", f"1 size trong {sorted(valid_sizes)}")
            assert False, f"{code}: AI không trả size cho {height}cm/{weight}kg"

        ok = result in valid_sizes
        status = "✅ PASS" if ok else "❌ FAIL"
        self._record_check(
            code, f"{code} AI gợi ý size ({height}cm/{weight}kg)",
            status, result, f"1 trong {sorted(valid_sizes)}"
        )
        assert ok, f"{code}: AI trả '{result}' — không thuộc bộ size hợp lệ {valid_sizes}"
        self.__class__._results.extend(self._results)
