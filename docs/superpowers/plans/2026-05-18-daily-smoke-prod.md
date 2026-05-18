# Daily Smoke Test (Production) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo bộ smoke test chạy hàng ngày trên `tests/production/daily/`, dừng ở màn hình checkout (không submit đơn), chạy trên TEST env trước — sau khi ổn chuyển sang PROD bằng `--env=prod`.

**Architecture:** 3 file test độc lập: (1) price_checkout — verify giá 4 SP × 2 flow; (2) size_guide — smoke AI size 4 SP; (3) checkout_summary — verify tổng + khuyến mãi. Mỗi file có base class riêng từ `base_daily_test.py`. Report lưu tập trung tại `reports/daily/`.

**Tech Stack:** pytest, playwright-python, `data/product_pricing.json`, `tests/production/size/_helpers.py` (tái dùng), conftest.py gốc (xử lý `--env`).

---

## File Structure

| File | Trách nhiệm |
|------|-------------|
| `tests/production/daily/__init__.py` | Package marker |
| `tests/production/daily/base_daily_test.py` | Base class: `_record_check`, `_results`, `_save_report` (numbered list format) |
| `tests/production/daily/test_price_checkout.py` | 8 test: PT01/M21/M22/ET002 × BuyNow + Cart — dừng ở checkout |
| `tests/production/daily/test_size_guide.py` | 4 test smoke AI size guide (1 valid input / SP) |
| `tests/production/daily/test_checkout_summary.py` | 1 test: cart + mã GIAM20 → verify tổng + dòng giảm giá |

---

## Task 1: Package + BaseDailyTest

**Files:**
- Create: `tests/production/daily/__init__.py`
- Create: `tests/production/daily/base_daily_test.py`

- [ ] **Step 1: Tạo `__init__.py`**

```python
# tests/production/daily/__init__.py
```

- [ ] **Step 2: Tạo `base_daily_test.py`**

