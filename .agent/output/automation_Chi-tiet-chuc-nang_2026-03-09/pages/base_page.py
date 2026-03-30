from playwright.sync_api import Page, expect
import os

class BasePage:
    """Base framework layer — all Page Objects inherit from this."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")
        self.page.wait_for_load_state("networkidle")

    def take_screenshot(self, name: str, folder: str = "") -> str:
        base_dir = "screenshots"
        if folder:
            base_dir = os.path.join(base_dir, folder)
        os.makedirs(base_dir, exist_ok=True)
        path = os.path.join(base_dir, f"{name}.png")
        self.page.screenshot(path=path)
        return path
