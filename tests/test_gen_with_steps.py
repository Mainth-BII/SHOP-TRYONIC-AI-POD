"""
TC_GEN_001 — Step-by-step với screenshot từng bước làm bằng chứng.
Chạy: pytest tests/test_gen_with_steps.py --headed -v
"""

import time
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.report_writer import ReportWriter

PROMPT_VI = "Tôi yêu bóng đá và màu xanh lá — tạo cho tôi một thiết kế thể thao"


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
        screenshots = []
        start_time = time.time()

        try:
            # ── Step 1: Truy cập trang ────────────────────────────────────────
            home.goto()
            s = home.take_screenshot("STEP1_trang_chu", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"\n[PASS] Step 1: Truy cap {base_url} - Story Box hien thi")

            # ── Step 2: Drag Story Box để mở form ────────────────────────────
            home.open_story_box()
            s = home.take_screenshot("STEP2_sau_drag_story_box", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 2: Drag Story Box thanh cong - form hien ra")

            # ── Step 3: Kiểm tra textarea visible ────────────────────────────
            inp = home.get_prompt_input()
            expect(inp).to_be_visible()
            s = home.take_screenshot("STEP3_input_visible", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 3: Textarea visible - OK")

            # ── Step 4: Nhập prompt ───────────────────────────────────────────
            home.enter_prompt(PROMPT_VI)
            s = home.take_screenshot("STEP4_nhap_prompt", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 4: Nhap prompt - OK")

            # ── Step 5: Kiểm tra button, click Generate ───────────────────────
            btn = home.get_generate_button()
            expect(btn).to_be_visible()
            expect(btn).to_be_enabled()
            s = home.take_screenshot("STEP5_truoc_click", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 5: Button 'Tao chiec ao' visible + enabled - Dang click...")

            start_time = time.time()
            home.click_generate()

            # ── Step 6: Email gate ────────────────────────────────────────────
            page.wait_for_timeout(1_500)
            s = home.take_screenshot("STEP6_email_gate", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 6: Email gate captured")

            handled = home.handle_email_gate("mainth@bccii.co.jp")
            page.wait_for_timeout(800)
            s = home.take_screenshot("STEP6b_sau_email", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 6b: Email gate handled={handled}, email=mainth@bccii.co.jp")

            # ── Step 7: Chờ artwork ───────────────────────────────────────────
            print(f"[WAIT] Step 7: Dang cho AI tao artwork (toi da 120s)...")
            artwork = home.wait_for_artwork()
            elapsed = time.time() - start_time
            print(f"[PASS] Step 7: Artwork xuat hien sau {elapsed:.1f}s")

            s = home.take_screenshot("STEP7_artwork_appeared", folder="TC_GEN_001")
            screenshots.append(s)

            # ── Step 8: Kiểm tra dimensions + viewport ────────────────────────
            artwork.scroll_into_view_if_needed()
            home.assert_artwork_visible(artwork)
            home.assert_artwork_has_dimensions(artwork)

            dims = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const real = imgs.find(i => i.naturalWidth > 0);
                return real ? { w: real.naturalWidth, h: real.naturalHeight, src: real.src.substring(0, 80) } : null;
            }""")
            print(f"[PASS] Step 8: Artwork dimensions - {dims}")

            # ── Step 9: Screenshot cuối đầy đủ ────────────────────────────────
            page.wait_for_timeout(500)
            s = home.take_screenshot("STEP9_PASS_ket_qua_cuoi", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"[PASS] Step 9: Final screenshot - {s}")

            # ── Báo cáo ───────────────────────────────────────────────────────
            print(f"\n{'='*60}")
            print(f"[PASS] TC_GEN_001 PASS - Hoan thanh trong {elapsed:.1f}s")
            print(f"[INFO] Screenshots ({len(screenshots)}):")
            for i, sc in enumerate(screenshots, 1):
                print(f"   {i}. {sc}")
            print(f"{'='*60}")

            report.add(
                tc_id, "PASS",
                screen="HomePage", module="ArtworkGeneration",
                title="Generate artwork — Vietnamese prompt (step-by-step)",
                priority="P0",
                actual=f"Artwork visible. Dimensions: {dims}",
                gen_time=f"{elapsed:.1f}s",
                screenshot=screenshots[-1],
            )

        except Exception as exc:
            s = home.take_screenshot("STEP_FAIL", folder="TC_GEN_001")
            screenshots.append(s)
            print(f"\n[FAIL] TC_GEN_001 FAIL: {exc}")
            print(f"[INFO] Screenshots captured: {screenshots}")
            report.add(
                tc_id, "FAIL",
                screen="HomePage", module="ArtworkGeneration",
                title="Generate artwork — Vietnamese prompt (step-by-step)",
                priority="P0",
                actual=str(exc),
                gen_time=f"{time.time() - start_time:.1f}s",
                screenshot=s,
                bug_id="BUG-GEN-001",
                bug_desc=str(exc),
            )
            raise
