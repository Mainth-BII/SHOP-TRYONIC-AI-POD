"""M22 — Áo Phông Cơ Bản: Gợi Ý Size Bằng AI.

Luồng:
  Home → CLick sản phẩm → Mua ngay → Click [Gợi ý size]
  → Popup "Gợi Ý Size Bằng AI": chọn giới tính / nhập chiều cao & cân nặng → Gợi ý size
  → Verify size kết quả phải là 1 trong XS/S/M/L/XL/2XL/3XL
  → Test case invalid: thiếu chiều cao hoặc cân nặng → không có kết quả

Giá:
  Màu Trắng → 143,000đ | Màu khác → 152,000đ

URL: /product/ao-phong-co-ban
"""
import pytest
from playwright.sync_api import Page

from ._helpers import (
    open_ai_size_popup, submit_recommendation,
    read_recommended_size, is_result_displayed, click_chon_size,
    get_expected_size,
)
from .base_size_test import BaseSizeTest

_SLUG        = "ao-phong-co-ban"
_VALID_SIZES = {"M", "L", "XL", "2XL"}

# M22 Unisex chỉ có 4 size: M(150-160/50-60kg) L(160-170/60-70kg) XL(170-175/70-80kg) 2XL(175-180/80-90kg)
_VALID_CASES = [
    ("Nam", 155, 55,  "Nam 155cm/55kg → M"),
    ("Nam", 165, 65,  "Nam 165cm/65kg → L"),
    ("Nam", 172, 75,  "Nam 172cm/75kg → XL"),
    ("Nữ",  158, 52,  "Nữ 158cm/52kg → M"),
    ("Nữ",  177, 85,  "Nữ 177cm/85kg → 2XL"),
]

_INVALID_CASES = [
    ("Nam", None, 65,   "thiếu chiều cao"),
    ("Nam", 170,  None, "thiếu cân nặng"),
    ("Nam", None, None, "thiếu cả hai"),
]

# Giới hạn form: giá trị quá nhỏ / quá lớn → form validation phải chặn
_FORM_LIMIT_CASES = [
    ("Nam", 50,  65,  "chiều cao dưới min — 50cm"),
    ("Nam", 999, 65,  "chiều cao trên max — 999cm"),
    ("Nam", 170, 1,   "cân nặng dưới min — 1kg"),
    ("Nam", 170, 999, "cân nặng trên max — 999kg"),
]

# M22 Unisex: M(150-160/50-60) L(160-170/60-70) XL(170-175/70-80) 2XL(175-180/80-90)
_ACCURACY_CASES = [
    ("Nam", 155, 55, "M — giữa range 150-160cm / 50-60kg",   "M"),
    ("Nam", 165, 65, "L — giữa range 160-170cm / 60-70kg",   "L"),
    ("Nam", 172, 75, "XL — giữa range 170-175cm / 70-80kg",  "XL"),
    ("Nữ",  177, 85, "2XL — giữa range 175-180cm / 80-90kg", "2XL"),
]

# Boundary cases: height đúng tại điểm giao 2 size liền kề
_BOUNDARY_CASES = [
    ("Nam", 160, 65, "biên M/L — height=160cm",    ("M",  "L")),
    ("Nam", 170, 72, "biên L/XL — height=170cm",   ("L",  "XL")),
    ("Nam", 175, 82, "biên XL/2XL — height=175cm", ("XL", "2XL")),
]

# Out-of-range: M22 chart 150-180cm, 50-90kg
_OUT_OF_RANGE_CASES = [
    ("Nam", 145, 45, "dưới min — height=145cm < 150cm",  "M"),
    ("Nam", 185, 95, "trên max — height=185cm > 180cm",  "2XL"),
]


