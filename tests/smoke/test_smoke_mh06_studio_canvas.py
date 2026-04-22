"""
Smoke — MH06: Studio — Giao diện & Canvas
TC_DAILY_002 · TC_DAILY_006 · TC_DAILY_025 · TC_DAILY_027 · TC_DAILY_028 · TC_DAILY_031
TC_DAILY_032

Chay: pytest tests/smoke/test_smoke_mh06_studio_canvas.py -v
"""
import sys
import time
import pytest
from playwright.sync_api import Page

from pages import StudioPage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH06StudioCanvas(BaseSmokeTest):
    """MH06 — Studio Canvas: load T-shirt/Hoodie, product page, mockup, mobile, performance."""

    _MH_DIR = "MH06_studio_canvas"
    _TC_IDS = [
        "TC_DAILY_002", "TC_DAILY_006", "TC_DAILY_025",
        "TC_DAILY_027", "TC_DAILY_028", "TC_DAILY_031",
        "TC_DAILY_032",
    ]

    # ── TC_DAILY_002 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_002_studio_loads(self, page: Page, base_url: str):
        """TC_DAILY_002 — Studio page load, canvas hien thi."""
        page.goto(f"{base_url}/studio?category=t-shirts",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("load", timeout=30000)
        page.wait_for_timeout(3000)

        assert "/studio" in page.url, \
            f"TC_DAILY_002 FAIL: Khong o trang studio, URL: {page.url}"
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_002 FAIL: Studio tra ve 404"

        canvas_visible = (
            page.locator(".canvas-container").is_visible(timeout=8000)
            or page.locator("canvas").first.is_visible(timeout=2000)
            or page.locator("main").is_visible(timeout=2000)
        )
        assert canvas_visible, \
            "TC_DAILY_002 FAIL: Studio khong hien thi canvas/main area"

        self.shot(page, "TC_DAILY_002", "1", "studio_page_loaded")
        print(f"  [PASS] Studio URL: {page.url}")

    # ── TC_DAILY_006 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_006_product_page_loads(self, page: Page, base_url: str):
        """TC_DAILY_006 — Trang San pham load duoc, co noi dung san pham."""
        page.goto(
            f"{base_url}/studio?view=product",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        assert "/studio" in page.url, \
            f"TC_DAILY_006 FAIL: URL khong chua /studio, URL: {page.url}"
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_006 FAIL: Product page tra ve 404"

        content_ok = page.locator(
            "[class*='product'], [class*='grid'], [class*='card'], main"
        ).first.is_visible(timeout=8000)
        assert content_ok, \
            "TC_DAILY_006 FAIL: Khong thay noi dung san pham (product grid/cards)"

        self.shot(page, "TC_DAILY_006", "1", "product_page_loaded")
        print(f"  [PASS] Product page URL: {page.url}")

    # ── TC_DAILY_025 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_025_studio_hoodie_loads(self, page: Page, base_url: str):
        """TC_DAILY_025 — Studio voi category Hoodie load duoc, canvas hien thi."""
        HOODIE_CANDIDATES = [
            f"{base_url}/studio?category=hoodies",
            f"{base_url}/studio?category=hoodie",
            f"{base_url}/studio?category=ao-hoodie",
        ]
        loaded_url = None
        for url in HOODIE_CANDIDATES:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(2000)
                status = resp.status if resp else 0
                if status not in (404, 500):
                    loaded_url = url
                    break
            except Exception:
                continue

        assert loaded_url, \
            f"TC_DAILY_025 FAIL: Tat ca URL Studio Hoodie deu tra ve loi: {HOODIE_CANDIDATES}"
        page.wait_for_timeout(2000)

        assert "/studio" in page.url, \
            f"TC_DAILY_025 FAIL: Khong o trang Studio sau khi navigate Hoodie. URL: {page.url}"
        assert not page.locator(":text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_025 FAIL: Studio Hoodie hien thi 404"

        canvas_visible = (
            page.locator(".canvas-container").is_visible(timeout=8000)
            or page.locator("canvas").first.is_visible(timeout=3000)
            or page.locator("main").is_visible(timeout=3000)
        )
        assert canvas_visible, \
            f"TC_DAILY_025 FAIL: Canvas/main khong hien thi khi load Studio Hoodie. URL: {page.url}"

        self.shot(page, "TC_DAILY_025", "1", "studio_hoodie_loaded")
        print(f"  [PASS] Studio Hoodie load OK — URL: {page.url}")

    # ── TC_DAILY_027 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_027_product_mockup_image_renders(self, page: Page, base_url: str):
        """TC_DAILY_027 — Studio: Anh mockup san pham load thanh cong, khong bi broken."""
        page.goto(f"{base_url}/studio?category=t-shirts",
                  wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        self.shot(page, "TC_DAILY_027", "1", "studio_before_check")

        total_imgs = page.locator("img").count()
        assert total_imgs > 0, \
            "TC_DAILY_027 FAIL: Khong co phan tu <img> nao trong Studio"

        broken_srcs = page.evaluate("""
            () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                return imgs
                    .filter(img => img.src && img.src.startsWith('http'))
                    .filter(img => img.complete && img.naturalWidth === 0)
                    .map(img => img.src.split('?')[0].slice(-60));
            }
        """)
        self.shot(page, "TC_DAILY_027", "2", "product_image_state")

        if broken_srcs:
            print(f"  [WARN] TC_DAILY_027: Co {len(broken_srcs)} anh bi broken: {broken_srcs[:3]}")
        else:
            print(f"  [PASS] Tat ca {total_imgs} anh load thanh cong (khong broken)")

        canvas_broken = page.evaluate("""
            () => {
                const areas = document.querySelectorAll(
                    '.canvas-container img, canvas ~ img, [class*="product"] img, '
                    + '[class*="mockup"] img, [class*="preview"] img'
                );
                return Array.from(areas)
                    .filter(img => img.complete && img.naturalWidth === 0)
                    .map(img => img.src.split('?')[0].slice(-60));
            }
        """)
        assert not canvas_broken, \
            f"TC_DAILY_027 FAIL: Anh product/mockup trong canvas area bi broken: {canvas_broken}"
        print("  [PASS] Product mockup image hien thi binh thuong trong Studio")

    # ── TC_DAILY_028 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_028_mobile_viewport_smoke(self, mobile_page: Page, base_url: str):
        """TC_DAILY_028 — Mobile viewport (390x844): Home + Studio khong crash, noi dung hien thi."""
        mobile_page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
        try:
            mobile_page.wait_for_load_state("load", timeout=25000)
        except Exception:
            pass
        mobile_page.wait_for_timeout(2000)
        self.shot(mobile_page, "TC_DAILY_028", "1", "mobile_home")

        assert not mobile_page.locator(
            ":text('Internal Server Error'), :text('500'), :text('Application error')"
        ).is_visible(timeout=3000), \
            "TC_DAILY_028 FAIL: Home tren Mobile tra ve 500/crash"

        home_content_ok = mobile_page.locator("h1, main, :text('Tạo ngay')").first.is_visible(timeout=8000)
        assert home_content_ok, \
            "TC_DAILY_028 FAIL: Home Mobile khong hien thi noi dung chinh (h1/main)"

        mobile_page.goto(
            f"{base_url}/studio?category=t-shirts",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            mobile_page.wait_for_load_state("load", timeout=25000)
        except Exception:
            pass
        mobile_page.wait_for_timeout(3000)
        self.shot(mobile_page, "TC_DAILY_028", "2", "mobile_studio")

        assert "/studio" in mobile_page.url, \
            f"TC_DAILY_028 FAIL: Mobile Studio khong load dung URL: {mobile_page.url}"
        assert not mobile_page.locator(
            ":text('Internal Server Error'), :text('500'), :text('Application error')"
        ).is_visible(timeout=3000), \
            "TC_DAILY_028 FAIL: Studio tren Mobile tra ve 500/crash"

        studio_content_ok = mobile_page.locator(
            ".canvas-container, canvas, main"
        ).first.is_visible(timeout=8000)
        assert studio_content_ok, \
            "TC_DAILY_028 FAIL: Studio Mobile khong hien thi canvas/main"

        self.shot(mobile_page, "TC_DAILY_028", "3", "mobile_studio_canvas")
        print(f"  [PASS] Mobile (390x844): Home + Studio deu hien thi dung — URL: {mobile_page.url}")

    # ── TC_DAILY_031 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_031_page_load_performance(self, page: Page, base_url: str):
        """TC_DAILY_031 — Cac trang quan trong phai load xong trong nguong thoi gian cho phep."""
        THRESHOLDS = [
            ("/",                            "Home",                   4.0,  8.0),
            ("/studio?category=t-shirts",    "Studio",                 6.0, 12.0),
            ("/pages/chinh-sach-thanh-toan", "Chinh sach thanh toan",  3.0,  6.0),
        ]
        results = []
        for path, name, warn_s, fail_s in THRESHOLDS:
            t0 = time.time()
            try:
                page.goto(
                    f"{base_url}{path}",
                    wait_until="domcontentloaded",
                    timeout=int(fail_s * 1000) + 5000
                )
                elapsed = time.time() - t0
            except Exception as e:
                elapsed = time.time() - t0
                results.append((name, elapsed, warn_s, fail_s, f"Exception: {e}"))
                continue
            results.append((name, elapsed, warn_s, fail_s, None))

        self.shot(page, "TC_DAILY_031", "1", "last_page_timing")

        failed = []
        for name, elapsed, warn_s, fail_s, err in results:
            if err:
                failed.append(f"{name} — {err}")
                print(f"  [FAIL]  {name}: {err}")
            elif elapsed > fail_s:
                failed.append(f"{name} — {elapsed:.1f}s vuot nguong FAIL {fail_s}s")
                print(f"  [FAIL]  {name}: {elapsed:.1f}s > {fail_s}s")
            elif elapsed > warn_s:
                print(f"  [WARN]  {name}: {elapsed:.1f}s > warn {warn_s}s")
            else:
                print(f"  [PASS]  {name}: {elapsed:.1f}s (nguong {warn_s}s/{fail_s}s)")

        assert not failed, (
            f"TC_DAILY_031 FAIL: {len(failed)} trang vuot nguong thoi gian:\n"
            + "\n".join(f"  * {f}" for f in failed)
        )

    # ── TC_DAILY_032 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_032_terms_dialog_on_first_visit(self, page: Page, base_url: str):
        """TC_DAILY_032 — Studio: Man hinh Dieu khoan xuat hien khi vao lan dau (chua dang nhap)."""
        studio = StudioPage(page, base_url)
        page.goto(
            f"{base_url}/studio?category=t-shirts",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(3000)

        terms_dialog = page.locator(
            "button:has-text('Tôi đồng ý với Điều khoản sử dụng'), "
            "button:has-text('Toi dong y'), [class*='terms'], [class*='dieu-khoan']"
        ).first
        assert terms_dialog.is_visible(timeout=8000), \
            "TC_DAILY_032 FAIL: Man hinh Dieu khoan khong xuat hien khi vao Studio lan dau"
        self.shot(studio, "TC_DAILY_032", "1", "terms_dialog_visible")
        print("  [PASS] S1: Popup Dieu khoan hien thi dung")

        page.mouse.click(10, 10)
        page.wait_for_timeout(1000)
        assert terms_dialog.is_visible(timeout=3000), \
            "TC_DAILY_032 FAIL: Popup Dieu khoan bi dong khi click ra ngoai — phai giu nguyen"
        self.shot(studio, "TC_DAILY_032", "2", "terms_still_visible_after_click_outside")
        print("  [PASS] S2: Click ngoai popup → popup van hien thi")

        order_btn = page.locator(
            "button:has-text('Hoàn tất thiết kế'), button:has-text('Hoan tat thiet ke')"
        ).first
        if order_btn.is_visible(timeout=3000):
            is_disabled = order_btn.get_attribute("disabled") is not None
            if is_disabled:
                print("  [PASS] S3: Nut 'Hoàn tất thiết kế' dung disabled truoc khi dong y")
            else:
                print("  [INFO] S3: Nut 'Hoàn tất thiết kế' KHONG disabled — website da thay doi behavior")

        terms_agree_btn = page.locator(
            "button:has-text('Tôi đồng ý với Điều khoản sử dụng'), "
            "button:has-text('Toi dong y'), button:has-text('Đồng ý')"
        ).first
        terms_agree_btn.click()
        page.wait_for_timeout(3000)
        self.shot(studio, "TC_DAILY_032", "3", "after_agree_terms")

        still_showing = terms_dialog.is_visible(timeout=1000)
        if still_showing:
            print("  [WARN] TC_DAILY_032: Dialog Dieu khoan van hien thi sau khi click dong y")

        assert order_btn.is_visible(timeout=5000), \
            "TC_DAILY_032 FAIL: Nut 'Hoàn tất thiết kế' mat di sau khi dong y"
        assert order_btn.get_attribute("disabled") is None, \
            "TC_DAILY_032 FAIL: Nut 'Hoàn tất thiết kế' van DISABLED sau khi da dong y Dieu khoan"
        self.shot(studio, "TC_DAILY_032", "4", "order_btn_enabled_after_agree")
        print("  [PASS] S4: Sau khi dong y → nut 'Hoàn tất thiết kế' da ENABLED")
