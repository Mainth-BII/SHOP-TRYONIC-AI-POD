"""
Smoke — MH02: Header · Footer · Điều hướng
TC_DAILY_004 · TC_DAILY_005 · TC_DAILY_008 · TC_DAILY_009
TC_DAILY_022 · TC_DAILY_023 · TC_DAILY_024

Chay: pytest tests/smoke/test_smoke_mh02_navigation.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH02Navigation(BaseSmokeTest):
    """MH02 — Header · Footer · Điều hướng: nav links, footer, trang phụ, 404."""

    _MH_DIR = "MH02_navigation"
    _TC_IDS = [
        "TC_DAILY_004", "TC_DAILY_005", "TC_DAILY_008", "TC_DAILY_009",
        "TC_DAILY_022", "TC_DAILY_023", "TC_DAILY_024",
    ]

    # ── TC_DAILY_004 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_004_header_navigation(self, page: Page, base_url: str):
        """TC_DAILY_004 — Kiem tra cac nut/link tren Header hien thi day du."""
        page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

        header = page.locator("header").first
        assert header.is_visible(timeout=10000), \
            "TC_DAILY_004 FAIL: Phan tu <header> khong hien thi"
        self.shot(page, "TC_DAILY_004", "1", "header_before_check")

        logo = header.locator("a[href='/'], img[alt*='Tryonic'], img[alt*='logo']").first
        assert logo.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Logo khong hien thi trong Header"

        product_link = header.locator(
            "a:has-text('Sản phẩm'), a:has-text('San pham')"
        ).first
        assert product_link.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Link 'Sản phẩm' khong hien thi trong Header"

        chinh_sach_btn = header.locator(
            "a:has-text('Chính sách'), button:has-text('Chính sách'), "
            "span:has-text('Chính sách')"
        ).first
        assert chinh_sach_btn.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Menu 'Chính sách' khong hien thi trong Header"
        chinh_sach_btn.hover()
        page.wait_for_timeout(1000)
        self.shot(page, "TC_DAILY_004", "2", "header_chinh_sach_dropdown")

        huong_dan_btn = header.locator(
            "a:has-text('Hướng dẫn'), button:has-text('Hướng dẫn'), "
            "span:has-text('Hướng dẫn')"
        ).first
        assert huong_dan_btn.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Menu 'Hướng dẫn' khong hien thi trong Header"
        huong_dan_btn.hover()
        page.wait_for_timeout(1000)
        self.shot(page, "TC_DAILY_004", "3", "header_huong_dan_dropdown")

        about_link = header.locator(
            "a:has-text('Về Tryonic AI'), a:has-text('Ve Tryonic AI'), "
            "a:has-text('Về Chúng tôi'), a:has-text('Ve Chung toi')"
        ).first
        assert about_link.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Link 'Về Tryonic AI' khong hien thi trong Header"

        login_btn = header.locator(
            ":text('Đăng nhập'), button:has-text('Đăng nhập')"
        ).first
        assert login_btn.is_visible(timeout=5000), \
            "TC_DAILY_004 FAIL: Nut 'Đăng nhập' khong hien thi trong Header"
        self.shot(page, "TC_DAILY_004", "4", "header_all_verified")

        page.mouse.move(0, 0)
        page.wait_for_timeout(500)
        CHINH_SACH_SUB = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
        ]
        missing_sub = []
        for href, label in CHINH_SACH_SUB:
            count = page.locator(f"a[href*='{href}']").count()
            if count == 0:
                missing_sub.append(label)
                print(f"  [WARN] Sub-link khong co trong DOM: {label}")
        assert not missing_sub, \
            f"TC_DAILY_004 FAIL: Sub-link Chinh sach khong co trong DOM: {missing_sub}"
        print("  [PASS] Header: Logo, Sản phẩm, Chính sách (+sub), Hướng dẫn, Về Tryonic AI, Đăng nhập OK")

    # ── TC_DAILY_005 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_005_footer_links(self, page: Page, base_url: str):
        """TC_DAILY_005 — Kiem tra cac link trong Footer hien thi day du."""
        page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

        footer = page.locator("footer").first
        assert footer.is_visible(timeout=10000), \
            "TC_DAILY_005 FAIL: Phan tu <footer> khong hien thi"
        footer.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        self.shot(page, "TC_DAILY_005", "1", "footer_visible")

        FOOTER_LINKS = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi trả"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
            ("/pages/huong-dan-mua-hang",    "Hướng dẫn mua hàng"),
            ("/care-guide",                  "Hướng dẫn bảo quản"),
            ("/pages/lien-he-cskh",          "Liên hệ CSKH"),
        ]
        missing = []
        for href, label in FOOTER_LINKS:
            link = footer.locator(f"a[href*='{href}'], a:has-text('{label}')").first
            if not link.is_visible(timeout=3000):
                missing.append(label)
                print(f"  [WARN] Footer link khong thay: {label} ({href})")

        assert not missing, \
            f"TC_DAILY_005 FAIL: {len(missing)} link footer khong hien thi: {missing}"
        self.shot(page, "TC_DAILY_005", "2", "footer_links_verified")
        print(f"  [PASS] Footer: {len(FOOTER_LINKS)} link hien thi day du")

    # ── TC_DAILY_008 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_008_contact_and_about_pages(self, page: Page, base_url: str):
        """TC_DAILY_008 — Trang Lien he CSKH va Ve Tryonic AI load duoc."""
        page.goto(
            "https://shop.tryonic.ai/pages/lien-he-cskh",
            wait_until="domcontentloaded", timeout=30000
        )
        page.wait_for_timeout(1500)
        self.shot(page, "TC_DAILY_008", "1", "lien_he_page")
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_008 FAIL: Trang Lien he CSKH tra ve 404"
        print(f"  [PASS] Trang Lien he CSKH load OK — URL: {page.url}")

        page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

        about = page.locator(
            "header a:has-text('Về Tryonic AI'), header a:has-text('Ve Tryonic AI'), "
            "header a:has-text('Về Chúng tôi'), header a:has-text('Ve Chung toi')"
        ).first
        assert about.is_visible(timeout=8000), \
            "TC_DAILY_008 FAIL: Link 'Về Tryonic AI' khong hien thi trong header"

        about_href = about.get_attribute("href") or ""
        about.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(1500)
        self.shot(page, "TC_DAILY_008", "2", "ve_tryonic_ai_page")
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            f"TC_DAILY_008 FAIL: Trang Ve Tryonic AI tra ve 404 (href: {about_href})"
        print(f"  [PASS] Trang Ve Tryonic AI load OK — URL: {page.url}")

    # ── TC_DAILY_009 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_009_care_guide_page(self, page: Page, base_url: str):
        """TC_DAILY_009 — Trang Huong dan bao quan (/care-guide) load duoc."""
        page.goto(
            f"{base_url}/care-guide",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(1500)

        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_009 FAIL: Trang /care-guide tra ve 404"
        content_ok = page.locator("h1, h2, main, article").first.is_visible(timeout=8000)
        assert content_ok, \
            "TC_DAILY_009 FAIL: Trang /care-guide khong co noi dung chinh"

        self.shot(page, "TC_DAILY_009", "1", "care_guide_loaded")
        print(f"  [PASS] Care guide URL: {page.url}")

    # ── TC_DAILY_022 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_022_policy_pages_load(self, page: Page, base_url: str):
        """TC_DAILY_022 — 4 trang chinh sach phai load duoc va co noi dung thuc su."""
        POLICY_PAGES = [
            ("/pages/chinh-sach-thanh-toan", "Chính sách thanh toán"),
            ("/pages/chinh-sach-van-chuyen", "Chính sách vận chuyển"),
            ("/pages/chinh-sach-doi-tra",    "Chính sách đổi trả"),
            ("/pages/chinh-sach-bao-mat",    "Bảo mật thông tin"),
        ]
        failed = []
        for path, label in POLICY_PAGES:
            try:
                resp = page.goto(
                    f"{base_url}{path}",
                    wait_until="domcontentloaded", timeout=20000
                )
                page.wait_for_timeout(1000)
                status = resp.status if resp else 0

                if status in (404, 500):
                    failed.append(f"{label} — HTTP {status}")
                    print(f"  [FAIL] {label}: HTTP {status}")
                    continue
                if page.locator(":text('404'), :text('Not Found')").is_visible(timeout=2000):
                    failed.append(f"{label} — Noi dung trang hien thi 404")
                    print(f"  [FAIL] {label}: Trang hien thi 404 text")
                    continue
                has_content = page.locator("h1, h2, main, article, p").first.is_visible(timeout=5000)
                if not has_content:
                    failed.append(f"{label} — Trang trang, khong co noi dung")
                    print(f"  [FAIL] {label}: Trang trang")
                    continue
                print(f"  [PASS] {label} — URL: {page.url}")
            except Exception as e:
                failed.append(f"{label} — Exception: {e}")
                print(f"  [FAIL] {label}: {e}")

        self.shot(page, "TC_DAILY_022", "1", "last_policy_page")
        assert not failed, (
            f"TC_DAILY_022 FAIL: {len(failed)}/{len(POLICY_PAGES)} trang chinh sach bi loi:\n"
            + "\n".join(f"  * {f}" for f in failed)
        )
        print(f"  [PASS] Tat ca {len(POLICY_PAGES)} trang chinh sach load OK va co noi dung")

    # ── TC_DAILY_023 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_023_404_error_handling(self, page: Page, base_url: str):
        """TC_DAILY_023 — URL khong ton tai phai tra ve 404 UI, khong crash server (500)."""
        FAKE_PATH = "/trang-nay-khong-ton-tai-tryonic-smoke-xyz-9999"
        resp = page.goto(
            f"{base_url}{FAKE_PATH}",
            wait_until="domcontentloaded", timeout=20000
        )
        page.wait_for_timeout(1500)
        self.shot(page, "TC_DAILY_023", "1", "404_page_state")

        http_status = resp.status if resp else 0
        assert http_status != 500, \
            f"TC_DAILY_023 FAIL: URL khong ton tai tra ve HTTP 500. Status: {http_status}"
        assert not page.locator(
            ":text('Internal Server Error'), :text('500'), :text('Application error')"
        ).is_visible(timeout=3000), \
            "TC_DAILY_023 FAIL: Trang hien thi loi 500/Application error"

        got_404_status = (http_status == 404)
        got_404_ui = page.locator(
            ":text('404'), :text('Không tìm thấy'), :text('Khong tim thay'), "
            ":text('Not Found'), :text('Trang không tồn tại'), "
            ":text('trang khong ton tai'), h1:has-text('404')"
        ).first.is_visible(timeout=5000)
        redirected_home = page.url.rstrip("/") == base_url.rstrip("/")

        assert got_404_status or got_404_ui or redirected_home, (
            f"TC_DAILY_023 FAIL: URL khong ton tai khong tra ve 404 UI va khong redirect ve Home.\n"
            f"  HTTP status: {http_status} | URL: {page.url}"
        )
        if got_404_status:
            print(f"  [PASS] HTTP 404 chinh xac — Status: {http_status}, URL: {page.url}")
        elif got_404_ui:
            print(f"  [PASS] 404 UI hien thi dung — URL: {page.url}")
        else:
            print(f"  [PASS] Redirect ve Home (404 graceful) — URL: {page.url}")

    # ── TC_DAILY_024 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_024_huong_dan_mua_hang_page(self, page: Page, base_url: str):
        """TC_DAILY_024 — Trang Huong dan mua hang load duoc va co noi dung."""
        resp = page.goto(
            f"{base_url}/pages/huong-dan-mua-hang",
            wait_until="domcontentloaded", timeout=20000
        )
        page.wait_for_timeout(1500)
        self.shot(page, "TC_DAILY_024", "1", "huong_dan_mua_hang_loaded")

        http_status = resp.status if resp else 0
        assert http_status != 404, \
            "TC_DAILY_024 FAIL: Trang /pages/huong-dan-mua-hang tra ve HTTP 404"
        assert http_status != 500, \
            "TC_DAILY_024 FAIL: Trang /pages/huong-dan-mua-hang tra ve HTTP 500"
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(timeout=2000), \
            "TC_DAILY_024 FAIL: Trang Huong dan mua hang hien thi 404"

        has_content = page.locator("h1, h2, main, article").first.is_visible(timeout=8000)
        assert has_content, \
            "TC_DAILY_024 FAIL: Trang Huong dan mua hang khong co noi dung (h1/h2/main/article)"
        print(f"  [PASS] Hướng dẫn mua hàng load OK — URL: {page.url}")
