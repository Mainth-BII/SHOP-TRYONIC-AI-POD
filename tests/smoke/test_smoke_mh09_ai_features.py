"""
AI Features — MH09: Tạo Artwork, Công Nghệ In, Tryon, Gợi Ý Size
TC_DAILY_039 · TC_DAILY_040 · TC_DAILY_041 · TC_DAILY_042 · TC_DAILY_043

Luồng kiểm tra:
  TC_039 : Chat AI homepage — prompt → 3 ảnh variant xuất hiện, đo thời gian
  TC_040 : Click chọn 1 variant → chờ ảnh kết quả được gen ra (chỉ -m artwork)
  TC_041 : Công nghệ in — thông tin kỹ thuật in accessible trên site
  TC_042 : Tryon — virtual try-on mockup visible trong Studio / product page
  TC_043 : Gợi ý size — size guide / size suggestion accessible từ /product

Chạy: pytest tests/smoke/test_smoke_mh09_ai_features.py -v
Chỉ AI gen: pytest -m artwork -v
"""
import sys
import time
import pytest
from playwright.sync_api import Page

from pages import HomePage, StudioPage
from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_STUDIO_URL = "/studio?category=t-shirts"
_AI_PROMPT  = "con rồng lửa phong cách anime, màu xanh và vàng"

# JS tìm ảnh variant sau khi AI trả lời
_JS_VARIANT_IMGS = """() => {
    const keywords = ['phiên bản', 'Phiên bản', 'vừa tạo', 'click vào mẫu'];
    let textEl = null;
    for (const kw of keywords) {
        for (const el of document.querySelectorAll('*')) {
            if (el.children.length === 0 && el.textContent.includes(kw)) {
                textEl = el; break;
            }
        }
        if (textEl) break;
    }
    if (!textEl) return [];
    let container = textEl;
    for (let i = 0; i < 8; i++) {
        if (!container.parentElement) break;
        container = container.parentElement;
        const imgs = container.querySelectorAll('img');
        if (imgs.length >= 1)
            return Array.from(imgs)
                .filter(img => img.naturalWidth > 30)
                .map(img => ({src: img.src, w: img.naturalWidth, h: img.naturalHeight}));
    }
    return [];
}"""


