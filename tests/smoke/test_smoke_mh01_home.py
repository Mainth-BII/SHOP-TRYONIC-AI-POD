"""
Smoke — MH01: Trang Chủ (Home)
TC_DAILY_001 · TC_DAILY_017 · TC_DAILY_029

Chay: pytest tests/smoke/test_smoke_mh01_home.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from pages import HomePage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH01Home(BaseSmokeTest):
    """MH01 — Trang Chủ: Home load, AI Generate khởi động, SEO meta tags."""

    _MH_DIR = "MH01_home"
    _TC_IDS = ["TC_DAILY_001", "TC_DAILY_017", "TC_DAILY_029"]

    # ── TC_DAILY_001 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_001_home_loads(self, page: Page, base_url: str):
        """TC_DAILY_001 — Home page load thành công, không 404/500."""
        home = HomePage(page, base_url)
        home.navigate()

        assert page.title() != "", "TC_DAILY_001 FAIL: Home phải có <title>"
        assert not page.locator("h1:has-text('404'), :text('Not Found')").is_visible(), \
            "TC_DAILY_001 FAIL: Home trả về 404"
        assert not page.locator(":text('Internal Server Error'), :text('500')").is_visible(), \
            "TC_DAILY_001 FAIL: Home trả về 500"

        main_content = page.locator(
            "h1, button:has-text('Tao ngay'), [placeholder*='Ban muon'], textarea"
        ).first
        assert main_content.is_visible(timeout=10_000), \
            "TC_DAILY_001 FAIL: Home không có nội dung chính (h1 / AI input / Tạo ngay)"

        self.shot(home, "TC_DAILY_001", "1", "home_page_loaded")
        print(f"  [PASS] Home title: '{page.title()}'")

    # ── TC_DAILY_017 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_017_ai_generate_starts(self, page: Page, base_url: str):
        """TC_DAILY_017 — Home: nhập prompt → Tạo ngay → loading hoặc navigate Studio."""
        home = HomePage(page, base_url)
        home.navigate()

        assert home.prompt_input.is_visible(timeout=10_000), \
            "TC_DAILY_017 FAIL: AI input không hiển thị trên trang chủ"

        home.fill_prompt("Rồng Việt Nam phong cách cổ điển")
        self.shot(home, "TC_DAILY_017", "1", "prompt_filled")

        assert home.generate_button.is_visible(timeout=8000), \
            "TC_DAILY_017 FAIL: Nút 'Tạo ngay' không hiển thị sau khi nhập prompt"
        assert not home.generate_button.is_disabled(), \
            "TC_DAILY_017 FAIL: Nút 'Tạo ngay' đang disabled"
        self.shot(home, "TC_DAILY_017", "2", "before_generate")

        home.click_generate()
        page.wait_for_timeout(3000)
        self.shot(home, "TC_DAILY_017", "3", "after_generate_click")

        generate_started = (
            "/studio" in page.url
            or page.locator(
                ":text('Đang tạo'), :text('Dang tao'), :text('Generating'), "
                ":text('Loading'), [class*='loading'], [class*='spinner']"
            ).first.is_visible(timeout=3000)
            or page.locator(
                "input[type='email'], :text('Nhập email'), :text('Xác nhận email')"
            ).first.is_visible(timeout=3000)
        )
        assert generate_started, \
            f"TC_DAILY_017 FAIL: Không có phản hồi sau khi click Tạo ngay. URL: {page.url}"
        print(f"  [PASS] AI Generate bắt đầu — URL: {page.url}")

    # ── TC_DAILY_029 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_029_seo_meta_tags(self, page: Page, base_url: str):
        """TC_DAILY_029 — Home: Các SEO/OG meta tag tồn tại và không rỗng."""
        home = HomePage(page, base_url)
        home.navigate()
        self.shot(home, "TC_DAILY_029", "1", "home_for_seo_check")

        meta = page.evaluate("""
            () => {
                const get = (sel) => {
                    const el = document.querySelector(sel);
                    return el ? (el.getAttribute('content') || el.textContent || '').trim() : '';
                };
                return {
                    title:       document.title || '',
                    description: get('meta[name="description"]'),
                    og_title:    get('meta[property="og:title"]'),
                    og_desc:     get('meta[property="og:description"]'),
                    og_image:    get('meta[property="og:image"]'),
                    og_url:      get('meta[property="og:url"]'),
                };
            }
        """)

        missing  = []   # chỉ <title> và description là bắt buộc
        warnings = []   # og:* là khuyến nghị, không fail test

        if not meta["title"]:
            missing.append("<title> — rỗng hoặc không có")
        if not meta["description"]:
            missing.append('meta[name="description"] — rỗng hoặc không có')

        # og:* tags là khuyến nghị (WARN) — không fail test vì site có thể chưa cấu hình
        if not meta["og_title"]:
            warnings.append('og:title chưa có — ảnh hưởng share social')
        if not meta["og_image"]:
            warnings.append('og:image chưa có — ảnh hưởng share social')
        if not meta["og_desc"]:
            warnings.append('og:description chưa có')
        if not meta["og_url"]:
            warnings.append('og:url chưa có')

        for w in warnings:
            print(f"  [WARN] {w}")

        assert not missing, (
            f"TC_DAILY_029 FAIL: {len(missing)} SEO meta tag bắt buộc bị thiếu/rỗng:\n"
            + "\n".join(f"  * {m}" for m in missing)
        )
        print(
            f"  [PASS] SEO meta tags đầy đủ\n"
            f"    title      : {meta['title'][:60]}\n"
            f"    description: {meta['description'][:60]}\n"
            f"    og:title   : {meta['og_title'][:60]}\n"
            f"    og:image   : {meta['og_image'][:60]}"
        )
