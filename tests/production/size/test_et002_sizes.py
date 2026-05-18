"""ET002 — Áo Phông Trẻ Em: Gợi Ý Size Bằng AI.

Luồng:
  Home → CLick sản phẩm → Mua ngay → Click [Gợi ý size]
  → Popup "Gợi Ý Size Bằng AI": chọn giới tính / nhập chiều cao & cân nặng → Gợi ý size
  → Verify size kết quả phải là 1 trong: 100, 110, 120, 130, 140, 150, 160
  → Test case invalid: thiếu chiều cao hoặc cân nặng → không có kết quả

2 nhóm giá:
  Size 100–140 → sale 96,000đ/chiếc
  Size 150–160 → sale 100,000đ/chiếc

URL: /product/ao-phong-tre-em
"""
import pytest
from playwright.sync_api import Page

from ._helpers import (
    open_ai_size_popup, submit_recommendation,
    read_recommended_size, is_result_displayed, click_chon_size,
    get_expected_size,
)
from .base_size_test import BaseSizeTest

_SLUG        = "ao-phong-tre-em"
_VALID_SIZES = {"100", "110", "120", "130", "140", "150", "160"}

# Trẻ em: chiều cao tương ứng với size (100cm→size100, 110cm→size110, ...)
_VALID_CASES = [
    ("Nam", 105, 18, "Nam 105cm/18kg — nhóm nhỏ"),
    ("Nam", 120, 25, "Nam 120cm/25kg — nhóm nhỏ"),
    ("Nam", 140, 35, "Nam 140cm/35kg — nhóm nhỏ"),
    ("Nam", 135, 27, "Nam 135cm/27kg — size 150"),
    ("Nữ",  110, 20, "Nữ 110cm/20kg"),
    ("Nữ",  145, 32, "Nữ 145cm/32kg — size 160"),
]

_INVALID_CASES = [
    ("Nam", None, 18,   "thiếu chiều cao"),
    ("Nam", 120,  None, "thiếu cân nặng"),
    ("Nam", None, None, "thiếu cả hai"),
]

# Giới hạn form: giá trị quá nhỏ / quá lớn → form validation phải chặn
_FORM_LIMIT_CASES = [
    ("Nam", 10,  20,  "chiều cao dưới min — 10cm"),
    ("Nam", 999, 20,  "chiều cao trên max — 999cm"),
    ("Nam", 120, 1,   "cân nặng dưới min — 1kg"),
    ("Nam", 120, 999, "cân nặng trên max — 999kg"),
]

# ET002 Kids: 100(90-100/11-13) 110(100-110/14-16) 120(110-120/17-18)
#             130(120-125/19-20) 140(125-130/21-24) 150(130-140/25-30) 160(140-150/30-35)
_ACCURACY_CASES = [
    ("Nam", 105, 15, "110 — giữa range 100-110cm / 14-16kg", "110"),
    ("Nam", 115, 17, "120 — giữa range 110-120cm / 17-18kg", "120"),
    ("Nam", 122, 19, "130 — giữa range 120-125cm / 19-20kg", "130"),
    ("Nam", 127, 22, "140 — giữa range 125-130cm / 21-24kg", "140"),
    ("Nam", 135, 27, "150 — giữa range 130-140cm / 25-30kg", "150"),
    ("Nam", 145, 32, "160 — giữa range 140-150cm / 30-35kg", "160"),
]

# Boundary cases: height đúng tại điểm giao 2 size liền kề
# ET002: 100(90-100) 110(100-110) 120(110-120) 130(120-125) 140(125-130) 150(130-140) 160(140-150)
_BOUNDARY_CASES = [
    ("Nam", 100, 13, "biên 100/110 — height=100cm",  ("100", "110")),
    ("Nam", 110, 16, "biên 110/120 — height=110cm",  ("110", "120")),
    ("Nam", 120, 18, "biên 120/130 — height=120cm",  ("120", "130")),
    ("Nam", 125, 20, "biên 130/140 — height=125cm",  ("130", "140")),
    ("Nam", 130, 24, "biên 140/150 — height=130cm",  ("140", "150")),
    ("Nam", 140, 30, "biên 150/160 — height=140cm",  ("150", "160")),
]

# Out-of-range: ET002 chart 90-150cm, 11-35kg
_OUT_OF_RANGE_CASES = [
    ("Nam",  85,  9, "dưới min — height=85cm / 9kg",   "100"),
    ("Nam", 155, 38, "trên max — height=155cm / 38kg",  "160"),
]


