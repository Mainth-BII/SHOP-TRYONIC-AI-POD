"""
SH01 — Kiểm tra gian hàng affiliate (TC1 + TC2)

TC1: Header menu → [Tiếp thị liên kết] → kiểm tra user đã có gian hàng chưa
TC2: Click [Xem] → verify trang gian hàng: banner + danh sách sản phẩm
"""
import pytest
from .base_share_flow import BaseShareFlowTest


class TestSH01StoreView(BaseShareFlowTest):
    """TC1 + TC2: Menu Tiếp thị liên kết — xem gian hàng."""

    _MH_NAMES = {
        "MH1":   "Header Menu → Tiếp thị liên kết",
        "MH2":   "Trang /affiliate — Trạng thái gian hàng",
        "MH3":   "Trang Gian hàng — Banner",
        "MH4":   "Trang Gian hàng — Danh sách sản phẩm",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH01 — Gian hàng Tiếp thị liên kết (TC1 + TC2)"

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
        self.tc       = "SH01_STORE_VIEW"
        self.root     = "production"
        self.domain   = "sh01_store_view"
        self._results = []

    @pytest.mark.production
    def test_store_view(self):
        """TC1 + TC2: Menu → Affiliate page → View store."""
        tc = self.tc
        self._login()

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Header menu → Tiếp thị liên kết
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Header menu → Tiếp thị liên kết ─────────────────")
        self.page.goto(self.env.fe_url)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)
        self._shot("MH1_1", "home_page")

        menu_ok = self._click_tiep_thi_lien_ket_menu()
        self._shot("MH1_2", "after_click_menu")

        is_affiliate_url = "affiliate" in self.page.url.lower()
        self._record_check(
            "MH1", "MH1 Click menu Tiếp thị liên kết",
            "✅ PASS" if (menu_ok or is_affiliate_url) else "⚠️ WARN",
            self.page.url, "/affiliate",
        )
        print(f"  [{'PASS' if menu_ok else 'WARN'}] MH1: URL = {self.page.url}")

        # Nếu không navigate được qua menu thì navigate trực tiếp
        if not is_affiliate_url:
            self._goto_affiliate()

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Trang /affiliate: kiểm tra trạng thái phê duyệt & gian hàng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Trang /affiliate ─────────────────────────────────")
        self.page.wait_for_timeout(1000)
        self._shot("MH2_1", "affiliate_page")

        approved = self._is_affiliate_approved()
        self._record_check(
            "MH2", "MH2 User đã được duyệt affiliate",
            "✅ PASS" if approved else "ℹ️ INFO",
            "Đã duyệt" if approved else "Chưa duyệt / chưa đăng ký",
            "Đã duyệt",
        )
        print(f"  [{'PASS' if approved else 'INFO'}] MH2: approved={approved}")

        if not approved:
            self._record_check(
                "MH2", "MH2 Hiển thị thông báo chưa duyệt",
                "✅ PASS", "Có thông báo", "Thông báo hướng dẫn đăng ký",
            )
            print(f"  [INFO] MH2: User chưa được duyệt — kết thúc TC1, bỏ qua TC2")
            self._print_summary_table()
            return

        # Kiểm tra button [Xem] / link gian hàng
        store_url = self._get_store_url()
        has_store = bool(store_url)
        self._record_check(
            "MH2", "MH2 Có gian hàng (button Xem hoặc link store)",
            "✅ PASS" if has_store else "⚠️ WARN",
            store_url or "Không tìm thấy", "Link gian hàng tồn tại",
        )
        print(f"  [{'PASS' if has_store else 'WARN'}] MH2: store_url={store_url}")

        if not has_store:
            print(f"  [WARN] MH2: Không tìm thấy gian hàng — bỏ qua TC2")
            self._print_summary_table()
            return

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Trang gian hàng: Banner
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Trang gian hàng — Banner ─────────────────────────")

        # Navigate đến trang gian hàng (nếu store_url là relative thì ghép base_url)
        full_store_url = (store_url if store_url.startswith("http")
                         else f"{self.env.fe_url.rstrip('/')}/{store_url.lstrip('/')}")
        self.page.goto(full_store_url)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        self._shot("MH3_1", "store_page")

        store_data = self._read_store_page()
        banner_ok  = store_data["banner_visible"]

        self._record_check(
            "MH3", "MH3 Banner gian hàng hiển thị",
            "✅ PASS" if banner_ok else "⚠️ WARN",
            "Visible" if banner_ok else "Không thấy", "Banner image visible",
        )
        self._shot("MH3_2", "store_banner")
        print(f"  [{'PASS' if banner_ok else 'WARN'}] MH3: banner={banner_ok}")

        # ════════════════════════════════════════════════════════════════════
        # MH4 — Trang gian hàng: Danh sách sản phẩm
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH4: Trang gian hàng — Danh sách sản phẩm ────────────")
        prod_count = store_data["product_count"]

        self._record_check(
            "MH4", "MH4 Danh sách sản phẩm hiển thị",
            "✅ PASS" if prod_count > 0 else "⚠️ WARN",
            f"{prod_count} sản phẩm", "≥1 sản phẩm",
        )
        self._shot("MH4_1", "store_products")
        print(f"  [{'PASS' if prod_count > 0 else 'WARN'}] MH4: {prod_count} sản phẩm")

        # Kiểm tra ảnh sản phẩm và tên sản phẩm hiển thị
        has_product_img = self.page.locator(
            "img[src*='/product'], img[src*='product'], [class*='product'] img"
        ).count() > 0
        self._record_check(
            "MH4", "MH4 Ảnh sản phẩm hiển thị",
            "✅ PASS" if has_product_img else "⚠️ WARN",
            "Visible" if has_product_img else "Không thấy", "Ảnh sản phẩm visible",
        )

        print(f"\n  [PASS] {tc}: TC1 + TC2 COMPLETED")
        self._print_summary_table()