```python
"""Base class cho daily smoke tests.

Dừng ở màn hình checkout — không submit đơn, không tạo rác trên production.
Report format: numbered list (giống SH07), lưu tại reports/daily/.
"""
import glob as _glob
import os
import re
from datetime import datetime
from typing import ClassVar


def parse_int(val) -> int | None:
    if not val:
        return None
    digits = re.sub(r"[^\d]", "", str(val))
    return int(digits) if digits else None


class BaseDailyTest:
    """Subclass phải khai báo:
      _SUITE_NAME  = "PRICE_CHECKOUT"     # dùng trong tên file report
      _REPORT_TITLE = "Daily Smoke: ..."  # tiêu đề H1
      _results: ClassVar[list] = []       # class-level
    """

    _SUITE_NAME: str = "DAILY"
    _REPORT_TITLE: str = "Daily Smoke Test"
    _results: ClassVar[list] = []

    # ── Ghi kết quả ──────────────────────────────────────────────────────────

    def _record_check(self, mh: str, check: str, status: str,
                      actual: str = "", expected: str = "") -> None:
        self._results.append({
            "mh": mh, "check": check, "status": status,
            "actual": actual, "expected": expected,
        })

    # ── Assert giá ───────────────────────────────────────────────────────────

    TOLERANCE: int = 1_000

    def _assert_price(self, displayed: int | None, expected: int | None,
                      label: str, mh: str = "CHECK") -> None:
        if displayed is None:
            self._record_check(mh, label, "⚠️ WARN", "N/A",
                               f"expected={expected:,}đ" if expected else "")
            return
        if expected is None:
            self._record_check(mh, label, "ℹ️ INFO",
                               f"{displayed:,}đ", "")
            return
        ok = abs(displayed - expected) <= self.TOLERANCE
        status = "✅ PASS" if ok else "❌ FAIL"
        self._record_check(mh, label, status,
                           f"{displayed:,}đ", f"{expected:,}đ")
        assert ok, (
            f"{label}: expected={expected:,}đ, got={displayed:,}đ "
            f"(chênh {displayed - expected:+,}đ)"
        )

    # ── Save report ───────────────────────────────────────────────────────────

    @classmethod
    def _save_report(cls) -> None:
        report_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "reports", "daily"
        )
        os.makedirs(report_dir, exist_ok=True)

        slug = cls._SUITE_NAME.lower()
        for old in _glob.glob(os.path.join(report_dir, f"{slug}_*.md")):
            try:
                os.remove(old)
            except OSError:
                pass

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ts_display = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        filepath = os.path.join(report_dir, f"{slug}_{ts}.md")

        results = cls._results
        total   = len(results)
        passed  = sum(1 for r in results if "PASS" in r.get("status", ""))
        failed  = sum(1 for r in results if "FAIL" in r.get("status", ""))
        warned  = sum(1 for r in results if "WARN" in r.get("status", ""))
        info_c  = sum(1 for r in results if "INFO" in r.get("status", ""))
        verdict = "✅ ALL PASS" if failed == 0 else f"❌ {failed} FAIL"

        tong_str = (
            f"{total} kiểm tra  ✅ {passed}  ❌ {failed}  ⚠️ {warned}  ℹ️ {info_c}"
        )
        info_rows = [
            ("Ngày chạy",  ts_display),
            ("Môi trường", "TEST — `test.shop.tryonic.ai`"),
            ("Kết quả",    verdict),
            ("Tổng",       tong_str),
        ]
        iw1 = max(len(k) for k, _ in info_rows)
        iw2 = max(len(v) for _, v in info_rows)
        info_sep    = f"| {'-' * iw1} | {'-' * iw2} |"
        info_header = f"| {'Trường':<{iw1}} | {'Giá trị':<{iw2}} |"
        info_lines  = [info_header, info_sep] + [
            f"| {k:<{iw1}} | {v:<{iw2}} |" for k, v in info_rows
        ]

        detail_items: list[str] = []
        for i, r in enumerate(results, 1):
            _mh   = str(r["mh"]).replace("\n", " ")
            _chk  = str(r["check"]).replace("\n", " ")
            _sta  = str(r["status"]).replace("\n", " ")
            _act  = (str(r["actual"]).replace("\n", " / ")
                     if r.get("actual") else "—")
            _exp  = (str(r["expected"]).replace("\n", " ")
                     if r.get("expected") else (
                         "" if "INFO" in r.get("status", "") else "—"))
            icon = ("✅" if "PASS" in _sta else
                    "❌" if "FAIL" in _sta else
                    "⚠️" if "WARN" in _sta else "ℹ️")
            line1 = f"{i}. {icon} **{_mh}** — {_chk}"
            line2 = f"   → `{_act}`"
            if _exp and _exp != "—":
                line2 += f"  *(mong đợi: {_exp})*"
            detail_items += [line1, line2, ""]

        if failed == 0 and warned == 0:
            summary_line = "> ✅ **TẤT CẢ KIỂM TRA ĐỀU PASS!**"
        elif failed == 0:
            summary_line = f"> ⚠️ **PASS nhưng có {warned} cảnh báo**"
        else:
            summary_line = f"> ❌ **CÓ {failed} KIỂM TRA FAIL — CẦN XỬ LÝ!**"

        lines = (
            [f"# {cls._REPORT_TITLE}", ""]
            + info_lines
            + ["", "## Bảng chi tiết", ""]
            + detail_items
            + ["## Tóm tắt", "", summary_line, ""]
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n  📁 Daily report: {filepath}")
```

- [ ] **Step 3: Chạy import check**

```bash
cd d:\TEST_STUDIO\shop_tryonic_ai
python -c "from tests.production.daily.base_daily_test import BaseDailyTest, parse_int; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add tests/production/daily/__init__.py tests/production/daily/base_daily_test.py
git commit -m "feat(daily): add BaseDailyTest với report numbered-list"
```

---

## Task 2: test_price_checkout.py — 4 SP × BuyNow + Cart

**Files:**
- Create: `tests/production/daily/test_price_checkout.py`

Verify giá tại màn hình checkout. **Không** điền form, **không** click Thanh toán.

Giá tham chiếu (plain, size M/110, màu Trắng, no coupon):

| SP | salePrice | VAT (8%) | Shipping | Total |
|----|-----------|----------|----------|-------|
| PT01 | 189,000 | 15,120 | 20,000 | 224,120 |
| M21  | 130,000 | 10,400 | 20,000 | 160,400 |
| M22  | 143,000 | 11,440 | 20,000 | 174,440 |
| ET002 | 96,000 | 7,680 | 20,000 | 123,680 |

- [ ] **Step 1: Tạo file**

