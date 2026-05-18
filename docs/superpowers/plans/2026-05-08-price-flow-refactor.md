# Price Flow Tests — Refactor POM & BasePriceFlowTest Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Loại bỏ code trùng lặp trong `tests/production/price/` bằng cách đưa popup/cart logic vào `CheckoutPage` POM và các flow chung vào `BasePriceFlowTest`, đảm bảo tất cả test class đều kế thừa từ base.

**Architecture:**
- `CheckoutPage` POM chứa tất cả locator + actions liên quan đến modal popup, cart panel, checkout.
- `BasePriceFlowTest` chứa tất cả helper blocks MH6→MH11 dùng chung.
- Mỗi test file chỉ chứa: constants từ `product_pricing.json`, `_MH_NAMES`, `setup` fixture, và 1 `test_*` method.

**Tech Stack:** Python 3, Playwright sync API, pytest, Page Object Model

---

## Vấn đề cần fix

| Vấn đề | File | Dòng |
|--------|------|------|
| Không kế thừa `BasePriceFlowTest`, duplicate ~600 dòng | `test_pt01_trang_full_price_flow.py` | toàn file |
| `_size_in_qty_section`, `_select_all_sizes_qty*`, `_click_them_vao_gio`, `_open_cart_panel`, `_read_cart_panel_total`, `_click_checkout_from_cart` duplicate ở 5 file | pt01_den, m21_trang, m21_den, m22_den, et002_* | ~120 dòng/file |
| `_wait_checkout_breakdown()` duplicate | m21_trang, m22_den | — |
| Review price JS parsing duplicate | m21_trang, m21_den, m22_den | — |
| MH6 QR + cancel flow duplicate | m21_trang, m22_den (inline), các file khác dùng `_do_mh6_qr` chưa tồn tại | — |
| `_print_summary_table()` không được gọi | m21_den | cuối test |

## File Structure

| File | Thay đổi |
|------|----------|
| `tests/pages/checkout_page.py` | **Thêm** 6 methods: `is_size_in_qty_section`, `select_all_sizes_in_modal`, `click_them_vao_gio`, `open_cart_panel`, `read_cart_panel_total`, `click_checkout_from_cart` |
| `tests/production/price/base_price_flow.py` | **Thêm** 3 helpers: `_wait_checkout_breakdown`, `_read_review_prices`, `_do_mh6_qr` |
| `tests/production/price/test_pt01_trang_full_price_flow.py` | **Refactor** kế thừa `BasePriceFlowTest`, xóa ~700 dòng duplicate |
| `tests/production/price/test_pt01_den_cart_flow.py` | **Xóa** 5 methods duplicate, dùng `self.checkout.*` và `self._do_mh6_qr` |
| `tests/production/price/test_m21_trang_studio_cart_flow.py` | **Xóa** 5 methods duplicate + MH6 inline, dùng POM và base helpers |
| `tests/production/price/test_m21_den_studio_flow.py` | **Xóa** 5 methods duplicate, fix `_print_summary_table()`, dùng `_do_mh6_qr` |
| `tests/production/price/test_m22_den_studio_cart_flow.py` | **Xóa** 5 methods duplicate + MH6/MH7/MH8 inline, dùng POM và base helpers |
| `tests/production/price/test_et002_trang_studio_cart_flow.py` | **Xóa** popup methods duplicate |
| `tests/production/price/test_et002_150_160_studio_cart_flow.py` | **Xóa** popup methods duplicate |

---

## Task 1: Thêm popup/cart POM methods vào CheckoutPage

**Files:**
- Modify: `tests/pages/checkout_page.py`

- [ ] **Step 1: Đọc cuối file checkout_page.py để biết vị trí thêm**

```bash
# Đọc từ dòng 1200 trở đi để tìm cuối file
```

- [ ] **Step 2: Thêm 6 methods vào cuối class `CheckoutPage`**

Append vào cuối `tests/pages/checkout_page.py` (trước dòng cuối cùng, sau method cuối cùng hiện có):

