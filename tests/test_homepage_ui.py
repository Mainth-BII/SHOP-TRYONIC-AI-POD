"""
TC_HOME: Homepage UI tests — pre-launch.tryonic.ai
Covers: TC_HOME_001 to TC_HOME_006
"""

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from utils.report_writer import ReportWriter


class TestHomepageUI:

    # ── TC_HOME_001 ──────────────────────────────────────────────────────────

    def test_TC_HOME_001_page_loads(self, page: Page, base_url: str, report: ReportWriter):
        """Homepage loads successfully — HTTP 200, React root mounted."""
        tc_id = "TC_HOME_001"
        home = HomePage(page, base_url)
        try:
            response = page.goto(base_url)
            assert response is not None, "No response received"
            assert response.status == 200, f"Expected HTTP 200, got {response.status}"
            page.wait_for_load_state("networkidle")
            home.assert_page_loaded()

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Homepage")
            report.add(
                tc_id, "PASS",
                screen="Homepage", module="Home", title="Homepage loads",
                priority="P0", actual="HTTP 200, React root visible",
                screenshot=shot,
            )
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
            report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                       title="Homepage loads", priority="P0",
                       actual=str(exc), screenshot=shot,
                       bug_id="BUG-HOME-001", bug_desc=str(exc))
            raise

    # ── TC_HOME_002 ──────────────────────────────────────────────────────────

    def test_TC_HOME_002_page_title(self, page: Page, base_url: str, report: ReportWriter):
        """Page title contains 'Tryonic'."""
        tc_id = "TC_HOME_002"
        home = HomePage(page, base_url)
        try:
            home.goto()
            title = page.title()
            assert "Tryonic" in title or "tryonic" in title.lower(), \
                f"Title does not contain 'Tryonic': '{title}'"

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Homepage")
            report.add(tc_id, "PASS", screen="Homepage", module="Home",
                       title="Page title correct", priority="P1",
                       actual=f"Title: {title}", screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
            report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                       title="Page title correct", priority="P1",
                       actual=str(exc), screenshot=shot,
                       bug_id="BUG-HOME-002", bug_desc=str(exc))
            raise

    # ── TC_HOME_003 ──────────────────────────────────────────────────────────

    def test_TC_HOME_003_prompt_input_visible(self, page: Page, base_url: str, report: ReportWriter):
        """Prompt input field is visible and interactive."""
        tc_id = "TC_HOME_003"
        home = HomePage(page, base_url)
        try:
            home.goto()
            inp = home.get_prompt_input()
            expect(inp).to_be_visible()
            expect(inp).to_be_in_viewport(ratio=0.5)
            expect(inp).to_be_enabled()

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Homepage")
            report.add(tc_id, "PASS", screen="Homepage", module="Home",
                       title="Prompt input visible", priority="P0",
                       actual="Input visible, in viewport, enabled", screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
            report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                       title="Prompt input visible", priority="P0",
                       actual=str(exc), screenshot=shot,
                       bug_id="BUG-HOME-003", bug_desc=str(exc))
            raise

    # ── TC_HOME_004 ──────────────────────────────────────────────────────────

    def test_TC_HOME_004_generate_button_visible(self, page: Page, base_url: str, report: ReportWriter):
        """Generate button is visible and enabled."""
        tc_id = "TC_HOME_004"
        home = HomePage(page, base_url)
        try:
            home.goto()
            home.assert_generate_button_enabled()
            btn = home.get_generate_button()
            expect(btn).to_be_in_viewport(ratio=0.5)

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Homepage")
            report.add(tc_id, "PASS", screen="Homepage", module="Home",
                       title="Generate button visible", priority="P0",
                       actual="Button visible, in viewport, enabled", screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
            report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                       title="Generate button visible", priority="P0",
                       actual=str(exc), screenshot=shot,
                       bug_id="BUG-HOME-004", bug_desc=str(exc))
            raise

    # ── TC_HOME_005 ──────────────────────────────────────────────────────────

    def test_TC_HOME_005_no_console_errors(self, page: Page, base_url: str, report: ReportWriter):
        """Page loads without critical JavaScript console errors."""
        tc_id = "TC_HOME_005"
        errors: list[str] = []

        def capture_error(msg):
            if msg.type == "error":
                errors.append(msg.text)

        page.on("console", capture_error)
        home = HomePage(page, base_url)
        try:
            home.goto()
            page.wait_for_timeout(2_000)

            critical = [e for e in errors if "TypeError" in e or "ReferenceError" in e]
            shot = home.take_screenshot(f"{tc_id}_{'FAIL' if critical else 'PASS'}", folder="Homepage")

            if critical:
                report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                           title="No console errors", priority="P1",
                           actual=f"JS errors: {critical}", screenshot=shot,
                           bug_id="BUG-HOME-005", bug_desc=f"JS errors: {critical}")
                pytest.fail(f"Console errors: {critical}")
            else:
                report.add(tc_id, "PASS", screen="Homepage", module="Home",
                           title="No console errors", priority="P1",
                           actual=f"No critical errors. Warnings: {len(errors)}", screenshot=shot)
        except Exception as exc:
            if "BUG-HOME-005" not in str(exc):
                shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
                report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                           title="No console errors", priority="P1",
                           actual=str(exc), screenshot=shot,
                           bug_id="BUG-HOME-005", bug_desc=str(exc))
            raise

    # ── TC_HOME_006 ──────────────────────────────────────────────────────────

    def test_TC_HOME_006_responsive_mobile(self, mobile_page: Page, base_url: str, report: ReportWriter):
        """UI renders on iPhone 390x844 without horizontal overflow."""
        tc_id = "TC_HOME_006"
        home = HomePage(mobile_page, base_url)
        try:
            home.goto()
            # Check no horizontal scroll (scrollWidth <= clientWidth)
            overflow = mobile_page.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not overflow, "Horizontal overflow detected on mobile"

            shot = home.take_screenshot(f"{tc_id}_PASS", folder="Homepage")
            report.add(tc_id, "PASS", screen="Homepage", module="Home",
                       title="Mobile layout no overflow", priority="P1",
                       actual="No horizontal overflow at 390x844", screenshot=shot)
        except Exception as exc:
            shot = home.take_screenshot(f"{tc_id}_FAIL", folder="Homepage")
            report.add(tc_id, "FAIL", screen="Homepage", module="Home",
                       title="Mobile layout no overflow", priority="P1",
                       actual=str(exc), screenshot=shot,
                       bug_id="BUG-HOME-006", bug_desc=str(exc))
            raise
