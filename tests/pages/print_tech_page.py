"""Print Tech Page Object — /my-designs → /studio/<id>/review → Gợi ý công nghệ in AI."""
import time

from playwright.sync_api import Locator, Page

from .base_page import BasePage

MY_DESIGNS_PATH = "/my-designs"


class PrintTechPage(BasePage):
    """Covers: navigation to review, AI print-tech suggestion, expand tech list."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Locators ──────────────────────────────────────────────────────────────

    @property
    def hoan_tat_button(self) -> Locator:
        return self.page.locator("button:has-text('Hoàn tất thiết kế')").first

    @property
    def goi_y_ai_button(self) -> Locator:
        return self.page.locator("button:has-text('Gợi ý bằng AI')").first

    def expand_tech_button(self, tech: str = "") -> Locator:
        """Button 'PET ^' / 'DTG ^' — xuất hiện sau khi AI gợi ý xong."""
        if tech:
            return self.page.locator(f"button:has-text('{tech}')").first
        # Fallback: bất kỳ button ngắn chứa tên công nghệ in phổ biến
        return self.page.locator(
            "button:has-text('PET'), button:has-text('DTG'), "
            "button:has-text('UV'), button:has-text('Screen')"
        ).first

    # ── Navigation (giống TryonReviewPage) ───────────────────────────────────

    def get_studio_urls(self, max_n: int = 10) -> list[str]:
        """Navigate to /my-designs → chờ links xuất hiện → return up to max_n studio URLs."""
        self.goto(MY_DESIGNS_PATH)

        # Chờ network idle để lazy-load design cards hoàn tất
        try:
            self.page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass

        # Chờ ít nhất 1 link studio UUID xuất hiện
        try:
            self.page.wait_for_selector(
                'a[href*="/studio/"][href*="-"]',  # UUID có dấu gạch ngang
                timeout=15_000,
            )
            self.page.wait_for_timeout(1_500)
        except Exception:
            self.page.wait_for_timeout(3_000)

        urls = self.page.evaluate(f"""() => {{
            const links = [];
            document.querySelectorAll('a[href*="/studio/"]').forEach(a => {{
                // Chỉ lấy link có UUID (chứa dấu -)
                if (a.href.match(/\\/studio\\/[\\w-]{{20,}}/)) {{
                    if (!links.includes(a.href)) links.push(a.href);
                }}
            }});
            return links.slice(0, {max_n});
        }}""")

        if not urls:
            urls = self._collect_urls_by_clicking(max_n)

        print(f"  [INFO] Tìm thấy {len(urls)} design URL(s)")
        return urls

    def _collect_urls_by_clicking(self, max_n: int) -> list[str]:
        """Fallback: click từng card (dùng onClick router.push) → ghi URL → back."""
        urls = []
        self.goto(MY_DESIGNS_PATH)
        self.page.wait_for_timeout(3_000)

        # Detect empty state — tài khoản chưa có design nào
        try:
            if self.page.locator(
                ":text('chưa có thiết kế'), :text('Chưa có thiết kế')"
            ).is_visible(timeout=2_000):
                print("  [INFO] Trang thiết kế trống — tài khoản chưa có design nào")
                return []
        except Exception:
            pass

        # Design cards dùng onClick={router.push} — không có <a href>
        # Thử nhiều selector để bắt được grid card
        card_sel = (
            "main [class*='grid'] > div[class*='cursor'], "
            "main [class*='grid'] > div[class], "
            "main > div > div > div[class]"
        )
        cards = self.page.locator(card_sel).all()
        count = min(len(cards), max_n)
        for i in range(count):
            try:
                self.goto(MY_DESIGNS_PATH)
                self.page.wait_for_timeout(2_000)
                cards = self.page.locator(card_sel).all()
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
        """Navigate thẳng vào /review (bỏ qua editor click để tránh canvas issues trên CI)."""
        review_url = studio_url.rstrip("/") + "/review"
        try:
            self.page.goto(review_url, wait_until="load", timeout=30_000)
        except Exception as e:
            print(f"  [WARN] goto review timeout/error: {e}")
            return False
        try:
            self.page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        self.page.wait_for_timeout(1_500)
        self.accept_terms()
        self.page.wait_for_timeout(500)

        if "/review" not in self.page.url:
            print(f"  [WARN] Không vào được /review — URL: {self.page.url}")
            return False

        print(f"  [PASS] Xác nhận thiết kế: {self.page.url}")
        return True

    # ── Print Tech Actions ────────────────────────────────────────────────────

    def click_ai_suggest(self) -> bool:
        """Click 'Gợi ý bằng AI' → start timer. Return False nếu button không thấy."""
        try:
            self.goi_y_ai_button.scroll_into_view_if_needed()
            self.goi_y_ai_button.wait_for(state="visible", timeout=10_000)
            self._suggest_start = time.time()
            self.goi_y_ai_button.click()
            self.page.wait_for_timeout(800)
            return True
        except Exception as e:
            print(f"    [WARN] Không click 'Gợi ý bằng AI': {e}")
            return False

    def wait_ai_done(self, timeout: int = 120_000) -> tuple[bool, float]:
        """Chờ AI phân tích công nghệ in xong. Return (success, elapsed_seconds)."""
        start = getattr(self, "_suggest_start", time.time())
        try:
            self.page.wait_for_function("""() => {
                const body = document.body.innerText || '';

                // Text loading phải biến mất — đây là dấu hiệu chính xác nhất
                if (body.includes('Đang gợi ý'))        return false;
                if (body.includes('AI đang phân tích'))  return false;
                if (body.includes('chờ trong giây lát')) return false;

                // 'Gợi ý bằng AI' button phải biến mất (replaced bởi result)
                const suggestBtns = Array.from(document.querySelectorAll('button')).filter(
                    b => (b.innerText || '').includes('Gợi ý bằng AI')
                );
                return suggestBtns.every(b => b.offsetWidth === 0 || b.offsetHeight === 0);
            }""", timeout=timeout)
            self.page.wait_for_timeout(800)
            elapsed = round(time.time() - start, 1)
            print(f"    [TIME] AI công nghệ in xong trong {elapsed}s")
            return True, elapsed
        except Exception:
            elapsed = round(time.time() - start, 1)
            print(f"    [TIME] AI timeout sau {elapsed}s")
            return False, elapsed

    def get_suggested_tech(self) -> str:
        """Đọc tên công nghệ in được AI gợi ý (PET / DTG / ...)."""
        try:
            return self.page.evaluate("""() => {
                const section = document.querySelector(
                    'section, div[class*="print"], div[class*="tech"]'
                );
                const text = (document.body.innerText || '');
                const match = text.match(/\\b(PET|DTG|Screen|UV|Sublimation|Embroidery)\\b/);
                return match ? match[1] : '';
            }""") or ""
        except Exception:
            return ""

    def expand_tech_list(self, tech: str = "") -> bool:
        """Click button 'PET ^' / 'DTG ^' để mở danh sách công nghệ in gợi ý."""
        try:
            btn = self.expand_tech_button(tech)
            btn.scroll_into_view_if_needed()
            btn.wait_for(state="visible", timeout=8_000)
            btn.click()
            self.page.wait_for_timeout(1_200)
            return True
        except Exception as e:
            print(f"    [WARN] Không click expand tech list: {e}")
            return False
