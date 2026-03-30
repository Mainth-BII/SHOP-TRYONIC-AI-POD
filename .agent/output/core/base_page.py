from playwright.sync_api import Page, Locator

class BasePage:
    """
    Base framework layer containing common wrapper methods 
    for all Page Object Model instances.
    """
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url)

    def wait_for_load(self, state="networkidle"):
        self.page.wait_for_load_state(state)

    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str):
        self.find(selector).click()

    def fill(self, selector: str, value: str):
        self.find(selector).fill(value)
        
    def is_visible(self, selector: str) -> bool:
        return self.find(selector).is_visible()
