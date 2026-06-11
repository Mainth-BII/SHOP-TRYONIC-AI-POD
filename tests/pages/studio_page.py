from __future__ import annotations
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
    def send_button(self) -> Locator:
        """Nút GỬI prompt trong AI chat — là icon (lucide-send), KHÔNG có chữ 'Tạo'.
        Ưu tiên icon send; fallback aria-label / nút 'Tạo ngay'."""
        return self.page.locator(
            "button:has(svg.lucide-send), button:has(svg[class*='send' i]), "
            "button[aria-label*='gửi' i], button[aria-label*='send' i], "
            "button:has-text('Tạo ngay')"
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
    def product_name_button(self) -> Locator:
        """Nút hiển thị tên sản phẩm hiện tại ở bottom bar (dùng để đổi loại áo)."""
        return self.page.locator(
            "button:has-text('Áo Phông'), button:has-text('Áo phông'), "
            "button:has-text('Ao Phong'), button:has-text('áo')"
        ).first

    @property
    def color_dot_buttons(self) -> Locator:
        """Các ô màu (color swatches) để đổi màu áo."""
        return self.page.locator(
            "button[style*='background'], button[style*='background-color'], "
            "[class*='color-dot'], [class*='ColorDot'], "
            "[class*='color-swatch'], [class*='ColorSwatch'], "
            "button:has([style*='background'])"
        )

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

    def submit_prompt(self, prompt: str, retries: int = 3) -> bool:
        """Điền prompt vào ô chat + GỬI, có VERIFY thực sự đã gửi (ô prompt trống lại).

        Lý do: nút gửi là icon (lucide-send), không có chữ; trên CI headless việc
        nhấn Enter thường KHÔNG submit (chỉ xuống dòng) → prompt nằm yên, AI không
        nhận. Hàm này ưu tiên click nút send icon, fallback Enter, và VERIFY bằng
        cách kiểm tra ô prompt đã trống (chat clear input sau khi gửi). Trả True nếu
        gửi thành công.
        """
        inp = self.prompt_input
        try:
            inp.wait_for(state="visible", timeout=15_000)
        except Exception:
            print("  [WARN] submit_prompt: không thấy ô prompt")
            return False

        for attempt in range(1, retries + 1):
            try:
                inp.click()
                inp.fill("")
                inp.fill(prompt)
                self.page.wait_for_timeout(400)
            except Exception as e:
                print(f"  [WARN] fill prompt lần {attempt}: {e}")
                self.page.wait_for_timeout(1_000)
                continue

            # Submit: ưu tiên nút send icon (lucide-send), fallback Enter
            clicked = False
            try:
                btn = self.send_button
                if btn.is_visible(timeout=2_000) and btn.is_enabled(timeout=1_000):
                    btn.click()
                    clicked = True
            except Exception:
                pass
            if not clicked:
                try:
                    inp.press("Enter")
                except Exception:
                    pass

            # VERIFY: ô prompt đã trống (= đã gửi). Chat thường clear input sau gửi.
            self.page.wait_for_timeout(1_000)
            try:
                val = (inp.input_value() or "").strip()
            except Exception:
                val = ""
            if val == "":
                print(f"  [INFO] prompt đã gửi (lần {attempt}, {'send-icon' if clicked else 'Enter'})")
                return True
            print(f"  [WARN] prompt CHƯA gửi (ô còn '{val[:30]}…') — thử lại lần {attempt+1}")

        return False

    def generate(self, prompt: str) -> None:
        """Giữ tương thích — gọi submit_prompt (có verify + retry)."""
        self.submit_prompt(prompt)

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

    def rotate_shirt(self, timeout: int = 10) -> tuple:
        """Click nút 'Xoay áo' → verify xoay sang Mặt sau.
        Verify bằng cách:
        1. Snapshot canvas img src trước khi click (để so sánh thay đổi)
        2. Click 'Xoay áo'
        3. Chờ canvas thay đổi HOẶC 'Mặt sau' active-indicator xuất hiện
        Trả về (success, elapsed_seconds, label_found).
        """
        import time

        # Snapshot canvas hiện tại (src ảnh trên canvas area)
        canvas_src_before = self.page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left > 300 && r.left < 900 && r.width > 100 && img.complete;
            });
            return imgs.map(i => i.src).join(',');
        }""")

        # Tìm nút "Xoay áo" — chỉ khớp text "xoay" (không khớp "Mặt sau")
        btn = self.page.evaluate("""() => {
            const xoay = Array.from(document.querySelectorAll('button, [role="button"]')).find(b => {
                const t = (b.innerText || b.getAttribute('aria-label') || b.title || '').toLowerCase();
                return t.includes('xoay') || t.includes('rotate');
            });
            if (xoay) {
                xoay.click();
                return 'clicked:' + (xoay.innerText || xoay.getAttribute('aria-label') || '').trim();
            }
            return 'not-found';
        }""")
        print(f"  [INFO] rotate_shirt btn: {btn}")
        if btn == "not-found":
            return False, 0.0, ""

        start = time.time()
        deadline = start + timeout
        while time.time() < deadline:
            result = self.page.evaluate(f"""() => {{
                // Kiểm tra 1: canvas img src thay đổi sau khi xoay
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const r = img.getBoundingClientRect();
                    return r.left > 300 && r.left < 900 && r.width > 100 && img.complete;
                }});
                const newSrc = imgs.map(i => i.src).join(',');
                const canvasChanged = newSrc !== {repr(canvas_src_before)};

                // Kiểm tra 2: button "Mặt sau" hoặc label "Mặt sau" active/selected
                const matSauEl = Array.from(document.querySelectorAll('button, span, div, p')).find(el => {{
                    if (el.childElementCount > 2) return false;
                    const t = (el.innerText || '').trim();
                    if (t !== 'Mặt sau') return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 0;
                }});
                // Nút "Xoay áo" biến mất hoặc đổi thành "Mặt trước"
                const xoayBtn = Array.from(document.querySelectorAll('button, [role="button"]')).find(b => {{
                    const t = (b.innerText || '').toLowerCase();
                    return t.includes('xoay');
                }});
                const matTruocBtn = Array.from(document.querySelectorAll('button, [role="button"]')).find(b => {{
                    const t = (b.innerText || '').toLowerCase();
                    return t.includes('mặt trước') || t.includes('mat truoc');
                }});

                return JSON.stringify({{
                    canvasChanged,
                    matSauVisible: !!matSauEl,
                    xoayStillThere: !!xoayBtn,
                    matTruocVisible: !!matTruocBtn,
                }});
            }}""")
            try:
                import json
                state = json.loads(result)
                print(f"  [INFO] rotate state: {state}")
                if state.get("matSauVisible") or state.get("canvasChanged") or state.get("matTruocVisible"):
                    elapsed = round(time.time() - start, 2)
                    label = "Mặt sau" if state.get("matSauVisible") else ("canvas changed" if state.get("canvasChanged") else "Mặt trước visible")
                    print(f"  [INFO] rotate_shirt confirmed: {label} after {elapsed}s — chờ animation xong")
                    # Chờ animation xoay áo hoàn thành trước khi chụp screenshot
                    self.page.wait_for_timeout(2_500)
                    return True, elapsed, label
            except Exception:
                pass
            self.page.wait_for_timeout(500)

        elapsed = round(time.time() - start, 2)
        print(f"  [WARN] rotate_shirt: không verify được sau {elapsed}s")
        return False, elapsed, ""

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

    def get_canvas_screenshot(self) -> bytes:
        """Chụp vùng canvas trung tâm (áo + artwork) để so sánh thay đổi."""
        try:
            return self.page.screenshot(
                clip={"x": 290, "y": 60, "width": 560, "height": 720}
            )
        except Exception:
            return b""

    def wait_for_canvas_artwork(
        self,
        pre_shot: bytes = b"",
        timeout: int = 30,
        poll_ms: int = 500,
    ) -> float:
        """Detect artwork đã render lên canvas áo.

        Studio dùng Fabric.js — artwork nằm trên <canvas>, KHÔNG phải <img>.
        → Dùng screenshot diff thay vì DOM img detection.

        pre_shot: bytes từ get_canvas_screenshot() chụp TRƯỚC khi AI generate.
                  Nếu canvas đã thay đổi so với pre_shot → artwork đã render.
        Trả về elapsed seconds, hoặc -1.0 nếu timeout.
        """
        import time
        import hashlib
        start    = time.time()
        deadline = start + timeout

        pre_hash = hashlib.md5(pre_shot).hexdigest() if pre_shot else ""

        while time.time() < deadline:
            # ── Method 1: screenshot diff (so sánh với baseline trước gen) ───
            if pre_hash:
                try:
                    cur = self.page.screenshot(
                        clip={"x": 290, "y": 60, "width": 560, "height": 720}
                    )
                    if hashlib.md5(cur).hexdigest() != pre_hash:
                        return round(time.time() - start, 2)
                except Exception:
                    pass

            # ── Method 2: CORS-taint detection (artwork từ CDN → canvas bị taint) ─
            try:
                tainted = self.page.evaluate("""() => {
                    for (const c of document.querySelectorAll('canvas')) {
                        const ctx = c.getContext('2d');
                        if (!ctx) continue;
                        try { ctx.getImageData(0, 0, 1, 1); }
                        catch (e) { return true; }   // cross-origin → artwork present
                    }
                    return false;
                }""")
                if tainted:
                    return round(time.time() - start, 2)
            except Exception:
                pass

            # ── Method 3: img ở vùng canvas rộng hơn (fallback cho non-Fabric UI) ─
            try:
                found = self.page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('img[src]')).some(img => {
                        const r   = img.getBoundingClientRect();
                        const cx  = r.left + r.width / 2;
                        return cx > 310 && cx < 930
                               && r.width > 60 && r.height > 60
                               && img.complete && img.naturalWidth > 0;
                    });
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

    def dismiss_color_tooltip(self) -> None:
        """Đóng tooltip 'Đổi màu áo tại đây' nếu đang hiển thị."""
        try:
            self.page.evaluate("""() => {
                const all = Array.from(document.querySelectorAll('*'));
                const tooltip = all.find(
                    el => el.innerText && el.innerText.includes('Đổi màu áo tại đây')
                        && el.getBoundingClientRect().width > 0
                );
                if (!tooltip) return;
                // Click nút X đóng tooltip
                const closeBtn = Array.from(tooltip.querySelectorAll('button, [class*="close" i]'))
                    .find(b => b.getBoundingClientRect().width > 0);
                if (closeBtn) { closeBtn.click(); return; }
                // Fallback: thử click parent
                tooltip.closest('[class*="tooltip" i], [class*="popup" i], [class*="banner" i]')?.remove();
            }""")
            self.page.wait_for_timeout(600)
        except Exception:
            pass

    def get_product_name(self) -> str:
        """Lấy tên sản phẩm từ button cùng hàng với 'Hoàn tất thiết kế'."""
        try:
            return self.page.evaluate("""() => {
                const finish = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất')
                );
                if (!finish) return '';
                const fr = finish.getBoundingClientRect();
                const productBtn = Array.from(document.querySelectorAll('button')).find(b => {
                    if (b === finish) return false;
                    const r = b.getBoundingClientRect();
                    return Math.abs(r.y - fr.y) < 30 && r.x < fr.x && r.width > 30
                        && b.innerText.trim().length > 0;
                });
                return productBtn ? productBtn.innerText.trim() : '';
            }""") or ""
        except Exception:
            return ""

    def change_product_type(self, index: int = 1) -> tuple:
        """Mở dialog Chọn sản phẩm → double-click sản phẩm tại `index`.
        Trả về (success, old_name, new_name).
        """
        self.dismiss_color_tooltip()
        old_name = self.get_product_name()

        try:
            # JS: tìm button cùng hàng với "Hoàn tất" → click để mở dialog
            clicked = self.page.evaluate("""() => {
                const finish = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất')
                );
                if (!finish) return 'no-finish-btn';
                const fr = finish.getBoundingClientRect();
                const productBtn = Array.from(document.querySelectorAll('button')).find(b => {
                    if (b === finish) return false;
                    const r = b.getBoundingClientRect();
                    return Math.abs(r.y - fr.y) < 30 && r.x < fr.x && r.width > 30
                        && b.innerText.trim().length > 0;
                });
                if (!productBtn) return 'no-product-btn';
                productBtn.click();
                return 'clicked:' + productBtn.innerText.trim();
            }""")
            print(f"  [INFO] open product selector: {clicked}")
            self.page.wait_for_timeout(1_500)

            # Dialog Chọn sản phẩm đã mở → chọn sản phẩm tại index
            title_loc = self.page.locator("text='Chọn sản phẩm'")
            if not title_loc.is_visible(timeout=5_000):
                return False, old_name, old_name

            result = self.page.evaluate(f"""() => {{
                const heading = Array.from(document.querySelectorAll('*')).find(
                    el => el.childElementCount === 0
                       && el.textContent.trim() === 'Chọn sản phẩm'
                );
                if (!heading) return 'no-heading';
                let modal = heading.parentElement;
                for (let i = 0; i < 10 && modal && modal !== document.body; i++) {{
                    if (modal.querySelectorAll('img[src]').length >= 2) break;
                    modal = modal.parentElement;
                }}
                if (!modal || modal === document.body) return 'no-modal';
                const cards = Array.from(modal.querySelectorAll('div, button, a, li'))
                    .filter(el => {{
                        if (!el.querySelector('img[src]')) return false;
                        const r = el.getBoundingClientRect();
                        return r.width >= 100 && r.width <= 420
                            && r.height >= 150 && r.height <= 600;
                    }})
                    .sort((a, b) => {{
                        const ra = a.getBoundingClientRect();
                        const rb = b.getBoundingClientRect();
                        return (ra.width * ra.height) - (rb.width * rb.height);
                    }});
                if (cards.length <= {index}) return 'not-enough-cards:' + cards.length;
                const card = cards[{index}];
                card.dispatchEvent(new MouseEvent('click',   {{bubbles: true, cancelable: true}}));
                card.dispatchEvent(new MouseEvent('dblclick',{{bubbles: true, cancelable: true}}));
                return 'ok:' + cards.length + 'cards';
            }}""")
            print(f"  [INFO] change_product_type index={index}: {result}")

            try:
                title_loc.wait_for(state="hidden", timeout=8_000)
            except Exception:
                pass
            self.page.wait_for_timeout(2_000)
            new_name = self.get_product_name()
            return True, old_name, new_name
        except Exception as e:
            print(f"  [WARN] change_product_type error: {e}")
            return False, old_name, ""

    def _find_buttons_in_bottom_bar(self) -> dict:
        """Tìm các nút trong bottom bar theo vị trí tương đối."""
        return self.page.evaluate("""() => {
            const finish = Array.from(document.querySelectorAll('button')).find(
                b => b.innerText && b.innerText.includes('Hoàn tất')
            );
            if (!finish) return null;
            const fr = finish.getBoundingClientRect();
            const barY = fr.y;

            // Tất cả buttons trong cùng hàng với Hoàn tất
            const barBtns = Array.from(document.querySelectorAll('button')).filter(b => {
                const r = b.getBoundingClientRect();
                return Math.abs(r.y - barY) < 35 && r.x < fr.x && r.width > 0;
            }).sort((a, b) => a.getBoundingClientRect().x - b.getBoundingClientRect().x);

            // Product name btn: rộng nhất, có text dài
            const productBtn = barBtns.find(b => b.innerText.trim().length > 3);
            const pr = productBtn?.getBoundingClientRect();

            // Color dropdown btn: nằm giữa product và finish, KHÔNG phải product btn
            const colorBtn = barBtns.find(b => {
                if (b === productBtn) return false;
                const r = b.getBoundingClientRect();
                return (!pr || r.x > pr.x + pr.width - 20) && r.x + r.width < fr.x + 20;
            });
            const cr = colorBtn?.getBoundingClientRect();

            return {
                finishX: Math.round(fr.x), finishY: Math.round(fr.y),
                productText: productBtn?.innerText.trim() || '',
                colorBtnX: cr ? Math.round(cr.x) : -1,
                colorBtnY: cr ? Math.round(cr.y) : -1,
                colorBtnW: cr ? Math.round(cr.width) : -1,
            };
        }""") or {}

    def open_color_dropdown(self) -> bool:
        """Click nút color dropdown (●▼) ở bottom bar để mở panel chọn màu."""
        try:
            result = self.page.evaluate("""() => {
                const finish = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất')
                );
                if (!finish) return 'no-finish';
                const fr = finish.getBoundingClientRect();

                const barBtns = Array.from(document.querySelectorAll('button')).filter(b => {
                    const r = b.getBoundingClientRect();
                    return Math.abs(r.y - fr.y) < 35 && r.x < fr.x && r.width > 0;
                }).sort((a, b) => a.getBoundingClientRect().x - b.getBoundingClientRect().x);

                const productBtn = barBtns.find(b => b.innerText.trim().length > 3);
                const pr = productBtn?.getBoundingClientRect();

                // Color dropdown: ngay bên phải product btn, nhỏ hơn product btn
                const colorBtn = barBtns.find(b => {
                    if (b === productBtn) return false;
                    const r = b.getBoundingClientRect();
                    return (!pr || r.x > pr.x + pr.width - 20) && r.x + r.width < fr.x + 20;
                });

                if (!colorBtn) return 'no-color-btn';
                colorBtn.click();
                const r = colorBtn.getBoundingClientRect();
                return `clicked:${Math.round(r.x)},${Math.round(r.y)},${Math.round(r.width)}`;
            }""")
            print(f"  [INFO] open_color_dropdown: {result}")
            self.page.wait_for_timeout(1_000)
            return result.startswith("clicked")
        except Exception as e:
            print(f"  [WARN] open_color_dropdown: {e}")
            return False

    def get_color_swatches(self) -> list:
        """Sau khi mở color dropdown, lấy danh sách màu trong panel."""
        try:
            return self.page.evaluate("""() => {
                const finish = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất')
                );
                const fr = finish ? finish.getBoundingClientRect() : {y: window.innerHeight};

                // Tìm màu trong panel đã mở (trên bottom bar, có circle shape)
                return Array.from(document.querySelectorAll('button, div, span, li')).filter(el => {
                    const style = window.getComputedStyle(el);
                    const bg = style.backgroundColor;
                    const br = parseFloat(style.borderRadius) || 0;
                    const r = el.getBoundingClientRect();
                    return bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent'
                        && r.width >= 16 && r.width <= 56 && r.height >= 16 && r.height <= 56
                        && r.y < fr.y - 10  // trên bottom bar
                        && r.y > 50         // không phải header
                        && r.width > 0 && r.x > 0 && r.x < window.innerWidth * 0.8;
                }).map((el, i) => ({
                    index: i,
                    bg: window.getComputedStyle(el).backgroundColor,
                    rect: {x: Math.round(el.getBoundingClientRect().x), y: Math.round(el.getBoundingClientRect().y)}
                }));
            }""") or []
        except Exception:
            return []

    def select_color_by_index(self, index: int = 1) -> tuple:
        """Mở color dropdown → chọn màu KHÁC với màu hiện tại (ưu tiên không phải trắng).
        Trả về (success, color_bg).
        """
        opened = self.open_color_dropdown()
        if not opened:
            return False, ""

        self.page.wait_for_timeout(500)
        try:
            result = self.page.evaluate(f"""() => {{
                const finish = Array.from(document.querySelectorAll('button')).find(
                    b => b.innerText && b.innerText.includes('Hoàn tất')
                );
                const fr = finish ? finish.getBoundingClientRect() : {{y: window.innerHeight}};

                const swatches = Array.from(document.querySelectorAll('button, div, span, li')).filter(el => {{
                    const style = window.getComputedStyle(el);
                    const bg = style.backgroundColor;
                    const r = el.getBoundingClientRect();
                    return bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent'
                        && r.width >= 16 && r.width <= 56 && r.height >= 16 && r.height <= 56
                        && r.y < fr.y - 10 && r.y > 50 && r.width > 0
                        && r.x > 0 && r.x < window.innerWidth * 0.8;
                }});

                // Ưu tiên màu KHÔNG phải trắng/gần trắng để thấy thay đổi rõ ràng
                const isNearWhite = bg => {{
                    const m = bg.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                    if (!m) return true;
                    return +m[1] > 240 && +m[2] > 240 && +m[3] > 240;
                }};

                const nonWhite = swatches.find(el => !isNearWhite(window.getComputedStyle(el).backgroundColor));
                const target = nonWhite || (swatches.length > {index} ? swatches[{index}] : swatches[0]);
                if (!target) return 'no-swatches:' + swatches.length;

                const bg = window.getComputedStyle(target).backgroundColor;
                const r = target.getBoundingClientRect();
                target.click();
                return `${{bg}}|${{Math.round(r.x)}},${{Math.round(r.y)}}`;
            }}""")
            if result and not result.startswith("no-"):
                self.page.wait_for_timeout(1_500)
                color_bg = result.split("|")[0]
                print(f"  [INFO] color selected: {result}")
                return True, color_bg
            print(f"  [WARN] select_color_by_index: {result}")
        except Exception as e:
            print(f"  [WARN] select_color_by_index error: {e}")
        return False, ""

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

