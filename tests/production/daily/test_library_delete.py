"""Daily smoke: Thư Viện — Verify icon xoá trên ảnh của bạn + xoá thành công.

TC1: test_library_delete_image        — xoá ảnh có sẵn trong thư viện
TC2: test_library_delete_new_artwork  — tạo artwork mới → xoá luôn → không ảnh hưởng data cũ
"""
from typing import ClassVar

import pytest
from playwright.sync_api import Page

from production.daily.base_daily_test import BaseDailyTest
from pages.auth_modal_page import AuthModalPage

TC  = "LIBRARY_DELETE"
TC2 = "LIBRARY_DELETE_NEW"

# Prompt cố định để tạo test artwork — dễ nhận biết, không trùng data thật
_TEST_PROMPT = "QA automation test artwork"


class TestDailyLibraryDelete(BaseDailyTest):
    _SUITE_NAME   = "LIBRARY_DELETE"
    _REPORT_TITLE = "Daily Smoke: Library — Xoá ảnh"
    _results: ClassVar[list] = []

    @pytest.fixture(autouse=True)
    def _setup(self, page: Page, env, home_page):
        self.page  = page
        self.env   = env
        self.home  = home_page

    # ── Helper: Login ────────────────────────────────────────────────────────

    def _login(self) -> None:
        email, pwd = self.env.login_email, self.env.login_password
        if not email or not pwd:
            pytest.skip("Thiếu credentials — set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD")
        for attempt in range(1, 3):
            self.home.navigate()
            self.home.header.click_login()
            self.page.wait_for_timeout(1_000)
            AuthModalPage(self.page, self.env.fe_url).login(email, pwd)
            self.page.wait_for_timeout(3_000)
            if self.home.header.is_logged_in():
                print(f"  [INFO] Login thành công (lần {attempt})")
                return
            print(f"  [WARN] Login chưa xong lần {attempt} — thử lại...")
            self.page.wait_for_timeout(2_000)
        pytest.fail("Đăng nhập thất bại sau 2 lần thử — kiểm tra credentials/API")

    # ── Helper: Mở panel Thư Viện trong Studio ───────────────────────────────

    def _dismiss_product_dialog(self) -> None:
        """Đợi và đóng dialog 'Chọn sản phẩm' nếu xuất hiện.
        QUAN TRỌNG: phải xử lý dialog XONG trước khi tương tác với library.
        """
        try:
            dialog_title = self.page.locator("text='Chọn sản phẩm'")
            if not dialog_title.is_visible(timeout=5_000):
                print("  [INFO] Không có dialog Chọn sản phẩm")
                return

            print("  [INFO] Dialog Chọn sản phẩm đang mở — đang chọn sản phẩm...")

            # Click vào card sản phẩm đầu tiên (double-click)
            result = self.page.evaluate("""() => {
                const heading = Array.from(document.querySelectorAll('*')).find(
                    el => el.childElementCount === 0
                       && el.textContent.trim() === 'Chọn sản phẩm'
                );
                if (!heading) return 'no-heading';
                let modal = heading.parentElement;
                for (let i = 0; i < 10 && modal && modal !== document.body; i++) {
                    if (modal.querySelectorAll('img[src]').length >= 2) break;
                    modal = modal.parentElement;
                }
                if (!modal || modal === document.body) return 'no-modal';
                const cards = Array.from(modal.querySelectorAll('div, button, li'))
                    .filter(el => {
                        if (!el.querySelector('img[src]')) return false;
                        const r = el.getBoundingClientRect();
                        return r.width >= 80 && r.width <= 420 && r.height >= 100;
                    })
                    .sort((a, b) => {
                        const ra = a.getBoundingClientRect();
                        const rb = b.getBoundingClientRect();
                        return (ra.width * ra.height) - (rb.width * rb.height);
                    });
                if (cards.length === 0) return 'no-cards';
                const card = cards[0];
                card.dispatchEvent(new MouseEvent('dblclick', {bubbles: true}));
                card.dispatchEvent(new MouseEvent('click',   {bubbles: true}));
                return 'ok:' + card.tagName;
            }""")
            print(f"  [INFO] Double-click card: {result}")

            # Đợi dialog biến mất
            try:
                self.page.wait_for_selector(
                    "text='Chọn sản phẩm'", state="hidden", timeout=8_000
                )
                print("  [INFO] Dialog đã đóng")
            except Exception:
                # Fallback: click ra ngoài dialog
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(1_000)

            self.page.wait_for_timeout(2_000)

        except Exception as e:
            print(f"  [WARN] _dismiss_product_dialog: {e}")

    def _accept_terms_if_any(self) -> None:
        """Đóng dialog 'Điều khoản sử dụng' nếu đang hiển thị."""
        try:
            agree_btn = self.page.locator(
                "button:has-text('Tôi đồng ý với Điều khoản'), "
                "button:has-text('Tôi đồng ý'), "
                "button:has-text('Đồng ý với Điều khoản'), "
                "button:has-text('Đồng ý')"
            ).first
            if agree_btn.is_visible(timeout=3_000):
                agree_btn.click()
                self.page.wait_for_timeout(1_500)
                print("  [INFO] Đã đồng ý Điều khoản sử dụng")
        except Exception:
            pass

    def _open_library_tab_js(self) -> None:
        """Click tab Thư Viện bằng JS — button có thể là icon-only (bị hidden với Playwright)."""
        result = self.page.evaluate("""() => {
            // Tìm button có text / aria-label / title chứa 'Thư Viện'
            const candidates = Array.from(document.querySelectorAll('button, [role="tab"]'));
            for (const btn of candidates) {
                const text  = (btn.innerText || '').trim();
                const label = (btn.getAttribute('aria-label') || '').trim();
                const title = (btn.getAttribute('title') || '').trim();
                if ([text, label, title].some(s =>
                    s.includes('Thư Viện') || s.includes('Thu Vien') || s.includes('Library')
                )) {
                    btn.click();
                    return 'clicked: ' + (text || label || title);
                }
            }
            return 'not found';
        }""")
        print(f"  [INFO] Thư Viện tab: {result}")
        self.page.wait_for_timeout(1_000)

    def _dismiss_product_dialog_from_studio(self, studio) -> None:
        """Navigate vào Studio → xử lý dialog → đảm bảo studio sẵn sàng."""
        studio.navigate()
        self.page.wait_for_timeout(2_000)
        self._dismiss_product_dialog()

    def _open_library_panel(self) -> bool:
        """Navigate Studio → xử lý dialog → mở tab Thư Viện.
        Trả về True nếu panel có ảnh trong 'ẢNH CỦA BẠN'.
        """
        self.page.goto(f"{self.env.fe_url}/studio?category=t-shirts",
                       wait_until="domcontentloaded")
        self.page.wait_for_timeout(3_000)

        # Step 1: Accept terms nếu có
        try:
            terms_btn = self.page.locator(
                "button:has-text('Tôi đồng ý'), button:has-text('Đồng ý')"
            ).first
            if terms_btn.is_visible(timeout=3_000):
                terms_btn.click()
                self.page.wait_for_timeout(1_500)
        except Exception:
            pass

        # Step 2: Đóng dialog "Chọn sản phẩm" (PHẢI xử lý trước khi tương tác library)
        self._dismiss_product_dialog()

        # Step 3: Verify studio đã load (không còn dialog)
        try:
            self.page.wait_for_selector(
                "text='Chọn sản phẩm'", state="hidden", timeout=3_000
            )
        except Exception:
            pass
        self.page.wait_for_timeout(1_000)

        # Step 4: Click tab "Thư Viện" bằng JS
        self._open_library_tab_js()
        self.page.wait_for_timeout(2_000)

        # Step 5: Đếm ảnh trong 'ẢNH CỦA BẠN' (panel trái, x < 330px)
        count = self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left < 330 && r.width > 30 && r.height > 30
                    && img.complete && img.naturalWidth > 0;
            }).length;
        }""")
        print(f"  [INFO] Số ảnh trong panel Thư Viện: {count}")
        return count > 0

    # ── Helper: Hover card → lấy delete icon góc trên-phải ─────────────────

    def _hover_and_find_delete(self) -> dict:
        """Hover vào card ảnh đầu tiên trong 'ẢNH CỦA BẠN' → tìm icon xoá góc trên-phải.
        Trả về dict: {found, selector, x, y, img_src}
        """
        # Bước 1: Lấy tọa độ card ảnh đầu tiên (bỏ qua ô 'Thêm ảnh')
        coords = self.page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left < 330 && r.width > 30 && r.height > 30
                    && img.complete && img.naturalWidth > 0;
            });
            if (imgs.length === 0) return null;
            const img = imgs[0];
            const r = img.getBoundingClientRect();
            return {x: r.left + r.width / 2, y: r.top + r.height / 2, src: img.src,
                    cardLeft: r.left, cardTop: r.top, cardRight: r.right};
        }""")

        if not coords:
            return {"found": False, "reason": "Không tìm thấy ảnh trong panel"}

        # Bước 2: Hover bằng Playwright → trigger CSS :hover / :group-hover
        self.page.mouse.move(coords["x"], coords["y"])
        self.page.wait_for_timeout(1_500)   # CI headless cần thêm thời gian render hover

        # Bước 3: Tìm delete button xuất hiện sau hover
        # Icon xoá nằm góc trên-phải của card (absolute positioned)
        delete_info = self.page.evaluate(f"""() => {{
            const cardRight = {coords['cardRight']};
            const cardTop   = {coords['cardTop']};

            // Ưu tiên 1: button có aria-label / title liên quan đến xoá
            const labelSels = [
                'button[aria-label*="xoá" i]', 'button[aria-label*="delete" i]',
                'button[aria-label*="xoa" i]',  'button[aria-label*="remove" i]',
                'button[title*="xoá" i]',        'button[title*="delete" i]',
                'button[class*="delete" i]',     'button[class*="remove" i]',
                'button[class*="trash" i]',
            ];
            for (const sel of labelSels) {{
                for (const el of document.querySelectorAll(sel)) {{
                    const r = el.getBoundingClientRect();
                    if (r.width > 0 && r.left < 380)
                        return {{found: true, sel, x: r.left + r.width/2, y: r.top + r.height/2}};
                }}
            }}

            // Ưu tiên 2: button nhỏ (icon-only ≤ 44px) ở góc trên-phải của card
            const iconBtns = Array.from(document.querySelectorAll('button')).filter(b => {{
                const r = b.getBoundingClientRect();
                if (!r.width || r.width > 44 || r.height > 44) return false;
                if (r.left < 50 || r.left > 380) return false;
                // Nằm gần góc trên-phải của card
                const nearRight = Math.abs(r.right - cardRight) < 30;
                const nearTop   = Math.abs(r.top  - cardTop)   < 30;
                return nearRight && nearTop;
            }});
            if (iconBtns.length > 0) {{
                const b = iconBtns[0];
                const r = b.getBoundingClientRect();
                return {{found: true, sel: 'icon-btn-top-right',
                         x: r.left + r.width/2, y: r.top + r.height/2,
                         label: b.getAttribute('aria-label') || b.title || ''}};
            }}

            // Ưu tiên 3: bất kỳ button nhỏ nào trong vùng panel sau hover
            const anySmall = Array.from(document.querySelectorAll('button')).filter(b => {{
                const r = b.getBoundingClientRect();
                return r.width > 0 && r.width <= 44 && r.left > 50 && r.left < 380
                    && b.querySelector('svg');
            }});
            if (anySmall.length > 0) {{
                const b = anySmall[0];
                const r = b.getBoundingClientRect();
                return {{found: true, sel: 'svg-btn-fallback',
                         x: r.left + r.width/2, y: r.top + r.height/2}};
            }}

            return {{found: false, reason: 'Không tìm thấy delete button sau hover'}};
        }}""")

        delete_info["img_src"] = coords.get("src", "")
        return delete_info

    # ── Test chính ───────────────────────────────────────────────────────────

    @pytest.mark.daily
    def test_library_delete_image(self):
        """Login → Studio → Thư Viện → verify icon xoá → xoá ảnh → verify xoá thành công."""

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC, "S1: Login thành công", "✅ PASS",
                           f"email: {self.env.login_email}")
        self._shot(TC, "1", "after_login")

        # ── S2: Mở panel Thư Viện ────────────────────────────────────────────
        has_images = self._open_library_panel()
        self._shot(TC, "2", "library_panel_opened")

        if not has_images:
            self._record_check(TC, "S2: Panel Thư Viện có ảnh",
                               "⚠️ WARN", "Không có ảnh trong thư viện — không thể test xoá")
            pytest.skip("Thư Viện không có ảnh nào — upload ảnh trước khi chạy test này")

        # Đếm ảnh ban đầu
        count_before = self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left < 330 && r.width > 30 && r.height > 30
                    && img.complete && img.naturalWidth > 0;
            }).length;
        }""")
        self._record_check(TC, "S2: Panel Thư Viện có ảnh",
                           "✅ PASS", f"Có {count_before} ảnh trong thư viện")

        # ── S3: Hover → verify icon xoá hiển thị ────────────────────────────
        delete_info = self._hover_and_find_delete()
        self._shot(TC, "3", "hover_show_delete_icon")

        delete_found = delete_info.get("found", False)
        selector_used = delete_info.get("selector", "N/A")
        self._record_check(
            TC, "S3: Icon xoá hiển thị khi hover vào ảnh",
            "✅ PASS" if delete_found else "❌ FAIL",
            f"selector: {selector_used}" if delete_found
            else delete_info.get("reason", "Không tìm thấy delete button"),
        )

        if not delete_found:
            pytest.fail(
                f"Không tìm thấy icon xoá trong panel Thư Viện sau hover. "
                f"Reason: {delete_info.get('reason', 'unknown')}"
            )

        # ── S4: Click icon xoá ───────────────────────────────────────────────
        del_x = delete_info.get("x", 0)
        del_y = delete_info.get("y", 0)

        if del_x and del_y:
            self.page.mouse.click(del_x, del_y)
            self.page.wait_for_timeout(1_500)
        else:
            # Fallback: click bằng selector
            self.page.locator(selector_used).first.click()
            self.page.wait_for_timeout(1_500)

        self._shot(TC, "4", "after_click_delete")

        # ── S5: Xử lý confirm dialog (nếu có) ───────────────────────────────
        confirm_clicked = False
        confirm_selectors = [
            "button:has-text('Xoá')", "button:has-text('Xác nhận')",
            "button:has-text('OK')", "button:has-text('Đồng ý')",
            "button:has-text('Delete')", "button:has-text('Confirm')",
        ]
        for sel in confirm_selectors:
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=2_000):
                    btn.click()
                    confirm_clicked = True
                    print(f"  [INFO] Đã click confirm: {sel}")
                    self.page.wait_for_timeout(1_500)
                    break
            except Exception:
                continue

        self._record_check(TC, "S5: Confirm dialog xoá",
                           "✅ PASS" if confirm_clicked else "ℹ️ INFO",
                           "đã click confirm" if confirm_clicked
                           else "không có confirm dialog — xoá trực tiếp")
        self._shot(TC, "5", "after_confirm_delete")

        # ── S6: Verify xoá thành công (số ảnh giảm) ────────────────────────
        self.page.wait_for_timeout(1_000)
        count_after = self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left < 330 && r.width > 30 && r.height > 30
                    && img.complete && img.naturalWidth > 0;
            }).length;
        }""")

        deleted_ok = count_after < count_before
        self._shot(TC, "6", f"after_delete_count_{count_after}")
        self._record_check(
            TC, "S6: Xoá ảnh thành công — số ảnh giảm",
            "✅ PASS" if deleted_ok else "❌ FAIL",
            f"trước: {count_before} ảnh → sau: {count_after} ảnh"
            + (" (giảm 1)" if deleted_ok else " (không thay đổi — xoá thất bại)"),
        )

        if not deleted_ok:
            pytest.fail(
                f"Xoá ảnh thất bại — số ảnh không thay đổi "
                f"(before={count_before}, after={count_after})"
            )

        print(f"  [PASS] Xoá ảnh thành công: {count_before} → {count_after} ảnh")

    # ══════════════════════════════════════════════════════════════════════════
    # TC2: Tạo artwork mới → xoá luôn → không ảnh hưởng data cũ
    # ══════════════════════════════════════════════════════════════════════════

    def _count_library_images(self) -> int:
        """Đếm ảnh trong panel Thư Viện (x < 330px)."""
        return self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.left < 330 && r.width > 30 && r.height > 30
                    && img.complete && img.naturalWidth > 0;
            }).length;
        }""")

    def _do_delete_first_library_image(self, tc_id: str, step_prefix: str) -> bool:
        """Hover ảnh đầu tiên trong Thư Viện → click delete → confirm → verify giảm.
        Trả về True nếu xoá thành công. Dùng chung cho TC1 và TC2.
        """
        count_before = self._count_library_images()
        print(f"  [INFO] {tc_id}: count_before={count_before}")

        # Hover → tìm delete icon
        delete_info = self._hover_and_find_delete()
        self._shot(tc_id, f"{step_prefix}a", "hover_delete_icon")

        delete_found = delete_info.get("found", False)
        self._record_check(
            tc_id, "Icon xoá hiển thị khi hover",
            "✅ PASS" if delete_found else "❌ FAIL",
            delete_info.get("sel", delete_info.get("reason", "not found")),
        )
        if not delete_found:
            return False

        # Click delete icon
        del_x, del_y = delete_info.get("x", 0), delete_info.get("y", 0)
        if del_x and del_y:
            self.page.mouse.click(del_x, del_y)
        else:
            self.page.locator(delete_info.get("sel", "button")).first.click()
        self.page.wait_for_timeout(1_500)
        self._shot(tc_id, f"{step_prefix}b", "after_click_delete")

        # Xử lý confirm dialog
        confirm_clicked = False
        for sel in ["button:has-text('Xoá')", "button:has-text('Xác nhận')",
                    "button:has-text('OK')", "button:has-text('Đồng ý')",
                    "button:has-text('Delete')", "button:has-text('Confirm')"]:
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=2_000):
                    btn.click()
                    confirm_clicked = True
                    print(f"  [INFO] {tc_id}: confirm click: {sel}")
                    self.page.wait_for_timeout(1_500)
                    break
            except Exception:
                continue

        self._record_check(tc_id, "Confirm dialog xoá",
                           "✅ PASS" if confirm_clicked else "ℹ️ INFO",
                           "đã click confirm" if confirm_clicked else "không có confirm dialog")
        self._shot(tc_id, f"{step_prefix}c", "after_confirm")

        # Verify số ảnh giảm
        self.page.wait_for_timeout(1_000)
        count_after = self._count_library_images()
        deleted_ok = count_after < count_before
        self._record_check(
            tc_id, "Xoá ảnh thành công — số ảnh giảm",
            "✅ PASS" if deleted_ok else "❌ FAIL",
            f"{count_before} → {count_after} ảnh" + (" ✓" if deleted_ok else " ✗ không thay đổi"),
        )
        self._shot(tc_id, f"{step_prefix}d", f"final_count_{count_after}")
        print(f"  [{'PASS' if deleted_ok else 'FAIL'}] {tc_id}: {count_before} → {count_after}")
        return deleted_ok

    @pytest.mark.daily
    def test_library_delete_new_artwork(self):
        """Home → nhập prompt → AI tạo artwork → vào Thư Viện → xoá artwork vừa tạo.
        Không ảnh hưởng đến data cũ vì chỉ xoá ảnh mới tạo ra trong test này.
        """
        from pages.studio_page import StudioPage

        studio = StudioPage(self.page, self.env.fe_url)

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC2, "S1: Login thành công", "✅ PASS",
                           f"email: {self.env.login_email}")
        self._shot(TC2, "1", "after_login")

        # ── S2: Vào Home — kiểm tra prompt input ────────────────────────────
        self.home.navigate()
        self.page.wait_for_timeout(2_000)
        self._shot(TC2, "2", "home_page")

        has_prompt_input = self.home.prompt_input.is_visible(timeout=5_000)
        self._record_check(TC2, "S2: Home có ô nhập prompt",
                           "✅ PASS" if has_prompt_input else "ℹ️ INFO",
                           "có prompt input" if has_prompt_input else "home sau login không có prompt → vào Studio trực tiếp")

        # ── S3: Nhập prompt để tạo artwork ──────────────────────────────────
        if has_prompt_input:
            # Flow A: nhập prompt ở Home → Tạo ngay → navigate vào Studio
            self.home.fill_prompt(_TEST_PROMPT)
            self.page.wait_for_timeout(300)
            self._shot(TC2, "3", "prompt_filled_home")
            self.home.click_generate()
            try:
                self.page.wait_for_url("**/studio**", timeout=20_000)
            except Exception:
                pass
            self.page.wait_for_timeout(2_000)
            in_studio = "studio" in self.page.url
        else:
            # Flow B: đã login → Home hiện "Tạo ngay" → vào Studio → nhập prompt trong chat
            self._shot(TC2, "3", "home_no_prompt_go_studio")
            self._dismiss_product_dialog_from_studio(studio)
            in_studio = "studio" in self.page.url

        self._record_check(TC2, "S3: Navigate vào Studio",
                           "✅ PASS" if in_studio else "❌ FAIL", self.page.url)
        if not in_studio:
            pytest.fail(f"Không vào được Studio — URL: {self.page.url}")

        # ── S4: Xử lý setup Studio ──────────────────────────────────────────
        self._dismiss_product_dialog()
        self.page.wait_for_timeout(1_000)
        self._shot(TC2, "4", "studio_ready")

        # Nếu chưa nhập prompt ở Home → nhập trong Studio chat
        if not has_prompt_input:
            baseline = studio._count_chat_artworks()
            studio.generate(_TEST_PROMPT)
            self.page.wait_for_timeout(1_000)
            self._shot(TC2, "4b", "prompt_submitted_studio")
        else:
            baseline = studio._count_chat_artworks()

        # ── S5: Chờ AI tạo artwork mới ───────────────────────────────────────
        self._record_check(TC2, "S5: Bắt đầu tạo artwork",
                           "✅ PASS", f"prompt: '{_TEST_PROMPT}' | baseline: {baseline}")

        ok, elapsed, total, new_count = studio.wait_for_new_artworks(
            baseline=baseline, min_new=1, timeout=120
        )
        self._shot(TC2, "5", f"artwork_generated_{new_count}imgs_{elapsed}s")
        self._record_check(
            TC2, "S5: AI tạo artwork thành công",
            "✅ PASS" if ok else "❌ FAIL",
            f"{new_count} ảnh mới sau {elapsed}s (tổng chat: {total})",
        )
        if not ok or new_count == 0:
            pytest.fail(f"AI không tạo được artwork mới sau {elapsed}s")

        # ── S6: Dọn dialogs → mở tab Thư Viện ──────────────────────────────
        # Sau khi gen artwork, có thể xuất hiện: Terms dialog + Chọn sản phẩm dialog
        self._accept_terms_if_any()
        self._dismiss_product_dialog()
        self.page.wait_for_timeout(1_000)
        self._shot(TC2, "6_clean", "dialogs_dismissed")

        # Click tab Thư Viện bằng JS (button là icon-only, có thể bị hidden với Playwright)
        self._open_library_tab_js()
        self.page.wait_for_timeout(2_000)

        count_before_delete = self._count_library_images()
        self._shot(TC2, "6", f"library_open_count_{count_before_delete}")
        self._record_check(TC2, "S6: Mở Thư Viện — đếm ảnh ban đầu",
                           "✅ PASS", f"{count_before_delete} ảnh (ảnh mới nhất ở đầu danh sách)")

        # ── S7: Xoá ảnh đầu tiên (artwork vừa tạo) ──────────────────────────
        deleted = self._do_delete_first_library_image(TC2, step_prefix="7")

        if not deleted:
            pytest.fail("Xoá artwork mới tạo thất bại")

        print(f"  [PASS] TC2 hoàn thành — artwork test đã được tạo và xoá sạch")
