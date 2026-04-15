"""
TC_GEN_001 — Step-by-step với screenshot từng bước làm bằng chứng.
Chạy: pytest tests/test_gen_with_steps.py --headed -v
"""

import time
import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.report_writer import ReportWriter

import random

PROMPTS = [
    "Thiết kế phong cách Cyberpunk, một vận động viên trượt ván dưới ánh đèn neon rực rỡ",
    "Phong cách tối giản: Chân dung một cô gái đeo tai nghe hiện đại, đường nét thanh lịch",
    "Nghệ thuật Graffiti đường phố: Hình ảnh chó bull đeo kính râm cực ngầu và Hip-hop",
    "Phong cách Cinematic: Một ly cà phê bốc khói trên bàn làm việc của một startup công nghệ",
    "Thiết kế trẻ trung: Những khối màu trừu tượng kết hợp với biểu tượng mạng xã hội hiện đại",
    "Phong cách đời thực: Một buổi chiều hoàng hôn trên sân thượng thành phố với nhóm bạn trẻ",
    "Vẽ nét mảnh (Fine line): Hình ảnh phi hành gia đang chơi guitar giữa không gian vũ trụ",
    "Phong cách Pop-art: Một quả lăng trụ rực rỡ màu sắc đại diện cho sự năng động của giới trẻ",
    "Thiết kế Typography: Chữ 'GEN Z' cách điệu kết hợp với các họa tiết hình học năng động",
    "Phong cách Manga hiện đại: Một nhân vật anime đang chạy marathon trong trang phục thể thao techwear"
]


@pytest.mark.artwork
class TestArtworkGenerationSteps:

    def test_TC_GEN_001_step_by_step(self, page: Page, base_url: str, report: ReportWriter):
        """
        TC_GEN_001 — Full flow với screenshot mỗi bước:
        Step 1: Truy cập trang
        Step 2: Kiểm tra input visible
        Step 3: Nhập prompt
        Step 4: Kiểm tra button, click Generate
        Step 5: Loading indicator xuất hiện
        Step 6: Chờ artwork hoàn thành
        Step 7: Artwork visible + dimensions
        Step 8: Screenshot kết quả cuối
        """
        tc_id = "TC_GEN_001"
        home = HomePage(page, base_url)
        
        # Chon Prompt ngau nhien cho moi lan chay
        selected_prompt = random.choice(PROMPTS)
        print(f"\n[INFO] Selected Prompt for this run: {selected_prompt}")
        
        start_time = time.time()

        try:
            # ── Step 1: Truy cập trang ────────────────────────────────────────
            home.goto()
            print(f"\n[PASS] Step 1: Truy cap {base_url}")

            # ── Step 2: Drag Story Box để mở form ────────────────────────────
            home.open_story_box()
            print(f"[PASS] Step 2: Drag Story Box thanh cong")

            # ── Step 3: Kiểm tra textarea visible ────────────────────────────
            inp = home.get_prompt_input()
            expect(inp).to_be_visible()
            print(f"[PASS] Step 3: Textarea visible")

            # ── Step 4: Nhập prompt ───────────────────────────────────────────
            home.enter_prompt(selected_prompt)
            print(f"[PASS] Step 4: Nhap prompt '{selected_prompt}' xong")

            # ── Step 5: Kiểm tra button, click Generate ───────────────────────
            btn = home.get_generate_button()
            expect(btn).to_be_visible()
            expect(btn).to_be_enabled()
            
            start_time = time.time()
            home.click_generate()
            print(f"[PASS] Step 5: Click Generate thanh cong")

            # ── Step 6: Email gate ────────────────────────────────────────────
            page.wait_for_timeout(1_000)
            handled = home.handle_email_gate("mainth@bccii.co.jp")
            print(f"[PASS] Step 6: Email gate handled={handled}")

            # ── Step 7: Chờ artwork ───────────────────────────────────────────
            print(f"[WAIT] Step 7: Dang cho AI tao artwork (toi da 120s)...")
            artwork = home.wait_for_artwork()
            elapsed = time.time() - start_time
            print(f"[PASS] Step 7: Artwork xuat hien sau {elapsed:.1f}s")

            # ── Step 8: Kiểm tra nội dung ảnh (gift box / review) ─────────────
            print(f"[WAIT] Step 8: Dang kiem tra noi dung anh bang AI Vision...")
            _, vision_reason = home.assert_artwork_relevance(artwork, selected_prompt)
            print(f"[PASS] Step 8: Vision check finished - {vision_reason}")

            # ── Step 9: Kiểm tra dimensions + viewport ────────────────────────
            artwork.scroll_into_view_if_needed()
            home.assert_artwork_visible(artwork)
            home.assert_artwork_has_dimensions(artwork)

            dims = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const real = imgs.find(i => i.naturalWidth > 0);
                return real ? { w: real.naturalWidth, h: real.naturalHeight } : null;
            }""")

            # ── Step 10: Screenshot cuối đầy đủ ────────────────────────────
            print(f"DEBUG: Current URL before final screenshot: {page.url}")
            page.wait_for_load_state("networkidle")
            artwork.scroll_into_view_if_needed()
            page.wait_for_timeout(2000)
            final_shot = home.take_screenshot("TC_GEN_001_SUCCESS_FINAL", folder="TC_GEN_001")
            print(f"[PASS] Step 10: Final artwork screenshot captured: {final_shot}")

            # ── Báo cáo ───────────────────────────────────────────────────────
            report.add(
                tc_id, "PASS",
                screen="HomePage", module="ArtworkGeneration",
                title=f"Generate: {selected_prompt}",
                priority="P0",
                actual=f"Artwork OK. Vision: {vision_reason}. Kích thước: {{'Rộng': {dims['w']}, 'Cao': {dims['h']}}}",
                gen_time=f"{elapsed:.1f}s",
                screenshot=final_shot,
            )

        except AssertionError as exc:
            s = home.take_screenshot("TC_GEN_001_FAIL_assertion", folder="TC_GEN_001")
            err = str(exc)
            print(f"\n[FAIL] TC_GEN_001 FAIL (assertion): {err}")
            bug_id = "BUG-GEN-VISION-001" if "GIFT_BOX" in err or "NOT_RELEVANT" in err else "BUG-GEN-001"
            report.add(
                tc_id, "FAIL",
                screen="HomePage", module="ArtworkGeneration",
                title="Generate artwork — Vietnamese prompt",
                priority="P0", actual=err,
                gen_time=f"{time.time() - start_time:.1f}s",
                screenshot=s, bug_id=bug_id, bug_desc=err
            )
            raise

        except Exception as exc:
            s = home.take_screenshot("TC_GEN_001_FAIL_error", folder="TC_GEN_001")
            print(f"\n[FAIL] TC_GEN_001 ERROR: {exc}")
            report.add(
                tc_id, "FAIL",
                screen="HomePage", module="ArtworkGeneration",
                title="Generate artwork — Vietnamese prompt",
                priority="P0", actual=str(exc),
                gen_time=f"{time.time() - start_time:.1f}s",
                screenshot=s, bug_id="BUG-GEN-001", bug_desc=str(exc)
            )
            raise
