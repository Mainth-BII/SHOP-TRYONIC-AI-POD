"""Tryon Review Page Object — /my-designs → /studio/<id>/review → AI Thử đồ."""
import time
from playwright.sync_api import Page, Locator
from .base_page import BasePage

MY_DESIGNS_PATH = "/my-designs"
ALL_OPTIONS = ["Nam", "Nữ", "Bé trai", "Bé gái"]

# Button text: "Thử lại" nếu đã có kết quả trước, "Thử đồ ngay" nếu chưa thử lần nào
_TRYON_BTN_SELECTOR = "button:has-text('Thử lại'), button:has-text('Thử đồ ngay')"


class TryonReviewPage(BasePage):
    """Covers: my-designs listing, studio review page, tryon option selection."""

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)
        self.last_error: str = ""  # set bởi set_options_and_tryon / wait_tryon_done

    # ── Locators ──────────────────────────────────────────────────────────────

    @property
    def hoan_tat_button(self) -> Locator:
        return self.page.locator("button:has-text('Hoàn tất thiết kế')").first

    @property
    def thu_lai_button(self) -> Locator:
        """Khớp cả 'Thử lại' (đã có kết quả) lẫn 'Thử đồ ngay' (chưa thử lần nào)."""
        return self.page.locator(_TRYON_BTN_SELECTOR).first

    def option_button(self, opt: str) -> Locator:
        return self.page.locator(f"button:has-text('{opt}')").first

    # ── Error detection helpers ───────────────────────────────────────────────

    def get_ui_error_text(self) -> str:
        """Quét trang tìm error messages / toasts đang hiển thị."""
        found: list[str] = []

        # 1. ARIA roles thường dùng cho toasts/alerts
        for sel in ["[role='alert']", "[role='status']"]:
            try:
                for el in self.page.locator(sel).all()[:3]:
                    if el.is_visible(timeout=200):
                        t = (el.inner_text() or "").strip()
                        if t and len(t) < 300 and t not in found:
                            found.append(t)
            except Exception:
                pass

        # 2. Class-name hints
        for kw in ["toast", "notification", "snack", "alert__", "error-msg"]:
            try:
                for el in self.page.locator(f"[class*='{kw}']").all()[:2]:
                    if el.is_visible(timeout=200):
                        t = (el.inner_text() or "").strip()
                        if t and len(t) < 300 and t not in found:
                            found.append(t)
            except Exception:
                pass

        # 3. Vietnamese / English error keywords
        for phrase in ["Lỗi", "hết điểm", "không đủ điểm", "Thất bại",
                       "thất bại", "Không thể", "Error", "Failed", "hết tiền"]:
            try:
                el = self.page.locator(f":text('{phrase}')").first
                if el.is_visible(timeout=150):
                    t = (el.inner_text() or "").strip()
                    if t and len(t) < 300 and t not in found:
                        found.append(t)
            except Exception:
                pass

        return " | ".join(found) if found else ""

    def get_points_balance(self) -> str:
        """Đọc số điểm hiện tại hiển thị trong header, ví dụ: '26 Điểm'."""
        try:
            # Dùng regex trên toàn bộ text để bắt "26 Điểm" / "26 điểm"
            result = self.page.evaluate(r"""() => {
                const m = (document.body.innerText || '').match(/\d+\s*[Đđ]iểm/);
                return m ? m[0] : '';
            }""")
            if result:
                return result.strip()
        except Exception:
            pass
        return ""

    def start_network_capture(self) -> None:
        """Bắt đầu ghi nhận HTTP 4xx/5xx responses từ API domain."""
        self._api_errors: list[str] = []

        def _handler(response) -> None:
            try:
                if response.status >= 400:
                    url = response.url
                    if "api." in url or "/api/" in url:
                        self._api_errors.append(f"HTTP {response.status}: {url}")
            except Exception:
                pass

        self._net_handler = _handler
        self.page.on("response", _handler)

    def stop_network_capture(self) -> list[str]:
        """Dừng ghi nhận và trả về list lỗi API đã bắt được."""
        if hasattr(self, "_net_handler"):
            try:
                self.page.remove_listener("response", self._net_handler)
            except Exception:
                pass
            del self._net_handler
        captured = list(getattr(self, "_api_errors", []))
        self._api_errors = []
        return captured

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

        # Chờ preview ảnh thiết kế load xong trước khi chụp INPUT
        self._wait_image_rendered(timeout=30_000)
        print(f"  [PASS] Xác nhận thiết kế: {self.page.url}")
        return True

    def set_options_and_tryon(self, desired: list[str]) -> bool:
        """Chọn desired trước (enable nút) → bỏ unwanted → click Thử lại / Thử đồ ngay."""
        self.last_error = ""

        # Bước 1: BẬT các option trong desired — làm nút xuất hiện/enable
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

        # Bước 2.5: Chờ UI ổn định sau khi click options
        self.page.wait_for_timeout(500)

        # Bước 3: Chờ nút Thử lại / Thử đồ ngay visible + enabled → click
        try:
            tryon_btn = self.thu_lai_button
            tryon_btn.scroll_into_view_if_needed()
            tryon_btn.wait_for(state="visible", timeout=15_000)

            # Đọc text để biết đang ở trạng thái nào
            btn_text = ""
            try:
                btn_text = (tryon_btn.inner_text() or "").strip()
            except Exception:
                pass

            if tryon_btn.is_disabled():
                points = self.get_points_balance()
                ui_err = self.get_ui_error_text()

                # Diagnostics: dump trạng thái thực của từng option button
                opt_states: dict[str, str] = {}
                for opt in ALL_OPTIONS:
                    try:
                        ob = self.option_button(opt)
                        if ob.is_visible(timeout=300):
                            raw = ob.evaluate("""el => {
                                return JSON.stringify({
                                    cls: el.className,
                                    border: window.getComputedStyle(el).borderColor,
                                    bg: window.getComputedStyle(el).backgroundColor,
                                    aria: el.getAttribute('aria-pressed'),
                                    hasSvg: el.querySelector('svg') !== null,
                                    disabled: el.disabled,
                                })
                            }""")
                            import json as _j
                            d = _j.loads(raw)
                            sel = self._is_option_selected(ob)
                            opt_states[opt] = f"sel={sel} svg={d['hasSvg']} border={d['border']}"
                    except Exception:
                        opt_states[opt] = "?"
                print(f"    [DEBUG] option states: {opt_states}")

                self.last_error = f"Nút '{btn_text}' bị disabled"
                if points:
                    self.last_error += f" — còn {points}"
                if ui_err:
                    self.last_error += f" — UI: {ui_err}"
                print(f"    [WARN] Thử lại vẫn disabled"
                      + (f" — {points}" if points else ""))
                return False

            self._tryon_start = time.time()
            tryon_btn.click()
            self.page.wait_for_timeout(1_500)
            return True

        except Exception as e:
            points = self.get_points_balance()
            ui_err = self.get_ui_error_text()
            self.last_error = "Không tìm thấy nút Thử lại / Thử đồ ngay"
            if points:
                self.last_error += f" — còn {points}"
            if ui_err:
                self.last_error += f" — UI: {ui_err}"
            print(f"    [WARN] Không click Thử lại: {e}")
            return False

    def _is_option_selected(self, btn) -> bool:
        return btn.evaluate(r"""el => {
            // 1. Explicit ARIA / data attributes (React UI patterns)
            if (el.getAttribute('aria-pressed') === 'true') return true;
            if (el.getAttribute('aria-checked') === 'true') return true;
            if (el.getAttribute('data-selected') === 'true') return true;
            if (el.getAttribute('data-state') === 'on') return true;

            // 2. Checkmark icon visible inside button
            if (el.querySelector('svg') !== null) return true;
            if (el.querySelector('[class*="check"]') !== null) return true;

            // 3. Border/background is a specific non-gray accent color
            // (loại bỏ check cls.includes('border-') vì Tailwind gắn class này cho hầu hết buttons)
            const border = window.getComputedStyle(el).borderColor || '';
            const bg     = window.getComputedStyle(el).backgroundColor || '';
            const isNeutral = c => {
                if (!c || c === '' || c.includes('0, 0, 0, 0')) return true;
                const m = c.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
                if (!m) return true;
                const [r, g, b] = [+m[1], +m[2], +m[3]];
                // white (255,255,255) or gray (high value, similar channels)
                return r > 200 && Math.abs(r - g) < 20 && Math.abs(g - b) < 20;
            };
            if (!isNeutral(border)) return true;  // colored border → selected
            if (!isNeutral(bg) && bg !== 'rgb(255, 255, 255)') return true; // colored bg → selected
            return false;
        }""")

    def wait_tryon_done(self, timeout: int = 90_000) -> tuple[bool, float]:
        """Chờ tryon render xong. Return (success, elapsed_seconds) tính từ lúc click Thử lại."""
        self.last_error = ""
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

            # Thu thập thông tin lỗi để báo cáo
            ui_err    = self.get_ui_error_text()
            api_errs  = getattr(self, "_api_errors", [])  # từ network capture đang chạy
            if ui_err:
                self.last_error = f"UI error: {ui_err}"
            elif api_errs:
                self.last_error = "API: " + "; ".join(api_errs[:3])
            else:
                self.last_error = "Timeout — không có kết quả lẫn thông báo lỗi (silent failure)"

            print(f"    [TIME] Tryon timeout sau {elapsed}s — {self.last_error}")
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