```python
    # ── Popup modal & cart panel helpers (dùng cho price flow tests) ──────────

    _MODAL_SEL = "[class*='max-w-md'][class*='shadow']"

    def is_size_in_qty_section(self, size: str) -> bool:
        """Kiểm tra size đã xuất hiện trong phần SỐ LƯỢNG của popup chưa."""
        return bool(self.page.evaluate(f"""() => {{
            const modal = document.querySelector("{self._MODAL_SEL}") || document;
            const text = modal.innerText || '';
            const idx = text.indexOf('SỐ LƯỢNG');
            if (idx === -1) return false;
            return ('\\n' + text.substring(idx)).includes('\\n{size}\\n');
        }}"""))

    def select_all_sizes_in_modal(self, sizes: list, qty: int = 1) -> list:
        """Chọn tất cả sizes trong popup. qty=2 → click thêm nút + cho mỗi size.
        
        Trả về danh sách sizes đã chọn thành công.
        """
        selected = []
        for size in sizes:
            if self.is_size_in_qty_section(size):
                selected.append(size)
                continue
            ok = self.select_size_by_name(size)
            if not ok:
                ok = bool(self.page.evaluate(f"""() => {{
                    const modal = document.querySelector("{self._MODAL_SEL}") || document;
                    for (const el of modal.querySelectorAll('button')) {{
                        if (el.innerText && el.innerText.trim() === '{size}') {{
                            el.click(); return true;
                        }}
                    }}
                    return false;
                }}"""))
            if ok:
                selected.append(size)
            self.page.wait_for_timeout(300)

        if qty >= 2:
            self.page.wait_for_timeout(500)
            self.page.evaluate(f"""() => {{
                const modal = document.querySelector("{self._MODAL_SEL}") || document;
                for (const btn of modal.querySelectorAll('button')) {{
                    if ((btn.className.includes('w-7') && btn.className.includes('h-7')
                         && btn.querySelector('[class*="lucide-plus"]'))
                        || (btn.querySelector('svg') && btn.innerHTML.includes('lucide-plus'))) {{
                        btn.click();
                    }}
                }}
            }}""")
            self.page.wait_for_timeout(500)

        print(f"  [INFO] select_all_sizes_in_modal: chọn {len(selected)}/{len(sizes)} sizes: {selected}")
        return selected

    def click_them_vao_gio(self) -> bool:
        """Click nút [Thêm vào giỏ hàng] trong popup modal."""
        try:
            ok = bool(self.page.evaluate(r"""() => {
                const els = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
                const btn = els.find(e => e.innerText && /Thêm vào giỏ/i.test(e.innerText));
                if (btn) { btn.click(); return true; }
                return false;
            }"""))
            if ok:
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        return False

    def open_cart_panel(self) -> bool:
        """Mở cart panel slide-in. Thử shopping_cart icon trước, fallback menu → Giỏ hàng."""
        # Cách 1: icon shopping_cart (material icon text)
        try:
            btn = self.page.locator("button:has-text('shopping_cart')").first
            if btn.is_visible(timeout=2000):
                btn.click()
                self.page.wait_for_timeout(2000)
                return True
        except Exception:
            pass
        # Cách 2: menu → Giỏ hàng
        try:
            menu = self.page.locator("button:has-text('menu')").first
            if menu.is_visible(timeout=2000):
                menu.click()
                self.page.wait_for_timeout(800)
            cart_btn = self.page.locator("button:has-text('Giỏ hàng')").first
            if cart_btn.is_visible(timeout=3000):
                cart_btn.click()
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    def read_cart_panel_total(self) -> int | None:
        """Đọc tổng tiền trong cart panel slide-in (label 'Tổng tiền ...')."""
        from .base_page import BasePage
        import re
        raw = self.page.evaluate(r"""() => {
            const panel = document.querySelector('[class*="max-w-md"][class*="shadow"]');
            if (!panel) return null;
            const lines = (panel.innerText || '').split('\n').map(l => l.trim()).filter(Boolean);
            const priceRe = /(\d{1,3}(?:[,.]\d{3})+)/;
            for (let i = 0; i < lines.length; i++) {
                if (/Tổng tiền/i.test(lines[i])) {
                    let m = lines[i].match(priceRe);
                    if (m) return m[1];
                    if (i + 1 < lines.length) {
                        let m2 = lines[i + 1].match(priceRe);
                        if (m2) return m2[1];
                    }
                }
            }
            return null;
        }""")
        if not raw:
            return None
        digits = re.sub(r"[^\d]", "", str(raw))
        return int(digits) if digits else None

    def click_checkout_from_cart(self) -> bool:
        """Click [Thanh toán ngay] trong cart panel để đi sang checkout."""
        selectors = [
            f"{self._MODAL_SEL} button:has-text('Thanh toán ngay')",
            f"{self._MODAL_SEL} button:has-text('Thanh toán')",
            "button:has-text('Thanh toán ngay')",
            "button:has-text('Thanh toán')",
        ]
        for sel in selectors:
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    try:
                        self.page.wait_for_url("**/checkout**", timeout=10000)
                    except Exception:
                        self.page.wait_for_timeout(3000)
                    return True
            except Exception:
                pass
        return False
```

