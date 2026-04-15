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

        # ── Drag handle (slide-to-unlock on landing page) ───────────────────
        self._drag_handle = page.locator('.cursor-grab').first
        self._drag_container = page.locator('.cursor-pointer.overflow-hidden.rounded-full').first

        # ── Prompt textarea (visible after drag) ────────────────────────────
        self._prompt_selectors = [
            'textarea[placeholder*="chuy"]',   # "Câu chuyện của mình......"
            'textarea',
            'input[type="text"]',
            '[contenteditable="true"]',
            '[role="textbox"]',
            '[placeholder*="câu chuyện"]',
            '[placeholder*="chuyện"]',
            '[placeholder*="story"]',
            '[placeholder*="mô tả"]',
            '[placeholder*="nhập"]',
            '[placeholder*="Nhập"]',
        ]

        # ── Generate button (visible after drag) ─────────────────────────────
        self._generate_btn_selectors = [
            'button:has-text("Tạo chiếc áo")',
            'button:has-text("Tạo chiếc")',
            'button:has-text("Tạo")',
            'button[type="submit"]',
            'button:has-text("Generate")',
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

    def open_story_box(self) -> None:
        """Drag the slide-to-unlock handle to reveal the story input form."""
        self._drag_handle.wait_for(state="visible", timeout=10_000)
        handle_box = self._drag_handle.bounding_box()
        container_box = self._drag_container.bounding_box()
        if not handle_box or not container_box:
            raise RuntimeError("Could not find drag handle or container bounding box")

        start_x = handle_box["x"] + handle_box["width"] / 2
        start_y = handle_box["y"] + handle_box["height"] / 2
        end_x   = container_box["x"] + container_box["width"] - 30

        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        steps = 20
        for i in range(1, steps + 1):
            self.page.mouse.move(
                start_x + (end_x - start_x) * i / steps,
                start_y,
            )
            self.page.wait_for_timeout(30)
        self.page.mouse.up()
        # Wait for story form to appear
        self.page.wait_for_function(
            "() => !!document.querySelector('textarea')",
            timeout=8_000,
        )

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

    # Known static asset paths that must NOT be counted as generated artwork
    _STATIC_ASSET_PATTERNS = ("/assets/POD-", "/assets/gift-box-", "/favicon")

    def handle_email_gate(self, email: str = "mainth@bccii.co.jp") -> bool:
        """
        If the email gate modal is visible, fill in the email and submit.
        Returns True if gate was handled, False if gate not present.
        """
        email_input = self.page.locator('input[type="email"], input[placeholder*="email"]').first
        try:
            email_input.wait_for(state="visible", timeout=5_000)
        except Exception:
            return False  # No gate visible

        email_input.fill(email)
        submit_btn = self.page.locator('button:has-text("Gui"), button:has-text("Gửi"), button[type="submit"]').first
        submit_btn.wait_for(state="visible", timeout=5_000)
        submit_btn.click()
        # Wait for gate to disappear
        try:
            email_input.wait_for(state="hidden", timeout=10_000)
        except Exception:
            pass
        return True

    def wait_for_artwork(self) -> Locator:
        """
        Wait until the AI-generated artwork image is visible.

        Strategy:
          1. Handle email gate if present.
          2. Wait for loading indicator to disappear.
          3. Poll for a NEW <img> whose src is NOT a known static asset.
          4. Return that locator.
        """
        # Step 1 — handle email gate
        self.handle_email_gate()

        # Step 2 — wait for loading to clear
        for sel in self._loading_selectors:
            loc = self.page.locator(sel).first
            if loc.count() > 0:
                try:
                    loc.wait_for(state="hidden", timeout=self.ARTWORK_TIMEOUT_MS)
                    break
                except Exception:
                    continue

        # Step 3 — wait for a non-static img to appear (patterns embedded in JS)
        self.page.wait_for_function(
            """() => {
                const STATIC = ["/assets/POD-", "/assets/gift-box-", "/favicon"];
                const imgs = document.querySelectorAll('img');
                return Array.from(imgs).some(img => {
                    if (!img.src || img.src.endsWith('.svg')) return false;
                    if (img.naturalWidth === 0) return false;
                    return !STATIC.some(p => img.src.includes(p));
                });
            }""",
            timeout=self.ARTWORK_TIMEOUT_MS,
        )

        # Step 4 — return first qualifying generated image
        generated = self.page.locator("img").filter(
            has_not=self.page.locator('img[src*="/assets/POD-"]')
        ).first
        expect(generated).to_be_visible()
        return generated

    def generate_artwork(self, prompt_text: str) -> Locator:
        """Full end-to-end: enter prompt → click generate → email gate → wait for artwork."""
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
        has_dims = artwork.evaluate(
            "img => img.naturalWidth > 0 && img.naturalHeight > 0"
        )
        assert has_dims, "Artwork image has zero dimensions (likely broken/missing)"

    def assert_generate_button_enabled(self) -> None:
        btn = self.get_generate_button()
        expect(btn).to_be_enabled()

    def assert_artwork_relevance(self, artwork: Locator, prompt_text: str) -> tuple:
        """
        Kiểm tra ảnh artwork:
          1. Không phải static placeholder (kiểm tra URL)
          2. Không phải hình hộp quà (Claude Vision)
          3. Nội dung liên quan đến prompt (Claude Vision)

        Raise AssertionError nếu fail. Trả (True, reason) nếu pass.
        """
        from utils.image_verifier import check_artwork  # noqa: PLC0415

        # ── Kiểm tra URL tĩnh ────────────────────────────────────────────────
        src = artwork.get_attribute("src") or ""
        for pat in self._STATIC_ASSET_PATTERNS:
            if pat in src:
                raise AssertionError(
                    f"Artwork la static placeholder (URL: {src[:80]})"
                )

        # ── Lấy ảnh và gửi cho Claude Vision ────────────────────────────────
        try:
            img_bytes = artwork.screenshot()
        except Exception as e:
            raise AssertionError(f"Khong the chup anh artwork: {e}") from e

        ok, reason = check_artwork(img_bytes, prompt_text)
        if not ok:
            raise AssertionError(reason)

        return True, reason