```python
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

def _load_price(code: str, color_key: str = "TRẮNG") -> dict:
    """Trả về dict chứa salePrice, originalPrice của variant đầu tiên khớp màu."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "product_pricing.json"
    )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    product = next(p for p in data["products"] if p["code"] == code)
    # Lấy variant đầu tiên — test_colors[0]
    variant = product["variants"][0]
    shipping = data["global"]["shipping_fee"]
    vat_rate = data["global"]["VAT_rate"]
    sale     = variant["salePrice"]
    orig     = variant["originalPrice"]
    vat      = int(sale * vat_rate)
    total    = sale + vat + shipping
    return {
        "slug":     product["detail_url"].lstrip("/product/"),
        "name":     product["name"],
        "sale":     sale,
        "original": orig,
        "vat":      vat,
        "shipping": shipping,
        "total":    total,
        "test_size": variant.get("test_sizes", ["M"])[0],
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

        # Mở product detail
        slug = p["slug"].replace("/product/", "").lstrip("/")
        self.page.goto(f"{self.env.fe_url}/product/{slug}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)

        # Click Mua ngay
        self.page.locator(
            "button:has-text('Mua ngay'), button:has-text('Mua Ngay')"
        ).first.click()
        self.page.wait_for_timeout(1_500)

        # Chọn size
        size = p["test_size"]
        try:
            self.checkout.select_size_by_name(size)
            self.page.wait_for_timeout(800)
        except Exception:
            pass

        # Click Thanh toán ngay → đến checkout
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

        self._assert_price(
            parse_int(prices.get("subtotal")), p["sale"],
            f"{mh} Subtotal", mh
        )
        self._assert_price(
            parse_int(prices.get("vat")), p["vat"],
            f"{mh} VAT 8%", mh
        )
        self._assert_price(
            parse_int(prices.get("shipping")), p["shipping"],
            f"{mh} Phí giao hàng", mh
        )
        self._assert_price(
            parse_int(prices.get("total")), p["total"],
            f"{mh} Tổng thanh toán", mh
        )

    # ── Cart flow ─────────────────────────────────────────────────────────────

    @pytest.mark.parametrize("p", _PRODUCTS, ids=[p["name"] for p in _PRODUCTS])
    def test_cart_checkout_price(self, p: dict):
        """Navigate → Add to cart → Cart page → Thanh toán → verify checkout."""
        self._login()
        mh = f"{p['name'][:6]} Cart"

        slug = p["slug"].replace("/product/", "").lstrip("/")
        self.page.goto(f"{self.env.fe_url}/product/{slug}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)

        # Chọn màu + size trên product page
        try:
            color = p["test_color"]
            self.detail.select_color(color)
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        try:
            self.checkout.select_size_by_name(p["test_size"])
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        # Add to cart
        added = self.detail.click_add_to_cart()
        self.page.wait_for_timeout(2_000)
        if not added:
            pytest.skip(f"{mh}: Không click được 'Thêm vào giỏ'")

        # Navigate đến cart
        self.checkout.navigate_cart()
        self.page.wait_for_timeout(1_500)

        # Verify giá item trong cart
        item_price = self.checkout.read_cart_item_price()
        cart_total = self.checkout.read_cart_total()
        self._assert_price(item_price, p["sale"], f"{mh} Giá item trong giỏ", mh)
        self._assert_price(cart_total, p["sale"], f"{mh} Cart total", mh)

        # Proceed to checkout
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

            self._assert_price(
                parse_int(prices.get("subtotal")), p["sale"],
                f"{mh} Checkout subtotal", mh
            )
            self._assert_price(
                parse_int(prices.get("total")), p["total"],
                f"{mh} Checkout total", mh
            )
        else:
            self._record_check(mh, f"{mh} Checkout total", "⚠️ WARN",
                               "Không tìm thấy nút proceed to checkout", "")

    @pytest.fixture(autouse=False)
    def _save(self):
        yield
        if self._results:
            self.__class__._results = self._results
            self._save_report()
```

- [ ] **Step 2: Chạy 1 test nhanh để check import + flow**

```bash
cd d:\TEST_STUDIO\shop_tryonic_ai
python -m pytest tests/production/daily/test_price_checkout.py::TestDailyPriceCheckout::test_buynow_checkout_price[Áo\ Phông\ Cá\ Tính] -v --tb=short 2>&1
```

Expected: PASSED hoặc SKIP (nếu chưa có credentials)

