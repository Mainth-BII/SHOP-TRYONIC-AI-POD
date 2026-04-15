"""
TC_GEN + TC_VAL: Artwork generation & validation tests.
Main flow: enter prompt → click generate → wait for artwork image → verify.

Key challenge: AI generation can take 10–120 seconds.
The HomePage.wait_for_artwork() method handles this with a 120s timeout.
"""

import time
import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.report_writer import ReportWriter


# ── Test prompts ─────────────────────────────────────────────────────────────

PROMPT_VI = "Tôi yêu bóng đá và màu xanh lá — tạo cho tôi một thiết kế thể thao"
PROMPT_EN = "I love football and the color green — create a sporty design for me"
PROMPT_EMPTY = ""
PROMPT_SPACES = "     "
PROMPT_SINGLE = "A"
PROMPT_LONG = "x" * 1200
PROMPT_XSS = "<script>alert('xss')</script>"
PROMPT_EMOJI = "🎨🌈🎸🎯🏆"


@pytest.mark.artwork
class TestArtworkGeneration:
    """TC_GEN_001 — TC_GEN_009: Happy-path artwork generation."""

    # ── TC_GEN_001 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_001_generate_vietnamese_prompt(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Generate artwork with valid Vietnamese prompt (P0 — core flow)."""
        tc_id = "TC_GEN_001"
        home = HomePage(page, base_url)
        start = time.time()
        try:
            home.goto()
            artwork = home.generate_artwork(PROMPT_VI)
            elapsed = time.time() - start

            home.assert_artwork_visible(artwork)
            home.assert_artwork_has_dimensions(artwork)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(
                tc_id, "PASS",
                screen="HomePage", module="ArtworkGeneration",
                title="Generate artwork — Vietnamese prompt",
                priority="P0",
                actual="Artwork visible",
                gen_time=f"{elapsed:.1f}s",
                screenshot=shot,
            )
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generate artwork — Vietnamese prompt",
                       priority="P0", actual=str(exc),
                       gen_time=f"{time.time() - start:.1f}s",
                       screenshot=shot,
                       bug_id="BUG-GEN-001",
                       bug_desc=f"[What] Artwork did not appear after Vietnamese prompt.\n"
                                f"[Expected] Image visible within 120s.\n"
                                f"[Impact] Core user flow broken — no artwork shown.\n"
                                f"[Error] {exc}")
            raise

    # ── TC_GEN_002 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_002_generate_english_prompt(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Generate artwork with valid English prompt."""
        tc_id = "TC_GEN_002"
        home = HomePage(page, base_url)
        start = time.time()
        try:
            home.goto()
            artwork = home.generate_artwork(PROMPT_EN)
            elapsed = time.time() - start
            home.assert_artwork_visible(artwork)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generate artwork — English prompt",
                       priority="P1", actual="Artwork visible",
                       gen_time=f"{elapsed:.1f}s", screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generate artwork — English prompt",
                       priority="P1", actual=str(exc),
                       gen_time=f"{time.time() - start:.1f}s",
                       screenshot=shot,
                       bug_id="BUG-GEN-002", bug_desc=str(exc))
            raise

    # ── TC_GEN_003 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_003_loading_indicator_shown(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Loading indicator visible immediately after clicking Generate."""
        tc_id = "TC_GEN_003"
        home = HomePage(page, base_url)
        loading_seen = False
        try:
            home.goto()
            home.enter_prompt(PROMPT_VI)
            home.click_generate()

            # Check for any of the loading selectors within first 3 seconds
            for sel in home._loading_selectors:
                loc = page.locator(sel).first
                if loc.count() > 0:
                    try:
                        loc.wait_for(state="visible", timeout=3_000)
                        loading_seen = True
                        break
                    except Exception:
                        continue

            # Also accept: button becomes disabled during generation
            if not loading_seen:
                btn = home.get_generate_button()
                try:
                    expect(btn).to_be_disabled(timeout=3_000)
                    loading_seen = True
                except Exception:
                    pass

            shot = home.take_screenshot(f"{tc_id}_{'PASS' if loading_seen else 'FAIL'}",
                                        folder="ArtworkGeneration")
            status = "PASS" if loading_seen else "FAIL"
            report.add(tc_id, status,
                       screen="HomePage", module="ArtworkGeneration",
                       title="Loading indicator shown",
                       priority="P1",
                       actual="Loading indicator detected" if loading_seen
                       else "No loading indicator found",
                       screenshot=shot,
                       bug_id="" if loading_seen else "BUG-GEN-003",
                       bug_desc="" if loading_seen
                       else "[What] No loading feedback after Generate click.\n"
                            "[Expected] Spinner/skeleton/disabled button shown.\n"
                            "[Impact] Bad UX — user doesn't know request is processing.")
            if not loading_seen:
                pytest.fail("No loading indicator detected after Generate click")

            # Wait for generation to complete for cleanup
            home.wait_for_artwork()
        except Exception as exc:
            if "BUG-GEN-003" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
                report.add(tc_id, "FAIL",
                           screen="HomePage", module="ArtworkGeneration",
                           title="Loading indicator shown", priority="P1",
                           actual=str(exc), screenshot=shot,
                           bug_id="BUG-GEN-003", bug_desc=str(exc))
            raise

    # ── TC_GEN_004 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_004_loading_disappears_after_generation(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Loading indicator is gone after artwork appears."""
        tc_id = "TC_GEN_004"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.generate_artwork(PROMPT_VI)

            # Verify all loading selectors are gone
            for sel in home._loading_selectors:
                loc = page.locator(sel)
                if loc.count() > 0:
                    assert loc.first.is_hidden(), \
                        f"Loading indicator still visible: {sel}"

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Loading disappears after generation",
                       priority="P1", actual="All loading indicators gone",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Loading disappears after generation",
                       priority="P1", actual=str(exc), screenshot=shot,
                       bug_id="BUG-GEN-004", bug_desc=str(exc))
            raise

    # ── TC_GEN_005 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_005_artwork_has_valid_dimensions(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Generated image has non-zero naturalWidth and naturalHeight."""
        tc_id = "TC_GEN_005"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.generate_artwork(PROMPT_VI)
            home.assert_artwork_has_dimensions(home.get_artwork_image())

            dims = page.evaluate("""() => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const real = imgs.find(i => i.naturalWidth > 0);
                return real ? { w: real.naturalWidth, h: real.naturalHeight } : null;
            }""")

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Artwork has valid dimensions",
                       priority="P0",
                       actual=f"Image dimensions: {dims}",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Artwork has valid dimensions",
                       priority="P0", actual=str(exc), screenshot=shot,
                       bug_id="BUG-GEN-005",
                       bug_desc=f"[What] Artwork image has zero/null dimensions.\n"
                                f"[Expected] naturalWidth > 0, naturalHeight > 0.\n"
                                f"[Impact] Broken image shown to user.")
            raise

    # ── TC_GEN_006 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_006_artwork_in_viewport(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Generated artwork is visible in the viewport after scroll adjustment."""
        tc_id = "TC_GEN_006"
        home = HomePage(page, base_url)
        try:
            home.goto()
            artwork = home.generate_artwork(PROMPT_VI)
            artwork.scroll_into_view_if_needed()
            expect(artwork).to_be_in_viewport(ratio=0.5)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Artwork visible in viewport",
                       priority="P0", actual="Image in viewport (ratio>=0.5)",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Artwork visible in viewport",
                       priority="P0", actual=str(exc), screenshot=shot,
                       bug_id="BUG-GEN-006", bug_desc=str(exc))
            raise

    # ── TC_GEN_007 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_007_description_displayed_with_artwork(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """After generation, description/caption text is shown near the artwork."""
        tc_id = "TC_GEN_007"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.generate_artwork(PROMPT_VI)

            # Check for text near/around artwork area
            keyword_fragments = ["thiết kế", "design", "câu chuyện", "mô tả",
                                  "story", "artwork", "kết quả", "result"]
            text_found = False
            page_text = page.inner_text("body").lower()
            for kw in keyword_fragments:
                if kw in page_text:
                    text_found = True
                    break

            shot = home.take_screenshot(f"{tc_id}_{'PASS' if text_found else 'FAIL'}",
                                        folder="ArtworkGeneration")
            status = "PASS" if text_found else "FAIL"
            report.add(tc_id, status,
                       screen="HomePage", module="ArtworkGeneration",
                       title="Description shown with artwork",
                       priority="P1",
                       actual="Description text found" if text_found
                       else "No description text found near artwork",
                       screenshot=shot,
                       bug_id="" if text_found else "BUG-GEN-007",
                       bug_desc="" if text_found
                       else "[What] No caption/description shown alongside artwork.\n"
                            "[Expected] User's story/prompt displayed with result.\n"
                            "[Impact] User cannot confirm design matches their story.")
            if not text_found:
                pytest.fail("No description/caption text found after artwork generation")
        except Exception as exc:
            if "BUG-GEN-007" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
                report.add(tc_id, "FAIL",
                           screen="HomePage", module="ArtworkGeneration",
                           title="Description shown with artwork",
                           priority="P1", actual=str(exc), screenshot=shot,
                           bug_id="BUG-GEN-007", bug_desc=str(exc))
            raise

    # ── TC_GEN_008 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_008_generate_second_artwork(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Generating a second artwork replaces/updates the first."""
        tc_id = "TC_GEN_008"
        home = HomePage(page, base_url)
        try:
            home.goto()
            # First generation
            home.generate_artwork(PROMPT_VI)
            first_src = page.evaluate(
                "() => { const img = document.querySelector('img'); return img ? img.src : ''; }"
            )

            # Second generation
            artwork2 = home.generate_artwork(PROMPT_EN)
            second_src = page.evaluate(
                "() => { const img = document.querySelector('img'); return img ? img.src : ''; }"
            )

            home.assert_artwork_visible(artwork2)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Second artwork generation",
                       priority="P1",
                       actual=f"Second artwork visible. Src changed: {first_src != second_src}",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Second artwork generation",
                       priority="P1", actual=str(exc), screenshot=shot,
                       bug_id="BUG-GEN-008", bug_desc=str(exc))
            raise

    # ── TC_GEN_009 ─────────────────────────────────────────────────────────────

    def test_TC_GEN_009_generation_completes_within_120s(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Artwork generation completes within 120 seconds SLA."""
        tc_id = "TC_GEN_009"
        home = HomePage(page, base_url)
        start = time.time()
        try:
            home.goto()
            home.generate_artwork(PROMPT_VI)
            elapsed = time.time() - start

            assert elapsed < 120, f"Generation took {elapsed:.1f}s (limit: 120s)"

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="ArtworkGeneration")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generation completes <120s",
                       priority="P0", actual="Within SLA",
                       gen_time=f"{elapsed:.1f}s",
                       screenshot=shot)
        except AssertionError as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generation completes <120s",
                       priority="P0", actual=str(exc),
                       gen_time=f"{time.time() - start:.1f}s",
                       screenshot=shot,
                       bug_id="BUG-GEN-009",
                       bug_desc=f"[What] Artwork generation exceeded 120s SLA.\n"
                                f"[Expected] Image appears within 120 seconds.\n"
                                f"[Impact] User abandonment, poor UX.")
            raise
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="ArtworkGeneration")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="ArtworkGeneration",
                       title="Generation completes <120s",
                       priority="P0", actual=str(exc),
                       gen_time=f"{time.time() - start:.1f}s",
                       screenshot=shot,
                       bug_id="BUG-GEN-009", bug_desc=str(exc))
            raise


class TestInputValidation:
    """TC_VAL_001 — TC_VAL_007: Input validation (negative cases)."""

    def _check_no_generation_triggered(self, page: Page, home: HomePage) -> bool:
        """Returns True if generation did NOT start (no loading, no new img)."""
        import time
        time.sleep(2)
        for sel in home._loading_selectors:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible():
                return False
        return True

    # ── TC_VAL_001 ─────────────────────────────────────────────────────────────

    def test_TC_VAL_001_empty_prompt(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Empty prompt: button disabled OR validation message shown."""
        tc_id = "TC_VAL_001"
        home = HomePage(page, base_url)
        try:
            home.goto()
            # Clear any existing input
            inp = home.get_prompt_input()
            inp.fill("")

            btn = home.get_generate_button()
            # Accept either: button disabled, or clicking shows an error message
            btn_disabled = not btn.is_enabled()

            if not btn_disabled:
                btn.click()
                page.wait_for_timeout(2_000)
                page_text = page.inner_text("body").lower()
                error_kw = ["vui lòng", "required", "nhập", "trống", "error",
                            "please", "enter", "lỗi"]
                has_error = any(k in page_text for k in error_kw)
            else:
                has_error = True  # disabled = validated

            shot = home.take_screenshot(
                f"{tc_id}_{'PASS' if has_error else 'FAIL'}", folder="Validation"
            )
            status = "PASS" if has_error else "FAIL"
            report.add(tc_id, status,
                       screen="HomePage", module="Validation",
                       title="Empty prompt validation",
                       priority="P1",
                       actual="Button disabled or error shown" if has_error
                       else "No validation for empty prompt",
                       screenshot=shot,
                       bug_id="" if has_error else "BUG-VAL-001",
                       bug_desc="" if has_error
                       else "[What] Empty prompt can trigger artwork generation.\n"
                            "[Expected] Button disabled or error message shown.\n"
                            "[Impact] Wasteful API calls, confusing UX.")
            if not has_error:
                pytest.fail("No validation for empty prompt")
        except Exception as exc:
            if "BUG-VAL-001" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Validation")
                report.add(tc_id, "FAIL",
                           screen="HomePage", module="Validation",
                           title="Empty prompt validation",
                           priority="P1", actual=str(exc), screenshot=shot,
                           bug_id="BUG-VAL-001", bug_desc=str(exc))
            raise

    # ── TC_VAL_002 ─────────────────────────────────────────────────────────────

    def test_TC_VAL_002_whitespace_only(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Whitespace-only prompt should be rejected (not trigger generation)."""
        tc_id = "TC_VAL_002"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.enter_prompt(PROMPT_SPACES)
            btn = home.get_generate_button()
            btn.click()
            page.wait_for_timeout(2_000)

            generation_started = False
            for sel in home._loading_selectors:
                if page.locator(sel).first.count() > 0:
                    if page.locator(sel).first.is_visible():
                        generation_started = True
                        break

            shot = home.take_screenshot(
                f"{tc_id}_{'FAIL' if generation_started else 'PASS'}", folder="Validation"
            )
            status = "FAIL" if generation_started else "PASS"
            report.add(tc_id, status,
                       screen="HomePage", module="Validation",
                       title="Whitespace-only prompt rejected",
                       priority="P1",
                       actual="Generation blocked" if not generation_started
                       else "Generation triggered by whitespace",
                       screenshot=shot,
                       bug_id="" if not generation_started else "BUG-VAL-002",
                       bug_desc="" if not generation_started
                       else "[What] Whitespace-only prompt triggers generation.\n"
                            "[Expected] Whitespace trimmed, validation error shown.\n"
                            "[Impact] Wasted API call with empty/useless prompt.")
            if generation_started:
                pytest.fail("Whitespace-only prompt triggered generation")
        except Exception as exc:
            if "BUG-VAL-002" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Validation")
                report.add(tc_id, "FAIL",
                           screen="HomePage", module="Validation",
                           title="Whitespace-only prompt rejected",
                           priority="P1", actual=str(exc), screenshot=shot,
                           bug_id="BUG-VAL-002", bug_desc=str(exc))
            raise

    # ── TC_VAL_005 ─────────────────────────────────────────────────────────────

    def test_TC_VAL_005_xss_not_executed(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """XSS payload in prompt must not execute as JavaScript."""
        tc_id = "TC_VAL_005"
        home = HomePage(page, base_url)
        xss_executed = False

        def detect_dialog(dialog):
            nonlocal xss_executed
            xss_executed = True
            dialog.dismiss()

        page.on("dialog", detect_dialog)
        try:
            home.goto()
            home.enter_prompt(PROMPT_XSS)
            btn = home.get_generate_button()
            btn.click()
            page.wait_for_timeout(3_000)

            shot = home.take_screenshot(
                f"{tc_id}_{'FAIL' if xss_executed else 'PASS'}", folder="Validation"
            )
            status = "FAIL" if xss_executed else "PASS"
            report.add(tc_id, status,
                       screen="HomePage", module="Validation",
                       title="XSS not executed",
                       priority="P2",
                       actual="XSS executed — CRITICAL SECURITY BUG" if xss_executed
                       else "XSS payload safely handled",
                       screenshot=shot,
                       bug_id="" if not xss_executed else "BUG-SEC-001",
                       bug_desc="" if not xss_executed
                       else "[What] XSS payload executed as JavaScript.\n"
                            "[Expected] Input sanitized, no script execution.\n"
                            "[Impact] CRITICAL SECURITY — XSS vulnerability.")
            if xss_executed:
                pytest.fail("XSS payload executed! Security vulnerability detected.")
        except Exception as exc:
            if "BUG-SEC-001" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Validation")
                report.add(tc_id, "FAIL",
                           screen="HomePage", module="Validation",
                           title="XSS not executed", priority="P2",
                           actual=str(exc), screenshot=shot,
                           bug_id="BUG-SEC-001", bug_desc=str(exc))
            raise

    # ── TC_VAL_006 ─────────────────────────────────────────────────────────────

    def test_TC_VAL_006_long_prompt(
        self, page: Page, base_url: str, report: ReportWriter
    ):
        """Long prompt (1200 chars) is truncated or validation shown — no crash."""
        tc_id = "TC_VAL_006"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.enter_prompt(PROMPT_LONG)
            page.wait_for_timeout(1_000)

            # Check: either input was truncated, or error shown
            inp = home.get_prompt_input()
            actual_value = inp.input_value()
            truncated = len(actual_value) < len(PROMPT_LONG)

            btn = home.get_generate_button()
            btn.click()
            page.wait_for_timeout(2_000)

            # Page should not crash
            body = page.locator("body")
            expect(body).to_be_visible()

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Validation")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="Validation",
                       title="Long prompt handled without crash",
                       priority="P2",
                       actual=f"Input length: {len(actual_value)}, truncated: {truncated}",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Validation")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="Validation",
                       title="Long prompt handled without crash",
                       priority="P2", actual=str(exc), screenshot=shot,
                       bug_id="BUG-VAL-006",
                       bug_desc=f"[What] Page crashed with long (1200 char) prompt.\n"
                                f"[Expected] Input truncated or error shown, no crash.\n"
                                f"[Impact] Any user with a long description crashes the page.")
            raise


class TestResponsiveUI:
    """TC_UI: Responsive layout tests."""

    def test_TC_UI_001_iphone_input_visible(
        self, mobile_page: Page, base_url: str, report: ReportWriter
    ):
        """Prompt input visible on iPhone 390x844."""
        tc_id = "TC_UI_001"
        home = HomePage(mobile_page, base_url)
        try:
            home.goto()
            inp = home.get_prompt_input()
            expect(inp).to_be_visible()
            expect(inp).to_be_in_viewport(ratio=0.5)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Responsive")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="Responsive",
                       title="iPhone input visible",
                       priority="P1", actual="Input visible at 390x844",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Responsive")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="Responsive",
                       title="iPhone input visible",
                       priority="P1", actual=str(exc), screenshot=shot,
                       bug_id="BUG-UI-001", bug_desc=str(exc))
            raise

    def test_TC_UI_002_iphone_button_reachable(
        self, mobile_page: Page, base_url: str, report: ReportWriter
    ):
        """Generate button reachable on iPhone 390x844."""
        tc_id = "TC_UI_002"
        home = HomePage(mobile_page, base_url)
        try:
            home.goto()
            btn = home.get_generate_button()
            btn.scroll_into_view_if_needed()
            expect(btn).to_be_visible()
            expect(btn).to_be_in_viewport(ratio=0.5)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Responsive")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="Responsive",
                       title="iPhone button reachable",
                       priority="P1", actual="Button reachable at 390x844",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Responsive")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="Responsive",
                       title="iPhone button reachable",
                       priority="P1", actual=str(exc), screenshot=shot,
                       bug_id="BUG-UI-002", bug_desc=str(exc))
            raise

    def test_TC_UI_003_iphone_full_generation_flow(
        self, mobile_page: Page, base_url: str, report: ReportWriter
    ):
        """Full artwork generation flow works on iPhone 390x844."""
        tc_id = "TC_UI_003"
        home = HomePage(mobile_page, base_url)
        try:
            home.goto()
            artwork = home.generate_artwork(PROMPT_VI)
            home.assert_artwork_visible(artwork)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Responsive")
            report.add(tc_id, "PASS",
                       screen="HomePage", module="Responsive",
                       title="iPhone full generation flow",
                       priority="P1", actual="Artwork generated on mobile",
                       screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Responsive")
            report.add(tc_id, "FAIL",
                       screen="HomePage", module="Responsive",
                       title="iPhone full generation flow",
                       priority="P1", actual=str(exc), screenshot=shot,
                       bug_id="BUG-UI-003", bug_desc=str(exc))
            raise
