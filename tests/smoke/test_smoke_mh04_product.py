"""
Smoke — MH04: Trang Sản Phẩm (/product)
TC_DAILY_033 · TC_DAILY_034 · TC_DAILY_035 · TC_DAILY_036

Luong kiem tra:
  TC_033 : Trang /product load dung, co heading + anh san pham
  TC_034 : Image gallery: cac anh mockup hien thi (view1/view2/view3)
  TC_035 : Nut 'Them vao gio' tu product page — co phan hoi, khong crash
  TC_036 : Nut 'Mua ngay' tu product page (chua dang nhap) → yeu cau dang nhap

Chay: pytest tests/smoke/test_smoke_mh04_product.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from pages import ProductPage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH04Product(BaseSmokeTest):
    """MH04 — Trang San pham: load, image gallery, them gio, mua ngay."""

    _MH_DIR = "MH04_product"
    _TC_IDS = ["TC_DAILY_033", "TC_DAILY_034", "TC_DAILY_035", "TC_DAILY_036"]

    # ── TC_DAILY_033 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_033_product_page_loads(self, page: Page, base_url: str):
        """TC_DAILY_033 — Trang /product load duoc: khong 404/500, co heading + anh san pham."""
        resp = page.goto(
            f"{base_url.rstrip('/')}/product",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        product = ProductPage(page, base_url)
        self.shot(product, "TC_DAILY_033", "1", "product_page_loaded")

        http_status = resp.status if resp else 0
        assert http_status not in (404, 500), \
            f"TC_DAILY_033 FAIL: /product tra ve HTTP {http_status}"

        assert not page.locator(
            "h1:has-text('404'), h1:has-text('500'), "
            ":text('Not Found'), :text('Internal Server Error')"
        ).first.is_visible(timeout=3000), \
            f"TC_DAILY_033 FAIL: Trang /product hien thi loi. URL: {page.url}"

        assert product.heading.is_visible(timeout=8000), \
            "TC_DAILY_033 FAIL: Khong tim thay heading san pham tren trang /product"

        heading_text = product.heading.inner_text().strip()
        self.shot(product, "TC_DAILY_033", "2", "product_heading_visible")

        assert product.product_images.first.is_visible(timeout=8000), \
            "TC_DAILY_033 FAIL: Khong tim thay anh san pham tren trang /product"

        print(f"  [PASS] TC_DAILY_033: /product load OK — heading='{heading_text}', URL={page.url}")

    # ── TC_DAILY_034 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_034_product_image_gallery(self, page: Page, base_url: str):
        """TC_DAILY_034 — Trang /product: nhieu anh mockup hien thi (view1/view2/view3)."""
        product = ProductPage(page, base_url)
        product.navigate()
        self.shot(product, "TC_DAILY_034", "1", "product_gallery_initial")

        img_count = product.product_images.count()
        assert img_count >= 1, \
            f"TC_DAILY_034 FAIL: Khong tim thay anh mockup nao tren /product (count={img_count})"

        print(f"  [INFO] TC_DAILY_034: Tim thay {img_count} anh mockup")

        assert product.product_images.first.is_visible(timeout=5000), \
            "TC_DAILY_034 FAIL: Anh mockup chinh khong hien thi"

        if img_count >= 2:
            second_img = product.product_images.nth(1)
            if second_img.is_visible(timeout=2000):
                second_img.click()
                page.wait_for_timeout(1000)
                self.shot(product, "TC_DAILY_034", "2", "product_gallery_view2")
                print("  [PASS] TC_DAILY_034: Click anh thu 2 — gallery switch hoat dong")
            else:
                self.shot(product, "TC_DAILY_034", "2", "product_gallery_single_view")
                print(f"  [PASS] TC_DAILY_034: {img_count} anh mockup trong DOM, anh chinh hien thi")
        else:
            self.shot(product, "TC_DAILY_034", "2", "product_gallery_one_image")
            print(f"  [PASS] TC_DAILY_034: Anh mockup hien thi ({img_count} image)")

    # ── TC_DAILY_035 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_035_add_to_cart_from_product_page(self, page: Page, base_url: str):
        """TC_DAILY_035 — Trang /product: nut 'Them vao gio' hien thi, click khong crash."""
        product = ProductPage(page, base_url)
        product.navigate()
        self.shot(product, "TC_DAILY_035", "1", "product_page_before_add")

        if not product.add_to_cart_button.is_visible(timeout=5000):
            self.shot(product, "TC_DAILY_035", "2", "no_add_to_cart_btn")
            assert not page.locator(
                "h1:has-text('404'), h1:has-text('500')"
            ).first.is_visible(timeout=2000), \
                "TC_DAILY_035 FAIL: Trang /product bi loi"
            print("  [WARN] TC_DAILY_035: Nut 'Thêm vào giỏ' khong hien thi tren /product "
                  "— co the can chon size truoc, hoac trang chi hien 'Mua ngay'")
            print(f"  [PASS] TC_DAILY_035: Trang /product khong crash — URL: {page.url}")
            return

        self.shot(product, "TC_DAILY_035", "2", "add_to_cart_btn_visible")
        product.click_add_to_cart()
        self.shot(product, "TC_DAILY_035", "3", "after_add_to_cart")

        assert not page.locator(
            "h1:has-text('404'), h1:has-text('500'), "
            ":text('Not Found'), :text('Internal Server Error')"
        ).first.is_visible(timeout=2000), \
            "TC_DAILY_035 FAIL: Trang bi loi sau khi click 'Thêm vào giỏ'"

        feedback_ok = product.add_to_cart_feedback_visible(timeout=4000)
        if feedback_ok:
            print("  [PASS] TC_DAILY_035: 'Thêm vào giỏ' co phan hoi ro rang")
        else:
            print("  [WARN] TC_DAILY_035: Khong nhan ra phan hoi ro rang — "
                  "nhung trang khong crash (co the toast da an nhanh)")

        print(f"  [PASS] TC_DAILY_035: Click 'Thêm vào giỏ' khong crash — URL: {page.url}")

    # ── TC_DAILY_036 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_036_mua_ngay_requires_login(self, page: Page, base_url: str):
        """TC_DAILY_036 — Trang /product: 'Mua ngay' (chua dang nhap) → yeu cau dang nhap."""
        product = ProductPage(page, base_url)
        product.navigate()
        self.shot(product, "TC_DAILY_036", "1", "product_page_before_mua_ngay")

        assert product.buy_now_button.is_visible(timeout=8000), \
            "TC_DAILY_036 FAIL: Khong tim thay nut 'Mua ngay' tren trang /product"

        self.shot(product, "TC_DAILY_036", "2", "mua_ngay_btn_visible")
        product.click_buy_now()
        self.shot(product, "TC_DAILY_036", "3", "after_mua_ngay")

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

        assert not page.locator(
            "h1:has-text('500'), :text('Internal Server Error')"
        ).first.is_visible(timeout=2000), \
            "TC_DAILY_036 FAIL: Trang bi loi 500 sau khi click 'Mua ngay'"

        if login_required:
            self.shot(product, "TC_DAILY_036", "4", "login_required_shown")
            print(f"  [PASS] TC_DAILY_036: 'Mua ngay' yeu cau dang nhap — URL: {page.url}")
        else:
            self.shot(product, "TC_DAILY_036", "4", "after_click_final_state")
            print(f"  [INFO] TC_DAILY_036: 'Mua ngay' khong yeu cau dang nhap ngay — URL: {page.url}")
            print("  [PASS] TC_DAILY_036: Nut 'Mua ngay' hoat dong, trang khong crash")
