"""Base Page Object — all pages inherit from this."""

import os
from datetime import datetime
from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # ── Navigation ──────────────────────────────────────────────────────────

    def navigate(self, path: str = "") -> None:
        self.page.goto(f"{self.base_url}{path}")
        self.page.wait_for_load_state("networkidle")

    # ── Screenshots ─────────────────────────────────────────────────────────

    def take_screenshot(self, name: str, folder: str = "") -> str:
        """Capture screenshot and return relative file path."""
        base_dir = os.path.join("screenshots", folder) if folder else "screenshots"
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = os.path.join(base_dir, filename)
        self.page.screenshot(path=path, full_page=True)
        return path

    # ── Helpers ──────────────────────────────────────────────────────────────

    def wait_for_url(self, pattern: str, timeout: int = 10_000) -> None:
        self.page.wait_for_url(pattern, timeout=timeout)

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(300)