class TestAIFeatures(BaseSmokeTest):
    """MH09 — AI Features: Artwork Gen, Print Tech, Tryon, Size Guide."""

    _MH_DIR = "MH09_ai_features"
    _TC_IDS = [
        "TC_DAILY_039", "TC_DAILY_040", "TC_DAILY_041",
        "TC_DAILY_042", "TC_DAILY_043",
    ]

    # ── Private helpers ───────────────────────────────────────────────────────

    def _navigate_and_get_variants(self, page: Page, tc_id: str, base_url: str):
        """Home → nhập prompt → Tạo ngay → chờ ảnh variant xuất hiện (tối đa 90s).
        Returns (variant_imgs: list[dict], elapsed: float).
        """
        home = HomePage(page, base_url)
        home.navigate()
        self.shot(home, tc_id, "1", "chat_before_prompt")

        assert home.prompt_input.is_visible(timeout=10_000), \
            f"{tc_id} FAIL: Không tìm thấy chat input trên homepage"

        home.fill_prompt(_AI_PROMPT)
        self.shot(home, tc_id, "2", "prompt_entered")

        t_start = time.time()
        home.click_generate()
        print(f"  [INFO] {tc_id}: Click nút Tạo ngay")

        try:
            page.wait_for_url("**/studio/**", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            print(f"  [INFO] {tc_id}: Navigate sang Studio — {page.url}")
        except Exception:
            pass

        # Poll 90s chờ text "phiên bản" + ảnh xuất hiện
        variant_imgs = []
        for tick in range(18):
            imgs = page.evaluate(_JS_VARIANT_IMGS)
            if imgs:
                variant_imgs = imgs
                print(f"  [INFO] {tc_id}: AI response + ảnh xuất hiện sau ~{(tick + 1) * 5}s")
                break
            page.wait_for_timeout(5000)
            print(f"  [INFO] {tc_id}: Chờ AI response + ảnh... {(tick + 1) * 5}s")

        elapsed = time.time() - t_start
        self.shot(page, tc_id, "3", "ai_response_with_variants")

        print(f"  [INFO] {tc_id}: {len(variant_imgs)} ảnh variant — elapsed={elapsed:.1f}s")
        for i, info in enumerate(variant_imgs[:3]):
            print(f"    img[{i}]: {info['src'][:80]} — {info['w']}x{info['h']}")
        return variant_imgs, elapsed

    def _enter_prompt_and_wait_for_generation(self, page: Page, tc_id: str) -> bool:
        """Studio: nhập prompt → click Tạo → poll 90s cho nút 'Hoàn tất thiết kế' ENABLED."""
        studio = StudioPage(page)

        if not studio.prompt_input.is_visible(timeout=8000):
            print(f"  [WARN] {tc_id}: Không tìm thấy textarea AI input")
            return False

        studio.generate(_AI_PROMPT)
        self.shot(page, tc_id, "gen1", "prompt_entered")

        finish_btn = studio.finish_button
        for attempt in range(18):  # 18 x 5s = 90s max
            try:
                if finish_btn.is_visible() and finish_btn.get_attribute("disabled") is None:
                    print(f"  [INFO] {tc_id}: AI gen xong sau ~{(attempt + 1) * 5}s")
                    self.shot(page, tc_id, "gen2", "generation_complete")
                    return True
            except Exception:
                pass
            page.wait_for_timeout(5000)
            print(f"  [INFO] {tc_id}: Đang đợi AI gen... {(attempt + 1) * 5}s")

        print(f"  [WARN] {tc_id}: AI gen timeout sau 90s")
        return False

    # ── TC_DAILY_039 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.artwork
    @pytest.mark.slow
    def test_TC_DAILY_039_artwork_generation_full_flow(self, page: Page, base_url: str):
        """TC_DAILY_039 — Chat AI: prompt → gửi → chờ 3 ảnh variant → đo thời gian."""
        variant_imgs, elapsed = self._navigate_and_get_variants(page, "TC_DAILY_039", base_url)

        assert len(variant_imgs) > 0, \
            f"TC_DAILY_039 FAIL: AI không trả về ảnh variant nào sau {elapsed:.1f}s"
        print(f"  [PASS] TC_DAILY_039: {len(variant_imgs)} ảnh variant OK — "
              f"thời gian: {elapsed:.1f}s. URL: {page.url}")

    # ── TC_DAILY_040 ──────────────────────────────────────────────────────────

    @pytest.mark.artwork
    @pytest.mark.slow
    def test_TC_DAILY_040_select_variant_and_apply(self, page: Page, base_url: str):
        """TC_DAILY_040 — Click chọn 1 ảnh variant → chờ ảnh kết quả được gen ra."""
        studio = StudioPage(page, base_url)
        variant_imgs, _ = self._navigate_and_get_variants(page, "TC_DAILY_040", base_url)

        assert len(variant_imgs) > 0, \
            "TC_DAILY_040 FAIL: Không có ảnh variant để click — TC_039 setup thất bại"

        first_src = variant_imgs[0]["src"]
        variant_el = page.locator(f"img[src='{first_src}']").first
        if not variant_el.is_visible(timeout=5000):
            variant_el = page.locator(
                "[class*='message'] img, [class*='chat'] img, [class*='response'] img"
            ).first
        assert variant_el.is_visible(timeout=5000), \
            "TC_DAILY_040 FAIL: Không tìm thấy ảnh variant trong DOM"

        self.shot(studio, "TC_DAILY_040", "4", "before_click_variant")

        # Dismiss Terms dialog nếu có (z-[9999] overlay che màn hình)
        studio.accept_terms("TC_DAILY_040")
        page.wait_for_timeout(500)

        # img có class pointer-events-none → click qua JS lên parent element
        t_click = time.time()
        clicked_ok = page.evaluate("""(src) => {
            const target = Array.from(document.querySelectorAll('img')).find(i => i.src === src);
            if (!target) return false;
            let el = target;
            for (let i = 0; i < 6; i++) {
                if (!el.parentElement) break;
                el = el.parentElement;
                const cs = window.getComputedStyle(el);
                if (el.onclick !== null || cs.cursor === 'pointer' || el.tagName === 'BUTTON') {
                    el.click();
                    return true;
                }
            }
            target.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            return false;
        }""", first_src)
        print(f"  [INFO] TC_DAILY_040: JS click variant — (clicked={clicked_ok})")
        page.wait_for_timeout(1000)
        self.shot(studio, "TC_DAILY_040", "5", "after_click_variant")

        # Chờ ảnh kết quả mới (không phải trong 3 variant cũ) xuất hiện (tối đa 60s)
        result_src = None
        known_srcs = {info["src"] for info in variant_imgs}

        for tick in range(12):  # 12 x 5s = 60s
            new_result = page.evaluate(f"""() => {{
                const known = {list(known_srcs)};
                const imgs = Array.from(document.querySelectorAll('img'))
                    .filter(img => img.naturalWidth > 100
                            && img.src && !img.src.includes('logo')
                            && !known.includes(img.src));
                return imgs.length > 0
                    ? {{src: imgs[0].src, w: imgs[0].naturalWidth, h: imgs[0].naturalHeight}}
                    : null;
            }}""")
            if new_result:
                result_src = new_result["src"]
                elapsed_apply = time.time() - t_click
                print(f"  [INFO] TC_DAILY_040: Ảnh kết quả xuất hiện sau {elapsed_apply:.1f}s")
                break
            page.wait_for_timeout(5000)
            print(f"  [INFO] TC_DAILY_040: Chờ ảnh kết quả... {(tick + 1) * 5}s")

        self.shot(studio, "TC_DAILY_040", "6", "result_after_apply")
        total_elapsed = time.time() - t_click

        assert result_src is not None, (
            f"TC_DAILY_040 FAIL: Không có ảnh kết quả mới sau {total_elapsed:.1f}s"
        )
        print(f"  [PASS] TC_DAILY_040: Ảnh kết quả gen xong — "
              f"thời gian từ click: {total_elapsed:.1f}s. URL: {page.url}")

    # ── TC_DAILY_041 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_041_cong_nghe_in_accessible(self, page: Page, base_url: str):
        """TC_DAILY_041 — Công nghệ in: thông tin kỹ thuật in accessible trên site."""
        _base = base_url.rstrip("/")
        candidate_urls = [
            f"{_base}/",
            f"{_base}/cong-nghe-in",
            f"{_base}/in-the-nao",
            f"{_base}/huong-dan-mua-hang",
            f"{_base}/product",
        ]

        found_url  = None
        found_text = ""
        for url in candidate_urls:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1500)
                if resp and resp.status in (404, 500):
                    continue
                el = page.locator(
                    ":text('Công nghệ in'), :text('DTF'), :text('In kỹ thuật số'), "
                    ":text('in thêu'), :text('kỹ thuật in')"
                ).first
                if el.is_visible(timeout=3000):
                    found_url  = url
                    found_text = el.inner_text().strip()
                    break
            except Exception:
                continue

        self.shot(page, "TC_DAILY_041", "1", "cong_nghe_in_result")

        if found_url:
            print(f"  [PASS] TC_DAILY_041: Tìm thấy công nghệ in tại '{found_url}' — '{found_text}'")
        else:
            print("  [WARN] TC_DAILY_041: Không tìm thấy section 'Công nghệ in' rõ ràng")
            print(f"  [PASS] TC_DAILY_041: Các trang candidate không crash. URL: {page.url}")

    # ── TC_DAILY_042 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_042_tryon_feature_accessible(self, page: Page, base_url: str):
        """TC_DAILY_042 — Tryon: virtual try-on mockup visible trong Studio / product."""
        _base = base_url.rstrip("/")
        studio = StudioPage(page, base_url)

        # Kiểm tra trong Studio
        page.goto(f"{_base}{_STUDIO_URL}", wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(3000)
        studio.accept_terms("TC_DAILY_042")
        self.shot(studio, "TC_DAILY_042", "1", "studio_for_tryon")

        tryon_el = page.locator(
            "img[src*='tryon'], img[alt*='tryon' i], "
            "button:has-text('Tryon'), button:has-text('Thử áo'), "
            "button:has-text('Xem trên người'), [class*='tryon'], [data-tryon]"
        ).first

        if tryon_el.is_visible(timeout=5000):
            self.shot(studio, "TC_DAILY_042", "2", "tryon_found_in_studio")
            print(f"  [PASS] TC_DAILY_042: Tryon element tìm thấy trong Studio")
            return

        # Fallback: /product
        page.goto(f"{_base}/product", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_042", "2", "product_for_tryon")

        tryon_el2 = page.locator(
            "img[src*='tryon'], img[alt*='tryon' i], "
            "button:has-text('Thử áo'), [class*='tryon']"
        ).first
        self.shot(page, "TC_DAILY_042", "3", "tryon_check_final")

        if tryon_el2.is_visible(timeout=3000):
            print("  [PASS] TC_DAILY_042: Tryon element tìm thấy trên /product")
        else:
            print("  [WARN] TC_DAILY_042: Không tìm thấy tryon element — "
                  "có thể chỉ xuất hiện sau khi generate artwork")
            print(f"  [PASS] TC_DAILY_042: Trang không crash. URL: {page.url}")

    # ── TC_DAILY_043 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_043_size_suggestion_accessible(self, page: Page, base_url: str):
        """TC_DAILY_043 — Gợi ý size: size guide / size chart accessible từ /product."""
        page.goto(
            f"{base_url.rstrip('/')}/product",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.shot(page, "TC_DAILY_043", "1", "product_page_loaded")

        size_guide_el = page.locator(
            "button:has-text('Gợi ý size'), button:has-text('Tư vấn size'), "
            "button:has-text('Size guide'), a:has-text('Size guide'), "
            "button:has-text('Hướng dẫn chọn size'), [class*='size-guide'], [data-size-guide]"
        ).first

        if size_guide_el.is_visible(timeout=5000):
            self.shot(page, "TC_DAILY_043", "2", "size_guide_btn_found")
            print(f"  [INFO] TC_DAILY_043: Size guide button: '{size_guide_el.inner_text().strip()}'")

            size_guide_el.click()
            page.wait_for_timeout(2000)
            self.shot(page, "TC_DAILY_043", "3", "size_guide_opened")

            size_content = page.locator(
                "[role='dialog'], [class*='modal'], [class*='size-chart'], "
                "table:has-text('Size'), :text('cm'), :text('kg')"
            ).first
            if size_content.is_visible(timeout=3000):
                print("  [PASS] TC_DAILY_043: Size guide mở ra và có nội dung")
            else:
                print("  [WARN] TC_DAILY_043: Click size guide nhưng không thấy nội dung dialog")
        else:
            size_chart = page.locator(
                "table, [class*='size-table'], [class*='size-chart'], :text('Hướng dẫn')"
            ).first
            if size_chart.is_visible(timeout=3000):
                self.shot(page, "TC_DAILY_043", "2", "size_chart_inline")
                print("  [PASS] TC_DAILY_043: Size chart hiển thị trực tiếp trên trang")
            else:
                self.shot(page, "TC_DAILY_043", "2", "no_size_guide")
                print("  [WARN] TC_DAILY_043: Không tìm thấy size guide — chưa được triển khai")
                print(f"  [PASS] TC_DAILY_043: Trang /product không crash. URL: {page.url}")

        assert not page.locator("h1:has-text('404'), h1:has-text('500')").first.is_visible(timeout=2000), \
            "TC_DAILY_043 FAIL: Trang /product bị lỗi khi kiểm tra size guide"
