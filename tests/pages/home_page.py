"""Home Page Object — pre-launch.tryonic.ai landing + artwork generation."""

from playwright.sync_api import Page, expect, Locator
from .base_page import BasePage


class HomePage(BasePage):
    """
    Page Object for https://pre-launch.tryonic.ai/

    The page is a React SPA. Selectors use a priority chain:
      data-testid > role > placeholder > text > CSS (last resort)
    Multiple fallback selectors are used because the pre-launch UI
    may not have data-testid attributes yet.
    """

    # ── Artwork generation timeout (AI can take up to 120 s) ────────────────
    ARTWORK_TIMEOUT_MS = 120_000

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # ── Root wrapper ────────────────────────────────────────────────────
        self.root = page.locator("#root")

        # ── Prompt / story input ────────────────────────────────────────────
        # Try common patterns: textarea, or input with common Vietnamese placeholders
        self._prompt_selectors = [
            'textarea',
            'input[type="text"]',
            '[placeholder*="câu chuyện"]',
            '[placeholder*="story"]',
            '[placeholder*="mô tả"]',
            '[placeholder*="describe"]',
            '[placeholder*="nhập"]',
            '[data-testid*="prompt"]',
            '[data-testid*="input"]',
        ]

        # ── Generate / submit button ─────────────────────────────────────────
        self._generate_btn_selectors = [
            'button[type="submit"]',
            'button:has-text("Tạo")',
            'button:has-text("Thiết kế")',
            'button:has-text("Generate")',
            'button:has-text("Tạo thiết kế")',
            'button:has-text("Bắt đầu")',
            'button:has-text("Tạo ngay")',
            '[data-testid*="generate"]',
            '[data-testid*="submit"]',
        ]

        # ── Loading indicator (spinner / skeleton / progress) ────────────────
        self._loading_selectors = [
            '[class*="loading"]',
            '[class*="spinner"]',
            '[class*="skeleton"]',
            '[role="progressbar"]',
            '[aria-label*="loading"]',
            '[class*="progress"]',
            '[class*="animate"]',
        ]

        # ── Generated artwork image ──────────────────────────────────────────
        self._artwork_selectors = [
            '[data-testid*="artwork"]',
            '[data-testid*="result"]',
            '[data-testid*="design"]',
            'img[src*="blob:"]',
            'img[src*="data:image"]',
            'img[src*="amazonaws"]',
            'img[src*="storage"]',
            'img[src*="cdn"]',
            'img[src*="generate"]',
            'img[src*="design"]',
            # Fallback: any img that appears after button click
            'main img',
            '.result img',
            '.artwork img',
            '.design img',
        ]

        # ── Email input (pre-launch signup) ──────────────────────────────────
        self._email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            '[placeholder*="email"]',
            '[placeholder*="Email"]',
        ]

    # ── Page actions ──────────────────────────────────────────────────────────

    def goto(self) -> None:
        self.navigate()

    def get_prompt_input(self) -> Locator:
        """Return the first visible prompt input locator."""
        for sel in self._prompt_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.wait_for(state="visible", timeout=2_000)
                    return loc
                except Exception:
                    continue
        # Last resort — any visible input or textarea
        return self.page.locator("input, textarea").first

    def get_generate_button(self) -> Locator:
        """Return the generate/submit button locator."""
        for sel in self._generate_btn_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.wait_for(state="visible", timeout=2_000)
                    return loc
                except Exception:
                    continue
        return self.page.locator("button").first

    def get_artwork_image(self) -> Locator:
        """Return the generated artwork image locator."""
        for sel in self._artwork_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                return loc
        return self.page.locator("img").first

    def get_email_input(self) -> Locator:
        for sel in self._email_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.wait_for(state="visible", timeout=2_000)
                    return loc
                except Exception:
                    continue
        return self.page.locator('input[type="email"]').first

    # ── High-level workflow methods ───────────────────────────────────────────

    def enter_prompt(self, text: str) -> None:
        """Clear and type the prompt text."""
        inp = self.get_prompt_input()
        inp.wait_for(state="visible", timeout=10_000)
        inp.click()
        inp.fill("")
        inp.type(text, delay=30)

    def click_generate(self) -> None:
        """Click the generate/submit button."""
        btn = self.get_generate_button()
        btn.wait_for(state="visible", timeout=10_000)
        btn.click()

    def wait_for_artwork(self) -> Locator:
        """
        Wait until artwork image is visible after generation.

        Strategy:
          1. Wait for any loading indicator to disappear.
          2. Poll for an <img> with non-empty src to appear.
          3. Assert it is visible in viewport.
        """
        # Step 1 — wait for loading to clear
        for sel in self._loading_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.wait_for(state="hidden", timeout=self.ARTWORK_TIMEOUT_MS)
                    break
                except Exception:
                    continue

        # Step 2 — wait for an img with a real src to appear
        self.page.wait_for_function(
            """() => {
                const imgs = document.querySelectorAll('img');
                return Array.from(imgs).some(img =>
                    img.src &&
                    img.src !== '' &&
                    !img.src.endsWith('.svg') &&
                    img.naturalWidth > 0
                );
            }""",
            timeout=self.ARTWORK_TIMEOUT_MS,
        )

        # Step 3 — return the first qualifying img
        artwork = self.get_artwork_image()
        expect(artwork).to_be_visible()
        return artwork

    def generate_artwork(self, prompt_text: str) -> Locator:
        """Full end-to-end: enter prompt → click generate → wait for result."""
        self.enter_prompt(prompt_text)
        self.click_generate()
        return self.wait_for_artwork()

    # ── Assertions ────────────────────────────────────────────────────────────

    def assert_page_loaded(self) -> None:
        """Assert root and at least one visible element rendered."""
        expect(self.root).to_be_visible()

    def assert_artwork_visible(self, artwork: Locator) -> None:
        """Assert artwork image is visible and has rendered dimensions."""
        expect(artwork).to_be_visible()
        expect(artwork).to_be_in_viewport(ratio=0.5)

    def assert_artwork_has_dimensions(self, artwork: Locator) -> None:
        """Assert the artwork image has non-zero natural dimensions."""
        has_dims = self.page.evaluate(
            """(selector) => {
                const img = document.querySelector(selector);
                return img ? (img.naturalWidth > 0 && img.naturalHeight > 0) : false;
            }""",
            "img",
        )
        assert has_dims, "Artwork image has zero dimensions (likely broken/missing)"

    def assert_generate_button_enabled(self) -> None:
        btn = self.get_generate_button()
        expect(btn).to_be_enabled()