class TestM22AISizeGuide(BaseSizeTest):
    """Gợi Ý Size Bằng AI — M22 Áo Phông Cơ Bản."""

    _PRODUCT_CODE = "M22"
    _PRODUCT_NAME = "Áo Phông Cơ Bản"
    _REPORT_SLUG  = "m22"
    _results: list = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, base_url: str):
        self.page = page
        opened = open_ai_size_popup(page, base_url, _SLUG)
        if not opened:
            pytest.skip("Không mở được popup Gợi Ý Size Bằng AI cho M22")

    def test_popup_has_required_elements(self, page: Page):
        """Popup phải có: giới tính Nam/Nữ, input chiều cao, input cân nặng, nút Gợi ý size."""
        assert page.locator("button:text-is('Nam')").first.is_visible(timeout=3000), \
            "M22: Thiếu button giới tính Nam"
        assert page.locator("button:text-is('Nữ')").first.is_visible(timeout=3000), \
            "M22: Thiếu button giới tính Nữ"
        assert page.locator("input[placeholder*='chiều cao']").first.is_visible(timeout=3000), \
            "M22: Thiếu input chiều cao"
        assert page.locator("input[placeholder*='cân nặng']").first.is_visible(timeout=3000), \
            "M22: Thiếu input cân nặng"
        assert page.locator("button[class*='EC4899']").first.is_visible(timeout=3000), \
            "M22: Thiếu nút Gợi ý size (hồng)"

    @pytest.mark.parametrize("gender,height,weight,label", _VALID_CASES)
    def test_valid_recommendation(self, page: Page, gender, height, weight, label):
        """Input hợp lệ → kết quả phải là size nằm trong bộ size M22."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is not None, \
            f"M22 [{label}]: Không nhận được kết quả gợi ý size"
        assert result in _VALID_SIZES, \
            f"M22 [{label}]: Kết quả '{result}' không thuộc bộ size hợp lệ {_VALID_SIZES}"

    @pytest.mark.parametrize("gender,height,weight,label", _INVALID_CASES)
    def test_invalid_no_result(self, page: Page, gender, height, weight, label):
        """Input thiếu thông tin → không được hiển thị kết quả gợi ý."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None, \
            f"M22 [{label}]: Nhập thiếu dữ liệu nhưng vẫn trả về size '{result}'"

    @pytest.mark.parametrize("gender,height,weight,label,expected", _ACCURACY_CASES)
    def test_recommendation_accuracy(self, page: Page, gender, height, weight, label, expected):
        """AI gợi ý size phải khớp với size_charts.json cho input rõ ràng trong 1 bucket."""
        chart_size = get_expected_size("M22", height, weight)
        assert chart_size == expected, \
            f"M22: Bug trong bảng config — get_expected_size({height},{weight}) trả '{chart_size}', mong '{expected}'"

        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is not None, \
            f"M22 [{label}]: Không nhận được kết quả gợi ý size"
        assert result == expected, \
            f"M22 [{label}]: AI gợi ý '{result}', bảng size chart kỳ vọng '{expected}'"

    @pytest.mark.parametrize("gender,height,weight,label,allowed", _BOUNDARY_CASES)
    def test_boundary_recommendation(self, page: Page, gender, height, weight, label, allowed):
        """Height tại điểm giao 2 size → AI phải trả 1 trong 2 size liền kề."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip(f"M22 [{label}]: AI không trả kết quả tại biên — bỏ qua")
        assert result in allowed, \
            f"M22 [{label}]: AI gợi ý '{result}', tại ranh giới chỉ chấp nhận {set(allowed)}"

    @pytest.mark.parametrize("gender,height,weight,label,edge_size", _OUT_OF_RANGE_CASES)
    def test_out_of_range_recommendation(self, page: Page, gender, height, weight, label, edge_size):
        """Giá trị ngoài khoảng chart → AI trả size gần nhất hoặc không trả."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None or result == edge_size, \
            f"M22 [{label}]: AI gợi ý '{result}', ngoài khoảng phải trả '{edge_size}' hoặc không trả"

    def test_bang_size_accessible(self, page: Page):
        """Nút 'bảng size tại đây' trong popup phải có và click được."""
        bang_btn = page.locator("button[class*='indigo']:has-text('bảng')")
        assert bang_btn.first.is_visible(timeout=3000), \
            "M22: Không tìm thấy link 'bảng size tại đây' trong popup"

    def test_chon_size_after_recommendation(self, page: Page):
        """Sau khi gợi ý → click 'Chọn Size X' → popup AI phải đóng và size được chọn."""
        submit_recommendation(page, "Nam", 165, 65)
        result = read_recommended_size(page)
        if result is None:
            pytest.skip("Không nhận được kết quả — bỏ qua test Chọn Size")

        ok = click_chon_size(page)
        assert ok, f"M22: Không click được nút 'Chọn Size {result}'"
        assert not is_result_displayed(page), \
            "M22: Popup AI vẫn còn mở sau khi click Chọn Size"

    @pytest.mark.parametrize("gender,height,weight,label", _FORM_LIMIT_CASES)
    def test_form_limit_validation(self, page: Page, gender, height, weight, label):
        """Giá trị vượt giới hạn min/max của form → không được trả size hợp lệ."""
        submit_recommendation(page, gender, height, weight)
        result = read_recommended_size(page)
        assert result is None, \
            f"M22 [{label}]: Nhập giá trị ngoài giới hạn nhưng vẫn trả size '{result}'"