- [ ] **Step 3: Verify không có syntax error**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.pages.checkout_page import CheckoutPage; print('OK')"
```

Kết quả mong đợi: `OK`

- [ ] **Step 4: Commit**

```bash
git add tests/pages/checkout_page.py
git commit -m "feat(pom): add popup/cart panel methods to CheckoutPage"
```

---

## Task 2: Thêm helpers vào BasePriceFlowTest

**Files:**
- Modify: `tests/production/price/base_price_flow.py`

- [ ] **Step 1: Thêm `_wait_checkout_breakdown`, `_read_review_prices`, `_do_mh6_qr` vào `BasePriceFlowTest`**

Append sau method `_do_admin_verify` trong class `BasePriceFlowTest` (trước dòng cuối cùng của class):

```python
    # ── Shared checkout/studio helpers ───────────────────────────────────────

    def _wait_checkout_breakdown(self) -> None:
        """Chờ checkout page render đủ phần Thuế VAT / Phí giao hàng."""
        try:
            self.page.wait_for_function(
                "() => document.body.innerText.includes('Thuế VAT')",
                timeout=15000,
            )
        except Exception:
            self.page.wait_for_timeout(3000)

    def _read_review_prices(self) -> dict:
        """Parse giá Áo, In, Tổng từ màn hình Review (/review).
        
        Trả về dict: { print_total, ao_total, sum_total }
        """
        return self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const prices = [...text.matchAll(/(\d{1,3}(?:[,.]\d{3})+)\s*[đ₫VND]/gi)]
                .map(m => parseInt(m[1].replace(/[^\d]/g, '')));
            let print_total = 0, ao_total = 0, sum_total = 0;
            const priceRe = /(\d{1,3}(?:[,.]\d{3})+)/;
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const next = i + 1 < lines.length ? lines[i + 1] : '';
                const get = l => { const m = l.match(priceRe); return m ? parseInt(m[1].replace(/[^\d]/g,'')) : 0; };
                if (/in DTG|in PET|hình in|phí in/i.test(line))
                    { const v = get(line) || get(next); if (v) print_total += v; }
                if (/áo phông|áo thun|giá áo/i.test(line) && !ao_total)
                    { const v = get(line) || get(next); if (v) ao_total = v; }
                if (/tạm tính|tổng cộng|tổng tiền/i.test(line) && !sum_total)
                    { const v = get(line) || get(next); if (v) sum_total = v; }
            }
            if (!sum_total && prices.length) sum_total = Math.max(...prices);
            if (!ao_total && prices.length) {
                const v = prices.find(p => p >= 80000 && p < sum_total);
                ao_total = v || 0;
            }
            if (!print_total && sum_total > ao_total) print_total = sum_total - ao_total;
            return { print_total, ao_total, sum_total };
        }""")

    def _do_mh6_qr(self, actual_total: int) -> str:
        """MH6 — QR Code: verify số tiền, hủy QR, click Xem đơn hàng.
        
        Trả về order_code (từ URL) hoặc chuỗi rỗng.
        """
        import re as _re
        print(f"\n  ── MH6: QR Code ──────────────────────────────────────────")
        self._shot("MH6_1", "qr_screen")
        qr_visible = self.checkout.is_qr_visible(timeout=10000)
        order_code = ""

        if not qr_visible:
            print(f"  [WARN] MH6: QR không hiển thị — URL: {self.page.url}")
            return order_code

        qr_amt = (self.checkout.read_qr_note_amount()
                  or self.checkout.read_qr_amount()
                  or parse_int(self.page.evaluate(
                      r"() => document.body.innerText.match(/thanh to[áa]n\s+(\d[\d,.]*\d)/i)?.[1]"
                  )))
        self._assert_price(qr_amt, actual_total, "MH6 Số tiền QR / lưu ý")
        print(f"  [PASS] MH6: QR amount OK")

        self.page.on("dialog", lambda d: d.accept())
        self.checkout.click_cancel_qr()
        self.page.wait_for_timeout(3000)
        self.checkout.confirm_cancel_dialog()
        self.page.wait_for_timeout(2000)
        self._shot("MH6_2", "qr_cancelled")
        self.checkout.click_view_order()
        self.page.wait_for_timeout(2000)

        if "payos" in self.page.url or "qr" in self.page.url.lower():
            self.checkout.goto("/my-orders")
            self.page.wait_for_timeout(2000)

        m = _re.search(r"orderCode=([\w-]+)", self.page.url)
        order_code = m.group(1) if m else ""
        print(f"  [INFO] MH6: order_code = {order_code}")
        return order_code
```

- [ ] **Step 2: Verify không có syntax error**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.base_price_flow import BasePriceFlowTest; print('OK')"
```

Kết quả mong đợi: `OK`

- [ ] **Step 3: Commit**

```bash
git add tests/production/price/base_price_flow.py
git commit -m "feat(base): add _wait_checkout_breakdown, _read_review_prices, _do_mh6_qr to BasePriceFlowTest"
```

---

## Task 3: Refactor test_pt01_trang_full_price_flow.py

**Files:**
- Modify: `tests/production/price/test_pt01_trang_full_price_flow.py`

File này (1.280 dòng) cần được viết lại hoàn toàn để kế thừa `BasePriceFlowTest`. Các helpers trùng lặp cần xóa: `_login`, `_shot`, `_assert_price`, `_record`, `_record_check`, `_text_width`, `_pad_cell`, `_print_summary_table`, `_save_summary_report`. Toàn bộ MH10 Admin inline cần thay bằng `self._do_admin_verify(...)`.

- [ ] **Step 1: Viết lại file với kế thừa BasePriceFlowTest**

Nội dung mới của `tests/production/price/test_pt01_trang_full_price_flow.py`:

```python
"""
PT01 Trắng — Full price flow (MH1 → MH10/Admin).

