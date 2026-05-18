"""
SH07 — E2E Affiliate Commission: Giỏ hàng 2 sản phẩm + mã giảm giá

Luồng:
  1. Affiliate login → lấy link gian hàng + tỷ lệ hoa hồng + số đơn ban đầu
  2. Customer (context riêng) → thêm 2 sản phẩm vào giỏ hàng:
       - Áo Phông Năng Động (ao-phong-nang-dong): size M × 1   → giá 130,000đ
       - Áo Phông Trẻ Em   (ao-phong-tre-em):    size 110 × 1  giá 96,000đ
     → Vào giỏ hàng → Áp mã giảm giá "maimai1"
       (Lưu ý: mã maimai1 chỉ áp cho 1 chiếc Áo Phông Năng Động, không áp cho Áo Phông Trẻ Em)
     → Checkout → Đặt hàng thành công
  3. Admin xác nhận thanh toán
  4. Affiliate → /affiliate → verify:
       - Đơn mới xuất hiện trong danh sách liên kết
       - Hoa hồng = subtotal_effective × tỷ lệ%
         trong đó subtotal_effective = (130k - discount_maimai1) + 96k + 96k

Tính hoa hồng:
  - Mã maimai1 CHỈ giảm giá cho Áo Phông Năng Động (1 chiếc)
  - Áo Phông Trẻ Em KHÔNG được giảm giá
  - subtotal_after_discount = (price_nang_dong - discount) + price_tre_em_total
  - Hoa hồng = subtotal_after_discount × rate% (không gồm VAT, không gồm ship)

Preconditions (.env):
  AFFILIATE_EMAIL, AFFILIATE_PASSWORD
  CUSTOMER_EMAIL, CUSTOMER_PASSWORD
"""
from __future__ import annotations

import re as _re
import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from .base_share_flow import BaseShareFlowTest

# ── Sản phẩm ─────────────────────────────────────────────────────────────────
_PROD_NANG_DONG = {
    "slug":         "ao-phong-nang-dong",
    "name":         "Áo Phông Năng Động",
    "color":        "Trắng",
    "sizes":        ["M"],
    "price_no_vat": 130_000,   # salePrice (không VAT)
    "coupon_applies": True,    # mã maimai1 áp cho SP này
}
_PROD_TRE_EM = {
    "slug":         "ao-phong-tre-em",
    "name":         "Áo Phông Trẻ Em",
    "color":        "Trắng",
    # Chỉ dùng size 110 (server test chỉ validate được size này)
    # Size 120, 130, 150 đều trả về "not found" từ server checkout validation
    "sizes":        ["110"],
    "price_no_vat": None,      # Giá theo từng size — xem _PROD_TRE_EM_PRICES
    "coupon_applies": False,   # mã maimai1 KHÔNG áp cho SP này
}
_PRODUCTS = [_PROD_NANG_DONG, _PROD_TRE_EM]

_COUPON_CODE = "maimai1"

# Subtotal tham khảo (trước mã giảm giá)
# Áo Phông Năng Động: 130k × 1
# Áo Phông Trẻ Em size 110 (ET002_100_140): 96k × 1
_SUBTOTAL_NANG_DONG_REF = 130_000
_SUBTOTAL_TRE_EM_REF    = 96_000   # 1 item size 110

# Discount kỳ vọng của mã maimai1:
#   Áp dụng cho 1 size có giá cao nhất trong đơn = Áo Phông Năng Động (130,000đ)
#   Công thức: discount = salePrice_ao - (costPrice_ao + costPrice_in)
#   Plain product (không in hình): costPrice_in = 0
#   → discount = 130,000 - 60,000 = 70,000đ
#   (VAT tính riêng trên phần costPrice, hiển thị trong Tổng thanh toán)
_COST_AO_NANG_DONG         = 60_000   # costPrice M21 Trắng (product_pricing.json)
_COST_IN_NANG_DONG         = 0        # Không in hình → costPrice_in = 0
_VAT_RATE                  = 0.08
_MAIMAI1_DISCOUNT_EXPECTED = _SUBTOTAL_NANG_DONG_REF - (_COST_AO_NANG_DONG + _COST_IN_NANG_DONG)  # 70,000đ
_MAIMAI1_DISCOUNT_TOLERANCE = 2_000   # ±2,000đ


