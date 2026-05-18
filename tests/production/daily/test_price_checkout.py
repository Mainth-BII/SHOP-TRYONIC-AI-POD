"""Daily smoke — Price Checkout.

Luồng BuyNow và Cart cho 4 sản phẩm đại diện.
Dừng ở màn hình Checkout: verify subtotal / VAT / shipping / total.
KHÔNG điền form giao hàng, KHÔNG click Thanh toán.
"""
import json
import os
import re

import pytest
from playwright.sync_api import Page

from .base_daily_test import BaseDailyTest, parse_int


# ── Load giá từ product_pricing.json ─────────────────────────────────────────

def _load_price(code: str) -> dict:
    """Trả về dict chứa salePrice, originalPrice, vat, shipping, total của variant đầu tiên."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "product_pricing.json"
    )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    product = next(p for p in data["products"] if p["code"] == code)
    variant  = product["variants"][0]
    shipping = data["global"]["shipping_fee"]
    vat_rate = data["global"]["VAT_rate"]
    sale     = variant["salePrice"]
    orig     = variant["originalPrice"]
    vat      = int(sale * vat_rate)
    total    = sale + vat + shipping
    return {
        "slug":       product["detail_url"].replace("/product/", ""),
        "name":       product["name"],
        "sale":       sale,
        "original":   orig,
        "vat":        vat,
        "shipping":   shipping,
        "total":      total,
        "test_size":  variant.get("test_sizes", ["M"])[0],
        "test_color": variant.get("test_colors", ["Trắng"])[0],
    }


_PT01  = _load_price("PT01")
_M21   = _load_price("M21")
_M22   = _load_price("M22")
_ET002 = _load_price("ET002")

_PRODUCTS = [_PT01, _M21, _M22, _ET002]


# ── Helpers đọc giá checkout ──────────────────────────────────────────────────

def _read_checkout_prices(page: Page) -> dict:
    """Đọc subtotal / VAT / shipping / total từ checkout page."""
    return page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        const re = /(\d{1,3}(?:[,.]\d{3})+)/;
        const result = {};
        for (let i = 0; i < lines.length; i++) {
            const l = lines[i];
            const next = lines[i + 1] || '';
            const parse = s => {
                const m = s.match(re);
                return m ? parseInt(m[1].replace(/[^\d]/g, '')) : null;
            };
            if (/^Tổng tiền$/i.test(l) && !result.subtotal) {
                result.subtotal = parse(l) || parse(next);
            }
            if (/Thuế VAT/i.test(l) && !result.vat) {
                result.vat = parse(l) || parse(next);
            }
            if (/Phí (vận chuyển|giao hàng)/i.test(l) && !result.shipping) {
                result.shipping = parse(l) || parse(next);
            }
            if (/Tổng (cộng|thanh toán)/i.test(l) && !result.total) {
                result.total = parse(l) || parse(next);
            }
        }
        return result;
    }""")


def _wait_checkout_prices(page: Page) -> None:
    try:
        page.wait_for_function(
            "() => document.body.innerText.includes('Thuế VAT')",
            timeout=15_000,
        )
    except Exception:
        page.wait_for_timeout(3_000)


# ── Test class ────────────────────────────────────────────────────────────────

