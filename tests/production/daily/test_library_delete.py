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

    def _open_my_images_tab(self) -> str:
        """Trong panel Thư Viện có 2 sub-tab: 'Mẫu hình in' (template) và 'Hình của bạn'
        (ảnh user — xoá được). Mặc định mở 'Mẫu hình in' → phải click 'Hình của bạn'
        để thấy ảnh user + nút xoá (nút xoá chỉ MOUNT ở tab này).
        """
        result = self.page.evaluate("""() => {
            const cands = Array.from(document.querySelectorAll(
                'button, [role="tab"], a, div[class*="tab" i], span'));
            for (const el of cands) {
                const t = (el.innerText || '').trim();
                // match chính xác text tab, tránh bắt nhầm node cha quá dài
                if (t.length <= 24 && /(Hình của bạn|Ảnh của bạn|Của bạn|My (Images|Designs))/i.test(t)) {
                    el.click();
                    return 'clicked: ' + t;
                }
            }
            return 'not found';
        }""")
        print(f"  [INFO] Tab 'Hình của bạn': {result}")
        self.page.wait_for_timeout(1_500)
        return result

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
        self.page.wait_for_timeout(1_500)

        # Step 4b: Click sub-tab "Hình của bạn" (ảnh user xoá được; nút xoá chỉ
        # mount ở tab này, KHÔNG có ở tab mặc định "Mẫu hình in").
        self._open_my_images_tab()
        self.page.wait_for_timeout(1_500)

        # Step 5: Đếm ảnh user (= số nút xoá) trong 'Hình của bạn'
        count = self._count_library_images()
        print(f"  [INFO] Số ảnh user trong 'Hình của bạn': {count}")
        return count > 0

    # ── Test chính ───────────────────────────────────────────────────────────

    @pytest.mark.daily
    def test_library_delete_image(self):
        """Login → Studio → Thư Viện → tab 'Hình của bạn' → VERIFY icon xoá hiển thị.

        AN TOÀN: chỉ VERIFY nút xoá tồn tại trên card ảnh user (KHÔNG xoá ảnh có
        sẵn để tránh mất data thật trên PROD). Việc 'xoá thành công' được test ở
        TC2 (test_library_delete_new_artwork) với ảnh do chính test tự tạo ra.
        """

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC, "S1: Login thành công", "✅ PASS",
                           f"email: {self.env.login_email}")
        self._shot(TC, "1", "after_login")

        # ── S2: Mở panel Thư Viện → tab 'Hình của bạn' ──────────────────────
        has_images = self._open_library_panel()
        self._shot(TC, "2", "library_panel_opened")

        if not has_images:
            self._record_check(TC, "S2: Tab 'Hình của bạn' có ảnh",
                               "⚠️ WARN", "Không có ảnh user nào — không thể verify icon xoá")
            pytest.skip("Tab 'Hình của bạn' chưa có ảnh — tạo/upload ảnh trước khi chạy test này")

        count = self._count_library_images()
        self._record_check(TC, "S2: Tab 'Hình của bạn' có ảnh",
                           "✅ PASS", f"Có {count} ảnh user (mỗi ảnh 1 nút xoá)")

        # ── S3: Hover card đầu → verify nút xoá (svg.lucide-trash-2) hiển thị ─
        cards = self._grid_cards_info()
        delete_found = bool(cards) and bool(cards[0].get("trashX"))
        if delete_found:
            c0 = cards[0]
            # hover để xác nhận nút lộ ra (group-hover) — KHÔNG click xoá
            if c0.get("imgX") and c0.get("imgY"):
                self.page.mouse.move(c0["imgX"], c0["imgY"])
                self.page.wait_for_timeout(1_000)
        self._shot(TC, "3", "hover_show_delete_icon")

        self._record_check(
            TC, "S3: Icon xoá hiển thị trên ảnh user",
            "✅ PASS" if delete_found else "❌ FAIL",
            f"{len(cards)} card có nút xoá (svg.lucide-trash-2)" if delete_found
            else "Không tìm thấy nút xoá trên card ảnh user",
        )

        if not delete_found:
            pytest.fail(
                "Không tìm thấy icon xoá (svg.lucide-trash-2) trên card ảnh user "
                "trong tab 'Hình của bạn'."
            )

        print(f"  [PASS] Verify icon xoá: {len(cards)} ảnh user đều có nút xoá")

    # ══════════════════════════════════════════════════════════════════════════
    # TC2: Tạo artwork mới → xoá luôn → không ảnh hưởng data cũ
    # ══════════════════════════════════════════════════════════════════════════

    def _count_library_images(self) -> int:
        """Đếm ảnh user trong tab 'Hình của bạn' = số nút xoá (svg.lucide-trash-2)
        trong panel trái. Đếm theo nút xoá để loại logo/icon (mỗi ảnh user có đúng
        1 nút xoá; template ở tab 'Mẫu hình in' KHÔNG có nút xoá).
        """
        return self.page.evaluate(r"""() => {
            return [...document.querySelectorAll('button')].filter(b => {
                if (!b.querySelector('svg[class*="trash" i]')) return false;
                const r = b.getBoundingClientRect();
                return r.width > 0 && r.left < 380 && r.top > 60;
            }).length;
        }""")

    def _grid_cards_info(self) -> list:
        """Trả về danh sách card ảnh user trong 'Hình của bạn' theo thứ tự DOM:
        [{src, imgX, imgY, trashX, trashY}]. Mỗi card = 1 img + 1 nút xoá (trash).
        Dùng để (a) snapshot baseline src, (b) xoá đúng card theo src.
        """
        return self.page.evaluate(r"""() => {
            const btns = [...document.querySelectorAll('button')].filter(b => {
                if (!b.querySelector('svg[class*="trash" i]')) return false;
                const r = b.getBoundingClientRect();
                return r.width > 0 && r.left < 380 && r.top > 60;
            });
            return btns.map(b => {
                const br = b.getBoundingClientRect();
                let img = null, p = b, depth = 0;
                while (p && depth < 6) {
                    const i = p.querySelector('img[src]');
                    if (i && i.src && !/logo/i.test(i.src)) { img = i; break; }
                    p = p.parentElement; depth++;
                }
                const ir = img ? img.getBoundingClientRect() : null;
                return {
                    src: img ? img.src : '',
                    imgX: ir ? Math.round(ir.left + ir.width / 2) : 0,
                    imgY: ir ? Math.round(ir.top + ir.height / 2) : 0,
                    trashX: Math.round(br.left + br.width / 2),
                    trashY: Math.round(br.top + br.height / 2),
                };
            });
        }""")

    def _delete_card_by_coords(self, tc_id: str, step_prefix: str,
                               card: dict) -> bool:
        """Hover card → click nút xoá → confirm dialog. card = item từ _grid_cards_info()."""
        # Hover ảnh để lộ nút xoá (opacity-0 group-hover)
        if card.get("imgX") and card.get("imgY"):
            self.page.mouse.move(card["imgX"], card["imgY"])
            self.page.wait_for_timeout(1_200)
        self._shot(tc_id, f"{step_prefix}a", "hover_card")
        # Click nút xoá theo toạ độ
        self.page.mouse.click(card["trashX"], card["trashY"])
        self.page.wait_for_timeout(1_200)
        self._shot(tc_id, f"{step_prefix}b", "after_click_trash")
        # Confirm dialog (nếu có)
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
        return confirm_clicked

    @pytest.mark.daily
    def test_library_delete_new_artwork(self):
        """Studio → snapshot 'Hình của bạn' → AI tạo artwork → xoá ĐÚNG ảnh mới (src-diff).
        An toàn data cũ: chỉ xoá ảnh có src KHÔNG nằm trong baseline (tức ảnh test tự tạo).
        """
        from pages.studio_page import StudioPage

        studio = StudioPage(self.page, self.env.fe_url)

        # ── S1: Login ────────────────────────────────────────────────────────
        self._login()
        self._record_check(TC2, "S1: Login thành công", "✅ PASS",
                           f"email: {self.env.login_email}")
        self._shot(TC2, "1", "after_login")

        # ── S2: Vào Studio + dismiss dialogs ───────────────────────────────
        studio.navigate()
        self.page.wait_for_timeout(2_000)
        self._accept_terms_if_any()
        self._dismiss_product_dialog()
        self.page.wait_for_timeout(1_000)
        in_studio = "studio" in self.page.url
        self._record_check(TC2, "S2: Vào Studio",
                           "✅ PASS" if in_studio else "❌ FAIL", self.page.url)
        if not in_studio:
            pytest.fail(f"Không vào được Studio — URL: {self.page.url}")
        self._shot(TC2, "2", "studio_ready")

        # ── S3: Snapshot baseline 'Hình của bạn' TRƯỚC khi tạo artwork ─────
        # (để xác định chính xác ảnh MỚI theo src-diff → chỉ xoá ảnh test tự tạo,
        #  KHÔNG đụng ảnh cũ.)
        self._open_library_tab_js()
        self.page.wait_for_timeout(1_000)
        self._open_my_images_tab()
        self.page.wait_for_timeout(1_500)
        baseline_cards = self._grid_cards_info()
        baseline_srcs = {c["src"] for c in baseline_cards if c.get("src")}
        count_before = len(baseline_cards)
        self._shot(TC2, "3", f"baseline_my_images_{count_before}")
        self._record_check(TC2, "S3: Snapshot baseline 'Hình của bạn'",
                           "✅ PASS", f"{count_before} ảnh user hiện có (baseline để diff)")

        # ── S4: Tạo artwork mới qua Studio chat ────────────────────────────
        chat_baseline = studio._count_chat_artworks()
        studio.generate(_TEST_PROMPT)
        self.page.wait_for_timeout(1_000)
        self._shot(TC2, "4", "prompt_submitted")
        self._record_check(TC2, "S4: Gửi prompt tạo artwork",
                           "✅ PASS", f"prompt: '{_TEST_PROMPT}'")

        # ── S5: Chờ AI tạo artwork mới ─────────────────────────────────────
        ok, elapsed, total, new_count = studio.wait_for_new_artworks(
            baseline=chat_baseline, min_new=1, timeout=180
        )
        self._shot(TC2, "5", f"artwork_generated_{new_count}imgs_{elapsed}s")
        self._record_check(
            TC2, "S5: AI tạo artwork thành công",
            "✅ PASS" if ok else "❌ FAIL",
            f"{new_count} ảnh mới sau {elapsed}s (chat total: {total})",
        )
        if not ok or new_count == 0:
            pytest.fail(f"AI không tạo được artwork mới sau {elapsed}s")

        # ── S6: Mở lại 'Hình của bạn' → tìm artwork MỚI (src ∉ baseline) ───
        self._accept_terms_if_any()
        self._dismiss_product_dialog()
        self._open_library_tab_js()
        self.page.wait_for_timeout(800)
        self._open_my_images_tab()
        self.page.wait_for_timeout(1_500)

        fresh_srcs = set()
        for _ in range(10):  # ảnh mới có thể mất vài giây mới lưu vào thư viện
            cards = self._grid_cards_info()
            fresh_srcs = {c["src"] for c in cards
                          if c.get("src") and c["src"] not in baseline_srcs}
            if fresh_srcs:
                break
            self.page.wait_for_timeout(2_000)
        count_now = self._count_library_images()
        self._shot(TC2, "6", f"my_images_after_gen_{count_now}")

        if not fresh_srcs:
            # KHÔNG có ảnh mới trong thư viện → KHÔNG xoá gì (tránh xoá nhầm ảnh cũ).
            self._record_check(
                TC2, "S6: Tìm artwork mới trong 'Hình của bạn'", "⚠️ WARN",
                f"Không thấy ảnh mới (baseline={count_before}, now={count_now}) — "
                f"artwork chưa lưu vào thư viện; BỎ QUA xoá để an toàn data cũ")
            self.__class__._results = self._results
            self._save_report()
            pytest.skip("Artwork mới chưa lưu vào 'Hình của bạn' — không có ảnh test để xoá an toàn")
        self._record_check(TC2, "S6: Tìm artwork mới trong 'Hình của bạn'",
                           "✅ PASS",
                           f"{len(fresh_srcs)} ảnh mới (src ∉ baseline {count_before})")

        # ── S7: Xoá HẾT ảnh fresh (chỉ ảnh test tự tạo) → verify ─────────────
        # Mỗi lần xoá toạ độ dịch → re-query card theo src còn lại sau mỗi vòng.
        targets = set(fresh_srcs)
        deleted_n = 0
        for i in range(len(targets) + 2):
            cards = self._grid_cards_info()
            todo = [c for c in cards if c.get("src") in targets]
            if not todo:
                break
            self._delete_card_by_coords(TC2, step_prefix=f"7_{i}", card=todo[0])
            targets.discard(todo[0]["src"])
            deleted_n += 1
            self.page.wait_for_timeout(800)

        # Verify: KHÔNG còn src fresh nào trong grid
        after_cards = self._grid_cards_info()
        after_srcs = {c["src"] for c in after_cards if c.get("src")}
        remaining = fresh_srcs & after_srcs
        count_after = len(after_cards)
        deleted_ok = not remaining
        self._shot(TC2, "7d", f"final_count_{count_after}")
        self._record_check(
            TC2, "S7: Xoá artwork mới thành công",
            "✅ PASS" if deleted_ok else "❌ FAIL",
            f"đã xoá {deleted_n}/{len(fresh_srcs)} ảnh mới; "
            f"còn sót {len(remaining)} | số ảnh: {count_now} → {count_after} (baseline {count_before})",
        )
        if not deleted_ok:
            pytest.fail(
                f"Xoá artwork mới thất bại — còn sót {len(remaining)} src fresh "
                f"(đã xoá {deleted_n}/{len(fresh_srcs)})"
            )

        print(f"  [PASS] TC2 — tạo & xoá sạch {deleted_n} artwork test (src-diff), data cũ nguyên vẹn")