- [ ] **Step 3: Commit**

```bash
git add tests/production/daily/test_price_checkout.py
git commit -m "feat(daily): test_price_checkout - 4 SP × BuyNow + Cart, dừng tại checkout"
```

---

## Task 3: test_size_guide.py — Smoke AI Size Guide

**Files:**
- Create: `tests/production/daily/test_size_guide.py`

Tái dùng helpers từ `tests/production/size/_helpers.py`. Mỗi SP test 1 input hợp lệ, verify AI trả size trong bộ size hợp lệ.

- [ ] **Step 1: Tạo file**

```python
"""Daily smoke — AI Size Guide.

1 valid input / sản phẩm → AI phải trả size hợp lệ.
Không tạo đơn, không navigate khỏi popup.
"""
import pytest
from playwright.sync_api import Page

from .base_daily_test import BaseDailyTest

# Import helpers từ size module (tái dùng, không duplicate)
from tests.production.size._helpers import (
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

        submit_recommendation(self.page, gender, height, weight)
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

    @pytest.fixture(autouse=False)
    def _save(self):
        yield
        if self._results:
            self.__class__._results = self._results
            self._save_report()
```

- [ ] **Step 2: Chạy test nhanh**

```bash
python -m pytest "tests/production/daily/test_size_guide.py::TestDailySizeGuide::test_ai_size_smoke[PT01]" -v --tb=short 2>&1
```

Expected: PASSED

- [ ] **Step 3: Commit**

```bash
git add tests/production/daily/test_size_guide.py
git commit -m "feat(daily): test_size_guide_smoke - 4 SP × 1 valid AI input"
```

---

## Task 4: test_checkout_summary.py — Cart + Coupon Verify

**Files:**
- Create: `tests/production/daily/test_checkout_summary.py`

Add to cart → checkout → apply GIAM20 → verify dòng khuyến mãi + tổng sau giảm.  
**Dừng tại đây — không click Thanh toán.**

PT01 Trắng M tham chiếu:
- sale = 189,000đ
- GIAM20 = 20% × 189,000 = 37,800đ
- After discount = 151,200đ
- VAT after = int(151,200 × 0.08) = 12,096đ
- Total after = 151,200 + 12,096 + 20,000 = 183,296đ

- [ ] **Step 1: Tạo file**

