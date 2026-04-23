"""Base Page Object — tất cả page objects kế thừa từ class này."""

import os
from datetime import datetime
from playwright.sync_api import Page

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url.rstrip("/") if base_url else ""

    # ── Navigation ──────────────────────────────────────────────────────────

    def goto(self, path: str = "", *, wait: str = "domcontentloaded", timeout: int = 30_000) -> None:
        url = f"{self.base_url}{path}" if path else self.base_url
        self.page.goto(url, wait_until=wait, timeout=timeout)
        try:
            self.page.wait_for_load_state("load", timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(1500)

    def navigate(self, path: str = "") -> None:
        """Alias cho goto() — giữ backward compat."""
        self.goto(path)

    def wait_for_url(self, pattern: str, timeout: int = 10_000) -> None:
        self.page.wait_for_url(pattern, timeout=timeout)

    # ── Screenshots ─────────────────────────────────────────────────────────

    def shot(self, tc_id: str, step: str, label: str, domain: str = "smoke", sub_dir: str = "", root: str = "daily") -> None:
        """Chụp screenshot vào screenshots/[root]/[domain]/[sub_dir]/[tc_id]/."""
        parts = [_BASE_DIR, "screenshots", root, domain]
        if sub_dir:
            parts.append(sub_dir)
        parts.append(tc_id)
        shot_dir = os.path.join(*parts)
        os.makedirs(shot_dir, exist_ok=True)
        ts = datetime.now().strftime("%H%M%S")
        fpath = os.path.join(shot_dir, f"S{step}_{label}_{ts}.png")
        try:
            self.page.screenshot(path=fpath, full_page=True)
            print(f"  [SHOT] {tc_id} S{step}: {label}")
        except Exception as e:
            print(f"  [SHOT FAIL] {tc_id} S{step}: {e}")

    # ── Dialogs ─────────────────────────────────────────────────────────────

    def accept_terms(self, tc_id: str = "") -> None:
        """Đóng Terms dialog nếu đang hiển thị (z-[9999] overlay)."""
        try:
            terms_btn = self.page.locator(
                "button:has-text('Tôi đồng ý với Điều khoản sử dụng'), "
                "button:has-text('Toi dong y'), "
                "button:has-text('Đồng ý')"
            ).first
            if terms_btn.is_visible(timeout=4000):
                terms_btn.click()
                self.page.wait_for_timeout(1500)
                if tc_id:
                    print(f"  [INFO] {tc_id}: Đã đồng ý Điều khoản sử dụng")
        except Exception:
            pass

    # ── Scroll ──────────────────────────────────────────────────────────────

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(500)

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")
        self.page.wait_for_timeout(300)