Sản phẩm: PT01 Áo Phông Cá Tính / Màu Trắng / Size M / Qty 1 / Không in
Giá:
  salePrice     = 189.000đ   originalPrice = 227.000đ
  VAT 8%        = 15.120đ    Phí GH        = 20.000đ
  Tổng TT       = 224.120đ   GIAM20 (20%)  → Tổng = 183.296đ
"""
import json
import os
import re

import pytest

from .base_price_flow import BasePriceFlowTest


def _pricing_data() -> dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "data", "product_pricing.json",
    )
    with open(p, encoding="utf-8") as f:
        return json.load(f)


_DATA      = _pricing_data()
_PRODUCT   = next(x for x in _DATA["products"] if x["code"] == "PT01")
_VARIANT   = _PRODUCT["variants"][0]
_SALE      = _VARIANT["salePrice"]        # 189_000
_ORIGINAL  = _VARIANT["originalPrice"]   # 227_000
_SHIPPING  = _DATA["global"]["shipping_fee"]          # 20_000
_VAT_RATE  = _DATA["global"]["VAT_rate"]              # 0.08
_GIAM20    = _DATA["discount_codes"]["GIAM20"]["value"]  # 0.20
_TOLERANCE = 1_000

_VAT_NO_DC    = int(_SALE * _VAT_RATE)
_TOTAL_NO_DC  = _SALE + _VAT_NO_DC + _SHIPPING
_AFTER_DC     = int(_SALE * (1 - _GIAM20))
_VAT_DC       = int(_AFTER_DC * _VAT_RATE)
_TOTAL_DC     = _AFTER_DC + _VAT_DC + _SHIPPING
_DISCOUNT_AMT = int(_SALE * _GIAM20)

_SLUG  = "ao-phong-ca-tinh"
_NAME  = "Áo Phông Cá Tính"
_COLOR = "Trắng"
_SIZE  = "M"


class TestPT01TrangFullPriceFlow(BasePriceFlowTest):
    """PT01 Trắng — full flow MH1→MH10 (Mua ngay, không in)."""

    _MH_NAMES = {
        "Login": "Đăng nhập",
        "MH1":   "Product Listing",
        "MH2":   "Product Detail",
        "MH3":   "Studio",
        "MH4":   "Popup Mua ngay",
        "MH5":   "Checkout",
        "MH6":   "QR Code",
        "MH7":   "Order (sau hủy QR)",
        "MH8":   "Đơn hàng của tôi",
        "MH9":   "Chi tiết đơn hàng",
        "MH10":  "Admin — Chi tiết đơn",
    }
    _REPORT_TITLE = "PT01 Áo Phông Cá Tính (Trắng / Mua ngay / MH1→MH10)"
    TOLERANCE = _TOLERANCE

    @pytest.fixture(autouse=True)
    def setup(self, home_page, product_list_page, product_detail_page,
              studio_page, auth_page, checkout_page, env):
        self.home     = home_page
        self.listing  = product_list_page
        self.detail   = product_detail_page
        self.studio   = studio_page
        self.auth     = auth_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = home_page.page
        self.tc       = "PT01_TRANG"
        self.root     = "production"
        self.domain   = "pt01_trang_flow"
        self._results = []

    # ── Main test ─────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_full_price_flow_mua_ngay(self):
        """PT01 Trắng — full flow Mua ngay qua MH1→MH10."""
        tc = self.tc
        self._login()

        # ── MH1: Product Listing ──────────────────────────────────────────────
        print(f"\n  ── MH1: Product Listing ──────────────────────────────────")
        self.listing.navigate()
        self._shot("MH1_1", "listing_page")
        if self.listing.is_product_card_visible(_NAME):
            self._assert_price(self.listing.read_listing_sale_price(_NAME),     _SALE,     "MH1 Giá sale listing")
            self._assert_price(self.listing.read_listing_original_price(_NAME), _ORIGINAL, "MH1 Giá gốc listing (gạch ngang)")
            self._shot("MH1_2", "listing_prices")
            print(f"  [PASS] MH1: OK")
        else:
            self._record_check("MH1", "MH1 Product card", "⚠️ WARN", "không tìm thấy", _NAME)

        # ── MH2: Product Detail ───────────────────────────────────────────────
        print(f"\n  ── MH2: Product Detail ───────────────────────────────────")
        self.detail.navigate(_SLUG)
        self._shot("MH2_1", "detail_page")
        name = self.detail.read_product_name()
        self._record_check("MH2", "MH2 Tên sản phẩm",
                           "✅ PASS" if (_NAME.split()[-1].lower() in (name or "").lower()) else "⚠️ WARN",
                           name or "N/A", _NAME)
        self._assert_price(self.detail.read_sale_price(),     _SALE,     "MH2 Giá sale default (Trắng)")
        self._assert_price(self.detail.read_original_price(), _ORIGINAL, "MH2 Giá gốc gạch ngang")
        self._shot("MH2_2", "detail_prices_default")

        if self.detail.select_color("Đen"):
            self.page.wait_for_timeout(800)
            self._shot("MH2_3", "detail_color_den")
        self.detail.select_color(_COLOR)
        self.page.wait_for_timeout(500)
        print(f"  [PASS] MH2: OK")

        # ── MH3: Studio (chỉ verify navigate, không thiết kế) ────────────────
        print(f"\n  ── MH3: Studio ───────────────────────────────────────────")
        studio_ok = self.detail.click_thiet_ke_hinh_in()
        if studio_ok:
            self.page.wait_for_timeout(2000)
            self.studio.accept_terms(tc)
            canvas_ok = self.studio.is_canvas_visible()
            self._shot("MH3_1", "studio_from_detail")
            self._record_check("MH3", "MH3 Studio canvas",
                               "✅ PASS" if canvas_ok else "⚠️ WARN",
                               "visible" if canvas_ok else "not found", "canvas visible")
            self.page.go_back()
            try:
                self.page.wait_for_url(f"**/{_SLUG}**", timeout=10000)
            except Exception:
                self.detail.navigate(_SLUG)
            self.page.wait_for_timeout(1500)
            self.detail.select_color(_COLOR)
            self.page.wait_for_timeout(500)
        else:
            self._record_check("MH3", "MH3 Studio", "⚠️ WARN", "button không tìm thấy", "Thiết kế hình in")
        self._shot("MH3_2", "back_to_detail")

        # ── MH4: Popup Mua ngay ───────────────────────────────────────────────
        print(f"\n  ── MH4: Popup Mua ngay ───────────────────────────────────")
        if not self.detail.click_mua_ngay():
            pytest.skip(f"SKIP MH4 ({tc}): Không mở được popup Mua ngay")
        self.page.wait_for_timeout(1500)

        if self.checkout.is_buynow_modal_visible(timeout=5000):
            self._shot("MH4_1", "buynow_modal")
            modal_name  = self.checkout.read_buynow_modal_product_name()
            modal_price = self.checkout.read_buynow_modal_price()
            btn_price   = self.checkout.read_buynow_button_price()
            self._record_check("MH4", "MH4 Tên sản phẩm",
                               "✅ PASS" if (_NAME.split()[-1] in (modal_name or "")) else "⚠️ WARN",
                               modal_name or "N/A", _NAME)
            self._assert_price(modal_price, _SALE, "MH4 Đơn giá trong popup")
            self._assert_price(btn_price,   _SALE, "MH4 Giá button Thanh toán ngay")

            self.checkout.select_size_by_name(_SIZE)
            self.page.wait_for_timeout(800)
            self._assert_price(self.checkout.read_buynow_modal_price(), _SALE, f"MH4 Giá sau chọn size {_SIZE}")
            self._shot("MH4_2", f"buynow_size_{_SIZE}")
            print(f"  [PASS] MH4: OK")
        else:
            print(f"  [WARN] MH4: Modal không detect — tiếp tục")

        # ── Navigate sang Checkout ────────────────────────────────────────────
        if not self.checkout.click_thanh_toan_ngay():
            self.detail.goto("/checkout")
        try:
            self.page.wait_for_url("**/checkout**", timeout=10000)
        except Exception:
            self.page.wait_for_timeout(3000)

        # ── MH5: Checkout ─────────────────────────────────────────────────────
        print(f"\n  ── MH5: Checkout ─────────────────────────────────────────")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self._shot("MH5_1", "checkout_page")

        subtotal = self.checkout.read_checkout_subtotal()
        vat      = self.checkout.read_checkout_vat()
        shipping = self.checkout.read_checkout_shipping()
        total    = self.checkout.read_checkout_total()
        btn_p    = self.checkout.read_payment_button_price()

        self._assert_price(subtotal, _SALE,        "MH5 Tổng tiền")
        self._assert_price(vat,      _VAT_NO_DC,   "MH5 Thuế VAT (8%)")
        self._assert_price(shipping, _SHIPPING,    "MH5 Phí giao hàng")
        self._assert_price(total,    _TOTAL_NO_DC, "MH5 Tổng thanh toán")
        self._assert_price(btn_p,    _TOTAL_NO_DC, "MH5 Giá trên button Thanh toán")

        # Apply GIAM20
        dc_ok = False
        self.checkout.apply_discount_code("GIAM20")
        self.page.wait_for_timeout(2000)
        self._shot("MH5_2", "checkout_after_GIAM20")

        discount_amt = self.checkout.read_checkout_discount()
        if discount_amt and discount_amt > 0:
            dc_ok = True
            self._assert_price(discount_amt, _DISCOUNT_AMT, "MH5 Giảm giá GIAM20 (20%)")
            self._assert_price(self.checkout.read_checkout_total(), _TOTAL_DC, "MH5 Tổng TT sau GIAM20")
            print(f"  [PASS] MH5: GIAM20 OK — giảm {discount_amt:,}đ")
        else:
            print(f"  [INFO] MH5: GIAM20 không áp — tiếp tục với giá gốc")

        actual_total_paid = self.checkout.read_payment_button_price() or _TOTAL_NO_DC
        print(f"  [INFO] MH5: Giá thực tế = {actual_total_paid:,}đ")

        # Đọc size/qty thực tế từ UI
        checkout_info = self.page.evaluate(r"""() => {
            const m = (document.body.innerText || '').match(/([XSML234]+)\s*[×x]\s*(\d+)/i);
            return { size: m ? m[1] : '', qty: m ? parseInt(m[2]) : 1 };
        }""") or {}
        order_info = {
            "product_name": _NAME,
            "color": _COLOR,
            "size": checkout_info.get("size", _SIZE),
            "qty":  checkout_info.get("qty", 1),
        }

        # Điền thông tin giao hàng
        self.checkout.fill_guest_shipping_info(
            "Test Tryonic", "0912345678",
            "123 Đường Test, Quận 1, TP. Hồ Chí Minh",
            tc_id=tc,
        )
        self.checkout.fill_tax_code("012345678901", tc_id=tc)
        self._shot("MH5_3", "checkout_filled")
        self.checkout.click_checkout_payment()
        self.page.wait_for_timeout(3000)

        # ── MH6 → MH9 dùng base helpers ──────────────────────────────────────
        order_code = self._do_mh6_qr(actual_total_paid)
        self._do_mh7_order(actual_total_paid, _SHIPPING)
        self._do_mh8_my_orders(actual_total_paid)
        self._do_mh9_order_detail(
            order_info=order_info,
            actual_total_paid=actual_total_paid,
            shipping=_SHIPPING,
            dc_ok=dc_ok,
            discount_amount=_DISCOUNT_AMT if dc_ok else None,
        )

        # ── MH10: Admin ───────────────────────────────────────────────────────
        self._do_admin_verify(
            mh_label="MH10",
            order_code=order_code,
            order_info=order_info,
            actual_total_paid=actual_total_paid,
            shipping=_SHIPPING,
        )

        print(f"\n  [PASS] {tc}: MH1→MH10 ALL PASSED")
        self._print_summary_table()

    # ── MH10-Cart flow (riêng) ────────────────────────────────────────────────

    @pytest.mark.production
    def test_MH10_cart_price(self):
        """PT01 Trắng — MH10: Verify giá trong Giỏ hàng sau Thêm vào giỏ."""
        tc = self.tc + "_MH10"
        self._login()

        print(f"\n  ── MH2 → MH10: Add to cart flow ─────────────────────────")
        self.detail.navigate(_SLUG)
        self.page.wait_for_timeout(1500)
        self.detail.select_color(_COLOR)
        self.page.wait_for_timeout(500)
        self.checkout.select_size_by_name(_SIZE)

        if not self.detail.click_add_to_cart():
            pytest.skip(f"SKIP MH10 ({tc}): Không click được button 'Thêm vào giỏ'")
        self.page.wait_for_timeout(2000)
        self._shot("MH10_add", "add_to_cart_result")

        self.checkout.navigate_cart()
        self.page.wait_for_timeout(1500)
        self._shot("MH10_1", "cart_page")

        self._assert_price(self.checkout.read_cart_item_price(), _SALE, "MH10 Giá item PT01 Trắng trong giỏ")
        self._assert_price(self.checkout.read_cart_total(),      _SALE, "MH10 Tổng giỏ hàng")
        self._shot("MH10_2", "cart_prices")
        print(f"  [PASS] MH10: Cart price OK")
        self._print_summary_table()
```

- [ ] **Step 2: Verify import và syntax**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.test_pt01_trang_full_price_flow import TestPT01TrangFullPriceFlow; print('OK')"
```

Kết quả mong đợi: `OK`

- [ ] **Step 3: Commit**

```bash
git add tests/production/price/test_pt01_trang_full_price_flow.py
git commit -m "refactor(price): PT01_TRANG kế thừa BasePriceFlowTest, xóa ~700 dòng duplicate"
```

---

## Task 4: Xóa popup methods duplicate khỏi test_pt01_den_cart_flow.py

**Files:**
- Modify: `tests/production/price/test_pt01_den_cart_flow.py`

- [ ] **Step 1: Xóa 5 methods trong class, thay bằng `self.checkout.*`**

Xóa toàn bộ các methods sau khỏi class `TestPT01DenCartFlow` (dòng 110–263):
- `_MODAL_SEL = ...`
- `_size_in_qty_section(self, size)`
- `_select_all_sizes_qty2(self)`
- `_click_them_vao_gio(self)`
- `_open_cart_panel(self)`
- `_read_cart_panel_text(self)`
- `_read_cart_panel_total(self)`
- `_click_checkout_from_cart(self)`

Thay thế tất cả call sites trong `test_full_price_flow_gio_hang`:
- `self._select_all_sizes_qty2()` → `self.checkout.select_all_sizes_in_modal(_ALL_SIZES, qty=2)`
- `self._click_them_vao_gio()` → `self.checkout.click_them_vao_gio()`
- `self._open_cart_panel()` → `self.checkout.open_cart_panel()`
- `self._read_cart_panel_total()` → `self.checkout.read_cart_panel_total()`
- `self._click_checkout_from_cart()` → `self.checkout.click_checkout_from_cart()`

Cũng thay `_read_cart_panel_text()` bằng `self.page.evaluate("() => document.body.innerText || ''")`

- [ ] **Step 2: Verify**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.test_pt01_den_cart_flow import TestPT01DenCartFlow; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add tests/production/price/test_pt01_den_cart_flow.py
git commit -m "refactor(price): PT01_DEN dùng CheckoutPage POM thay cho duplicate popup methods"
```

---

## Task 5: Refactor test_m21_trang_studio_cart_flow.py

**Files:**
- Modify: `tests/production/price/test_m21_trang_studio_cart_flow.py`

- [ ] **Step 1: Xóa 5 methods duplicate**

Xóa khỏi class `TestM21TrangStudioCartFlow`:
- `_size_in_qty_section(self, size)`
- `_select_all_sizes_qty1(self)`
- `_click_them_vao_gio(self)`
- `_open_cart_panel(self)`
- `_read_cart_panel_total(self)`
- `_click_checkout_from_cart(self)`
- `_wait_checkout_breakdown(self)`

Thay call sites:
- `self._select_all_sizes_qty1()` → `sizes_selected = self.checkout.select_all_sizes_in_modal(_ALL_SIZES, qty=1); qty_actual = 1`
- `self._click_them_vao_gio()` → `self.checkout.click_them_vao_gio()`
- `self._open_cart_panel()` → `self.checkout.open_cart_panel()`
- `self._read_cart_panel_total()` → `self.checkout.read_cart_panel_total()`
- `self._click_checkout_from_cart()` → `self.checkout.click_checkout_from_cart()`
- `self._wait_checkout_breakdown()` → `self._wait_checkout_breakdown()` (**đã có trong base**)

- [ ] **Step 2: Thay MH6 inline (dòng 624–641) bằng `_do_mh6_qr`**

Xóa block MH6 inline và thay:
```python
order_code = self._do_mh6_qr(actual_total)
```

- [ ] **Step 3: Verify**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.test_m21_trang_studio_cart_flow import TestM21TrangStudioCartFlow; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add tests/production/price/test_m21_trang_studio_cart_flow.py
git commit -m "refactor(price): M21_TRANG dùng POM methods và _do_mh6_qr từ base"
```

---

## Task 6: Refactor test_m21_den_studio_flow.py

**Files:**
- Modify: `tests/production/price/test_m21_den_studio_flow.py`

- [ ] **Step 1: Xóa 5 methods duplicate**

Xóa:
- `_MODAL_SEL`
- `_size_in_qty_section(self, size)`
- `_select_all_sizes_qty2(self)` (trả về `selected, qty_actual, n_plus`)
- `_click_them_vao_gio(self)`
- `_open_cart_panel(self)`
- `_read_cart_panel_total(self)`
- `_click_checkout_from_cart(self)`
- `_get_review_prices(self)` (thay bằng `self._read_review_prices()` từ base)

Thay call sites bằng `self.checkout.*` và `self._read_review_prices()`.

`_select_all_sizes_qty2` trả về `(selected, qty_actual, n_plus)`. Sau refactor:
```python
sizes_selected = self.checkout.select_all_sizes_in_modal(_ALL_SIZES, qty=2)
n_sel = len(sizes_selected)
qty_actual = 2
```

- [ ] **Step 2: Thay MH6 inline bằng `_do_mh6_qr`**

Trong block MH6 (khoảng dòng 649–671), thay toàn bộ bằng:
```python
order_code = self._do_mh6_qr(actual_total)
```

- [ ] **Step 3: Fix cuối test — thay `_save_summary_report` bằng `_print_summary_table`**

Xóa đoạn cuối:
```python
passed = sum(1 for r in self._results if 'PASS' in r['status'])
...
try:
    self._save_summary_report(passed, failed, warned, info_count)
except Exception:
    pass
```

Thay bằng:
```python
self._print_summary_table()
```

- [ ] **Step 4: Verify**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.test_m21_den_studio_flow import TestM21DenStudioCartFlow; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add tests/production/price/test_m21_den_studio_flow.py
git commit -m "refactor(price): M21_DEN dùng POM methods, fix _print_summary_table, dùng _do_mh6_qr"
```

---

## Task 7: Refactor test_m22_den_studio_cart_flow.py

**Files:**
- Modify: `tests/production/price/test_m22_den_studio_cart_flow.py`

- [ ] **Step 1: Xóa 6 methods duplicate**

Xóa:
- `_size_in_qty_section(self, size)`
- `_select_all_sizes_qty1(self)`
- `_click_them_vao_gio(self)`
- `_open_cart_panel(self)`
- `_read_cart_panel_total(self)`
- `_click_checkout_from_cart(self)`
- `_wait_checkout_breakdown(self)`

Thay call sites bằng `self.checkout.*` và `self._wait_checkout_breakdown()` từ base.

- [ ] **Step 2: Thay MH6, MH7, MH8 inline bằng base helpers**

Xóa toàn bộ block MH6 (dòng ~579–593), MH7 (596–604), MH8 (608–630).

Thay bằng:
```python
order_code = self._do_mh6_qr(actual_total)
self._do_mh7_order(actual_total, _SHIPPING)
self._do_mh8_my_orders(actual_total)
```

- [ ] **Step 3: Verify**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "from tests.production.price.test_m22_den_studio_cart_flow import TestM22DenStudioCartFlow; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add tests/production/price/test_m22_den_studio_cart_flow.py
git commit -m "refactor(price): M22_DEN dùng POM methods và base MH6/MH7/MH8 helpers"
```

---

## Task 8: Refactor ET002 files

**Files:**
- Modify: `tests/production/price/test_et002_trang_studio_cart_flow.py`
- Modify: `tests/production/price/test_et002_150_160_studio_cart_flow.py`

- [ ] **Step 1: Xóa popup methods duplicate trong test_et002_trang_studio_cart_flow.py**

Tương tự Task 4–7: xóa `_size_in_qty_section`, `_select_all_sizes_*`, `_click_them_vao_gio`, `_open_cart_panel`, `_read_cart_panel_total`, `_click_checkout_from_cart`. Thay bằng `self.checkout.*`.

- [ ] **Step 2: Xóa popup methods duplicate trong test_et002_150_160_studio_cart_flow.py**

Tương tự Step 1.

- [ ] **Step 3: Verify cả 2 file**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -c "
from tests.production.price.test_et002_trang_studio_cart_flow import TestET002TrangStudioCartFlow
from tests.production.price.test_et002_150_160_studio_cart_flow import TestET002150160StudioCartFlow
print('OK')
"
```

- [ ] **Step 4: Commit**

```bash
git add tests/production/price/test_et002_trang_studio_cart_flow.py tests/production/price/test_et002_150_160_studio_cart_flow.py
git commit -m "refactor(price): ET002 files dùng CheckoutPage POM methods"
```

---

## Task 9: Smoke test — chạy collect để verify không có lỗi import

- [ ] **Step 1: Chạy pytest collect**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -m pytest tests/production/price/ --collect-only -q 2>&1 | head -40
```

Kết quả mong đợi: Danh sách test được collect, không có lỗi `ImportError` hoặc `SyntaxError`.

- [ ] **Step 2: Chạy 1 test smoke**

```bash
cd /d/TEST_STUDIO/shop_tryonic_ai && python -m pytest tests/production/price/test_price_verification.py::TestListingPriceVerification::test_LISTING_001_PT01 -v --env=test 2>&1 | tail -20
```

- [ ] **Step 3: Final commit nếu cần**

```bash
git add -A
git commit -m "chore(price): final cleanup sau refactor price flow tests"
```

---

## Kết quả mong đợi

| Metric | Trước | Sau |
|--------|-------|-----|
| Tổng dòng code `tests/production/price/` | ~3.000 dòng | ~1.400 dòng |
| Methods duplicate trong test files | ~50 methods × 5 files | 0 |
| Test files kế thừa `BasePriceFlowTest` | 6/7 | 7/7 |
| POM methods trong `checkout_page.py` | không có | +6 methods |
| Base helpers `base_price_flow.py` | 0 | +3 methods |
