"""Tryon Review Page Object — /my-designs → /studio/<id>/review → AI Thử đồ."""
import time
from playwright.sync_api import Page, Locator
from .base_page import BasePage

MY_DESIGNS_PATH = "/my-designs"
ALL_OPTIONS = ["Nam", "Nữ", "Bé trai", "Bé gái"]


class TryonReviewPage(BasePage):
    """Covers: my-designs listing, studio review page, tryon option selection."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Locators ──────────────────────────────────────────────────────────────

    @property
    def hoan_tat_button(self) -> Locator:
        return self.page.locator("button:has-text('Hoàn tất thiết kế')").first

    @property
    def thu_lai_button(self) -> Locator:
        return self.page.locator("button:has-text('Thử lại')").first

    def option_button(self, opt: str) -> Locator:
        return self.page.locator(f"button:has-text('{opt}')").first

    # ── Actions ───────────────────────────────────────────────────────────────

    def get_studio_urls(self, max_n: int = 10) -> list[str]:
        """Navigate to /my-designs → chờ links xuất hiện → return up to max_n studio URLs."""
        self.goto(MY_DESIGNS_PATH)

        # Chờ ít nhất 1 link studio xuất hiện trước khi extract
        try:
            self.page.wait_for_selector('a[href*="/studio/"]', timeout=10_000)
            self.page.wait_for_timeout(1_500)  # thêm buffer để lazy-load cards còn lại
        except Exception:
            self.page.wait_for_timeout(2_500)

        urls = self.page.evaluate(f"""() => {{
            const links = [];
            document.querySelectorAll('a[href*="/studio/"]').forEach(a => {{
                if (!links.includes(a.href)) links.push(a.href);
            }});
            return links.slice(0, {max_n});
        }}""")

        if not urls:
            urls = self._collect_urls_by_clicking(max_n)

        print(f"  [INFO] Tìm thấy {len(urls)} design URL(s)")
        return urls

    def _collect_urls_by_clicking(self, max_n: int) -> list[str]:
        """Fallback: click từng card → ghi URL → back."""
        urls = []
        self.goto(MY_DESIGNS_PATH)
        self.page.wait_for_timeout(2_000)

        cards = self.page.locator("main > div > div > div[class]").all()
        count = min(len(cards), max_n)

        for i in range(count):
            try:
                self.goto(MY_DESIGNS_PATH)
                self.page.wait_for_timeout(2_000)
                cards = self.page.locator("main > div > div > div[class]").all()
                if i >= len(cards):
                    break
                cards[i].click(timeout=5_000)
                self.page.wait_for_load_state("domcontentloaded")
                self.page.wait_for_timeout(2_000)
                url = self.page.url
                if "/studio/" in url and url not in urls:
                    urls.append(url.rstrip("/"))
            except Exception as e:
                print(f"  [WARN] Card {i+1}: {e}")
        return urls

    def open_review(self, studio_url: str) -> bool:
        """Navigate vào studio → dismiss terms → click 'Hoàn tất thiết kế' → verify /review."""
        self.page.goto(studio_url)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(3_000)
        self.accept_terms()
        self.page.wait_for_timeout(1_000)

        try:
            self.hoan_tat_button.wait_for(state="visible", timeout=10_000)
            self.hoan_tat_button.click()
            self.page.wait_for_timeout(2_500)
        except Exception as e:
            print(f"  [WARN] Không click 'Hoàn tất thiết kế': {e}")
            return False

        try:
            self.page.wait_for_url("**/review**", timeout=8_000)
        except Exception:
            pass

        if "/review" not in self.page.url:
            print(f"  [WARN] Không vào được /review — URL: {self.page.url}")
            return False

        # Chờ preview ảnh thiết kế load xong trước khi chụp INPUT
        self._wait_image_rendered(timeout=30_000)
        print(f"  [PASS] Xác nhận thiết kế: {self.page.url}")
        return True

    def set_options_and_tryon(self, desired: list[str]) -> bool:
        """Chọn desired trước (enable nút) → bỏ unwanted → click Thử lại."""
        # Bước 1: BẬT các option trong desired — làm nút Thử lại xuất hiện/enable
        for opt in desired:
            try:
                btn = self.option_button(opt)
                btn.scroll_into_view_if_needed()
                if not btn.is_visible(timeout=3_000):
                    continue
                if not self._is_option_selected(btn):
                    btn.click()
                    self.page.wait_for_timeout(350)
            except Exception:
                pass

        # Bước 2: TẮT các option không mong muốn
        for opt in ALL_OPTIONS:
            if opt in desired:
                continue
            try:
                btn = self.option_button(opt)
                if not btn.is_visible(timeout=2_000):
                    continue
                if self._is_option_selected(btn):
                    btn.click()
                    self.page.wait_for_timeout(350)
            except Exception:
                pass

        # Bước 3: Chờ Thử lại visible + enabled → click
        try:
            self.thu_lai_button.scroll_into_view_if_needed()
            self.thu_lai_button.wait_for(state="visible", timeout=15_000)
            if self.thu_lai_button.is_disabled():
                print("    [WARN] Thử lại vẫn disabled")
                return False
            self._tryon_start = time.time()
            self.thu_lai_button.click()
            self.page.wait_for_timeout(1_500)
            return True
        except Exception as e:
            print(f"    [WARN] Không click Thử lại: {e}")
            return False

    def _is_option_selected(self, btn) -> bool:
        return btn.evaluate("""el => {
            const hasSvg = el.querySelector('svg path[fill]') !== null;
            const cls = (el.className || '');
            const border = window.getComputedStyle(el).borderColor || '';
            return hasSvg || cls.includes('border-') || border.includes('88, 64') ||
                   el.querySelector('[class*="check"]') !== null;
        }""")

    def wait_tryon_done(self, timeout: int = 90_000) -> tuple[bool, float]:
        """Chờ tryon render xong. Return (success, elapsed_seconds) tính từ lúc click Thử lại."""
        start = getattr(self, "_tryon_start", time.time())
        try:
            self.page.wait_for_function("""() => {
                // 1. Text loading phải biến mất
                if ((document.body.innerText || '').includes('Đang tạo ảnh')) return false;

                // 2. Không còn spinner / skeleton visible
                const pulses = document.querySelectorAll(
                    '[class*="animate-pulse"], [class*="skeleton"], [class*="loading"]'
                );
                const noSpinner = Array.from(pulses).every(el =>
                    el.offsetWidth === 0 || el.offsetHeight === 0 ||
                    getComputedStyle(el).display === 'none' ||
                    getComputedStyle(el).visibility === 'hidden'
                );
                if (!noSpinner) return false;

                // 3. Ảnh preview chính (> 200px rendered) đã load hoàn toàn — loại trừ thumbnail nhỏ
                return Array.from(document.querySelectorAll('img')).some(img =>
                    img.complete && img.naturalWidth > 200 && img.naturalHeight > 200 &&
                    img.getBoundingClientRect().width > 200
                );
            }""", timeout=timeout)
            self._scroll_largest_image_into_view()
            self.page.wait_for_timeout(800)
            elapsed = round(time.time() - start, 1)
            print(f"    [TIME] Tryon hoàn tất trong {elapsed}s")
            return True, elapsed
        except Exception:
            self._scroll_largest_image_into_view()
            self.page.wait_for_timeout(3_000)
            elapsed = round(time.time() - start, 1)
            print(f"    [TIME] Tryon timeout sau {elapsed}s")
            return False, elapsed

    def _wait_image_rendered(self, timeout: int = 30_000) -> None:
        """Chờ ảnh preview chính (> 200px) load xong — dùng cho INPUT screenshot."""
        try:
            self.page.wait_for_function("""() => {
                if ((document.body.innerText || '').includes('Đang tạo ảnh')) return false;
                // Yêu cầu ảnh render width > 200px để loại trừ thumbnail
                return Array.from(document.querySelectorAll('img')).some(img =>
                    img.complete && img.naturalWidth > 200 && img.naturalHeight > 200 &&
                    img.getBoundingClientRect().width > 200
                );
            }""", timeout=timeout)
            self._scroll_largest_image_into_view()
        except Exception:
            pass

    def _scroll_largest_image_into_view(self) -> None:
        """Scroll ảnh có diện tích render lớn nhất vào giữa viewport trước khi chụp."""
        try:
            self.page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img')).filter(img =>
                    img.complete && img.naturalWidth > 200 && img.naturalHeight > 200
                );
                if (!imgs.length) return;
                const largest = imgs.reduce((a, b) => {
                    const ra = a.getBoundingClientRect();
                    const rb = b.getBoundingClientRect();
                    return ra.width * ra.height >= rb.width * rb.height ? a : b;
                });
                largest.scrollIntoView({ behavior: 'instant', block: 'center' });
            }""")
        except Exception:
            pass

