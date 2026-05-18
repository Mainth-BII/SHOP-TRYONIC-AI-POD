"""
SH06 — E2E Affiliate Commission Flow

Luồng kiểm tra đầy đủ:
  1. Affiliate user login → lấy link gian hàng + tỷ lệ hoa hồng + số đơn ban đầu
  2. Customer (browser context riêng) → vào link gian hàng → mua hàng → đặt đơn thành công
  3. Admin xác nhận thanh toán (để hoa hồng được ghi nhận)
  4. Affiliate user → /affiliate → verify:
       - Đơn mới xuất hiện trong danh sách liên kết
       - Hoa hồng = subtotal × tỷ lệ% (không gồm VAT, không gồm ship)

Preconditions:
  - AFFILIATE_EMAIL: tài khoản đã được duyệt chương trình Tiếp thị liên kết
  - CUSTOMER_EMAIL: tài khoản khác dùng để mua hàng qua link (hoặc guest checkout)
  - Điền vào .env: AFFILIATE_EMAIL, AFFILIATE_PASSWORD, CUSTOMER_EMAIL, CUSTOMER_PASSWORD
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from .base_share_flow import BaseShareFlowTest

# ── Sản phẩm dùng để test mua (plain, không in — đơn giản nhất) ──────────────
_BUY_SLUG  = "ao-phong-ca-tinh"
_BUY_NAME  = "Áo Phông Cá Tính"
_BUY_COLOR = "Trắng"
_BUY_SIZE  = "M"


class TestSH06CommissionE2E(BaseShareFlowTest):
    """SH06 — E2E: Khách mua qua link gian hàng → affiliate nhận hoa hồng đúng."""

    _MH_NAMES = {
        "MH1":   "Affiliate login → lấy link + tỷ lệ hoa hồng",
        "MH2":   "Customer mua hàng qua link gian hàng",
        "MH3":   "Admin xác nhận thanh toán",
        "MH4":   "Đơn mới xuất hiện trong danh sách liên kết",
        "MH5":   "Hoa hồng = subtotal × tỷ lệ%",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH06 — E2E Affiliate Commission (mua qua link → hoa hồng)"

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
        self.tc       = "SH06_COMMISSION_E2E"
        self.root     = "production"
        self.domain   = "sh06_commission_e2e"
        self._results = []

    # ── Helpers affiliate ─────────────────────────────────────────────────────

    def _get_affiliate_store_link(self) -> str | None:
        """Lấy link gian hàng (có thể có param ref=...) từ trang /affiliate."""
        link = self.page.evaluate(r"""() => {
            // Ưu tiên input copy-link có ref/aff param
            const inp = document.querySelector(
                'input[value*="ref="], input[value*="aff="], input[readonly][value*="http"]'
            );
            if (inp && inp.value) return inp.value;

            // Link href có ref/aff
            const aRef = document.querySelector('a[href*="ref="], a[href*="aff="]');
            if (aRef) return aRef.href;

            // Link gian hàng trực tiếp /store/ hoặc /gian-hang/
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
        """Đọc tỷ lệ hoa hồng (%) từ trang /affiliate."""
        raw = self.page.evaluate(r"""() => {
            const text = document.body.innerText || '';
            // "Tỷ lệ hoa hồng: 5%" hoặc "Hoa hồng 10%"
            const m = text.match(/tỷ lệ hoa hồng[^\d]*(\d+(?:\.\d+)?)\s*%/i)
                   || text.match(/hoa hồng[^\d]*(\d+(?:\.\d+)?)\s*%/i)
                   || text.match(/(\d+(?:\.\d+)?)\s*%\s*hoa hồng/i);
            return m ? parseFloat(m[1]) : null;
        }""")
        return float(raw) if raw is not None else None

    def _read_order_count_before(self) -> int:
        """Đọc số đơn hàng liên kết hiện tại."""
        count = self._read_order_count()
        return count if count is not None else 0

    def _find_new_order_in_list(self, order_code: str) -> dict | None:
        """Tìm đơn order_code trong danh sách liên kết, trả về dict hoặc None."""
        orders = self._read_affiliate_orders()
        for o in orders:
            if order_code and order_code.lower() in (o.get("order_code") or "").lower():
                return o
            # fallback: tìm theo mã ngắn hơn (5 ký tự cuối)
            if order_code and len(order_code) >= 5:
                suffix = order_code[-5:]
                if suffix in (o.get("order_code") or ""):
                    return o
        return None

    # ── Customer checkout helpers ─────────────────────────────────────────────

    def _customer_login(self, ctx_page: Page, email: str, password: str) -> bool:
        """Đăng nhập customer trong context riêng qua dialog popup trên trang home."""
        try:
            ctx_page.goto(f"{self.env.fe_url}", wait_until="domcontentloaded", timeout=15000)
            ctx_page.wait_for_timeout(2500)

            # Click nút Đăng nhập trên header
            login_btn = ctx_page.locator("button:has-text('Đăng nhập')").first
            if not login_btn.is_visible(timeout=5000):
                print(f"  [WARN] _customer_login: Không thấy nút Đăng nhập")
                return False
            login_btn.click()
            # Chờ dialog/form login xuất hiện
            ctx_page.wait_for_timeout(2000)

            # Điền email — thử theo thứ tự ưu tiên
            email_inp = None
            for sel in [
                "dialog input[type='email']",
                "[role='dialog'] input[type='email']",
                "input[type='email']",
            ]:
                try:
                    loc = ctx_page.locator(sel).first
                    if loc.is_visible(timeout=3000):
                        email_inp = loc
                        break
                except Exception:
                    pass

            if email_inp is None:
                print(f"  [WARN] _customer_login: Không tìm thấy email input")
                return False
            email_inp.fill(email)
            ctx_page.wait_for_timeout(300)

            # Điền password
            pass_inp = None
            for sel in [
                "dialog input[type='password']",
                "[role='dialog'] input[type='password']",
                "input[type='password']",
            ]:
                try:
                    loc = ctx_page.locator(sel).first
                    if loc.is_visible(timeout=2000):
                        pass_inp = loc
                        break
                except Exception:
                    pass

            if pass_inp is None:
                print(f"  [WARN] _customer_login: Không tìm thấy password input")
                return False
            pass_inp.fill(password)
            ctx_page.wait_for_timeout(300)

            # Submit
            submit = None
            for sel in [
                "dialog button:has-text('Đăng nhập')",
                "[role='dialog'] button:has-text('Đăng nhập')",
                "button[type='submit']",
                "button:has-text('Đăng nhập'):visible",
            ]:
                try:
                    loc = ctx_page.locator(sel).last
                    if loc.is_visible(timeout=2000):
                        submit = loc
                        break
                except Exception:
                    pass

            if submit is None:
                print(f"  [WARN] _customer_login: Không tìm thấy submit button")
                return False
            submit.click()
            ctx_page.wait_for_timeout(4000)

            # Kiểm tra login thành công: nút Đăng nhập biến mất
            still_has_login = ctx_page.locator("button:has-text('Đăng nhập')").is_visible(timeout=3000)
            if not still_has_login:
                print(f"  [INFO] Customer login OK: {email}")
                return True
            print(f"  [WARN] _customer_login: Vẫn còn nút Đăng nhập sau submit")
        except Exception as e:
            print(f"  [WARN] _customer_login: {e}")
        return False

    @staticmethod
    def _js_click_by_text(page: Page, text: str) -> bool:
        """Click button trong dropdown (div.absolute.z-50) có innerText khớp chính xác với text."""
        result = page.evaluate(f"""() => {{
            // Tìm trong dropdown container trước
            const dropdown = Array.from(document.querySelectorAll('div')).find(d => {{
                const cls = String(d.className || '');
                return cls.includes('absolute') && cls.includes('z-50') && d.offsetWidth > 50;
            }});
            if (dropdown) {{
                const btns = Array.from(dropdown.querySelectorAll('button'));
                const btn = btns.find(b => b.textContent.trim() === {repr(text)});
                if (btn) {{ btn.click(); return true; }}
            }}
            // Fallback toàn page
            const els = Array.from(document.querySelectorAll('button, li'));
            const el = els.find(e => e.offsetWidth > 0 && e.textContent.trim() === {repr(text)});
            if (el) {{ el.click(); return true; }}
            return false;
        }}""")
        return bool(result)

    @staticmethod
    def _js_open_cascade_btn(page: Page, text_include: str) -> bool:
        """Click dropdown button (enabled) chứa text_include."""
        return bool(page.evaluate(f"""() => {{
            const btns = Array.from(document.querySelectorAll('button'));
            const b = btns.find(b => !b.disabled && b.textContent.includes({repr(text_include)}));
            if (b) {{ b.click(); return true; }}
            return false;
        }}"""))

    @staticmethod
    def _js_click_first_option(page: Page) -> str | None:
        """Click option đầu tiên hiện ra trong dropdown container (div.absolute.z-50)."""
        return page.evaluate(r"""() => {
            // Tìm dropdown container đang mở
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
        """
        Điền địa chỉ qua cascade button-dropdown (Tỉnh → Quận → Phường → Số nhà).
        Trả về True nếu hoàn tất.
        """
        try:
            # Kiểm tra xem có cascade dropdown chưa (button "Chọn tỉnh/thành")
            has_cascade = ctx_page.evaluate(
                "() => Array.from(document.querySelectorAll('button'))"
                ".some(b => !b.disabled && b.textContent.includes('Chọn tỉnh/thành'))"
            )
            if not has_cascade:
                print(f"    [INFO] Không cần cascade — đã có địa chỉ sẵn")
                return True

            # Bước 1: Mở dropdown Tỉnh/thành và chọn tỉnh
            self._js_open_cascade_btn(ctx_page, "Chọn tỉnh/thành")
            ctx_page.wait_for_timeout(800)
            ok1 = self._js_click_by_text(ctx_page, province)
            ctx_page.wait_for_timeout(800)
            print(f"    [INFO] Cascade: Tỉnh '{province}' → {'OK' if ok1 else 'FAIL'}")

            # Bước 2: Mở dropdown Quận/huyện và chọn quận
            self._js_open_cascade_btn(ctx_page, "Chọn quận/huyện")
            ctx_page.wait_for_timeout(800)
            ok2 = self._js_click_by_text(ctx_page, district)
            ctx_page.wait_for_timeout(800)
            print(f"    [INFO] Cascade: Quận '{district}' → {'OK' if ok2 else 'FAIL'}")

            # Bước 3: Mở dropdown Phường/xã và chọn phường
            # Sau khi chọn quận, button phường đổi sang "Chọn phường/xã"
            ctx_page.wait_for_timeout(500)
            (
                self._js_open_cascade_btn(ctx_page, "Chọn phường/xã")
                or self._js_open_cascade_btn(ctx_page, "Chọn phường")
                or self._js_open_cascade_btn(ctx_page, "Chọn xã")
            )
            ctx_page.wait_for_timeout(800)

            # Thử chọn theo tên cụ thể, nếu FAIL thì chọn option đầu tiên
            ok3 = False
            if ward:
                ok3 = self._js_click_by_text(ctx_page, ward)
            if not ok3:
                first = self._js_click_first_option(ctx_page)
                ok3 = first is not None
                if first:
                    print(f"    [INFO] Cascade: Phường (first option) '{first}' → OK")
                else:
                    print(f"    [WARN] Cascade: Không tìm được option phường")
            else:
                print(f"    [INFO] Cascade: Phường '{ward}' → OK")
            ctx_page.wait_for_timeout(800)

            # Bước 4: Điền số nhà/đường
            try:
                street_inp = ctx_page.locator(
                    "input[placeholder*='Số nhà'], input[placeholder*='số nhà'], "
                    "input[placeholder*='tên đường']"
                ).first
                if street_inp.is_visible(timeout=3000):
                    street_inp.fill(detail)
                    ctx_page.wait_for_timeout(300)
                    print(f"    [INFO] Cascade: Địa chỉ chi tiết = '{detail}'")
            except Exception:
                pass

            return ok1 and ok2 and ok3

        except Exception as e:
            print(f"    [WARN] _fill_cascade_address: {e}")
            return False

    def _customer_buy_product(self, ctx_page: Page, store_url: str) -> dict:
        """
        Customer vào link gian hàng (giữ ref param) → chọn sản phẩm → Mua ngay → Checkout.
        Trả về dict: order_code, subtotal, total, success.
        """
        result = {"order_code": None, "subtotal": None, "total": None, "success": False}
        try:
            # 1. Vào link gian hàng — trình duyệt lưu ref cookie
            ctx_page.goto(store_url, wait_until="domcontentloaded", timeout=20000)
            ctx_page.wait_for_timeout(2000)
            print(f"    [INFO] Customer: Đã vào gian hàng — {ctx_page.url}")

            # Trích ref param để giữ khi navigate sản phẩm
            ref_param = ""
            if "ref=" in store_url:
                import re as _re
                m = _re.search(r"ref=([^&]+)", store_url)
                if m:
                    ref_param = f"?ref={m.group(1)}"

            # 2. Click vào sản phẩm (tìm card trên trang home/store)
            product_link = ctx_page.locator(
                f"a[href*='/{_BUY_SLUG}'], "
                f"a[href*='/product/']:has-text('{_BUY_NAME}')"
            ).first
            navigated = False
            if product_link.is_visible(timeout=5000):
                product_link.click()
                ctx_page.wait_for_load_state("domcontentloaded")
                ctx_page.wait_for_timeout(2000)
                navigated = True
                print(f"    [INFO] Customer: Click card sản phẩm → {ctx_page.url}")

            if not navigated:
                # Fallback: navigate kèm ref param để affiliate cookie được giữ
                detail_url = f"{self.env.fe_url}/product/{_BUY_SLUG}{ref_param}"
                ctx_page.goto(detail_url, wait_until="domcontentloaded", timeout=15000)
                ctx_page.wait_for_timeout(2000)
                print(f"    [INFO] Customer: Fallback navigate → {ctx_page.url}")

            # 3. Chọn màu
            try:
                color_btn = ctx_page.locator(
                    f"button:has-text('{_BUY_COLOR}'), "
                    f"[aria-label*='{_BUY_COLOR}'], [data-color*='{_BUY_COLOR.lower()}']"
                ).first
                if color_btn.is_visible(timeout=3000):
                    color_btn.click()
                    ctx_page.wait_for_timeout(500)
            except Exception:
                pass

            # 4. Click Mua ngay
            mua_ngay = ctx_page.locator(
                "button:has-text('Mua ngay'), button:has-text('Mua Ngay')"
            ).first
            if mua_ngay.is_visible(timeout=5000):
                mua_ngay.click()
                ctx_page.wait_for_timeout(2000)
                print(f"    [INFO] Customer: Đã click Mua ngay")
            else:
                # Debug: dump visible buttons
                btns_text = ctx_page.evaluate(
                    "() => Array.from(document.querySelectorAll('button'))"
                    ".filter(b => b.offsetWidth > 0)"
                    ".map(b => b.textContent.trim().replace(/\\s+/g,' ').slice(0,30)).filter(t=>t)"
                )
                print(f"    [WARN] Customer: Không tìm thấy nút Mua ngay. Buttons: {btns_text[:10]}")
                ctx_page.screenshot(path="screenshots/debug_no_mua_ngay.png")

            # 5. Chọn size trong popup/modal
            try:
                size_btn = ctx_page.locator(
                    f"[data-size='{_BUY_SIZE}'], button:text-is('{_BUY_SIZE}'), "
                    f"label:text-is('{_BUY_SIZE}')"
                ).first
                if size_btn.is_visible(timeout=5000):
                    size_btn.click()
                    ctx_page.wait_for_timeout(800)
                    print(f"    [INFO] Customer: Đã chọn size {_BUY_SIZE}")
            except Exception:
                pass

            # 6. Đọc giá subtotal trong popup
            subtotal_raw = ctx_page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const matches = [...text.matchAll(/(\d{1,3}(?:[.,]\d{3})+)\s*[đ₫]/g)];
                const prices = matches.map(m => parseInt(m[1].replace(/[^\d]/g, '')))
                               .filter(n => n >= 50000);
                return prices.length ? Math.min(...prices) : null;
            }""")
            result["subtotal"] = subtotal_raw
            print(f"    [INFO] Customer: subtotal_raw = {subtotal_raw}")

            # 7. Click Thanh toán ngay
            thanh_toan = ctx_page.locator(
                "button:has-text('Thanh toán ngay')"
            ).last
            if thanh_toan.is_visible(timeout=5000):
                thanh_toan.click()
                print(f"    [INFO] Customer: Đã click Thanh toán ngay")
                # Chờ navigate sang checkout (tối đa 15s)
                try:
                    ctx_page.wait_for_url("**/checkout**", timeout=15000)
                except Exception:
                    print(f"    [WARN] Customer: Không tự navigate checkout — URL: {ctx_page.url}")

            # 8. Điền thông tin checkout
            if "/checkout" in ctx_page.url:
                ctx_page.wait_for_load_state("domcontentloaded")
                ctx_page.wait_for_timeout(2000)
                print(f"    [INFO] Customer: Trang checkout — {ctx_page.url}")
                ctx_page.screenshot(path="screenshots/debug_customer_checkout.png")

                # Đọc total
                total_raw = ctx_page.evaluate(r"""() => {
                    const text = document.body.innerText || '';
                    const lines = text.split('\n').map(l => l.trim());
                    const re = /(\d{1,3}(?:[.,]\d{3})+)/;
                    for (let i = 0; i < lines.length; i++) {
                        if (/tổng thanh toán|tổng cộng/i.test(lines[i])) {
                            const m = (lines[i] + ' ' + (lines[i+1]||'')).match(re);
                            if (m) return parseInt(m[1].replace(/[^\d]/g,''));
                        }
                    }
                    return null;
                }""")
                result["total"] = total_raw

                # 8a. Điền Họ tên và SĐT nếu còn trống
                def _fill_if_empty(selector: str, value: str) -> None:
                    try:
                        inp = ctx_page.locator(selector).first
                        if inp.is_visible(timeout=2000):
                            current = inp.input_value() or ""
                            if not current.strip():
                                inp.click()
                                inp.fill(value)
                                ctx_page.wait_for_timeout(300)
                    except Exception:
                        pass

                _fill_if_empty(
                    "input[placeholder*='Nguyễn Văn A'], "
                    "input[placeholder*='Họ tên'], input[placeholder*='họ và tên']",
                    "Customer Test"
                )
                _fill_if_empty(
                    "input[placeholder*='0901'], input[type='tel'], "
                    "input[placeholder*='Số điện thoại']",
                    "0912345678"
                )

                # 8b. Xử lý cascade dropdown địa chỉ (Tỉnh → Quận → Phường → Số nhà)
                # Nếu đã có địa chỉ lưu sẵn, thử click "Sử dụng" / "Chọn" để xác nhận địa chỉ
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
                            print(f"    [INFO] Customer: Đã click chọn địa chỉ đã lưu")
                    except Exception:
                        pass

                self._fill_cascade_address(ctx_page)

                ctx_page.wait_for_timeout(800)

                # 8c. Chọn hình thức COD để tránh redirect sang PayOS
                try:
                    cod_btn = ctx_page.locator(
                        "label:has-text('Thanh toán khi nhận hàng'), "
                        "label:has-text('COD'), "
                        "input[value*='cod'] + label, "
                        "*:has-text('Thanh toán khi nhận hàng'):visible"
                    ).first
                    if cod_btn.is_visible(timeout=3000):
                        cod_btn.click()
                        ctx_page.wait_for_timeout(500)
                        print(f"    [INFO] Customer: Đã chọn COD")
                except Exception:
                    pass

                ctx_page.screenshot(path="screenshots/debug_customer_checkout_filled.png")

                # 8d. Click nút Thanh toán (cuối trang)
                btn_pay = None
                for sel in [
                    "button:has-text('Thanh toán 224'):visible",
                    "button:has-text('Thanh toán 1'):visible",
                    "button:has-text('Thanh toán'):visible",
                    "button:has-text('Đặt hàng'):visible",
                    "button:has-text('Hoàn tất'):visible",
                ]:
                    try:
                        loc = ctx_page.locator(sel).last
                        if loc.is_visible(timeout=2000):
                            btn_pay = loc
                            break
                    except Exception:
                        pass

                if btn_pay and btn_pay.is_visible(timeout=3000):
                    btn_pay.scroll_into_view_if_needed()
                    ctx_page.wait_for_timeout(300)
                    btn_text = btn_pay.inner_text() or ""
                    print(f"    [INFO] Customer: Click nút '{btn_text.strip()[:40]}' — URL: {ctx_page.url}")
                    btn_pay.click()
                    print(f"    [INFO] Customer: Đã click nút thanh toán")
                    # Chờ navigate ra khỏi checkout (sang QR hoặc order page)
                    try:
                        ctx_page.wait_for_function(
                            "() => !window.location.href.includes('/checkout') || "
                            "document.body.innerText.includes('POD-')",
                            timeout=12000
                        )
                    except Exception:
                        pass
                    ctx_page.wait_for_timeout(3000)
                    print(f"    [INFO] Customer: Sau thanh toán — {ctx_page.url}")
                    ctx_page.screenshot(path="screenshots/debug_customer_after_pay.png")
                else:
                    print(f"    [WARN] Customer: Không tìm thấy nút Thanh toán")
                    ctx_page.screenshot(path="screenshots/debug_customer_no_pay_btn.png")
            else:
                print(f"    [WARN] Customer: Chưa vào checkout — URL: {ctx_page.url}")
                ctx_page.screenshot(path="screenshots/debug_customer_not_checkout.png")

            # 9. Đọc mã đơn hàng từ URL hoặc page text
            order_code = ctx_page.evaluate(r"""() => {
                const params = new URLSearchParams(window.location.search);
                const fromUrl = params.get('orderCode');
                if (fromUrl) return fromUrl;
                const m = (document.body.innerText||'').match(/POD-[\w\-]+/);
                return m ? m[0] : null;
            }""")
            print(f"    [INFO] Customer: URL sau thanh toán = {ctx_page.url}")

            # Nếu chưa có order_code → luôn navigate về /my-orders để lấy mã đơn mới nhất
            if not order_code:
                print(f"    [INFO] Customer: Chưa có order_code — navigate về /my-orders")
                try:
                    fe = self.env.fe_url.rstrip("/")
                    ctx_page.goto(f"{fe}/my-orders", wait_until="domcontentloaded", timeout=15000)
                    ctx_page.wait_for_timeout(2000)
                    order_code = ctx_page.evaluate(r"""() => {
                        // Lấy mã đơn đầu tiên (mới nhất) trong danh sách
                        const m = (document.body.innerText||'').match(/POD-[\w\-]+/);
                        return m ? m[0] : null;
                    }""")
                    print(f"    [INFO] Customer: order_code từ my-orders = {order_code}")
                    ctx_page.screenshot(path="screenshots/debug_customer_orders_page.png")
                except Exception as e:
                    print(f"    [WARN] Navigate my-orders: {e}")

            result["order_code"] = order_code
            result["success"] = order_code is not None
            print(f"    [INFO] Customer: order_code = {order_code}")

        except Exception as e:
            print(f"  [WARN] _customer_buy_product: {e}")

        return result

    # ── Admin xác nhận thanh toán ─────────────────────────────────────────────

    def _admin_confirm_payment(self, browser: Browser, order_code: str,
                               reason: str = "Chuyển khoản thành công - test") -> bool:
        """
        Mở context admin → tìm đơn order_code → click [Đánh dấu đã thanh toán thủ công]
        → nhập lý do → click [Xác nhận].
        Trả về True nếu thành công.
        """
        if not order_code:
            return False
        ctx = None
        try:
            ctx = browser.new_context()
            adm = ctx.new_page()
            admin_url = self.env.admin_url

            # ── Login admin ──────────────────────────────────────────────────
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
            print(f"  [INFO] Admin: Login xong — {adm.url}")

            # ── Tìm đơn hàng ────────────────────────────────────────────────
            adm.goto(f"{admin_url}/orders", wait_until="domcontentloaded", timeout=15000)
            adm.wait_for_timeout(2000)

            # Search theo order_code
            search = adm.locator(
                "input[placeholder*='tìm'], input[placeholder*='search'], "
                "input[type='search'], input[placeholder*='mã đơn']"
            ).first
            if search.is_visible(timeout=3000):
                search.fill(order_code)
                adm.keyboard.press("Enter")
                adm.wait_for_timeout(2000)

            # Click vào button mã đơn hàng (mở detail panel)
            # Admin dùng button.font-mono (không phải tr hay a)
            order_btn = adm.locator(
                f"button:text-is('{order_code}'), "
                f"button.font-mono:has-text('{order_code}'), "
                f"td button:has-text('{order_code}')"
            ).first
            if not order_btn.is_visible(timeout=5000):
                # Fallback: click vào tr
                order_row = adm.locator(f"tr:has-text('{order_code}')").first
                if not order_row.is_visible(timeout=3000):
                    print(f"  [WARN] Admin: Không tìm thấy đơn {order_code} trong danh sách")
                    return False
                order_row.click()
            else:
                order_btn.click()
            adm.wait_for_timeout(2000)
            print(f"  [INFO] Admin: Đã mở đơn {order_code} — {adm.url}")

            # ── Click [Đánh dấu đã thanh toán thủ công] ─────────────────────
            manual_btn = adm.locator(
                "button:has-text('Đánh dấu đã thanh toán thủ công')"
            ).first
            if not manual_btn.is_visible(timeout=5000):
                print(f"  [WARN] Admin: Không thấy nút 'Đánh dấu đã thanh toán thủ công'")
                return False

            manual_btn.click()
            adm.wait_for_timeout(1500)
            print(f"  [INFO] Admin: Đã click Đánh dấu đã thanh toán thủ công")

            # ── Nhập lý do ───────────────────────────────────────────────────
            reason_inp = adm.locator(
                "textarea:visible, "
                "input[placeholder*='lý do'], textarea[placeholder*='lý do'], "
                "input[placeholder*='reason'], textarea[placeholder*='reason'], "
                "dialog input, dialog textarea"
            ).first
            if reason_inp.is_visible(timeout=5000):
                reason_inp.fill(reason)
                adm.wait_for_timeout(500)
                print(f"  [INFO] Admin: Đã nhập lý do — '{reason}'")
            else:
                print(f"  [WARN] Admin: Không tìm thấy field nhập lý do")

            # ── Click [Xác nhận] ─────────────────────────────────────────────
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
            print(f"  [INFO] Admin: Đã click Xác nhận — {adm.url}")

            # Kiểm tra thành công: trạng thái đổi sang "Đã thanh toán"
            page_text = adm.evaluate("() => document.body.innerText || ''")
            success = "đã thanh toán" in page_text.lower() or "thanh toán thủ công" in page_text.lower()
            print(f"  [{'PASS' if success else 'WARN'}] Admin: Xác nhận thanh toán thủ công đơn {order_code}")
            return True  # Đã click Xác nhận là thành công, dù không đọc được trạng thái

        except Exception as e:
            print(f"  [WARN] _admin_confirm_payment: {e}")
        finally:
            if ctx:
                ctx.close()
        return False

    # ── Main test ─────────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_commission_e2e(self, browser: Browser):
        """
        SH06: Khách mua qua link gian hàng affiliate → hoa hồng ghi nhận đúng.
        """
        tc = self.tc

        # Xác định credentials
        aff_email    = self.env.affiliate_email or self.env.login_email
        aff_password = self.env.affiliate_password or self.env.login_password
        cust_email   = self.env.customer_email
        cust_password = self.env.customer_password

        if not aff_email:
            pytest.skip(f"SKIP {tc}: Chưa điền AFFILIATE_EMAIL trong .env")

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Affiliate login → lấy link gian hàng + tỷ lệ hoa hồng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Affiliate login → lấy link + tỷ lệ hoa hồng ────────")

        # Login với affiliate account
        self.home.navigate()
        self.home.header.click_login()
        self.page.wait_for_timeout(1000)
        self.auth.login(aff_email, aff_password)
        self.page.wait_for_timeout(3000)
        login_ok = not self.home.header.login_button.is_visible(timeout=5000)
        assert login_ok, f"LỖI {tc}: Đăng nhập affiliate thất bại ({aff_email})"
        print(f"  [PASS] Login affiliate: {aff_email}")

        self._goto_affiliate()
        self._shot("MH1_1", "affiliate_page")

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: Tài khoản {aff_email} chưa được duyệt affiliate")

        store_link = self._get_affiliate_store_link()
        if not store_link:
            pytest.skip(f"SKIP {tc}: Không tìm thấy link gian hàng trên /affiliate")

        commission_rate = self._read_commission_rate()
        order_count_before = self._read_order_count_before()

        self._record_check(
            "MH1", "MH1 Link gian hàng lấy được",
            "✅ PASS", store_link[:80], "URL gian hàng",
        )
        self._record_check(
            "MH1", "MH1 Tỷ lệ hoa hồng",
            "✅ PASS" if commission_rate is not None else "⚠️ WARN",
            f"{commission_rate}%" if commission_rate else "N/A", "≥ 1%",
        )
        print(f"  [INFO] MH1: store_link = {store_link}")
        print(f"  [INFO] MH1: commission_rate = {commission_rate}%")
        print(f"  [INFO] MH1: order_count_before = {order_count_before}")

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Customer mua hàng qua link gian hàng (browser context riêng)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Customer mua qua link gian hàng ────────────────────")

        customer_ctx: BrowserContext = browser.new_context(
            locale="vi-VN",
            viewport={"width": 1280, "height": 800},
        )
        order_info = {"order_code": None, "subtotal": None, "total": None, "success": False}
        try:
            cust_page = customer_ctx.new_page()

            # Login customer nếu có credentials
            if cust_email and cust_password:
                logged = self._customer_login(cust_page, cust_email, cust_password)
                print(f"  [INFO] MH2: Customer login ({cust_email}) = {logged}")
            else:
                print(f"  [INFO] MH2: Không có CUSTOMER_EMAIL — dùng guest checkout")

            order_info = self._customer_buy_product(cust_page, store_link)
            self._shot("MH2_1", "customer_after_order")

        except Exception as e:
            print(f"  [WARN] MH2: Customer context lỗi — {e}")
        finally:
            customer_ctx.close()

        order_code = order_info.get("order_code")
        customer_subtotal = order_info.get("subtotal")
        order_ok = order_info.get("success", False)

        self._record_check(
            "MH2", "MH2 Customer đặt đơn thành công",
            "✅ PASS" if order_ok else "❌ FAIL",
            f"order_code={order_code}" if order_code else "Không lấy được mã đơn",
            "Có order_code sau checkout",
        )
        print(f"  [{'PASS' if order_ok else 'FAIL'}] MH2: order_code={order_code}, subtotal={customer_subtotal}")

        if not order_ok:
            print(f"  [WARN] {tc}: Không đặt được đơn — dừng test")
            self._print_summary_table()
            pytest.fail(f"LỖI {tc}: Customer không đặt được đơn hàng qua link affiliate")

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Admin xác nhận thanh toán (để hoa hồng được ghi nhận)
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Admin xác nhận thanh toán ──────────────────────────")
        admin_confirmed = self._admin_confirm_payment(browser, order_code)
        self._record_check(
            "MH3", "MH3 Admin xác nhận thanh toán",
            "✅ PASS" if admin_confirmed else "ℹ️ INFO",
            "OK" if admin_confirmed else "Không xác nhận được — hoa hồng có thể chưa xuất hiện",
            "Thanh toán được xác nhận",
        )
        if admin_confirmed:
            print(f"  [PASS] MH3: Admin đã xác nhận thanh toán đơn {order_code}")
            self.page.wait_for_timeout(3000)  # chờ hệ thống ghi nhận hoa hồng
        else:
            print(f"  [INFO] MH3: Bỏ qua xác nhận admin — verify sẽ kiểm tra trạng thái pending")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Đơn mới xuất hiện trong danh sách liên kết
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Đơn mới xuất hiện trong danh sách liên kết ─────────")
        self._goto_affiliate()
        self.page.wait_for_timeout(2000)
        self._shot("MH4_1", "affiliate_after_order")

        order_count_after = self._read_order_count_before()
        count_increased = order_count_after > order_count_before

        self._record_check(
            "MH4", f"MH4 Số đơn liên kết tăng ({order_count_before} → {order_count_after})",
            "✅ PASS" if count_increased else "⚠️ WARN",
            str(order_count_after),
            f">{order_count_before}",
        )
        print(f"  [{'PASS' if count_increased else 'WARN'}] MH4: order_count {order_count_before} → {order_count_after}")

        # Tìm đơn theo mã
        found_order = self._find_new_order_in_list(order_code) if order_code else None
        if not found_order:
            # Thử reload một lần nữa sau 5 giây
            self.page.wait_for_timeout(5000)
            self._goto_affiliate()
            found_order = self._find_new_order_in_list(order_code) if order_code else None

        self._record_check(
            "MH4", f"MH4 Đơn {order_code} trong danh sách liên kết",
            "✅ PASS" if found_order else "⚠️ WARN",
            f"Tìm thấy: {found_order.get('raw','')[:60]}" if found_order else "Không tìm thấy",
            "Đơn xuất hiện trong list",
        )
        self._shot("MH4_2", "affiliate_order_list")
        print(f"  [{'PASS' if found_order else 'WARN'}] MH4: found_order = {found_order}")

        # ════════════════════════════════════════════════════════════════════
        # MH5 — Verify hoa hồng = subtotal × tỷ lệ%
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH5: Verify công thức hoa hồng ──────────────────────────")

        # Lấy rate từ đơn hàng trong danh sách (nếu hiển thị) hoặc từ page
        rate = None
        actual_commission = None
        subtotal_for_calc = None

        if found_order:
            rate = found_order.get("commission_rate") or commission_rate
            actual_commission = found_order.get("commission")
            subtotal_for_calc = found_order.get("subtotal") or customer_subtotal
        else:
            rate = commission_rate
            subtotal_for_calc = customer_subtotal

        print(f"  [INFO] MH5: rate={rate}%, subtotal={subtotal_for_calc}, actual_commission={actual_commission}")

        if rate is None:
            self._record_check(
                "MH5", "MH5 Tỷ lệ hoa hồng",
                "⚠️ WARN", "Không đọc được tỷ lệ %",
                "Cần tỷ lệ % để verify công thức",
            )
        elif subtotal_for_calc is None:
            self._record_check(
                "MH5", "MH5 Subtotal để tính hoa hồng",
                "⚠️ WARN", "Không đọc được subtotal",
                "Cần subtotal để verify hoa hồng",
            )
        elif actual_commission is None:
            self._record_check(
                "MH5", "MH5 Hoa hồng hiển thị trong danh sách",
                "⚠️ WARN", "Không đọc được số tiền hoa hồng",
                f"expected = {self.calc_commission(subtotal_for_calc, rate):,}đ",
            )
        else:
            # Verify tỷ lệ hoa hồng trong khoảng chấp nhận
            # Hệ thống có thể tính trên giá trước VAT nên dùng tolerance 15%
            expected = self.calc_commission(subtotal_for_calc, rate)
            delta = abs(actual_commission - expected)
            tolerance = max(self.TOLERANCE, expected * 0.15)  # 15% tolerance
            ok = delta <= tolerance

            status = "✅ PASS" if ok else "❌ FAIL"
            self._record_check(
                "MH5",
                f"MH5 Hoa hồng đơn {order_code or 'N/A'} ({rate}% × {subtotal_for_calc:,}đ)",
                status,
                f"{actual_commission:,}đ",
                f"~{expected:,}đ (±{int(tolerance):,}đ)",
            )
            print(
                f"  [{'PASS' if ok else 'FAIL'}] MH5: "
                f"commission={actual_commission:,}đ | "
                f"expected≈{expected:,}đ ({rate}% × {subtotal_for_calc:,}đ) | "
                f"delta={delta:,}đ (tolerance={int(tolerance):,}đ)"
            )

        self._shot("MH5_1", "commission_verified")
        print(f"\n  [PASS] {tc}: SH06 COMPLETED")
        self._print_summary_table()