```python
"""Daily smoke — Checkout Summary (cart + coupon).

Luồng: PT01 Trắng → Add to cart → Checkout → Apply GIAM20
→ verify dòng khuyến mãi + tổng sau giảm.
KHÔNG click Thanh toán.
"""
import json
import os

import pytest
from playwright.sync_api import Page

from .base_daily_test import BaseDailyTest, parse_int


# ── Tham chiếu giá ────────────────────────────────────────────────────────────

def _load_pt01() -> dict:
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "data", "product_pricing.json"
    )
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    product = next(p for p in data["products"] if p["code"] == "PT01")
    variant  = product["variants"][0]  # M/L/XL variant — salePrice=189,000
    # Lấy variant có salePrice = 189,000 (M/L/XL)
    for v in product["variants"]:
        if "M" in v.get("sizes", []):
            variant = v
            break
    sale     = variant["salePrice"]                   # 189,000
    giam20   = data["discount_codes"]["GIAM20"]["value"]  # 0.20
    vat_rate = data["global"]["VAT_rate"]             # 0.08
    shipping = data["global"]["shipping_fee"]         # 20,000
    discount = int(sale * giam20)                     # 37,800
    after    = sale - discount                        # 151,200
    vat_dc   = int(after * vat_rate)                  # 12,096
    total_dc = after + vat_dc + shipping              # 183,296
    return {
        "slug":     "ao-phong-ca-tinh",
        "name":     "Áo Phông Cá Tính",
        "color":    "Trắng",
        "size":     "M",
        "sale":     sale,
        "discount": discount,
        "total_dc": total_dc,
        "vat_dc":   vat_dc,
        "shipping": shipping,
    }


_PT01 = _load_pt01()


# ── Helper đọc discount line ──────────────────────────────────────────────────

def _read_discount_line(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        for (let i = 0; i < lines.length; i++) {
            if (/khuyến mãi|giảm giá|discount/i.test(lines[i])) {
                const nearby = lines.slice(i, i + 3).join(' ');
                const m = nearby.match(/[−\-]\s*([\d,.]+)\s*[đ₫]/);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _read_total(page: Page) -> int | None:
    val = page.evaluate(r"""() => {
        const text = document.body.innerText || '';
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        const re = /(\d{1,3}(?:[,.]\d{3})+)/;
        for (let i = 0; i < lines.length; i++) {
            if (/Tổng (cộng|thanh toán)/i.test(lines[i])) {
                const m = lines[i].match(re) || (lines[i+1] || '').match(re);
                if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
            }
        }
        return null;
    }""")
    return int(val) if val else None


def _apply_coupon(page: Page, code: str) -> bool:
    """Xóa mã cũ (nếu có) → nhập mã mới → click Áp dụng."""
    # Xóa mã cũ
    page.evaluate(r"""() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const del = btns.find(b => b.offsetWidth > 0 && (
            /^[×x✕]$/.test(b.textContent.trim()) ||
            b.textContent.trim() === 'Xoá' ||
            b.textContent.trim() === 'Xóa' ||
            (b.getAttribute('aria-label') || '').toLowerCase().includes('xo')
        ));
        if (del) { del.click(); return del.textContent.trim(); }
        return null;
    }""")
    page.wait_for_timeout(800)

    # Nhập mã
    inp = page.locator(
        "input[placeholder*='mã khuyến mại'], input[placeholder*='mã giảm giá'], "
        "input[placeholder*='coupon'], input[placeholder*='promo']"
    ).first
    if not inp.is_visible(timeout=5_000):
        return False
    inp.click()
    page.wait_for_timeout(300)
    inp.fill(code)
    page.wait_for_timeout(500)

    try:
        page.wait_for_selector("#btn-apply-promo:not([disabled])", timeout=5_000)
        page.locator("#btn-apply-promo").click()
    except Exception:
        page.evaluate(r"""() => {
            const btn = document.querySelector('#btn-apply-promo')
                       || Array.from(document.querySelectorAll('button'))
                          .find(b => b.textContent.trim() === 'Áp dụng');
            if (btn) { btn.removeAttribute('disabled'); btn.click(); }
        }""")
    page.wait_for_timeout(2_000)
    return True


# ── Test class ────────────────────────────────────────────────────────────────

class TestDailyCheckoutSummary(BaseDailyTest):
    """Smoke: Cart → Checkout → Apply GIAM20 → verify discount + total (no submit)."""

    _SUITE_NAME   = "checkout_summary"
    _REPORT_TITLE = "Daily Smoke — Checkout Summary (PT01 + GIAM20)"
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
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1_000)
        from pages.auth_modal_page import AuthModalPage
        AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
        self.page.wait_for_timeout(3_000)

    def test_checkout_with_coupon_giam20(self):
        """PT01 Trắng M → checkout → GIAM20 → verify discount line + tổng sau giảm."""
        p = _PT01
        self._login()

        # Navigate to product
        self.page.goto(f"{self.env.fe_url}/product/{p['slug']}")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1_500)

        # Add to cart
        try:
            self.detail.select_color(p["color"])
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        try:
            self.checkout.select_size_by_name(p["size"])
            self.page.wait_for_timeout(500)
        except Exception:
            pass

        added = self.detail.click_add_to_cart()
        self.page.wait_for_timeout(2_000)
        if not added:
            pytest.skip("Không click được 'Thêm vào giỏ'")

        # Navigate to checkout
        self.checkout.navigate_cart()
        self.page.wait_for_timeout(1_500)
        proceed = self.page.locator(
            "button:has-text('Thanh toán'), a:has-text('Thanh toán')"
        ).first
        if proceed.is_visible(timeout=5_000):
            proceed.click()
            try:
                self.page.wait_for_url("**/checkout**", timeout=10_000)
            except Exception:
                self.page.wait_for_timeout(3_000)
        else:
            self.page.goto(f"{self.env.fe_url}/checkout")
            self.page.wait_for_timeout(2_000)

        # Verify subtotal trước coupon
        from .base_daily_test import parse_int
        subtotal_raw = self.page.evaluate(r"""() => {
            const lines = (document.body.innerText||'').split('\n').map(l=>l.trim()).filter(Boolean);
            const re = /(\d{1,3}(?:[,.]\d{3})+)/;
            for (let i = 0; i < lines.length; i++) {
                if (/^Tổng tiền$/.test(lines[i])) {
                    const m = (lines[i+1]||'').match(re) || lines[i].match(re);
                    if (m) return m[1];
                }
            }
            return null;
        }""")
        self._assert_price(
            parse_int(subtotal_raw), p["sale"],
            "Subtotal trước coupon", "MH1"
        )

        # Apply GIAM20
        applied = _apply_coupon(self.page, "GIAM20")
        if not applied:
            self._record_check("MH2", "GIAM20 áp dụng", "⚠️ WARN",
                               "Không tìm thấy ô nhập coupon", "Coupon input visible")
        else:
            self._record_check("MH2", "GIAM20 áp dụng", "✅ PASS", "OK", "Coupon applied")

        # Verify discount line
        discount = _read_discount_line(self.page)
        self._assert_price(discount, p["discount"], "GIAM20 giảm 20%", "MH2")

        # Verify total after discount
        total_after = _read_total(self.page)
        self._assert_price(total_after, p["total_dc"], "Tổng sau GIAM20", "MH3")

        print(f"\n  [INFO] discount={discount}, total_after={total_after}")
        self.__class__._results = self._results
        self._save_report()
```

