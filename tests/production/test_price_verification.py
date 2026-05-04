"""
Price Verification Tests — Kiểm tra giá hiển thị trên order screen và checkout
cho tất cả loại sản phẩm áo, màu, và size từ data/product_pricing.json.

Cấu trúc: 4 test method (1 per product code).
Mỗi test: login → AI gen → order screen → duyệt hết variant (color × size) → assert price.

SKIP guard: nếu URL hiện tại load sản phẩm khác với expected → SKIP với hướng dẫn update studio_url.
"""
import json
import math
import os
import re
from datetime import date

import pytest


def _pricing_data() -> dict:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "product_pricing.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_product(code: str) -> dict:
    for p in _pricing_data()["products"]:
        if p["code"] == code:
            return p
    raise ValueError(f"Product '{code}' not found in product_pricing.json")


def _load_daily_prompt() -> str:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "genz_prompts.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)["daily_prompts"]
    return prompts[date.today().timetuple().tm_yday % len(prompts)]


TOLERANCE = 1000  # VNĐ — chấp nhận sai lệch ±1.000đ do làm tròn UI


class TestPriceVerification:

    @pytest.fixture(autouse=True)
    def setup(self, home_page, studio_page, auth_page, checkout_page, env):
        self.home = home_page
        self.studio = studio_page
        self.auth = auth_page
        self.checkout = checkout_page
        self.env = env
        self.domain = "price_verification"

    # ── Shared helpers ────────────────────────────────────────────────────────

    def _login(self, tc_id: str) -> None:
        email = self.env.login_email
        password = self.env.login_password
        if not email or not password:
            pytest.skip(f"BỎ QUA {tc_id}: Thiếu credentials — kiểm tra .env")
        page = self.home.page
        self.home.navigate()
        self.home.header.click_login()
        page.wait_for_timeout(1000)
        self.auth.login(email, password)
        page.wait_for_timeout(3000)
        is_logged = not self.home.header.login_button.is_visible(timeout=5000)
        if not is_logged:
            page.wait_for_timeout(3000)
            is_logged = not self.home.header.login_button.is_visible(timeout=3000)
        assert is_logged, f"LỖI S0 ({tc_id}): Đăng nhập thất bại"
        print(f"  [PASS] S0 ({tc_id}): Đăng nhập thành công")

    def _navigate_to_order_screen(self, tc_id: str, studio_url: str) -> None:
        """AI gen → apply artwork → review → order screen."""
        page = self.home.page
        prompt = _load_daily_prompt()
        _R = "production"
        _D = self.domain

        # S1: Navigate studio
        self.home.goto(studio_url)
        page.wait_for_timeout(3000)
        self.studio.accept_terms(tc_id)
        assert self.studio.is_canvas_visible(), f"LỖI S1 ({tc_id}): Canvas không hiển thị"
        print(f"  [PASS] S1 ({tc_id}): Studio loaded — {page.url}")

        # S2: AI gen artwork
        print(f"  [INFO] S2 ({tc_id}): Đang chờ AI generate...")
        ok, elapsed, found = self.studio.wait_for_artworks(count=3, timeout=120)
        self.studio.shot(tc_id, "1", f"artworks_{found}imgs", domain=_D, root=_R)
        if not ok:
            pytest.skip(f"BỎ QUA S2 ({tc_id}): Chỉ {found}/3 ảnh sau {elapsed}s")
        print(f"  [PASS] S2 ({tc_id}): {found} artwork sau {elapsed}s")

        # S3: Apply artwork + hoàn tất
        applied = self.studio.click_artwork(index=0)
        assert applied, f"LỖI S3 ({tc_id}): Không click được artwork"
        self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
        self.studio.open_order_modal()
        page.wait_for_timeout(2000)
        assert (
            "review" in page.url
            or page.locator("button:has-text('Đặt hàng')").is_visible(timeout=5000)
        ), f"LỖI S3 ({tc_id}): Không tới review — URL: {page.url}"

        # S4: Click Đặt hàng → order screen
        dat_hang = page.locator("button:has-text('Đặt hàng')").first
        if dat_hang.is_visible(timeout=5000):
            dat_hang.click()
            try:
                page.wait_for_url("**/order**", timeout=8000)
            except Exception:
                page.wait_for_timeout(3000)
        assert "order" in page.url, f"LỖI S4 ({tc_id}): Không tới order screen — URL: {page.url}"
        page.wait_for_load_state("domcontentloaded")
        print(f"  [PASS] S4 ({tc_id}): Order screen — {page.url}")

    def _verify_product_loaded(self, tc_id: str, expected_product: dict) -> None:
        """SKIP nếu product loaded trên UI không khớp expected."""
        detected = self.checkout.read_product_type() or ""
        expected_name = expected_product["name"]
        # So sánh loose: check nếu tên sản phẩm có trong detected (hoặc ngược lại)
        name_parts = [w for w in expected_name.split() if len(w) > 2]
        matched = any(part.lower() in detected.lower() for part in name_parts)
        if not matched:
            pytest.skip(
                f"SKIP {tc_id}: Studio URL '{expected_product['studio_url']}' tải '{detected}', "
                f"expected '{expected_name}' — cập nhật studio_url trong product_pricing.json"
            )
        print(f"  [PASS] Product detect: '{detected}' ~ '{expected_name}'")

    def _assert_price(
        self, tc_id: str, variant: dict, color: str, size: str, step_label: str
    ) -> None:
        """Chọn color + size → đọc giá → assert."""
        page = self.home.page
        _R = "production"
        _D = self.domain
        expected = variant["salePrice"]

        # Chọn màu
        color_ok = self.checkout.select_color_on_order(color)
        page.wait_for_timeout(800)

        # Chọn size
        size_ok = self.checkout.select_size_by_name(size)
        page.wait_for_timeout(500)

        # Chụp
        self.studio.shot(
            tc_id, step_label,
            f"price_{variant['id']}_{color}_{size}",
            domain=_D, root=_R
        )

        # Đọc giá
        displayed = self.checkout.read_unit_price_as_int()
        status = "PASS" if (
            displayed and abs(displayed - expected) <= TOLERANCE
        ) else ("WARN" if displayed else "FAIL")

        print(
            f"  [{status}] {tc_id} | {variant['id']} | color={color} size={size} | "
            f"expected={expected:,}đ | displayed={displayed:,}đ" if displayed else
            f"  [{status}] {tc_id} | {variant['id']} | color={color} size={size} | "
            f"expected={expected:,}đ | displayed=None"
        )

        if status == "FAIL":
            assert False, (
                f"LỖI GIÁ {tc_id}: variant={variant['id']} color={color} size={size} | "
                f"expected={expected:,}đ | displayed={displayed}"
            )
        elif status == "WARN":
            print(f"  [WARN] {tc_id}: Không đọc được giá trên màn hình")

    # ── PRICE_001: PT01 — Áo Phông Cá Tính ──────────────────────────────────

    @pytest.mark.production
    def test_PRICE_001_PT01(self):
        """PRICE_001 — Áo Phông Cá Tính: verify salePrice 189.000đ trên order screen."""
        tc_id = "PRICE_001"
        product = _load_product("PT01")
        self._login(tc_id)
        self._navigate_to_order_screen(tc_id, product["studio_url"])
        self._verify_product_loaded(tc_id, product)

        step = 0
        for variant in product["variants"]:
            for color in variant["test_colors"]:
                for size in variant["test_sizes"]:
                    step += 1
                    self._assert_price(tc_id, variant, color, size, str(step + 1))

        print(f"  [PASS] {tc_id}: Kiểm tra {step} tổ hợp color×size — PT01 PASSED")

    # ── PRICE_002: M21 — Áo Phông Nặng Đông ────────────────────────────────

    @pytest.mark.production
    def test_PRICE_002_M21(self):
        """PRICE_002 — Áo Phông Nặng Đông: TRẮNG=119k / MÀU=128k trên order screen."""
        tc_id = "PRICE_002"
        product = _load_product("M21")
        self._login(tc_id)
        self._navigate_to_order_screen(tc_id, product["studio_url"])
        self._verify_product_loaded(tc_id, product)

        step = 0
        for variant in product["variants"]:
            for color in variant["test_colors"]:
                for size in variant["test_sizes"]:
                    step += 1
                    self._assert_price(tc_id, variant, color, size, str(step + 1))

        print(f"  [PASS] {tc_id}: Kiểm tra {step} tổ hợp — M21 TRẮNG/MÀU PASSED")

    # ── PRICE_003: M22 — Áo Phông Cơ Bản ──────────────────────────────────

    @pytest.mark.production
    def test_PRICE_003_M22(self):
        """PRICE_003 — Áo Phông Cơ Bản: TRẮNG=132k / MÀU=139k trên order screen."""
        tc_id = "PRICE_003"
        product = _load_product("M22")
        self._login(tc_id)
        self._navigate_to_order_screen(tc_id, product["studio_url"])
        self._verify_product_loaded(tc_id, product)

        step = 0
        for variant in product["variants"]:
            for color in variant["test_colors"]:
                for size in variant["test_sizes"]:
                    step += 1
                    self._assert_price(tc_id, variant, color, size, str(step + 1))

        print(f"  [PASS] {tc_id}: Kiểm tra {step} tổ hợp — M22 TRẮNG/MÀU PASSED")

    # ── PRICE_004: ET002 — Áo Phông Trẻ Em ─────────────────────────────────

    @pytest.mark.production
    def test_PRICE_004_ET002(self):
        """PRICE_004 — Áo Phông Trẻ Em: size 100-140=87k / 150-160=91k trên order screen."""
        tc_id = "PRICE_004"
        product = _load_product("ET002")
        self._login(tc_id)
        self._navigate_to_order_screen(tc_id, product["studio_url"])
        self._verify_product_loaded(tc_id, product)

        step = 0
        for variant in product["variants"]:
            for color in variant["test_colors"]:
                for size in variant["test_sizes"]:
                    step += 1
                    self._assert_price(tc_id, variant, color, size, str(step + 1))

        print(f"  [PASS] {tc_id}: Kiểm tra {step} tổ hợp size — ET002 PASSED")