class TestET002AISizeGuide(BaseSizeTest):
    """Gợi Ý Size Bằng AI — ET002 Áo Phông Trẻ Em."""

    _PRODUCT_CODE = "ET002"
    _PRODUCT_NAME = "Áo Phông Trẻ Em"
    _REPORT_SLUG  = "et002"
    _results: list = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, base_url: str):
        self.page = page
        opened = open_ai_size_popup(page, base_url, _SLUG)
        if not opened:
            pytest.skip("Không mở được popup Gợi Ý Size Bằng AI cho ET002")

    def test_popup_has_required_elements(self, page: Page):
        """Popup phải có: giới tính Nam/Nữ, input chiều cao, input cân nặng, nút Gợi ý size."""
        assert page.locator("button:text-is('Nam')").first.is_visible(timeout=3000), \
            "ET002: Thiếu button giới tính Nam"
        assert page.locator("button:text-is('Nữ')").first.is_visible(timeout=3000), \
            "ET002: Thiếu button giới tính Nữ"
        assert page.locator("input[placeholder*='chiều cao']").first.is_visible(timeout=3000), \
            "ET002: Thiếu input chiều cao"
        assert page.locator("input[placeholder*='cân nặng']").first.is_visible(timeout=3000), \
            "ET002: Thiếu input cân nặng"
        assert page.locator("button[class*='EC4899']").first.is_visible(timeout=3000), \
            "ET002: Thiếu nút Gợi ý size (hồng)"

    @pytest.mark.parametrize("gender,height,weight,label", _VALID_CASES)
    def test_valid_recommendation(self, page: Page, gender, height, weight, label):
        """Input hợp lệ → kết quả phải là size nằm trong bộ size ET002 (100–160)."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is not None, \
            f"ET002 [{label}]: Không nhận được kết quả gợi ý size"
        assert result in _VALID_SIZES, \
            f"ET002 [{label}]: Kết quả '{result}' không thuộc bộ size hợp lệ {_VALID_SIZES}"

    @pytest.mark.parametrize("gender,height,weight,label", _INVALID_CASES)
    def test_invalid_no_result(self, page: Page, gender, height, weight, label):
        """Input thiếu thông tin → không được hiển thị kết quả gợi ý."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None, \
            f"ET002 [{label}]: Nhập thiếu dữ liệu nhưng vẫn trả về size '{result}'"

    @pytest.mark.parametrize("gender,height,weight,label,expected", _ACCURACY_CASES)
    def test_recommendation_accuracy(self, page: Page, gender, height, weight, label, expected):
        """AI gợi ý size phải khớp với size_charts.json cho input rõ ràng trong 1 bucket."""
        chart_size = get_expected_size("ET002", height, weight)
        assert chart_size == expected, \
            f"ET002: Bug trong bảng config — get_expected_size({height},{weight}) trả '{chart_size}', mong '{expected}'"

        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is not None, \
            f"ET002 [{label}]: Không nhận được kết quả gợi ý size"
        assert result == expected, \
            f"ET002 [{label}]: AI gợi ý '{result}', bảng size chart kỳ vọng '{expected}'"

    @pytest.mark.parametrize("gender,height,weight,label,allowed", _BOUNDARY_CASES)
    def test_boundary_recommendation(self, page: Page, gender, height, weight, label, allowed):
        """Height tại điểm giao 2 size → AI phải trả 1 trong 2 size liền kề."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip(f"ET002 [{label}]: AI không trả kết quả tại biên — bỏ qua")
        assert result in allowed, \
            f"ET002 [{label}]: AI gợi ý '{result}', tại ranh giới chỉ chấp nhận {set(allowed)}"

    @pytest.mark.parametrize("gender,height,weight,label,edge_size", _OUT_OF_RANGE_CASES)
    def test_out_of_range_recommendation(self, page: Page, gender, height, weight, label, edge_size):
        """Giá trị ngoài khoảng chart → AI trả size gần nhất hoặc không trả."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None or result == edge_size, \
            f"ET002 [{label}]: AI gợi ý '{result}', ngoài khoảng phải trả '{edge_size}' hoặc không trả"

    def test_bang_size_accessible(self, page: Page):
        """Nút 'bảng size tại đây' trong popup phải có và click được."""
        bang_btn = page.locator("button[class*='indigo']:has-text('bảng')")
        assert bang_btn.first.is_visible(timeout=3000), \
            "ET002: Không tìm thấy link 'bảng size tại đây' trong popup"

    def test_small_group_recommendation(self, page: Page):
        """Chiều cao 105cm → kết quả phải thuộc nhóm size nhỏ (100–140)."""
        submit_recommendation(page, "Nam", 105, 18)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip("Không nhận được kết quả — bỏ qua test nhóm size nhỏ")
        assert result in {"100", "110", "120", "130", "140"}, \
            f"ET002: height 105cm → expected nhóm 100–140, got '{result}'"

    def test_large_group_recommendation(self, page: Page):
        """Chiều cao 145cm → kết quả phải thuộc nhóm size lớn (150–160)."""
        submit_recommendation(page, "Nam", 145, 32)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip("Không nhận được kết quả — bỏ qua test nhóm size lớn")
        assert result in {"150", "160"}, \
            f"ET002: height 145cm → expected nhóm 150–160, got '{result}'"

    def test_chon_size_after_recommendation(self, page: Page):
        """Sau khi gợi ý → click 'Chọn Size X' → popup AI phải đóng và size được chọn."""
        submit_recommendation(page, "Nam", 120, 25)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip("Không nhận được kết quả — bỏ qua test Chọn Size")

        ok = click_chon_size(page)
        assert ok, f"ET002: Không click được nút 'Chọn Size {result}'"
        assert not is_result_displayed(page), \
            "ET002: Popup AI vẫn còn mở sau khi click Chọn Size"

    @pytest.mark.parametrize("gender,height,weight,label", _FORM_LIMIT_CASES)
    def test_form_limit_validation(self, page: Page, gender, height, weight, label):
        """Giá trị vượt giới hạn min/max của form → không được trả size hợp lệ."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None, \
            f"ET002 [{label}]: Nhập giá trị ngoài giới hạn nhưng vẫn trả size '{result}'"