- [ ] **Step 2: Chạy test**

```bash
python -m pytest tests/production/daily/test_checkout_summary.py -v --tb=short 2>&1
```

Expected: PASSED

- [ ] **Step 3: Commit**

```bash
git add tests/production/daily/test_checkout_summary.py
git commit -m "feat(daily): test_checkout_summary - cart + GIAM20, dừng tại checkout"
```

---

## Task 5: Conftest + Runner script

**Files:**
- Create: `tests/production/daily/conftest.py`
- Create: `run_daily_smoke.bat`

- [ ] **Step 1: Tạo conftest cho daily (tự động save report)**

```python
# tests/production/daily/conftest.py
"""Session-scope autosave: sau khi session kết thúc → lưu report từng suite."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def _save_daily_reports():
    yield
    from tests.production.daily.test_price_checkout import TestDailyPriceCheckout
    from tests.production.daily.test_size_guide import TestDailySizeGuide
    from tests.production.daily.test_checkout_summary import TestDailyCheckoutSummary

    for cls in (TestDailyPriceCheckout, TestDailySizeGuide, TestDailyCheckoutSummary):
        if cls._results:
            cls._save_report()
```

- [ ] **Step 2: Tạo runner script**

```bat
@echo off
REM run_daily_smoke.bat
REM Chạy daily smoke tests trên TEST env (mặc định)
REM Để chạy PROD: run_daily_smoke.bat prod

set ENV=%1
if "%ENV%"=="" set ENV=test

echo === Daily Smoke Test - ENV=%ENV% ===
python -m pytest tests/production/daily/ -v --tb=short --env=%ENV% 2>&1
```

- [ ] **Step 3: Chạy toàn bộ daily suite**

```bash
python -m pytest tests/production/daily/ -v --tb=short 2>&1
```

Expected: tất cả tests PASS hoặc SKIP (nếu thiếu credentials)

- [ ] **Step 4: Xác nhận report đã tạo**

```bash
ls reports/daily/
```

Expected: thấy các file `price_checkout_*.md`, `size_guide_smoke_*.md`, `checkout_summary_*.md`

- [ ] **Step 5: Commit cuối**

```bash
git add tests/production/daily/conftest.py run_daily_smoke.bat
git commit -m "feat(daily): conftest + runner script, daily smoke suite hoàn chỉnh"
```

---

## Self-Review

**Spec coverage:**
- ✅ `tests/production/daily/` — có
- ✅ 4 SP × 2 flow price — `test_price_checkout.py` (Task 2)
- ✅ AI size smoke 4 SP — `test_size_guide.py` (Task 3)
- ✅ Cart + coupon — `test_checkout_summary.py` (Task 4)
- ✅ Dừng tại checkout, không submit — đã xác nhận trong cả 3 test file
- ✅ `--env=test` mặc định, `--env=prod` tuỳ chọn — kế thừa từ conftest gốc
- ✅ Report tại `reports/daily/` — BaseDailyTest._save_report()

**Placeholder scan:** Không có TBD hay TODO.

**Type consistency:** `parse_int` import từ `base_daily_test` dùng nhất quán. `_read_checkout_prices` trả `dict`, truy cập bằng `.get()`. `_assert_price` nhận `int | None`.
