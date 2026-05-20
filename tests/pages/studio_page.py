"""Studio Page Object — /studio canvas, AI generation, điểm thưởng."""

from playwright.sync_api import Page, Locator
from .base_page import BasePage


class StudioPage(BasePage):
    """Trang Studio: AI gen artwork, chọn variant, đặt hàng, kiểm tra điểm."""

    MH_DIR = "MH09_ai_features"

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url)

    # ── Locators ─────────────────────────────────────────────────────────────
    @property
    def prompt_input(self) -> Locator:
        return self.page.locator(
            "textarea[placeholder*='Mô tả ý tưởng'], textarea[placeholder*='Mo ta y tuong'], "
            "textarea[placeholder*='Mô tả'], "
            "input[placeholder*='Bạn muốn'], input[placeholder*='ý tưởng'], "
            "textarea[placeholder*='Bạn']"
        ).first

    @property
    def generate_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Tạo ngay'), button:has-text('Tạo'), "
            "button:has-text('Generate')"
        ).first

    @property
    def finish_button(self) -> Locator:
        """Nút 'Hoàn tất thiết kế' — xuất hiện sau khi gen xong."""
        return self.page.locator(
            "button:has-text('Hoàn tất thiết kế'), button:has-text('Hoan tat'), "
            "button:has-text('Finish')"
        ).first

    @property
    def order_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('Hoàn tất thiết kế'), button:has-text('Hoan tat thiet ke'), "
            "button:has-text('Đặt hàng'), button:has-text('Dat hang'), "
            "button:has-text('Order')"
        ).first

    @property
    def variant_images(self) -> Locator:
        return self.page.locator("img[src*='generation'], img[class*='variant'], img[class*='result']")

    @property
    def color_swatches(self) -> Locator:
        return self.page.locator("[class*='color'], [class*='swatch'], button:has([style*='background-color'])")

    @property
    def size_chart_link(self) -> Locator:
        return self.page.locator("button:has-text('Bảng size'), a:has-text('Bảng size'), :text('Bảng size')").first

    @property
    def back_button(self) -> Locator:
        # 'Xoay áo' button là nút xoay áo sang mặt sau trên Studio
        return self.page.locator(
            "button:has-text('Xoay áo'), button:has-text('Xoay ao'), "
            "button:has-text('Mặt sau'), button:has-text('Mat sau'), "
            "button[aria-label*='xoay'], button[aria-label*='Xoay']"
        ).first

    @property
    def front_button(self) -> Locator:
        return self.page.locator("button:has-text('Mặt trước'), button:has-text('Mat truoc')").first

    @property
    def category_selector(self) -> Locator:
        return self.page.locator(
            "button:has-text('Áo Thun'), button:has-text('T-Shirt'), "
            "button:has-text('T-shirt'), [class*='category']"
        ).first

    @property
    def library_button(self) -> Locator:
        return self.page.locator("button:has-text('Thư Viện'), button:has-text('Thu Vien')").first

    @property
    def artwork_images(self) -> Locator:
        """Ảnh artwork AI đã generate — hiển thị trong panel kết quả / thư viện."""
        return self.page.locator(
            "img[src*='generation'], img[src*='artwork'], img[src*='ai-'], "
            "[class*='library'] img, [class*='Library'] img, "
            "[class*='artwork'] img, [class*='result'] img, "
            "[class*='generated'] img"
        )

    @property
    def library_panel_images(self) -> Locator:
        """Ảnh trong panel Thư Viện (ẢNH CỦA BẠN) — đã hiển thị sẵn ở sidebar trái."""
        return self.page.locator(
            "[class*='library'] img:visible, [class*='Library'] img:visible, "
            "[class*='image-item'] img:visible, [class*='ImageItem'] img:visible, "
            "[class*='thumb'] img:visible, [class*='Thumb'] img:visible, "
            "[class*='gallery'] img:visible, [class*='panel'] img:visible"
        )

    # ── Actions ──────────────────────────────────────────────────────────────

    def navigate(self, category_id: str = "t-shirts") -> None:
        self.goto(f"/studio?category={category_id}")
        self.ready()

    def ready(self) -> None:
        """Xử lý toàn bộ setup sau khi navigate vào studio: terms + chọn sản phẩm."""
        self.accept_terms()
        self.select_product_if_needed()

    def select_product_if_needed(self) -> bool:
        """Nếu xuất hiện dialog 'Chọn sản phẩm', double-click sản phẩm đầu tiên.
        Trả về True nếu dialog đã được xử lý, False nếu không có dialog."""
        try:
            title_loc = self.page.locator("text='Chọn sản phẩm'")
            if not title_loc.is_visible(timeout=5_000):
                return False

            # JS: walk từ heading lên đến modal container, tìm product card nhỏ nhất
            result = self.page.evaluate("""() => {
                const heading = Array.from(document.querySelectorAll('*')).find(
                    el => el.childElementCount === 0
                       && el.textContent.trim() === 'Chọn sản phẩm'
                );
                if (!heading) return 'no-heading';

                // Walk up đến container chứa ít nhất 2 ảnh sản phẩm
                let modal = heading.parentElement;
                for (let i = 0; i < 10 && modal && modal !== document.body; i++) {
                    if (modal.querySelectorAll('img[src]').length >= 2) break;
                    modal = modal.parentElement;
                }
                if (!modal || modal === document.body) return 'no-modal';

                // Tìm card: phần tử chứa img, size 100-400 x 150-600px
                const cards = Array.from(modal.querySelectorAll('div, button, a, li'))
                    .filter(el => {
                        if (!el.querySelector('img[src]')) return false;
                        const r = el.getBoundingClientRect();
                        return r.width >= 100 && r.width <= 420
                            && r.height >= 150 && r.height <= 600;
                    })
                    .sort((a, b) => {
                        const ra = a.getBoundingClientRect();
                        const rb = b.getBoundingClientRect();
                        return (ra.width * ra.height) - (rb.width * rb.height);
                    });

                if (cards.length === 0) return 'no-cards';

                const card = cards[0];
                const r = card.getBoundingClientRect();
                // Double-click để chọn sản phẩm
                card.dispatchEvent(new MouseEvent('click',   {bubbles: true, cancelable: true}));
                card.dispatchEvent(new MouseEvent('dblclick',{bubbles: true, cancelable: true}));
                return `dblclicked:${Math.round(r.width)}x${Math.round(r.height)}`;
            }""")
            print(f"  [INFO] select_product: {result}")

            # Chờ dialog đóng
            try:
                title_loc.wait_for(state="hidden", timeout=8_000)
            except Exception:
                pass
            self.page.wait_for_timeout(2_000)
            return True
        except Exception as e:
            print(f"  [WARN] select_product_if_needed error: {e}")
            return False

    def generate(self, prompt: str) -> None:
        inp = self.prompt_input
        inp.fill(prompt)
        # Thử click nút generate; nếu không tìm thấy, dùng Enter để submit chat
        try:
            btn = self.generate_button
            if btn.is_visible(timeout=2_000):
                btn.click()
                return
        except Exception:
            pass
        inp.press("Enter")

    def select_color(self, name: str) -> bool:
        """Tìm và click color swatch theo text, aria-label, title, data-color."""
        # 1. Text content
        btn = self.page.locator("button").filter(has_text=name).first
        if btn.is_visible(timeout=3000):
            btn.click()
            return True
        # 2. aria-label or title attribute
        btn = self.page.locator(
            f"button[aria-label*='{name}'], button[title*='{name}'], "
            f"[data-color*='{name}']"
        ).first
        if btn.is_visible(timeout=3000):
            btn.click()
            return True
        # 3. White-specific: background color style
        if name.lower() in ("trắng", "trang", "white"):
            btn = self.page.locator(
                "button[style*='#fff'], button[style*='white'], "
                "button[style*='#FFF'], button[style*='rgb(255, 255, 255)'], "
                "[data-color='white'], [data-color='#ffffff']"
            ).first
            if btn.is_visible(timeout=3000):
                btn.click()
                return True
        return False

    def toggle_side(self, side: str = "back") -> None:
        btn = self.back_button if side.lower() == "back" else self.front_button
        # force=True để bypass overlay (color swatch có thể che phủ button)
        btn.click(force=True)

    def wait_for_artworks(self, count: int = 3, timeout: int = 120) -> tuple:
        """Chờ AI tạo đủ `count` ảnh. Trả về (success, elapsed_seconds, found_count).

        finish_button enabled nhưng found=0 → đợi thêm 1 cycle (DOM chưa render xong).
        """
        import time
        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            try:
                btn = self.finish_button
                if btn.is_visible() and not btn.is_disabled():
                    found_now = self.artwork_images.count()
                    if found_now > 0:
                        break
                    # Button enabled nhưng DOM chưa render artworks — đợi thêm 1 cycle
            except Exception:
                pass
            self.page.wait_for_timeout(3000)
        elapsed = round(time.time() - start, 1)
        found = self.artwork_images.count()
        return found >= count, elapsed, found

    def _count_chat_artworks(self) -> int:
        """Đếm artwork trong AI chat panel (bên phải màn hình).
        Threshold 65% viewport để bỏ qua thumbnail canvas/product preview."""
        try:
            return self.page.evaluate("""() => {
                const vw = window.innerWidth;
                const threshold = vw * 0.65;
                return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                    const r = img.getBoundingClientRect();
                    return r.x > threshold && r.width >= 80 && r.height >= 80
                        && img.complete && img.naturalWidth > 0;
                }).length;
            }""")
        except Exception:
            return 0

    def wait_for_new_artworks(self, baseline: int = 0, min_new: int = 1,
                              timeout: int = 120) -> tuple:
        """Chờ AI tạo ít nhất `min_new` ảnh MỚI trong chat panel bên phải.
        baseline = số ảnh trong chat panel TRƯỚC khi gen (thường = 0).
        Trả về (success, elapsed_seconds, chat_count, new_count).
        """
        import time
        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            current = self._count_chat_artworks()
            if current > baseline and (current - baseline) >= min_new:
                break
            self.page.wait_for_timeout(2_000)
        elapsed = round(time.time() - start, 1)
        chat_count = self._count_chat_artworks()
        new_count = max(0, chat_count - baseline)
        return new_count >= min_new, elapsed, chat_count, new_count

    def click_artwork(self, index: int = 0) -> bool:
        """Click ảnh từ left library panel (x < 330px) bằng JS position-based detection."""
        try:
            # Skip index 0 ('Thêm ảnh' card) → actual_index = index + 1
            clicked = self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index + 1}];  // +1 to skip 'Thêm ảnh'
                if (target) {{ target.click(); return true; }}
                return false;
            }}""")
            if clicked:
                self.page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
        return False

    def wait_for_canvas_artwork(self, timeout: int = 30, poll_ms: int = 500) -> float:
        """Poll đến khi artwork hiện lên canvas áo (center x: 380–830px).
        Trả về elapsed seconds, hoặc -1.0 nếu timeout."""
        import time
        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            try:
                found = self.page.evaluate("""() => {
                    const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {
                        const rect = img.getBoundingClientRect();
                        return rect.left > 380 && rect.left < 830
                               && rect.width > 50 && rect.height > 50
                               && img.complete && img.naturalWidth > 0;
                    });
                    return imgs.length > 0;
                }""")
                if found:
                    return round(time.time() - start, 2)
            except Exception:
                pass
            self.page.wait_for_timeout(poll_ms)
        return -1.0

    def click_library_image(self, index: int = 0) -> bool:
        """Click ảnh thứ `index` trong left library panel bằng JS position-based detection."""
        try:
            clicked = self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index}];
                if (target) {{ target.click(); return true; }}
                return false;
            }}""")
            if clicked:
                self.page.wait_for_timeout(1000)
                return True
        except Exception:
            pass
        return False

    def open_library(self) -> None:
        """Mở panel Thư Viện nếu chưa mở. Safe to call khi đã mở sẵn."""
        try:
            lib_btn = self.library_button
            if lib_btn.is_visible(timeout=2000):
                lib_btn.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass  # Library đã mở sẵn, bỏ qua

    def open_order_modal(self) -> None:
        self.order_button.wait_for(state="visible", timeout=15_000)
        self.order_button.scroll_into_view_if_needed()
        # force=True: bypass backdrop overlay (dialog/sheet của Radix UI có thể chặn click)
        self.order_button.click(force=True)
        # Chờ navigate tới trang /review (flow mới)
        try:
            self.page.wait_for_url("**/studio/**/review", timeout=8_000)
        except Exception:
            self.page.wait_for_timeout(2000)

    # ── Assertions / Checks ──────────────────────────────────────────────────

    def is_canvas_visible(self) -> bool:
        return (
            self.page.locator(".canvas-container").is_visible(timeout=8000)
            or self.page.locator("canvas").first.is_visible(timeout=2000)
        )

    def check_points(self, expected: int = 50, tc_id: str = "") -> bool:
        """Kiểm tra số điểm hiển thị trong Studio DOM."""
        has_points = self.page.evaluate(f"""() => {{
            const body = document.body.innerText || "";
            if (/{expected}\\s*(điểm|points)/i.test(body)) return true;
            return Array.from(document.querySelectorAll(
                '[class*="point"], [class*="credit"], [class*="balance"]'
            )).some(el => el.innerText && /{expected}/.test(el.innerText));
        }}""")
        if has_points:
            if tc_id: print(f"  [PASS] {tc_id}: Tìm thấy {expected} điểm trong Studio")
        else:
            if tc_id: print(f"  [WARN] {tc_id}: Không tìm thấy {expected} điểm")
        return has_points

    def wait_for_generation(self, timeout: int = 90_000) -> bool:
        try:
            self.finish_button.wait_for(state="visible", timeout=timeout)
            return not self.finish_button.is_disabled()
        except Exception:
            return False

    def read_panel_image_src(self, index: int) -> str | None:
        """Đọc src của artwork tại `index` trong left panel, skip 'Thêm ảnh' card (+1 offset)."""
        try:
            return self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index + 1}];  // +1 to skip 'Thêm ảnh'
                return target ? target.src : null;
            }}""")
        except Exception:
            return None

    def read_library_image_src(self, index: int) -> str | None:
        """Đọc src của ảnh thư viện tại `index` trong left panel (không skip)."""
        try:
            return self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index}];
                return target ? target.src : null;
            }}""")
        except Exception:
            return None

