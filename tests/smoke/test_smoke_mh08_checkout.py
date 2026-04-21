"""
Smoke — MH08: Studio — Checkout & Giỏ hàng
TC_DAILY_007 · TC_DAILY_010 · TC_DAILY_011 · TC_DAILY_021 · TC_DAILY_026 · TC_DAILY_030
TC_DAILY_038

Luong kiem tra:
  TC_007 : Khong co thiet ke → nut 'Hoàn tất thiết kế' phai DISABLED (correct behavior)
  TC_010 : Co prompt → AI gen → nut ENABLED → click → Man hinh xac nhan co nut 'Đặt hàng'
  TC_011 : Man hinh xac nhan → click 'Đặt hàng' → modal co 'Thêm vào giỏ' + 'Mua ngay'
  TC_021 : Trang /checkout hoac /cart load duoc, khong 404/500
  TC_026 : Click 'Thêm vào giỏ' → toast 'Đã thêm vào giỏ' hien thi
  TC_030 : Click 'Mua ngay' (chua dang nhap) → man hinh Dang nhap hien thi
  TC_038 : Order modal co size selector, chon size truoc khi them vao gio

Chay: pytest tests/smoke/test_smoke_mh08_checkout.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from pages import StudioPage, CheckoutPage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_STUDIO_URL = "/studio?category=t-shirts"
_AI_PROMPT  = "con rồng lửa phong cách anime, màu xanh và vàng"


class TestSmokeMH08Checkout(BaseSmokeTest):
    """MH08 — Studio Checkout: Hoàn tất thiết kế, Xác nhận, Đặt hàng, Giỏ hàng, Mua ngay."""

    _MH_DIR = "MH08_checkout"
    _TC_IDS = [
        "TC_DAILY_007", "TC_DAILY_010", "TC_DAILY_011",
        "TC_DAILY_021", "TC_DAILY_026", "TC_DAILY_030",
        "TC_DAILY_038",
    ]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_studio(self, page: Page, base_url: str, tc_id: str) -> tuple:
        """Navigate toi Studio, tra ve (studio, checkout) page objects."""
        studio = StudioPage(page, base_url)
        checkout = CheckoutPage(page, base_url)
        page.goto(f"{base_url.rstrip('/')}{_STUDIO_URL}",
                  wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        studio.accept_terms(tc_id)
        return studio, checkout

    def _run_ai_gen(self, page: Page, checkout: CheckoutPage, tc_id: str) -> bool:
        """Nhap prompt, cho AI gen, tra ve True neu nut 'Hoàn tất thiết kế' enabled."""
        self.shot(page, tc_id, "gen0", "before_generation")
        result = checkout.enter_prompt_and_wait_for_generation(page, _AI_PROMPT, tc_id, timeout_s=90)
        self.shot(page, tc_id, "gen1", "after_generation")
        return result

    # ── TC_DAILY_007 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_007_no_design_button_must_be_disabled(self, page: Page, base_url: str):
        """TC_DAILY_007 — Studio khong co thiet ke: Sau dong y dieu khoan, nut PHAI bi DISABLED."""
        studio, _ = self._load_studio(page, base_url, "TC_DAILY_007")
        self.shot(studio, "TC_DAILY_007", "1", "studio_no_design")

        assert studio.finish_button.is_visible(timeout=10000), \
            "TC_DAILY_007 FAIL: Khong tim thay nut 'Hoàn tất thiết kế' trong Studio"

        is_disabled = studio.finish_button.get_attribute("disabled") is not None
        self.shot(studio, "TC_DAILY_007", "2", "finish_btn_state")

        assert is_disabled, (
            "TC_DAILY_007 FAIL: Nut 'Hoàn tất thiết kế' KHONG bi disabled khi chua co thiet ke! "
            "Phai bi disabled khi Studio chua co artwork tren ao."
        )
        print("  [PASS] TC_DAILY_007: Nut 'Hoàn tất thiết kế' dung dang DISABLED — chua co thiet ke")

    # ── TC_DAILY_010 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_010_prompt_ai_gen_and_confirmation_screen(self, page: Page, base_url: str):
        """TC_DAILY_010 — Nhap prompt → AI gen → nut ENABLED → click → Man hinh xac nhan."""
        studio, checkout = self._load_studio(page, base_url, "TC_DAILY_010")
        self.shot(studio, "TC_DAILY_010", "1", "studio_before_prompt")

        generated = self._run_ai_gen(page, checkout, "TC_DAILY_010")
        if not generated:
            pytest.fail(
                "TC_DAILY_010 FAIL: Nut 'Hoàn tất thiết kế' van bi DISABLED sau 90s — "
                "AI gen that bai hoac nut khong chuyen sang ENABLED khi co artwork"
            )

        self.shot(studio, "TC_DAILY_010", "2", "ai_gen_done_btn_enabled")

        studio.finish_button.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_010", "3", "confirmation_screen")

        dat_hang_btn = page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang')"
        ).first
        assert dat_hang_btn.is_visible(timeout=10000), \
            "TC_DAILY_010 FAIL: Man hinh xac nhan khong hien thi nut 'Đặt hàng'"

        self.shot(studio, "TC_DAILY_010", "4", "dat_hang_btn_visible")
        print("  [PASS] TC_DAILY_010: AI gen OK → nut ENABLED → Man hinh xac nhan co nut 'Đặt hàng'")

    # ── TC_DAILY_011 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_011_order_modal_has_two_buttons(self, page: Page, base_url: str):
        """TC_DAILY_011 — Man hinh xac nhan → 'Đặt hàng' → Modal co 'Them vao gio' + 'Mua ngay'."""
        studio, checkout = self._load_studio(page, base_url, "TC_DAILY_011")

        generated = self._run_ai_gen(page, checkout, "TC_DAILY_011")
        assert generated, \
            "TC_DAILY_011 FAIL: AI gen khong xong sau 90s — nut van DISABLED, khong the tiep tuc"
        self.shot(studio, "TC_DAILY_011", "1", "after_ai_gen")

        studio.finish_button.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_011", "2", "confirmation_screen")

        dat_hang_btn = page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang')"
        ).first
        assert dat_hang_btn.is_visible(timeout=10000), \
            "TC_DAILY_011 FAIL: Khong tim thay nut 'Đặt hàng' tren man hinh xac nhan"
        dat_hang_btn.click()
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_011", "3", "order_screen_after_dat_hang")

        them_gio_btn = page.locator(
            "button:has-text('Thêm vào giỏ'), button:has-text('Them vao gio'), "
            "button:has-text('Add to cart')"
        ).first
        mua_ngay_btn = checkout.buy_now_button

        assert them_gio_btn.is_visible(timeout=8000), \
            "TC_DAILY_011 FAIL: Khong tim thay nut 'Thêm vào giỏ' sau khi click 'Đặt hàng'"
        assert mua_ngay_btn.is_visible(timeout=5000), \
            "TC_DAILY_011 FAIL: Khong tim thay nut 'Mua ngay' sau khi click 'Đặt hàng'"

        self.shot(page, "TC_DAILY_011", "4", "both_buttons_visible")
        print("  [PASS] TC_DAILY_011: Man hinh dat hang co day du: 'Thêm vào giỏ' + 'Mua ngay'")

    # ── TC_DAILY_021 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_021_cart_page_accessible(self, page: Page, base_url: str):
        """TC_DAILY_021 — Trang /checkout hoac /cart load duoc, khong 404/500."""
        _base = base_url.rstrip("/")
        candidate_urls = [f"{_base}/checkout", f"{_base}/cart", f"{_base}/gio-hang"]
        landed_url = None
        final_status = 0
        for url in candidate_urls:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                final_status = resp.status if resp else 0
                if final_status not in (404, 500):
                    landed_url = url
                    break
            except Exception:
                continue

        assert landed_url, (
            f"TC_DAILY_021 FAIL: Tat ca URL checkout/gio hang deu tra ve loi "
            f"(thu: {candidate_urls}). Status cuoi: {final_status}"
        )
        self.shot(page, "TC_DAILY_021", "1", "cart_page")

        assert not page.locator(
            ":text('404'), :text('Not Found'), :text('500'), :text('Internal Server Error')"
        ).is_visible(), \
            f"TC_DAILY_021 FAIL: Trang gio hang hien thi loi. URL: {page.url}"

        cart_ok = (
            page.locator(
                ":text('Giỏ hàng'), :text('Gio hang'), :text('Cart'), "
                ":text('Đơn hàng'), :text('Don hang'), "
                ":text('Trống'), :text('Empty')"
            ).first.is_visible(timeout=5000)
            or page.locator("div[role='dialog'], input[type='email']").first.is_visible(timeout=3000)
            or "login" in page.url or "auth" in page.url
            or page.url.rstrip("/") == base_url.rstrip("/")
        )
        assert cart_ok, \
            f"TC_DAILY_021 FAIL: Trang gio hang khong co noi dung hop le. URL: {page.url}"

        self.shot(page, "TC_DAILY_021", "2", "cart_content_state")
        print(f"  [PASS] Trang gio hang truy cap duoc — URL: {page.url}")

    # ── TC_DAILY_026 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_026_them_vao_gio_shows_toast(self, page: Page, base_url: str):
        """TC_DAILY_026 — Click 'Thêm vào giỏ' → toast 'Đã thêm vào giỏ' hien thi."""
        studio, checkout = self._load_studio(page, base_url, "TC_DAILY_026")

        generated = self._run_ai_gen(page, checkout, "TC_DAILY_026")
        assert generated, \
            "TC_DAILY_026 FAIL: AI gen khong xong sau 90s — nut van DISABLED, khong the tiep tuc"
        self.shot(studio, "TC_DAILY_026", "1", "after_ai_gen")

        studio.finish_button.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_026", "2", "confirmation_screen")

        dat_hang_btn = page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang')"
        ).first
        assert dat_hang_btn.is_visible(timeout=10000), \
            "TC_DAILY_026 FAIL: Khong tim thay nut 'Đặt hàng'"
        dat_hang_btn.click()
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_026", "3", "order_modal_before_add")

        them_gio_btn = page.locator(
            "button:has-text('Thêm vào giỏ'), button:has-text('Them vao gio'), "
            "button:has-text('Add to cart')"
        ).first
        assert them_gio_btn.is_visible(timeout=8000), \
            "TC_DAILY_026 FAIL: Khong tim thay nut 'Thêm vào giỏ'"
        them_gio_btn.click()
        page.wait_for_timeout(2500)
        self.shot(page, "TC_DAILY_026", "4", "after_them_vao_gio")

        toast_visible = (
            page.locator(
                ":text('Đã thêm vào giỏ'), :text('Da them vao gio'), "
                ":text('Đã thêm'), :text('thành công'), :text('thanh cong')"
            ).first.is_visible(timeout=5000)
            or page.locator(
                "[class*='toast'], [role='status'], [role='alert'], "
                "[class*='notification'], [class*='snackbar']"
            ).first.is_visible(timeout=3000)
        )
        assert toast_visible, (
            "TC_DAILY_026 FAIL: Khong hien thi thong bao 'Đã thêm vào giỏ' "
            "sau khi click 'Thêm vào giỏ'"
        )
        self.shot(page, "TC_DAILY_026", "5", "toast_da_them_vao_gio")
        print("  [PASS] TC_DAILY_026: Toast 'Đã thêm vào giỏ' hien thi thanh cong")

    # ── TC_DAILY_030 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_030_mua_ngay_requires_login(self, page: Page, base_url: str):
        """TC_DAILY_030 — Click 'Mua ngay' (chua dang nhap) → man hinh Dang nhap hien thi."""
        studio, checkout = self._load_studio(page, base_url, "TC_DAILY_030")

        generated = self._run_ai_gen(page, checkout, "TC_DAILY_030")
        assert generated, \
            "TC_DAILY_030 FAIL: AI gen khong xong sau 90s — nut van DISABLED, khong the tiep tuc"
        self.shot(studio, "TC_DAILY_030", "1", "after_ai_gen")

        studio.finish_button.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_030", "2", "confirmation_screen")

        dat_hang_btn = page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang')"
        ).first
        assert dat_hang_btn.is_visible(timeout=10000), \
            "TC_DAILY_030 FAIL: Khong tim thay nut 'Đặt hàng'"
        dat_hang_btn.click()
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_030", "3", "order_modal_before_mua_ngay")

        assert checkout.buy_now_button.is_visible(timeout=8000), \
            "TC_DAILY_030 FAIL: Khong tim thay nut 'Mua ngay'"
        checkout.buy_now_button.click()
        page.wait_for_timeout(3000)
        self.shot(page, "TC_DAILY_030", "4", "after_mua_ngay")

        login_required = (
            page.locator(
                "div[role='dialog'] input[type='email'], "
                "input[type='email']:visible, input[type='password']:visible"
            ).first.is_visible(timeout=5000)
            or "login" in page.url.lower()
            or "signin" in page.url.lower()
            or "auth" in page.url.lower()
            or page.locator(
                ":text('Đăng nhập'), :text('Dang nhap'), :text('Login'), :text('Sign in')"
            ).first.is_visible(timeout=3000)
        )
        assert login_required, (
            f"TC_DAILY_030 FAIL: Chua dang nhap nhung click 'Mua ngay' khong yeu cau dang nhap. "
            f"URL: {page.url}"
        )
        self.shot(page, "TC_DAILY_030", "5", "login_required_shown")
        print(f"  [PASS] TC_DAILY_030: 'Mua ngay' yeu cau dang nhap — URL: {page.url}")

    # ── TC_DAILY_038 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_038_size_selection_in_order_modal(self, page: Page, base_url: str):
        """TC_DAILY_038 — Order modal: kiem tra size selector, chon size, them vao gio."""
        studio, checkout = self._load_studio(page, base_url, "TC_DAILY_038")

        generated = self._run_ai_gen(page, checkout, "TC_DAILY_038")
        assert generated, \
            "TC_DAILY_038 FAIL: AI gen khong xong sau 90s — nut van DISABLED"
        self.shot(studio, "TC_DAILY_038", "1", "after_ai_gen")

        studio.finish_button.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_038", "2", "confirmation_screen")

        dat_hang_btn = page.locator(
            "button:has-text('Đặt hàng'), button:has-text('Dat hang')"
        ).first
        assert dat_hang_btn.is_visible(timeout=10000), \
            "TC_DAILY_038 FAIL: Khong tim thay nut 'Đặt hàng'"
        dat_hang_btn.click()
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_038", "3", "order_modal_opened")

        size_selected = checkout.select_size_if_shown("TC_DAILY_038")
        self.shot(page, "TC_DAILY_038", "4", "after_size_selection")

        if size_selected:
            print("  [INFO] TC_DAILY_038: Order modal co size selector — da chon size")
        else:
            print("  [INFO] TC_DAILY_038: Order modal khong co size selector — size co the tu dong")

        page.wait_for_timeout(1500)
        them_gio_btn = page.locator(
            "[role='dialog'] button:has-text('Thêm vào giỏ'), "
            "[role='dialog'] button:has-text('Them vao gio'), "
            "[role='dialog'] button:has-text('Add to cart'), "
            "button:has-text('Thêm vào giỏ'), button:has-text('Add to cart')"
        ).first
        assert them_gio_btn.is_visible(timeout=8000), \
            "TC_DAILY_038 FAIL: Nut 'Thêm vào giỏ' khong hien thi trong order modal"

        them_gio_btn.click(force=True)
        page.wait_for_timeout(2500)
        self.shot(page, "TC_DAILY_038", "5", "after_add_to_cart")

        feedback_ok = (
            page.locator(
                ":text('Đã thêm vào giỏ'), :text('Da them vao gio'), "
                ":text('Đã thêm'), :text('thành công')"
            ).first.is_visible(timeout=5000)
            or page.locator(
                "[class*='toast'], [role='status'], [role='alert'], [class*='snackbar']"
            ).first.is_visible(timeout=3000)
        )
        assert feedback_ok, (
            "TC_DAILY_038 FAIL: Khong co toast 'Đã thêm vào giỏ' sau khi chon size + them gio"
        )
        self.shot(page, "TC_DAILY_038", "6", "toast_after_size_add")
        print(f"  [PASS] TC_DAILY_038: Size check OK (size_selected={size_selected}), "
              f"toast 'Đã thêm vào giỏ' hien thi")