class TestDailyPriceCheckout(BaseDailyTest):
    """Verify giá checkout 4 SP × BuyNow + Cart (không submit đơn)."""

    _SUITE_NAME   = "price_checkout"
    _REPORT_TITLE = "Daily Smoke — Price Checkout (4 SP × 2 Flow)"
    _results: list = []

    @pytest.fixture(autouse=True)
    def _setup(self, home_page, product_detail_page, checkout_page, env, page):
        self.home     = home_page
        self.detail   = product_detail_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = page
        self._results = []

    def _login(self) -> None:
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD trong .env")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    # ── BuyNow flow ───────────────────────────────────────────────────────────

    @pytest.mark.parametrize("p", _PRODUCTS, ids=[p["name"] for p in _PRODUCTS])
    def test_buynow_checkout_price(self, p: dict):
        """Navigate → Mua ngay → chọn size → Thanh toán ngay → verify checkout."""
        self._login()
        mh = f"{p['name'][:6]} BuyNow"

        self.page.goto(f"{self.env.fe_url}/product/{p['slug']}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)

        self.page.locator(
            "button:has-text('Mua ngay'), button:has-text('Mua Ngay')"
        ).first.click()
        self.page.wait_for_timeout(1_500)

        try:
            self.checkout.select_size_by_name(p["test_size"])
            self.page.wait_for_timeout(800)
        except Exception:
            pass

        self.page.locator(
            "button:has-text('Thanh toán ngay'), button:has-text('Thanh Toán Ngay')"
        ).first.click()
        try:
            self.page.wait_for_url("**/checkout**", timeout=10_000)
        except Exception:
            self.page.wait_for_timeout(3_000)

        _wait_checkout_prices(self.page)
        prices = _read_checkout_prices(self.page)
        print(f"\n  [INFO] {mh}: prices={prices}")

        self._assert_price(parse_int(prices.get("subtotal")), p["sale"],    f"{mh} Subtotal",          mh)
        self._assert_price(parse_int(prices.get("vat")),      p["vat"],     f"{mh} VAT 8%",            mh)
        self._assert_price(parse_int(prices.get("shipping")), p["shipping"],f"{mh} Phí giao hàng",     mh)
        self._assert_price(parse_int(prices.get("total")),    p["total"],   f"{mh} Tổng thanh toán",   mh)
        self.__class__._results.extend(self._results)

    # ── Cart flow ─────────────────────────────────────────────────────────────

    @pytest.mark.parametrize("p", _PRODUCTS, ids=[p["name"] for p in _PRODUCTS])
    def test_cart_checkout_price(self, p: dict):
        """Navigate → Add to cart → Cart page → verify giá item + tổng."""
        self._login()
        mh = f"{p['name'][:6]} Cart"

        self.page.goto(f"{self.env.fe_url}/product/{p['slug']}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)

        try:
            self.detail.select_color(p["test_color"])
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        try:
            self.checkout.select_size_by_name(p["test_size"])
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        added = self.detail.click_add_to_cart()
        self.page.wait_for_timeout(2_000)
        if not added:
            pytest.skip(f"{mh}: Không click được 'Thêm vào giỏ'")

        self.checkout.navigate_cart()
        self.page.wait_for_timeout(1_500)

        item_price = self.checkout.read_cart_item_price()
        cart_total = self.checkout.read_cart_total()
        self._assert_price(item_price, p["sale"], f"{mh} Giá item trong giỏ", mh)
        self._assert_price(cart_total, p["sale"], f"{mh} Cart total",          mh)

        proceed_btn = self.page.locator(
            "button:has-text('Thanh toán'), button:has-text('Đặt hàng'), "
            "a:has-text('Thanh toán'), a:has-text('Đặt hàng')"
        ).first
        if proceed_btn.is_visible(timeout=5_000):
            proceed_btn.click()
            try:
                self.page.wait_for_url("**/checkout**", timeout=10_000)
            except Exception:
                self.page.wait_for_timeout(3_000)

            _wait_checkout_prices(self.page)
            prices = _read_checkout_prices(self.page)
            print(f"\n  [INFO] {mh} checkout: prices={prices}")

            self._assert_price(parse_int(prices.get("subtotal")), p["sale"],  f"{mh} Checkout subtotal", mh)
            self._assert_price(parse_int(prices.get("total")),    p["total"], f"{mh} Checkout total",    mh)
        else:
            self._record_check(mh, f"{mh} Checkout total", "⚠️ WARN",
                               "Không tìm thấy nút proceed to checkout", "")

        self.__class__._results.extend(self._results)