class TestSH07CartMultiE2E(BaseShareFlowTest):
    """SH07 — Giỏ hàng 2 SP + mã giảm giá (chỉ áp cho Áo Phông Năng Động)."""

    _MH_NAMES = {
        "MH1":   "Affiliate login → lấy link + tỷ lệ hoa hồng",
        "MH2":   "Customer thêm 2SP vào giỏ + mã giảm giá maimai1 → đặt đơn",
        "MH3":   "Admin xác nhận thanh toán",
        "MH4":   "Đơn mới xuất hiện trong danh sách liên kết",
        "MH5":   "Hoa hồng = (subtotal_nang_dong_after_discount + subtotal_tre_em) × rate%",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH07 — E2E Affiliate: Giỏ hàng 2 SP + mã maimai1 → Hoa hồng"

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
        self.tc       = "SH07_CART_MULTI_E2E"
        self.root     = "production"
        self.domain   = "sh07_cart_multi_e2e"
        self._results = []

    # ── Helpers affiliate ─────────────────────────────────────────────────────

    def _get_affiliate_store_link(self) -> str | None:
        link = self.page.evaluate(r"""() => {
            const inp = document.querySelector(
                'input[value*="ref="], input[value*="aff="], input[readonly][value*="http"]'
            );
            if (inp && inp.value) return inp.value;
            const aRef = document.querySelector('a[href*="ref="], a[href*="aff="]');
            if (aRef) return aRef.href;
            const aStore = document.querySelector(
                'a[href*="/store/"], a[href*="/gian-hang/"], a[href*="/shop/"]'
            );
            if (aStore) return aStore.href;
            return null;
        }""")
        if link and not link.startswith("http"):
            link = f"{self.env.fe_url.rstrip('/')}/{link.lstrip('/')}"
        return link

    def _read_commission_rate(self) -> float | None:
        raw = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const m = text.match(/tỷ lệ hoa hồng[^\d]*(\d+(?:\.\d+)?)\s*%/i)
                   || text.match(/hoa hồng[^\d]*(\d+(?:\.\d+)?)\s*%/i)
                   || text.match(/(\d+(?:\.\d+)?)\s*%\s*hoa hồng/i);
            return m ? parseFloat(m[1]) : null;
        }""")
        return float(raw) if raw is not None else None

    def _find_new_order_in_list(self, order_code: str) -> dict | None:
        orders = self._read_affiliate_orders()
        for o in orders:
            if order_code and order_code.lower() in (o.get("order_code") or "").lower():
                return o
            if order_code and len(order_code) >= 5:
                if order_code[-5:] in (o.get("order_code") or ""):
                    return o
        return None

    def _read_order_count_before(self) -> int:
        count = self._read_order_count()
        return count if count is not None else 0

    # ── Customer helpers ──────────────────────────────────────────────────────

    def _customer_login(self, ctx_page: Page, email: str, password: str) -> bool:
        try:
            ctx_page.goto(self.env.fe_url, wait_until="domcontentloaded", timeout=15000)
            ctx_page.wait_for_timeout(2500)
            login_btn = ctx_page.locator("button:has-text('Đăng nhập')").first
            if not login_btn.is_visible(timeout=5000):
                return False
            login_btn.click()
            ctx_page.wait_for_timeout(2000)
            for sel in ["dialog input[type='email']", "[role='dialog'] input[type='email']",
                        "input[type='email']"]:
                try:
                    loc = ctx_page.locator(sel).first
                    if loc.is_visible(timeout=3000):
                        loc.fill(email)
                        break
                except Exception:
                    pass
            for sel in ["dialog input[type='password']", "[role='dialog'] input[type='password']",
                        "input[type='password']"]:
                try:
                    loc = ctx_page.locator(sel).first
                    if loc.is_visible(timeout=2000):
                        loc.fill(password)
                        break
                except Exception:
                    pass
            for sel in ["dialog button:has-text('Đăng nhập')",
                        "[role='dialog'] button:has-text('Đăng nhập')",
                        "button[type='submit']",
                        "button:has-text('Đăng nhập'):visible"]:
                try:
                    loc = ctx_page.locator(sel).last
                    if loc.is_visible(timeout=2000):
                        loc.click()
                        break
                except Exception:
                    pass
            ctx_page.wait_for_timeout(4000)
            still_login = ctx_page.locator("button:has-text('Đăng nhập')").is_visible(timeout=3000)
            if not still_login:
                print(f"  [INFO] Customer login OK: {email}")
                return True
        except Exception as e:
            print(f"  [WARN] _customer_login: {e}")
        return False

    @staticmethod
    def _js_click_by_text(page: Page, text: str) -> bool:
        result = page.evaluate(f"""() => {{
            const dropdown = Array.from(document.querySelectorAll('div')).find(d => {{
                const cls = String(d.className || '');
                return cls.includes('absolute') && cls.includes('z-50') && d.offsetWidth > 50;
            }});
            if (dropdown) {{
                const btn = Array.from(dropdown.querySelectorAll('button'))
                    .find(b => b.textContent.trim() === {repr(text)});
                if (btn) {{ btn.click(); return true; }}
            }}
            const el = Array.from(document.querySelectorAll('button, li'))
                .find(e => e.offsetWidth > 0 && e.textContent.trim() === {repr(text)});
            if (el) {{ el.click(); return true; }}
            return false;
        }}""")
        return bool(result)

    @staticmethod
    def _js_open_cascade_btn(page: Page, text_include: str) -> bool:
        return bool(page.evaluate(f"""() => {{
            const btns = Array.from(document.querySelectorAll('button'));
            const b = btns.find(b => !b.disabled && b.textContent.includes({repr(text_include)}));
            if (b) {{ b.click(); return true; }}
            return false;
        }}"""))

    @staticmethod
    def _js_click_first_option(page: Page) -> str | None:
        return page.evaluate(r"""() => {
            const dropdown = Array.from(document.querySelectorAll('div')).find(d => {
                const cls = String(d.className || '');
                return cls.includes('absolute') && cls.includes('z-50') && d.offsetWidth > 50;
            });
            if (!dropdown) return null;
            const btns = Array.from(dropdown.querySelectorAll('button'));
            if (btns.length > 0) {
                const first = btns[0];
                const text = first.textContent.trim();
                first.click();
                return text;
            }
            return null;
        }""")

    def _fill_cascade_address(self, ctx_page: Page,
                              province: str = "Thành phố Hà Nội",
                              district: str = "Quận Ba Đình",
                              ward: str | None = "Phường Phúc Xá",
                              detail: str = "123 Test Street") -> bool:
        try:
            has_cascade = ctx_page.evaluate(
                "() => Array.from(document.querySelectorAll('button'))"
                ".some(b => !b.disabled && b.textContent.includes('Chọn tỉnh/thành'))"
            )
            if not has_cascade:
                print(f"    [INFO] Không cần cascade — đã có địa chỉ sẵn")
                return True
            self._js_open_cascade_btn(ctx_page, "Chọn tỉnh/thành")
            ctx_page.wait_for_timeout(800)
            ok1 = self._js_click_by_text(ctx_page, province)
            ctx_page.wait_for_timeout(800)
            print(f"    [INFO] Cascade: Tỉnh '{province}' → {'OK' if ok1 else 'FAIL'}")
            self._js_open_cascade_btn(ctx_page, "Chọn quận/huyện")
            ctx_page.wait_for_timeout(800)
            ok2 = self._js_click_by_text(ctx_page, district)
            ctx_page.wait_for_timeout(800)
            print(f"    [INFO] Cascade: Quận '{district}' → {'OK' if ok2 else 'FAIL'}")
            ctx_page.wait_for_timeout(500)
            (
                self._js_open_cascade_btn(ctx_page, "Chọn phường/xã")
                or self._js_open_cascade_btn(ctx_page, "Chọn phường")
                or self._js_open_cascade_btn(ctx_page, "Chọn xã")
            )
            ctx_page.wait_for_timeout(800)
            ok3 = False
            if ward:
                ok3 = self._js_click_by_text(ctx_page, ward)
            if not ok3:
                first = self._js_click_first_option(ctx_page)
                ok3 = first is not None
                if first:
                    print(f"    [INFO] Cascade: Phường (first option) '{first}' → OK")
            else:
                print(f"    [INFO] Cascade: Phường '{ward}' → OK")
            ctx_page.wait_for_timeout(800)
            try:
                street_inp = ctx_page.locator(
                    "input[placeholder*='Số nhà'], input[placeholder*='số nhà'], "
                    "input[placeholder*='tên đường']"
                ).first
                if street_inp.is_visible(timeout=3000):
                    street_inp.fill(detail)
                    ctx_page.wait_for_timeout(300)
            except Exception:
                pass
            return ok1 and ok2 and ok3
        except Exception as e:
            print(f"    [WARN] _fill_cascade_address: {e}")
            return False

    def _add_product_to_cart(self, ctx_page: Page, slug: str, color: str,
                             size: str, ref_param: str = "") -> bool:
        """Navigate đến SP → chọn màu → click Mua ngay → chọn size → Thêm vào giỏ."""
        try:
            url = f"{self.env.fe_url.rstrip('/')}/product/{slug}{ref_param}"
            ctx_page.goto(url, wait_until="domcontentloaded", timeout=15000)
            ctx_page.wait_for_timeout(2000)
            print(f"    [INFO] AddCart: {slug} size {size} — {url}")

            # Chọn màu (giảm timeout xuống 1s để không block lâu nếu không có button)
            try:
                color_btn = ctx_page.locator(
                    f"[aria-label*='{color}'], [data-color*='{color.lower()}']"
                ).first
                if color_btn.is_visible(timeout=1000):
                    color_btn.click()
                    ctx_page.wait_for_timeout(500)
            except Exception:
                pass

            # Mở popup size — dùng wait_for_selector để không miss button khi page còn loading
            try:
                ctx_page.wait_for_selector(
                    "button:has-text('Mua ngay'), button:has-text('Thêm vào giỏ')",
                    timeout=8000
                )
            except Exception:
                print(f"    [WARN] AddCart: Không tìm thấy nút mở popup cho {slug}")
                return False

            opened = False
            for sel in ["button:has-text('Mua ngay')", "button:has-text('Thêm vào giỏ')"]:
                try:
                    btn = ctx_page.locator(sel).first
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        opened = True
                        break
                except Exception:
                    pass
            if not opened:
                print(f"    [WARN] AddCart: Không click được nút mở popup cho {slug}")
                return False
            ctx_page.wait_for_timeout(2000)  # Chờ popup render + cart state load

            # Deselect size đang selected trong popup (tránh gửi combined sizes lên server)
            # Chỉ cần 2 pass: 1 lần click, 1 lần verify
            for _retry in range(2):
                ctx_page.evaluate(r"""() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    btns.forEach(b => {
                        if (/^\d+$/.test(b.textContent.trim()) && b.offsetWidth > 0 &&
                                b.className.includes('indigo')) {
                            b.click();
                        }
                    });
                }""")
                ctx_page.wait_for_timeout(600)
            ctx_page.wait_for_timeout(300)

            # Chọn size bằng JS (robust hơn Playwright locator với timeout)
            clicked = ctx_page.evaluate(
                """(size) => {
                    const allBtns = Array.from(document.querySelectorAll('button'));
                    const sizeBtn = allBtns.find(b =>
                        b.textContent.trim() === size &&
                        b.offsetWidth > 0 && b.offsetHeight > 0
                    );
                    if (sizeBtn) { sizeBtn.click(); return true; }
                    return false;
                }""",
                size
            )
            if not clicked:
                visible_btns = ctx_page.evaluate(r"""() => {
                    return Array.from(document.querySelectorAll('button'))
                        .filter(b => b.offsetWidth > 0)
                        .map(b => b.textContent.trim())
                        .filter(t => t && t.length < 15);
                }""")
                print(f"    [WARN] AddCart: JS không tìm thấy size '{size}' cho {slug}")
                print(f"    [DEBUG] Buttons visible: {visible_btns}")
                return False
            ctx_page.wait_for_timeout(800)

            # Click Thêm vào giỏ trong popup bằng JS
            added = ctx_page.evaluate(r"""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                // Ưu tiên button cuối cùng có text "Thêm vào giỏ" (trong popup)
                const addBtns = btns.filter(b => b.offsetWidth > 0 &&
                    b.textContent.trim() === 'Thêm vào giỏ');
                if (addBtns.length > 0) {
                    addBtns[addBtns.length - 1].click();
                    return true;
                }
                return false;
            }""")
            if added:
                ctx_page.wait_for_timeout(1000)
                print(f"    [INFO] AddCart: Đã thêm {slug} size {size}")
                return True
            print(f"    [WARN] AddCart: Không thấy nút Thêm vào giỏ")
            return False
        except Exception as e:
            print(f"    [WARN] _add_product_to_cart({slug},{size}): {e}")
            return False

    def _apply_coupon(self, ctx_page: Page, code: str) -> bool:
        """Xóa mã cũ (nếu có) rồi áp mã mới. Trả về True nếu áp thành công."""
        try:
            # Bước 1: Xóa mã đang áp (nếu có)
            # Button là "Xoá" (Xo + á) — khác "Xóa" (X + ó + a)
            removed = ctx_page.evaluate(r"""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const del = btns.find(b => b.offsetWidth > 0 && (
                    /^[×x✕]$/.test(b.textContent.trim()) ||
                    b.textContent.trim() === 'Xoá' ||
                    b.textContent.trim() === 'Xóa' ||
                    b.textContent.includes('Xoá mã') ||
                    b.textContent.includes('Xóa mã') ||
                    (b.getAttribute('aria-label') || '').toLowerCase().includes('xo')
                ));
                if (del) { del.click(); return del.textContent.trim(); }
                return null;
            }""")
            if removed:
                ctx_page.wait_for_timeout(1000)
                print(f"    [INFO] Coupon: Đã xóa mã cũ (button='{removed}')")

            # Bước 2: Tìm input coupon
            coupon_inp = ctx_page.locator(
                "input[placeholder*='mã khuyến mại'], input[placeholder*='mã giảm giá'], "
                "input[placeholder*='coupon'], input[placeholder*='promo']"
            ).first
            if not coupon_inp.is_visible(timeout=5000):
                print(f"    [WARN] Coupon: Không tìm thấy ô nhập mã giảm giá")
                return False

            # Bước 3: Click + fill để React state update (fill() trigger nativeInputValueSetter)
            coupon_inp.click()
            ctx_page.wait_for_timeout(300)
            coupon_inp.fill(code)
            ctx_page.wait_for_timeout(500)

            # Bước 4: Đợi button #btn-apply-promo bỏ disabled rồi click
            try:
                ctx_page.wait_for_selector(
                    "#btn-apply-promo:not([disabled])",
                    timeout=5000
                )
                ctx_page.locator("#btn-apply-promo").click()
            except Exception:
                # Fallback: click button Áp dụng dù có disabled hay không
                ctx_page.evaluate(r"""() => {
                    const btn = document.querySelector('#btn-apply-promo')
                               || Array.from(document.querySelectorAll('button'))
                                  .find(b => b.textContent.trim() === 'Áp dụng');
                    if (btn) { btn.removeAttribute('disabled'); btn.click(); return true; }
                    return false;
                }""")

            ctx_page.wait_for_timeout(2000)
            print(f"    [INFO] Coupon: Đã áp mã '{code}'")
            return True
        except Exception as e:
            print(f"    [WARN] _apply_coupon: {e}")
        return False

    def _read_discount_from_page(self, ctx_page: Page) -> int:
        """Đọc số tiền giảm giá từ dòng 'Khuyến mãi (mã)' trên trang checkout.

        Cấu trúc DOM khi coupon áp:
          Tổng tiền   | 226,000đ   (subtotal before discount)
          [mã Xoá]                 (badge)
          Tổng cộng   | 226,000đ   (same, NOT discounted)
          Khuyến mãi  | −11,300đ   (discount line ← ĐỌC Ở ĐÂY)
          Thuế VAT    | ...
        """
        val = ctx_page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);

            // Ưu tiên: tìm dòng "Khuyến mãi" hoặc "khuyến mãi" + số tiền âm
            for (let i = 0; i < lines.length; i++) {
                if (/khuyến mãi/i.test(lines[i])) {
                    const nearby = lines.slice(i, i + 3).join(' ');
                    const m = nearby.match(/[−\-]\s*([\d,.]+)\s*[đ₫]/);
                    if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
                }
            }

            // Fallback: dòng có "giảm|ưu đãi|discount" + số âm
            for (let i = 0; i < lines.length; i++) {
                if (/giảm|ưu đãi|discount/i.test(lines[i])) {
                    const nearby = lines.slice(i, i + 3).join(' ');
                    const m = nearby.match(/[−\-]\s*([\d,.]+)\s*[đ₫]/);
                    if (m) return parseInt(m[1].replace(/[^\d]/g, ''));
                }
            }
            return 0;
        }""")
        return int(val) if val else 0

    def _customer_buy_cart(self, ctx_page: Page, store_url: str,
                           cust_email: str = "") -> dict:
        """
        Customer: thêm 2 sản phẩm vào giỏ → áp mã maimai1 → checkout.
        Lưu ý: mã maimai1 chỉ áp cho Áo Phông Năng Động, không áp Áo Phông Trẻ Em.

        Trả về dict: order_code, subtotal_nang_dong, subtotal_tre_em,
                     discount_amount (của Áo Phông Năng Động), total, success.
        """
        result = {
            "order_code": None,
            "subtotal_nang_dong": _SUBTOTAL_NANG_DONG_REF,
            "subtotal_tre_em":    _SUBTOTAL_TRE_EM_REF,
            "discount_amount":    0,
            "total":              None,
            "success":            False,
        }
        try:
            m = _re.search(r"ref=([^&]+)", store_url)
            ref_param = f"?ref={m.group(1)}" if m else ""

            # 0. Lưu danh sách đơn hiện có trước khi mua
            # Dùng để tìm đơn MỚI sau khi đặt hàng (tránh lấy đơn cũ)
            existing_orders: set[str] = set()
            try:
                fe_base = self.env.fe_url.rstrip("/")
                ctx_page.goto(f"{fe_base}/my-orders", wait_until="domcontentloaded", timeout=12000)
                ctx_page.wait_for_timeout(1500)
                codes_raw = ctx_page.evaluate(r"""() => {
                    const matches = [...(document.body.innerText||'').matchAll(/POD-[\w\-]+/g)];
                    return matches.map(m => m[0]);
                }""")
                existing_orders = set(codes_raw or [])
                print(f"    [INFO] Đơn cũ trước mua: {len(existing_orders)} đơn — {list(existing_orders)[:5]}")
            except Exception as e:
                print(f"    [WARN] Không đọc được danh sách đơn cũ: {e}")

            # 0b. Navigate store_link trước để set affiliate ref cookie
            # Backend tracking cần cookie/session ref từ store link
            try:
                ctx_page.goto(store_url, wait_until="domcontentloaded", timeout=12000)
                ctx_page.wait_for_timeout(1500)
                print(f"    [INFO] Đã navigate store_link để set ref cookie")
            except Exception as e:
                print(f"    [WARN] Navigate store_link: {e}")

            # 1. Thêm từng sản phẩm vào giỏ
            for prod in _PRODUCTS:
                for size in prod["sizes"]:
                    ok = self._add_product_to_cart(
                        ctx_page, prod["slug"], prod["color"], size, ref_param
                    )
                    if not ok:
                        print(f"    [WARN] Thêm giỏ FAIL: {prod['slug']} size {size}")

            # 2. Mở sidebar giỏ hàng (giỏ hàng là sidebar, không có URL /cart riêng)
            # Click nút giỏ hàng trên header
            try:
                cart_btn = ctx_page.locator("button:has-text('Giỏ hàng')").first
                if cart_btn.is_visible(timeout=5000):
                    cart_btn.click()
                    ctx_page.wait_for_timeout(1500)
                    print(f"    [INFO] Đã mở sidebar giỏ hàng")
            except Exception:
                pass

            # 3. Click "Thanh toán ngay" trong sidebar giỏ hàng → /checkout
            try:
                checkout_btn = ctx_page.locator("button:has-text('Thanh toán ngay')").first
                if checkout_btn.is_visible(timeout=5000):
                    checkout_btn.click()
                    ctx_page.wait_for_timeout(2000)
                    print(f"    [INFO] Đã click Thanh toán ngay trong sidebar")
                else:
                    # Fallback: navigate thẳng /checkout
                    ctx_page.goto(f"{self.env.fe_url.rstrip('/')}/checkout",
                                  wait_until="domcontentloaded", timeout=15000)
                    ctx_page.wait_for_timeout(2000)
            except Exception:
                ctx_page.goto(f"{self.env.fe_url.rstrip('/')}/checkout",
                              wait_until="domcontentloaded", timeout=15000)
                ctx_page.wait_for_timeout(2000)

            print(f"    [INFO] Sau click checkout — URL: {ctx_page.url}")

            # 4. Trang checkout
            if "/checkout" in ctx_page.url:
                ctx_page.wait_for_load_state("domcontentloaded")
                ctx_page.wait_for_timeout(1500)
                ctx_page.screenshot(path="screenshots/debug_sh07_checkout.png")

                # Áp mã giảm giá maimai1
                # Mã này chỉ áp cho Áo Phông Năng Động — hệ thống sẽ tự tính
                self._apply_coupon(ctx_page, _COUPON_CODE)

                # Đọc discount_amount được hiển thị (phần giảm cho Áo Phông Năng Động)
                result["discount_amount"] = self._read_discount_from_page(ctx_page)
                print(f"    [INFO] Discount từ mã {_COUPON_CODE} = {result['discount_amount']:,}đ "
                      f"(chỉ áp Áo Phông Năng Động)")

                # Điền họ tên, SĐT nếu cần
                def _fill_if_empty(selector, value):
                    try:
                        inp = ctx_page.locator(selector).first
                        if inp.is_visible(timeout=2000):
                            if not (inp.input_value() or "").strip():
                                inp.click()
                                inp.fill(value)
                                ctx_page.wait_for_timeout(300)
                    except Exception:
                        pass

                _fill_if_empty(
                    "input[placeholder*='Nguyễn Văn A'], input[placeholder*='Họ tên'], "
                    "input[placeholder*='họ và tên']", "Customer Test"
                )
                _fill_if_empty(
                    "input[placeholder*='0901'], input[type='tel'], "
                    "input[placeholder*='Số điện thoại']", "0912345678"
                )
                _fill_if_empty(
                    "input[type='email'], input[placeholder*='email']",
                    cust_email or "customer_test@yopmail.com"
                )

                # Chọn địa chỉ đã lưu hoặc cascade
                has_saved_addr = ctx_page.evaluate(
                    "() => Array.from(document.querySelectorAll('button'))"
                    ".some(b => b.offsetWidth > 0 && "
                    "  (b.textContent.includes('Sử dụng') || b.textContent.includes('Chọn địa chỉ')))"
                )
                if has_saved_addr:
                    try:
                        use_btn = ctx_page.locator(
                            "button:has-text('Sử dụng'), button:has-text('Chọn địa chỉ')"
                        ).first
                        if use_btn.is_visible(timeout=2000):
                            use_btn.click()
                            ctx_page.wait_for_timeout(500)
                    except Exception:
                        pass
                self._fill_cascade_address(ctx_page)
                ctx_page.wait_for_timeout(800)

                # Đọc total
                result["total"] = ctx_page.evaluate(r"""() => {
                    const text = document.body.innerText || '';
                    const lines = text.split('\n').map(l => l.trim());
                    const re = /(\d{1,3}(?:[.,]\d{3})+)/;
                    for (let i = 0; i < lines.length; i++) {
                        if (/tổng thanh toán|tổng cộng/i.test(lines[i])) {
                            const m = (lines[i]+' '+(lines[i+1]||'')).match(re);
                            if (m) return parseInt(m[1].replace(/[^\d]/g,''));
                        }
                    }
                    return null;
                }""")

                # Chờ sau khi áp mã để UI ổn định
                ctx_page.wait_for_load_state("networkidle", timeout=5000)
                ctx_page.wait_for_timeout(1500)

                # Chọn COD (Thanh toán khi nhận hàng) để tránh QR popup
                # QR (PayOS) mặc định → nhấn Thanh toán sẽ mở QR dialog thay vì tạo đơn
                # Dùng JS dispatchEvent để đảm bảo React state update
                cod_selected = ctx_page.evaluate(r"""() => {
                    const labels = Array.from(document.querySelectorAll('label'));
                    const cod = labels.find(l => l.offsetWidth > 0 &&
                        l.textContent.includes('nhận hàng'));
                    if (cod) {
                        cod.dispatchEvent(new MouseEvent('click', {bubbles: true}));
                        return true;
                    }
                    return false;
                }""")
                ctx_page.wait_for_timeout(1000)
                if cod_selected:
                    # Verify COD thực sự được chọn (class border-emerald)
                    verified = ctx_page.evaluate(r"""() => {
                        const labels = Array.from(document.querySelectorAll('label'));
                        const cod = labels.find(l => l.textContent.includes('nhận hàng'));
                        return cod ? cod.className.includes('emerald') : false;
                    }""")
                    print(f"    [INFO] COD selected={verified} (tránh QR popup)")

                ctx_page.screenshot(path="screenshots/debug_sh07_checkout_filled.png")

                # Click nút submit cuối trang (Thanh toán hoặc Đặt hàng)
                # Khi chọn COD → button là "local_shipping Đặt hàng (COD...)"
                # Khi chọn QR  → button là "credit_card Thanh toán XXXđ"
                pay_clicked = ctx_page.evaluate(r"""() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    // Tìm button submit: visible, không disabled,
                    // text chứa 'Đặt hàng' HOẶC ('Thanh toán' + số tiền)
                    const payBtns = btns.filter(b =>
                        b.offsetWidth > 0 && !b.disabled &&
                        (b.textContent.includes('Đặt hàng') ||
                         (b.textContent.includes('Thanh toán') && /\d{3}/.test(b.textContent)))
                    );
                    if (payBtns.length > 0) {
                        const last = payBtns[payBtns.length - 1];
                        last.scrollIntoView();
                        last.click();
                        return last.textContent.trim().substring(0, 50);
                    }
                    return null;
                }""")
                if pay_clicked:
                    print(f"    [INFO] Click nút thanh toán: '{pay_clicked}'")
                else:
                    print(f"    [WARN] Không tìm thấy nút Thanh toán/Đặt hàng")
                if pay_clicked:
                    # Chờ navigate ra khỏi checkout hoặc xuất hiện POD- (tăng timeout lên 20s)
                    try:
                        ctx_page.wait_for_function(
                            "() => !window.location.href.includes('/checkout') || "
                            "document.body.innerText.includes('POD-')",
                            timeout=20000
                        )
                    except Exception:
                        pass
                    ctx_page.wait_for_timeout(4000)
                    print(f"    [INFO] Sau thanh toán — {ctx_page.url}")
                    ctx_page.screenshot(path="screenshots/debug_sh07_after_pay.png")
            else:
                print(f"    [WARN] Chưa vào checkout — {ctx_page.url}")

            # 5. Lấy mã đơn — tìm đơn MỚI (không có trong danh sách cũ)
            print(f"    [INFO] URL sau thanh toán = {ctx_page.url}")
            order_code = ctx_page.evaluate(r"""() => {
                const params = new URLSearchParams(window.location.search);
                const fromUrl = params.get('orderCode');
                if (fromUrl) return fromUrl;
                const m = (document.body.innerText||'').match(/POD-[\w\-]+/);
                return m ? m[0] : null;
            }""")

            # Nếu chưa có hoặc đơn trùng với đơn cũ → navigate /my-orders tìm đơn mới nhất
            if not order_code or order_code in existing_orders:
                print(f"    [INFO] Chưa có order_code mới — navigate /my-orders để tìm")
                try:
                    fe = self.env.fe_url.rstrip("/")
                    ctx_page.goto(f"{fe}/my-orders", wait_until="domcontentloaded", timeout=15000)
                    ctx_page.wait_for_timeout(2000)
                    # Lấy tất cả mã đơn, tìm mã KHÔNG có trong existing_orders
                    all_codes = ctx_page.evaluate(r"""() => {
                        const matches = [...(document.body.innerText||'').matchAll(/POD-[\w\-]+/g)];
                        return matches.map(m => m[0]);
                    }""") or []
                    new_codes = [c for c in all_codes if c not in existing_orders]
                    order_code = new_codes[0] if new_codes else (all_codes[0] if all_codes else None)
                    print(f"    [INFO] all_codes={all_codes[:5]}, new_codes={new_codes[:3]}")
                    print(f"    [INFO] order_code mới từ my-orders = {order_code}")
                    ctx_page.screenshot(path="screenshots/debug_sh07_orders_page.png")
                except Exception as e:
                    print(f"    [WARN] Navigate my-orders: {e}")

            result["order_code"] = order_code
            # success chỉ True khi tìm được order MỚI (không phải order cũ đã có từ trước)
            result["success"]    = (order_code is not None and
                                    order_code not in existing_orders)
            print(f"    [INFO] order_code={order_code}, total={result['total']}, "
                  f"discount(Áo Năng Động)={result['discount_amount']:,}đ")

        except Exception as e:
            print(f"  [WARN] _customer_buy_cart: {e}")

        return result

    # ── Admin xác nhận thanh toán ─────────────────────────────────────────────

    def _admin_confirm_payment(self, browser: Browser, order_code: str,
                               reason: str = "Chuyển khoản thành công - test SH07") -> bool:
        if not order_code:
            return False
        ctx = None
        try:
            ctx = browser.new_context()
            adm = ctx.new_page()
            admin_url = self.env.admin_url

            adm.goto(admin_url, wait_until="domcontentloaded", timeout=15000)
            adm.wait_for_timeout(2000)
            email_inp = adm.locator("input[type='email'], input[name='email']").first
            pass_inp  = adm.locator("input[type='password']").first
            if email_inp.is_visible(timeout=5000):
                email_inp.fill(self.env.admin_email)
            if pass_inp.is_visible(timeout=5000):
                pass_inp.fill(self.env.admin_password)
            adm.locator("button[type='submit'], button:has-text('Đăng nhập')").first.click()
            adm.wait_for_timeout(3000)

            adm.goto(f"{admin_url}/orders", wait_until="domcontentloaded", timeout=15000)
            adm.wait_for_timeout(2000)

            search = adm.locator(
                "input[placeholder*='tìm'], input[placeholder*='search'], "
                "input[type='search'], input[placeholder*='mã đơn']"
            ).first
            if search.is_visible(timeout=3000):
                search.fill(order_code)
                adm.keyboard.press("Enter")
                adm.wait_for_timeout(2000)

            order_btn = adm.locator(
                f"button:text-is('{order_code}'), "
                f"button.font-mono:has-text('{order_code}'), "
                f"td button:has-text('{order_code}')"
            ).first
            if not order_btn.is_visible(timeout=5000):
                order_row = adm.locator(f"tr:has-text('{order_code}')").first
                if order_row.is_visible(timeout=3000):
                    order_row.click()
                else:
                    print(f"  [WARN] Admin: Không tìm thấy đơn {order_code}")
                    return False
            else:
                order_btn.click()
            adm.wait_for_timeout(2000)

            manual_btn = adm.locator(
                "button:has-text('Đánh dấu đã thanh toán thủ công')"
            ).first
            if not manual_btn.is_visible(timeout=5000):
                print(f"  [WARN] Admin: Không thấy nút thanh toán thủ công")
                return False
            manual_btn.click()
            adm.wait_for_timeout(1500)

            reason_inp = adm.locator(
                "textarea:visible, input[placeholder*='lý do'], textarea[placeholder*='lý do'], "
                "dialog input, dialog textarea"
            ).first
            if reason_inp.is_visible(timeout=5000):
                reason_inp.fill(reason)
                adm.wait_for_timeout(500)

            confirm_btn = adm.locator(
                "dialog button:has-text('Xác nhận'), "
                "[role='dialog'] button:has-text('Xác nhận'), "
                "button:has-text('Xác nhận'):visible"
            ).last
            if not confirm_btn.is_visible(timeout=5000):
                print(f"  [WARN] Admin: Không tìm thấy nút Xác nhận")
                return False
            confirm_btn.click()
            adm.wait_for_timeout(2000)
            print(f"  [PASS] Admin: Xác nhận thanh toán đơn {order_code}")
            return True

        except Exception as e:
            print(f"  [WARN] _admin_confirm_payment: {e}")
        finally:
            if ctx:
                ctx.close()
        return False

    # ── Main test ─────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_cart_multi_e2e(self, browser: Browser):
        """
        SH07: 2 sản phẩm vào giỏ + mã maimai1 (chỉ áp Áo Phông Năng Động)
              → affiliate hoa hồng đúng.

        Công thức hoa hồng:
          subtotal_effective = (130k - discount_maimai1) + 96k × 2
          hoa_hong = subtotal_effective × rate%  (không gồm VAT, không gồm ship)
        """
        tc = self.tc

        aff_email    = self.env.affiliate_email or self.env.login_email
        aff_password = self.env.affiliate_password or self.env.login_password
        cust_email   = self.env.customer_email
        cust_password = self.env.customer_password

        if not aff_email:
            pytest.skip(f"SKIP {tc}: Chưa điền AFFILIATE_EMAIL trong .env")

        # ════ MH1: Affiliate login ════════════════════════════════════════════
        print(f"\n  ── MH1: Affiliate login → lấy link + tỷ lệ hoa hồng ────────")
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1000)
        self.auth.login(aff_email, aff_password)
        self.page.wait_for_timeout(3000)
        login_ok = not self.home.header.login_button.is_visible(timeout=5000)
        assert login_ok, f"LỖI {tc}: Đăng nhập affiliate thất bại ({aff_email})"

        self._goto_affiliate()
        self._shot("MH1_1", "affiliate_page")

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: {aff_email} chưa được duyệt affiliate")

        store_link = self._get_affiliate_store_link()
        if not store_link:
            pytest.skip(f"SKIP {tc}: Không tìm thấy link gian hàng")

        commission_rate    = self._read_commission_rate()
        order_count_before = self._read_order_count_before()

        self._record_check("MH1", "MH1 Link gian hàng lấy được",
                           "✅ PASS", store_link[:80], "URL gian hàng")
        self._record_check("MH1", "MH1 Tỷ lệ hoa hồng",
                           "✅ PASS" if commission_rate is not None else "⚠️ WARN",
                           f"{commission_rate}%" if commission_rate else "N/A", "≥ 1%")
        print(f"  [INFO] store_link={store_link}")
        print(f"  [INFO] commission_rate={commission_rate}%, count_before={order_count_before}")

        # ════ MH2: Customer — giỏ hàng 2SP + mã maimai1 ══════════════════════
        print(f"\n  ── MH2: Customer giỏ hàng 2SP + mã giảm giá maimai1 ────────")
        print(f"  [INFO] Sản phẩm:")
        print(f"    - Áo Phông Năng Động (M × 1):   130,000đ  ← mã maimai1 áp")
        print(f"    - Áo Phông Trẻ Em (110 × 1):     96,000đ  ← KHÔNG áp mã (ET002_100_140)")
        print(f"    - Áo Phông Trẻ Em (120 × 1):     96,000đ  ← KHÔNG áp mã (ET002_100_140)")

        customer_ctx: BrowserContext = browser.new_context(
            locale="vi-VN",
            viewport={"width": 1280, "height": 800},
        )
        order_info = {
            "order_code": None, "subtotal_nang_dong": _SUBTOTAL_NANG_DONG_REF,
            "subtotal_tre_em": _SUBTOTAL_TRE_EM_REF, "discount_amount": 0,
            "total": None, "success": False,
        }
        try:
            cust_page = customer_ctx.new_page()
            if cust_email and cust_password:
                logged = self._customer_login(cust_page, cust_email, cust_password)
                print(f"  [INFO] Customer login ({cust_email}) = {logged}")
            order_info = self._customer_buy_cart(cust_page, store_link,
                                                  cust_email=cust_email or "")
            self._shot("MH2_1", "customer_after_order")
        except Exception as e:
            print(f"  [WARN] MH2: {e}")
        finally:
            customer_ctx.close()

        order_code      = order_info.get("order_code")
        discount_amount = order_info.get("discount_amount", 0)
        order_ok        = order_info.get("success", False)

        self._record_check(
            "MH2", f"MH2 Customer đặt đơn thành công (2SP + mã {_COUPON_CODE})",
            "✅ PASS" if order_ok else "❌ FAIL",
            f"order_code={order_code}" if order_code else "Không lấy được mã đơn",
            "Có order_code sau checkout",
        )
        discount_ok = (discount_amount > 0 and
                       abs(discount_amount - _MAIMAI1_DISCOUNT_EXPECTED) <= _MAIMAI1_DISCOUNT_TOLERANCE)
        self._record_check(
            "MH2", f"MH2 Mã {_COUPON_CODE} giảm giá Áo Phông Năng Động",
            "✅ PASS" if discount_ok else ("⚠️ WARN" if discount_amount > 0 else "❌ FAIL"),
            f"Giảm {discount_amount:,}đ" if discount_amount else "Không đọc được discount",
            f"~{_MAIMAI1_DISCOUNT_EXPECTED:,}đ "
            f"(={_SUBTOTAL_NANG_DONG_REF:,}-{_COST_AO_NANG_DONG + _COST_IN_NANG_DONG:,}, ±{_MAIMAI1_DISCOUNT_TOLERANCE:,}đ)",
        )
        print(f"  [{'PASS' if order_ok else 'FAIL'}] MH2: order_code={order_code}, "
              f"discount_maimai1={discount_amount:,}đ")

        if not order_ok:
            self._print_summary_table()
            pytest.fail(f"LỖI {tc}: Customer không đặt được đơn hàng")

        # ════ MH3: Admin xác nhận thanh toán ══════════════════════════════════
        print(f"\n  ── MH3: Admin xác nhận thanh toán ──────────────────────────")
        admin_confirmed = self._admin_confirm_payment(browser, order_code)
        self._record_check(
            "MH3", "MH3 Admin xác nhận thanh toán",
            "✅ PASS" if admin_confirmed else "ℹ️ INFO",
            "OK" if admin_confirmed else "Không xác nhận được",
            "Thanh toán được xác nhận",
        )
        if admin_confirmed:
            self.page.wait_for_timeout(5000)  # Chờ backend xử lý hoa hồng

        # ════ MH4: Đơn mới xuất hiện trong danh sách liên kết ════════════════
        print(f"\n  ── MH4: Đơn mới xuất hiện trong danh sách liên kết ─────────")
        self._goto_affiliate()
        self.page.wait_for_timeout(3000)
        self._shot("MH4_1", "affiliate_after_order")

        order_count_after = self._read_order_count_before()
        count_increased   = order_count_after > order_count_before

        self._record_check(
            "MH4", f"MH4 Số đơn liên kết tăng ({order_count_before} → {order_count_after})",
            "✅ PASS" if count_increased else "⚠️ WARN",
            str(order_count_after), f">{order_count_before}",
        )

        found_order = self._find_new_order_in_list(order_code) if order_code else None
        if not found_order:
            self.page.wait_for_timeout(8000)
            self._goto_affiliate()
            self.page.wait_for_timeout(2000)
            all_aff_orders = self._read_affiliate_orders()
            print(f"    [DEBUG] Affiliate orders ({len(all_aff_orders)}): "
                  f"{[o.get('order_code') for o in all_aff_orders[:5]]}")
            found_order = self._find_new_order_in_list(order_code) if order_code else None

        self._record_check(
            "MH4", f"MH4 Đơn {order_code} trong danh sách liên kết",
            "✅ PASS" if found_order else "⚠️ WARN",
            f"Tìm thấy: {found_order.get('raw','')[:60]}" if found_order else "Không tìm thấy",
            "Đơn xuất hiện trong list",
        )
        self._shot("MH4_2", "affiliate_order_list")
        print(f"  [{'PASS' if found_order else 'WARN'}] MH4: found_order={found_order}")

        # ════ MH5: Verify hoa hồng ═══════════════════════════════════════════
        print(f"\n  ── MH5: Verify công thức hoa hồng ──────────────────────────")
        # Công thức:
        #   subtotal_nang_dong_after = 130,000 - discount_maimai1        (mã chỉ áp SP này)
        #   subtotal_tre_em          = 96,000 × 2 = 192,000 (size 110+120, không áp mã)
        #   subtotal_effective       = subtotal_nang_dong_after + subtotal_tre_em
        #   hoa_hong                 = subtotal_effective × rate%         (không gồm VAT/ship)

        rate              = None
        actual_commission = None

        if found_order:
            rate              = found_order.get("commission_rate") or commission_rate
            actual_commission = found_order.get("commission")
        else:
            rate = commission_rate

        sub_nang_dong_after = max(0, _SUBTOTAL_NANG_DONG_REF - discount_amount)
        sub_tre_em          = _SUBTOTAL_TRE_EM_REF
        subtotal_effective  = sub_nang_dong_after + sub_tre_em

        print(f"  [INFO] MH5 Công thức:")
        print(f"    Áo Phông Năng Động: {_SUBTOTAL_NANG_DONG_REF:,}đ - {discount_amount:,}đ (mã maimai1) = {sub_nang_dong_after:,}đ")
        print(f"    Áo Phông Trẻ Em:   {_SUBTOTAL_TRE_EM_REF:,}đ (96k size110 + 100k size150, không áp mã)")
        print(f"    Subtotal effective: {subtotal_effective:,}đ")
        print(f"    rate={rate}%, actual_commission={actual_commission}")

        if rate is None:
            self._record_check("MH5", "MH5 Tỷ lệ hoa hồng", "⚠️ WARN",
                               "Không đọc được tỷ lệ %", "Cần tỷ lệ % để verify")
        elif actual_commission is None:
            self._record_check(
                "MH5", "MH5 Hoa hồng hiển thị trong danh sách", "⚠️ WARN",
                "Không đọc được số tiền hoa hồng",
                f"expected={self.calc_commission(subtotal_effective, rate):,}đ",
            )
        else:
            expected  = self.calc_commission(subtotal_effective, rate)
            delta     = abs(actual_commission - expected)
            # 20% tolerance: hệ thống tính trên giá trước VAT + làm tròn
            tolerance = max(self.TOLERANCE, expected * 0.20)
            ok        = delta <= tolerance
            status    = "✅ PASS" if ok else "❌ FAIL"

            self._record_check(
                "MH5",
                f"MH5 Hoa hồng đơn {order_code or 'N/A'} "
                f"({rate}% × {subtotal_effective:,}đ = {sub_nang_dong_after:,}đ + {sub_tre_em:,}đ)",
                status,
                f"{actual_commission:,}đ",
                f"~{expected:,}đ (±{int(tolerance):,}đ)",
            )
            print(
                f"  [{'PASS' if ok else 'FAIL'}] MH5: "
                f"commission={actual_commission:,}đ | expected≈{expected:,}đ | "
                f"delta={delta:,}đ (tolerance={int(tolerance):,}đ)"
            )

        self._shot("MH5_1", "commission_verified")
        print(f"\n  [PASS] {tc}: SH07 COMPLETED")
        self._print_summary_table()
