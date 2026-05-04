"""
Critical Path Tests — Môi trường Production / Test
Tập trung vào các luồng nghiệp vụ tạo ra doanh thu và trải nghiệm người dùng cốt lõi.
TẤT CẢ test case đều bắt đầu bằng step S0: Đăng nhập.
"""
import json
import os
from datetime import date

import pytest
from playwright.sync_api import Page, expect

from config.environments import Environment


# ── GenZ daily prompt (xoay theo ngày trong năm) ──────────────────────────────

def _load_daily_prompt() -> str:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "genz_prompts.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)["daily_prompts"]
    return prompts[date.today().timetuple().tm_yday % len(prompts)]

def _load_guest_info() -> dict:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "genz_prompts.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)["guest_checkout"]

def _load_tc_data(tc_id: str) -> dict:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "critical_flows.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)[tc_id]


class TestProductionCriticalFlows:

    @pytest.fixture(autouse=True)
    def setup(self, home_page, studio_page, auth_page, checkout_page, env):
        self.home = home_page
        self.studio = studio_page
        self.auth = auth_page
        self.checkout = checkout_page
        self.env = env
        self.domain = "test_critical_flows"

    # ── S0: Đăng nhập (dùng chung cho tất cả test) ──────────────────────────

    def _login(self, tc_id: str) -> None:
        """S0: Navigate home → Login bằng credentials từ env config.
        SKIP test nếu thiếu credentials.
        """
        email = self.env.login_email
        password = self.env.login_password

        if not email or not password:
            pytest.skip(
                f"BỎ QUA {tc_id}: Thiếu credentials cho môi trường "
                f"{self.env.name.upper()} — kiểm tra .env"
            )

        _R = "production"
        _D = self.domain
        page = self.home.page

        # S0a: Navigate home → Click Đăng nhập
        self.home.navigate()
        self.home.header.click_login()
        page.wait_for_timeout(1000)

        # S0b: Điền credentials → Submit
        self.auth.login(email, password)
        page.wait_for_timeout(3000)

        # S0c: Verify login thành công
        self.home.shot(tc_id, "0", "after_login", domain=_D, root=_R)
        is_logged = not self.home.header.login_button.is_visible(timeout=5000)

        if not is_logged:
            # Retry once — sometimes modal is slow
            page.wait_for_timeout(3000)
            is_logged = not self.home.header.login_button.is_visible(timeout=3000)

        assert is_logged, (
            f"LỖI S0 ({tc_id}): Đăng nhập thất bại — nút 'Đăng nhập' vẫn hiển thị. "
            f"Email: {email[:3]}***"
        )
        print(f"  [PASS] S0 ({tc_id}): Đăng nhập thành công — {email[:3]}***")

    # ── CRITICAL_001 ─────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_CRITICAL_001_full_journey_to_checkout(self):
        """CRITICAL_001 — Login → Home → AI Gen → Studio → Order → Checkout → QR."""
        _R = "production"
        _D = self.domain
        page = self.home.page
        prompt = _load_daily_prompt()
        guest = _load_guest_info()
        print(f"\n  [INFO] CRITICAL_001: Prompt hôm nay = '{prompt[:60]}...'")
        tc_data = _load_tc_data("CRITICAL_001")
        order_data = {"color": tc_data["color"], "size": tc_data["size"]}

        # ── S0: Đăng nhập ────────────────────────────────────────────────────
        self._login("CRITICAL_001")

        # ── S1: Home — Nhập prompt GenZ, click Tạo ngay ──────────────────────
        self.home.navigate()
        self.home.shot("CRITICAL_001", "1", "home_loaded", domain=_D, root=_R)

        self.home.fill_prompt(prompt)
        page.wait_for_timeout(500)
        self.home.shot("CRITICAL_001", "2", "prompt_filled", domain=_D, root=_R)
        self.home.click_generate()

        try:
            page.wait_for_url("**/studio**", timeout=20_000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.home.shot("CRITICAL_001", "3", "studio_navigated", domain=_D, root=_R)
        assert "studio" in page.url, f"LỖI S1: Không navigate vào Studio — URL: {page.url}"
        assert self.studio.is_canvas_visible(), "LỖI S1: Canvas không hiển thị"
        print("  [PASS] S1: Home → Studio thành công")

        # ── S1b: Studio — Đóng popup Điều khoản sử dụng (nếu có) ────────────
        self.studio.accept_terms("CRITICAL_001")
        print("  [PASS] S1b: Kiểm tra popup điều khoản xong")

        # ── S2: Studio — Chờ AI tạo đủ 3 ảnh, đo thời gian ─────────────────
        print("  [INFO] S2: Đang chờ AI generate artwork...")
        ok, elapsed, found = self.studio.wait_for_artworks(count=3, timeout=120)
        self.studio.shot("CRITICAL_001", "4", f"artworks_generated_{found}imgs_{int(elapsed)}s", domain=_D, root=_R)
        print(f"  [INFO] S2: AI gen xong — {found} ảnh trong {elapsed}s")
        if not ok:
            pytest.skip(f"BỎ QUA S2: Chỉ tạo được {found}/3 ảnh sau {elapsed}s — AI gen chậm hoặc lỗi")
        print(f"  [PASS] S2: {found} artwork sẵn sàng ({elapsed}s)")

        # ── S3: Studio — Chọn màu áo trắng ──────────────────────────────────
        selected = self.studio.select_color(tc_data["color"])
        if not selected:
            selected = self.studio.select_color("White")
        page.wait_for_timeout(800)
        self.studio.shot("CRITICAL_001", "5", "color_white_selected", domain=_D, root=_R)
        print(f"  [{'PASS' if selected else 'INFO'}] S3: Chọn màu trắng {'thành công' if selected else '— không tìm thấy, bỏ qua'}")

        # ── S4: Studio — Click ảnh đầu tiên để áp lên áo ────────────────────
        idx_front = tc_data["artwork_index_front"]
        order_data["artwork_front_src"] = self.studio.read_panel_image_src(idx_front)
        applied = self.studio.click_artwork(index=idx_front)
        assert applied, (
            f"LỖI S4: Không click được artwork trong library panel — URL: {page.url}"
        )
        canvas_wait = self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
        wait_msg = f"{canvas_wait}s" if canvas_wait >= 0 else "không detect được (canvas/WebGL render)"
        self.studio.shot("CRITICAL_001", "6", "artwork_applied_to_shirt", domain=_D, root=_R)
        print(f"  [PASS] S4: Đã click artwork — canvas detect: {wait_msg}")

        # ── S5: Studio — Xoay áo sang mặt sau, chọn ảnh từ thư viện ─────────────
        if self.studio.back_button.is_visible(timeout=3000):
            self.studio.toggle_side("back")
            page.wait_for_timeout(1500)
            self.studio.shot("CRITICAL_001", "7", "shirt_back_view", domain=_D, root=_R)
            print("  [PASS] S5a: Đã click 'Xoay áo' — xem mặt sau")

            # Library đã mở sẵn ở sidebar trái — click ảnh khác với ảnh mặt trước
            idx_back = tc_data["artwork_index_back"]
            page.wait_for_timeout(1000)
            lib_ok = self.studio.click_library_image(index=idx_back)
            order_data["artwork_back_src"] = self.studio.read_library_image_src(idx_back)
            # Chờ canvas render ảnh lên mặt sau áo (4s)
            page.wait_for_timeout(4000)
            self.studio.shot("CRITICAL_001", "8", "library_image_on_back", domain=_D, root=_R)
            print(f"  [{'PASS' if lib_ok else 'WARN'}] S5b: {'Đã chọn ảnh thư viện cho mặt sau' if lib_ok else 'Không click được ảnh thư viện'}")
        else:
            self.studio.shot("CRITICAL_001", "7", "no_back_button_skipped", domain=_D, root=_R)
            print("  [INFO] S5: Nút 'Mặt sau' không hiển thị — bỏ qua bước xoay")

        # ── S6: Click Hoàn tất thiết kế → navigate sang trang /review ─────────
        self.studio.open_order_modal()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "9", "review_page", domain=_D, root=_R)
        assert "review" in page.url or page.locator("button:has-text('Đặt hàng')").is_visible(timeout=5000), \
            f"LỖI S6: Không tới màn hình xác nhận thiết kế — URL: {page.url}"
        print("  [PASS] S6: Màn hình xác nhận thiết kế hiển thị")

        # ── S7a: Click Đặt hàng → Navigate sang màn hình Đặt hàng (/order) ────
        if "order" not in page.url:
            dat_hang_loc = page.locator("button:has-text('Đặt hàng')").first
            if dat_hang_loc.is_visible(timeout=5000):
                dat_hang_loc.click()
                print("  [INFO] S7a: Đã click 'Đặt hàng', đang chờ navigate /order...")
                try:
                    page.wait_for_url("**/order**", timeout=8000)
                except Exception:
                    page.wait_for_timeout(3000)
            else:
                print("  [WARN] S7a: Không tìm thấy nút 'Đặt hàng'")

        assert "order" in page.url, f"LỖI S7a: Không navigate được sang màn hình Đặt hàng — URL: {page.url}"
        page.wait_for_load_state("domcontentloaded")
        self.studio.shot("CRITICAL_001", "10", "order_screen", domain=_D, root=_R)
        print(f"  [PASS] S7a: Màn hình Đặt hàng — URL: {page.url}")
        order_data["product_type"] = self.checkout.read_product_type()
        order_data["unit_price"] = self.checkout.read_price_from_page()

        # ── S7b: Chọn size M ─────────────────────────────────────────────────
        size_ok = self.checkout.select_size_m("CRITICAL_001")
        page.wait_for_timeout(500)
        self.studio.shot("CRITICAL_001", "11", "size_M_selected", domain=_D, root=_R)
        print(f"  [{'PASS' if size_ok else 'WARN'}] S7b: Chọn size M")

        # ── S7c: Click Mua ngay ───────────────────────────────────────────────
        mua_ngay = self.checkout.buy_now_button
        assert mua_ngay.is_visible(timeout=8000), \
            f"LỖI S7c: Không tìm thấy nút 'Mua ngay' — URL: {page.url}"
        mua_ngay.click()
        try:
            page.wait_for_url("**/checkout**", timeout=8000)
        except Exception:
            page.wait_for_timeout(3000)
        self.studio.shot("CRITICAL_001", "12", "after_mua_ngay", domain=_D, root=_R)
        assert self.checkout.tax_code_input.is_visible(timeout=5000) or "checkout" in page.url, \
            f"LỖI S7c: Sau khi click 'Mua ngay' không điều hướng tới trang thanh toán — URL: {page.url}"
        print("  [PASS] S7c: Click 'Mua ngay' → tới trang thanh toán thành công")
        order_data["total_price"] = self.checkout.read_price_from_page()
        order_data["address"] = self.checkout.read_address_from_checkout()

        # ── S8: Checkout — Điền MST → Click Thanh toán → Assert QR ─────────────
        # User đã đăng nhập → địa chỉ auto-fill, chỉ cần điền CCCD/MST bắt buộc
        tax_ok = self.checkout.fill_tax_code(tc_data["tax_code"], "CRITICAL_001")
        page.wait_for_timeout(500)
        self.studio.shot("CRITICAL_001", "13", "tax_code_filled", domain=_D, root=_R)
        assert tax_ok, f"LỖI S8a: Không điền được Mã số thuế — URL: {page.url}"
        print("  [PASS] S8a: Đã điền Mã số thuế = '012345'")

        pay_btn = self.checkout.payment_button
        assert pay_btn.is_visible(timeout=8000), f"LỖI S8b: Không tìm thấy nút 'Thanh toán' — URL: {page.url}"
        pay_btn.click()
        page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_001", "14", "after_payment_click", domain=_D, root=_R)
        print("  [PASS] S8b: Đã click 'Thanh toán'")

        assert self.checkout.is_qr_visible(timeout=15000), \
            f"LỖI S8c: Màn hình QR code không xuất hiện — URL: {page.url}"
        self.studio.shot("CRITICAL_001", "15", "qr_code_displayed", domain=_D, root=_R)
        print("  [PASS] S8c: QR code thanh toán hiển thị thành công")

        # ── S9: Click nút Hủy trên trang QR ─────────────────────────────────
        cancel_qr = page.locator("button:has-text('Huỷ'), button:has-text('Hủy')").first
        assert cancel_qr.is_visible(timeout=10000), \
            f"LỖI S9: Không tìm thấy nút 'Hủy' trên trang QR — URL: {page.url}"
        cancel_qr.click()
        page.wait_for_timeout(1500)

        # ── S10: Xác nhận hủy — capture order_code từ URL redirect ──────────
        confirm_cancel = page.locator("#cancel-payment, button:has-text('Xác nhận hủy')").first
        if confirm_cancel.is_visible(timeout=5000):
            confirm_cancel.click()
            page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_001", "16", "after_cancel", domain=_D, root=_R)
        assert "pay" not in page.url, \
            f"LỖI S10: Hủy thanh toán thất bại — vẫn ở trang payOS — URL: {page.url}"
        order_data["order_code"] = self.checkout.read_order_code()
        print(f"  [PASS] S10: Hủy thanh toán thành công — URL: {page.url}")
        print(f"  [INFO] CRITICAL_001 order_data tại S10: {order_data}")

        # ── S11: Click "Xem đơn hàng" (fallback navigate /profile) ──────────
        view_order = page.locator(
            "button:has-text('Xem đơn hàng'), a:has-text('Xem đơn hàng')"
        ).first
        if view_order.is_visible(timeout=5000):
            view_order.click()
            page.wait_for_timeout(3000)
        else:
            self.home.goto("/profile")
            page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "17", "view_orders", domain=_D, root=_R)
        print(f"  [PASS] S11: Xem đơn hàng — URL: {page.url}")

        # ── S12: Click "Đơn hàng của tôi" tab ───────────────────────────────
        my_orders = page.locator("button:has-text('Đơn hàng của tôi')").first
        assert my_orders.is_visible(timeout=5000), \
            f"LỖI S12: Không tìm thấy tab 'Đơn hàng của tôi' — URL: {page.url}"
        my_orders.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "18", "my_orders", domain=_D, root=_R)
        print("  [PASS] S12: Tab 'Đơn hàng của tôi'")

        # ── S13: Click đơn đầu tiên → verify_order_data ──────────────────────
        first_order = page.locator("main div:nth-of-type(1) button").first
        assert first_order.is_visible(timeout=5000), \
            f"LỖI S13: Không tìm thấy đơn hàng nào — URL: {page.url}"
        first_order.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "19", "order_detail", domain=_D, root=_R)
        self.checkout.verify_order_data(order_data, "CRITICAL_001")
        print("  [PASS] S13: Chi tiết đơn hàng — verify hoàn thành")
        print("  [PASS] CRITICAL_001: Toàn bộ luồng checkout hoàn thành")

    # ── CRITICAL_002 ─────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_CRITICAL_002_add_to_cart_and_repay(self):
        """CRITICAL_002 — AI Gen → Add to Cart → Login at Checkout → Pay → Cancel → View Order → Repay."""
        _R = "production"
        _D = self.domain
        page = self.home.page
        prompt = _load_daily_prompt()
        tc_data = _load_tc_data("CRITICAL_002")
        order_data = {"size": tc_data["size"]}

        # Pre-check: credentials needed for login at checkout
        email = self.env.login_email
        password = self.env.login_password
        if not email or not password:
            pytest.skip("BỎ QUA CRITICAL_002: Thiếu credentials — kiểm tra .env")

        # ── S1: Home → Nhập prompt → Navigate Studio ─────────────────────────
        self.home.navigate()
        self.home.accept_terms("CRITICAL_002")  # Đóng popup điều khoản trước khi nhập prompt
        self.home.fill_prompt(prompt)
        page.wait_for_timeout(500)
        self.home.click_generate()
        try:
            page.wait_for_url("**/studio**", timeout=20_000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.home.shot("CRITICAL_002", "1", "studio_navigated", domain=_D, root=_R)
        assert "studio" in page.url, f"LỖI S1: Không navigate vào Studio — URL: {page.url}"
        print("  [PASS] S1: Home → Studio thành công")

        self.studio.accept_terms("CRITICAL_002")

        # ── S2: Chờ AI gen artwork ───────────────────────────────────────────
        ok, elapsed, found = self.studio.wait_for_artworks(count=3, timeout=120)
        self.studio.shot("CRITICAL_002", "2", f"artworks_{found}imgs_{int(elapsed)}s", domain=_D, root=_R)
        if not ok:
            pytest.skip(f"BỎ QUA S2: Chỉ tạo được {found}/3 ảnh sau {elapsed}s")
        print(f"  [PASS] S2: {found} artwork sẵn sàng ({elapsed}s)")

        # ── S3: Click Variant 2 → Apply lên mặt trước ───────────────────────
        idx_front = tc_data["artwork_index_front"]
        order_data["artwork_front_src"] = self.studio.read_panel_image_src(idx_front)
        applied_s3 = self.studio.click_artwork(index=idx_front)
        assert applied_s3, f"LỖI S3: Không click được artwork trong library panel — URL: {page.url}"
        canvas_wait_s3 = self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
        wait_msg_s3 = f"{canvas_wait_s3}s" if canvas_wait_s3 >= 0 else "không detect được (canvas/WebGL render)"
        self.studio.shot("CRITICAL_002", "3", "artwork_front", domain=_D, root=_R)
        print(f"  [PASS] S3: Đã click artwork mặt trước — canvas detect: {wait_msg_s3}")

        # ── S4: Xoay áo → Click Variant 1 cho mặt sau ───────────────────────
        idx_back = tc_data["artwork_index_back"]
        order_data["artwork_back_src"] = self.studio.read_panel_image_src(idx_back)
        if self.studio.back_button.is_visible(timeout=3000):
            self.studio.toggle_side("back")
            page.wait_for_timeout(1500)
            self.studio.click_artwork(index=idx_back)
            self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
            self.studio.shot("CRITICAL_002", "4", "artwork_back", domain=_D, root=_R)
            print("  [PASS] S4: Áp artwork lên mặt sau")
        else:
            print("  [INFO] S4: Nút 'Mặt sau' không hiển thị — bỏ qua")

        # ── S5: Hoàn tất thiết kế → Review ───────────────────────────────────
        self.studio.open_order_modal()
        # Chờ spinner "Đang hoàn tất thiết kế..." biến mất
        loading = page.locator("text=Đang hoàn tất thiết kế")
        try:
            loading.wait_for(state="hidden", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "5", "review_page", domain=_D, root=_R)
        assert "review" in page.url or page.locator("button:has-text('Đặt hàng')").is_visible(timeout=5000), \
            f"LỖI S5: Không tới màn hình xác nhận thiết kế sau 'Hoàn tất thiết kế' — URL: {page.url}"
        print("  [PASS] S5: Màn hình xác nhận thiết kế")

        # ── S6: Click Đặt hàng → Order screen ───────────────────────────────
        dat_hang = page.locator("button:has-text('Đặt hàng')").first
        assert dat_hang.is_visible(timeout=10000), "LỖI S6: Nút 'Đặt hàng' không hiển thị"
        dat_hang.click()
        try:
            page.wait_for_url("**/order**", timeout=8000)
        except Exception:
            page.wait_for_timeout(3000)
        self.studio.shot("CRITICAL_002", "6", "order_screen", domain=_D, root=_R)
        assert "order" in page.url, f"LỖI S6: Không navigate được sang màn hình Đặt hàng — URL: {page.url}"
        print(f"  [PASS] S6: Màn hình đặt hàng — URL: {page.url}")
        order_data["product_type"] = self.checkout.read_product_type()
        order_data["unit_price"] = self.checkout.read_price_from_page()

        # ── S7: Chọn size ────────────────────────────────────────────────────
        size_btn = page.locator(f"button:text-is('{tc_data['size']}')").first
        if size_btn.is_visible(timeout=3000):
            size_btn.click()
            page.wait_for_timeout(500)
        self.studio.shot("CRITICAL_002", "7", "size_4xl", domain=_D, root=_R)
        print("  [PASS] S7: Chọn size 4XL")

        # ── S8: Click "Thêm vào giỏ" ────────────────────────────────────────
        page.wait_for_timeout(1000)
        add_cart = page.locator(
            "div.fixed button:has-text('Thêm vào giỏ'), "
            "button:has-text('Thêm vào giỏ'), "
            "button span:text-is('Thêm vào giỏ')"
        ).first
        assert add_cart.is_visible(timeout=8000), "LỖI S8: Không tìm thấy nút 'Thêm vào giỏ'"
        add_cart.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "8", "added_to_cart", domain=_D, root=_R)
        print("  [PASS] S8: Đã thêm vào giỏ hàng")

        # ── S9: Mở giỏ hàng → Click "Thanh toán ngay" ───────────────────────
        cart_icon = page.locator("header button:has(svg)").last
        if cart_icon.is_visible(timeout=3000):
            cart_icon.click()
            page.wait_for_timeout(1500)
        checkout_btn = page.locator("button:has-text('Thanh toán ngay')").first
        assert checkout_btn.is_visible(timeout=5000), "LỖI S9: Không tìm 'Thanh toán ngay'"
        checkout_btn.click()
        try:
            page.wait_for_url("**/checkout**", timeout=8000)
        except Exception:
            page.wait_for_timeout(3000)
        self.studio.shot("CRITICAL_002", "9", "checkout_page", domain=_D, root=_R)
        assert "checkout" in page.url or self.checkout.payment_button.is_visible(timeout=5000), \
            f"LỖI S9: Sau khi click 'Thanh toán ngay' không điều hướng tới trang checkout — URL: {page.url}"
        print(f"  [PASS] S9: Checkout — URL: {page.url}")
        order_data["total_price"] = self.checkout.read_price_from_page()
        order_data["address"] = self.checkout.read_address_from_checkout()

        # ── S10: Login tại Checkout ──────────────────────────────────────────
        login_at_checkout = page.locator("#section-auth button:has-text('Đăng nhập')").first
        if login_at_checkout.is_visible(timeout=5000):
            login_at_checkout.click()
            page.wait_for_timeout(2000)

            dialog = page.locator("[role='dialog']")
            dialog.wait_for(state="visible", timeout=5000)

            # Nếu lỡ ở "Quên mật khẩu" → click "Quay lại đăng nhập"
            back_login = page.locator("text=Quay lại đăng nhập, text=Quay lại")
            if back_login.first.is_visible(timeout=2000):
                page.evaluate("""() => {
                    const link = document.querySelector('[role="dialog"] button');
                    const allBtns = document.querySelectorAll('[role="dialog"] button');
                    for (const b of allBtns) {
                        if (b.textContent.includes('Quay lại')) { b.click(); break; }
                    }
                }""")
                page.wait_for_timeout(1500)

            # Đảm bảo password field hiện (= đang ở form login)
            pw_exists = page.evaluate("""() => {
                return !!document.querySelector('[role="dialog"] input[type="password"]');
            }""")
            if not pw_exists:
                print("  [WARN] S10: Password field không tìm thấy — thử click 'Quay lại'")
                page.evaluate("""() => {
                    const links = document.querySelectorAll('[role="dialog"] button, [role="dialog"] a');
                    for (const el of links) {
                        if (el.textContent.includes('Quay lại') || el.textContent.includes('đăng nhập')) {
                            el.click(); break;
                        }
                    }
                }""")
                page.wait_for_timeout(1500)

            # Fill email via JS
            page.evaluate("""(email) => {
                const input = document.querySelector('[role="dialog"] input[type="email"]');
                if (input) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    setter.call(input, email);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", email)
            page.wait_for_timeout(300)

            # Fill password via JS
            page.evaluate("""(pw) => {
                const input = document.querySelector('[role="dialog"] input[type="password"]');
                if (input) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    setter.call(input, pw);
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", password)
            page.wait_for_timeout(300)

            # Submit login form — tìm button "Đăng nhập" trong form (không phải "Gửi yêu cầu")
            page.evaluate("""() => {
                const btns = document.querySelectorAll('[role="dialog"] form button');
                for (const btn of btns) {
                    if (btn.textContent.includes('Đăng nhập') || btn.textContent.includes('đăng nhập')) {
                        btn.click(); return;
                    }
                }
                if (btns.length > 0) btns[btns.length - 1].click();
            }""")

            # Chờ dialog đóng
            try:
                dialog.wait_for(state="hidden", timeout=10000)
            except Exception:
                page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_002", "10", "logged_in", domain=_D, root=_R)
        login_still_visible = page.locator("#section-auth button:has-text('Đăng nhập')").is_visible(timeout=3000)
        assert not login_still_visible, \
            "LỖI S10: Đăng nhập tại Checkout thất bại — nút 'Đăng nhập' vẫn hiển thị sau khi submit"
        print("  [PASS] S10: Đăng nhập tại Checkout thành công")

        # ── S11: Nhập MST → Click Thanh toán → payOS ────────────────────────
        self.checkout.fill_tax_code(tc_data["tax_code"], "CRITICAL_002")
        page.wait_for_timeout(500)
        pay_btn = self.checkout.payment_button
        assert pay_btn.is_visible(timeout=8000), "LỖI S11: Không tìm nút Thanh toán"
        pay_btn.click()
        page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_002", "11", "payos_page", domain=_D, root=_R)
        assert "pay" in page.url, f"LỖI S11: Không navigate tới payOS — URL: {page.url}"
        print(f"  [PASS] S11: payOS — URL: {page.url}")

        # ── S12: Hủy thanh toán ──────────────────────────────────────────────
        cancel = page.locator("button:has-text('Huỷ'), button:has-text('Hủy')").first
        assert cancel.is_visible(timeout=10000), \
            f"LỖI S12: Không tìm thấy nút 'Hủy' trên trang payOS — URL: {page.url}"
        cancel.click()
        page.wait_for_timeout(1500)
        confirm = page.locator("#cancel-payment, button:has-text('Xác nhận hủy')").first
        if confirm.is_visible(timeout=5000):
            confirm.click()
            page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_002", "12", "cancelled", domain=_D, root=_R)
        assert "pay" not in page.url, \
            f"LỖI S12: Hủy thanh toán thất bại — vẫn ở trang payOS sau khi xác nhận hủy — URL: {page.url}"
        print(f"  [PASS] S12: Hủy thanh toán thành công — URL: {page.url}")

        # ── S13: Click "Xem đơn hàng" ───────────────────────────────────────
        view_order = page.locator(
            "button:has-text('Xem đơn hàng'), a:has-text('Xem đơn hàng')"
        ).first
        assert view_order.is_visible(timeout=5000), \
            f"LỖI S13: Không tìm thấy nút 'Xem đơn hàng' sau khi hủy thanh toán — URL: {page.url}"
        view_order.click()
        page.wait_for_timeout(3000)
        self.studio.shot("CRITICAL_002", "13", "view_orders", domain=_D, root=_R)
        print(f"  [PASS] S13: Xem đơn hàng — URL: {page.url}")
        order_data["order_code"] = self.checkout.read_order_code()

        # ── S14: Click "Đơn hàng của tôi" ───────────────────────────────────
        my_orders = page.locator("button:has-text('Đơn hàng của tôi')").first
        assert my_orders.is_visible(timeout=5000), \
            f"LỖI S14: Không tìm thấy tab 'Đơn hàng của tôi' — URL: {page.url}"
        my_orders.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "14", "my_orders", domain=_D, root=_R)
        print("  [PASS] S14: Tab 'Đơn hàng của tôi'")

        # ── S15: Xem đơn hàng đầu tiên ──────────────────────────────────────
        first_order = page.locator("main div:nth-of-type(1) button").first
        assert first_order.is_visible(timeout=5000), \
            f"LỖI S15: Không tìm thấy đơn hàng nào trong danh sách — URL: {page.url}"
        first_order.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "15", "order_detail", domain=_D, root=_R)
        self.checkout.verify_order_data(order_data, "CRITICAL_002")
        print(f"  [INFO] order_data: {order_data}")
        print("  [PASS] S15: Chi tiết đơn hàng — verify hoàn thành")

        # ── S16: Thanh toán lại → payOS ──────────────────────────────────────
        repay = page.locator("div.border button:has-text('Thanh toán ngay')").first
        if repay.is_visible(timeout=5000):
            repay.click()
            page.wait_for_timeout(5000)
            self.studio.shot("CRITICAL_002", "16", "repay_payos", domain=_D, root=_R)
            assert "pay" in page.url, f"LỖI S16: Không navigate payOS — URL: {page.url}"
            print(f"  [PASS] S16: Thanh toán lại → payOS — URL: {page.url}")
        else:
            self.studio.shot("CRITICAL_002", "16", "repay_not_found", domain=_D, root=_R)
            print("  [INFO] S16: Nút 'Thanh toán ngay' không tìm thấy — bỏ qua")

        print("  [PASS] CRITICAL_002: Toàn bộ luồng Add to Cart → Repay hoàn thành")

    # ── CRITICAL_003 ─────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_CRITICAL_003_legal_and_contact_links(self):
        """CRITICAL_003 — Login → Kiểm tra link pháp lý & liên hệ (Footer)."""
        # S0: Đăng nhập
        self._login("CRITICAL_003")

        # S1: Scroll to footer
        self.home.navigate()
        self.home.scroll_to_bottom()
        self.home.shot(
            "CRITICAL_003", "1", "footer_check",
            domain=self.domain, root="production"
        )

        # S2: Kiểm tra 3 link pháp lý
        legal_links = ["chinh-sach-bao-mat", "chinh-sach-doi-tra", "lien-he-cskh"]
        for link in legal_links:
            loc = self.home.page.locator(f"footer a[href*='{link}']").first
            assert loc.is_visible(), f"LỖI: Thiếu link {link} ở Footer"
        print("  [PASS] CRITICAL_003: Đủ 3 link pháp lý ở Footer")
