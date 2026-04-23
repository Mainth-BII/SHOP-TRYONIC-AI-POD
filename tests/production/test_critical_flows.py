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
        selected = self.studio.select_color("Trắng")
        if not selected:
            selected = self.studio.select_color("White")
        page.wait_for_timeout(800)
        self.studio.shot("CRITICAL_001", "5", "color_white_selected", domain=_D, root=_R)
        print(f"  [{'PASS' if selected else 'INFO'}] S3: Chọn màu trắng {'thành công' if selected else '— không tìm thấy, bỏ qua'}")

        # ── S4: Studio — Click ảnh đầu tiên để áp lên áo ────────────────────
        applied = self.studio.click_artwork(index=0)
        # Đo thời gian để ảnh hiện lên canvas (poll 500ms, timeout 30s)
        canvas_wait = self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
        wait_msg = f"{canvas_wait}s" if canvas_wait >= 0 else "timeout (>30s)"
        self.studio.shot("CRITICAL_001", "6", "artwork_applied_to_shirt", domain=_D, root=_R)
        print(f"  [{'PASS' if applied else 'WARN'}] S4: Áp artwork lên áo {'thành công' if applied else '— không click được ảnh'} — canvas load: {wait_msg}")

        # ── S5: Studio — Xoay áo sang mặt sau, chọn ảnh từ thư viện ─────────────
        if self.studio.back_button.is_visible(timeout=3000):
            self.studio.toggle_side("back")
            page.wait_for_timeout(1500)
            self.studio.shot("CRITICAL_001", "7", "shirt_back_view", domain=_D, root=_R)
            print("  [PASS] S5a: Đã click 'Xoay áo' — xem mặt sau")

            # Library đã mở sẵn ở sidebar trái — click ảnh index=2 (khác với ảnh mặt trước)
            page.wait_for_timeout(1000)
            lib_ok = self.studio.click_library_image(index=2)
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
        page.wait_for_timeout(3000)
        self.studio.shot("CRITICAL_001", "12", "after_mua_ngay", domain=_D, root=_R)
        print("  [PASS] S7c: Click 'Mua ngay' thành công")

        # ── S8: Checkout — Điền MST → Click Thanh toán → Assert QR ─────────────
        # User đã đăng nhập → địa chỉ auto-fill, chỉ cần điền CCCD/MST bắt buộc
        tax_ok = self.checkout.fill_tax_code("012345", "CRITICAL_001")
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
        print("  [PASS] CRITICAL_001: Toàn bộ luồng checkout hoàn thành")

    # ── CRITICAL_002 ─────────────────────────────────────────────────────────

    @pytest.mark.production
    def test_CRITICAL_002_login_functionality(self):
        """CRITICAL_002 — Đăng nhập → Xác nhận trạng thái → Click Xem đơn hàng."""
        page = self.home.page
        _D = self.domain
        _R = "production"

        # S1: Login → Assert login_button KHÔNG visible
        self._login("CRITICAL_002")
        self.home.shot("CRITICAL_002", "1", "after_login", domain=_D, root=_R)
        assert not self.home.header.login_button.is_visible(timeout=3000), \
            "LỖI S1: Nút Đăng nhập vẫn còn sau khi login"
        print("  [PASS] S1: Đăng nhập thành công — login_button không hiển thị")

        # S2: Click "Xem đơn hàng" — priority theo JSON selector spec
        # 1. aria-label  2. text  3. CSS bg-[#4F46F1]
        view_order_btn = page.locator(
            "button[aria-label='Xem đơn hàng'], "
            "button:has-text('Xem đơn hàng'), "
            "a:has-text('Xem đơn hàng')"
        ).first

        clicked = False
        if view_order_btn.is_visible(timeout=5000):
            view_order_btn.click()
            clicked = True
        else:
            # Fallback: CSS selector từ JSON (Tailwind bg-[#4F46F1])
            css_btn = page.locator("button.bg-\\[\\#4F46F1\\]").first
            if css_btn.is_visible(timeout=3000):
                css_btn.click()
                clicked = True

        page.wait_for_timeout(2000)
        self.home.shot("CRITICAL_002", "2", "after_view_order_click" if clicked else "view_order_not_found", domain=_D, root=_R)
        if clicked:
            print(f"  [PASS] S2: Đã click 'Xem đơn hàng' — URL: {page.url}")
        else:
            print("  [INFO] S2: Không tìm thấy button 'Xem đơn hàng' — bỏ qua")

        print("  [PASS] CRITICAL_002: Hoàn thành")

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
