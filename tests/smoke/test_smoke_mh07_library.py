"""
Smoke — MH07: Studio — Thư Viện & Upload
TC_DAILY_018 · TC_DAILY_019

Chay: pytest tests/smoke/test_smoke_mh07_library.py -v
"""
import sys
import pytest
from playwright.sync_api import Page

from smoke.base_smoke import BaseSmokeTest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class TestSmokeMH07Library(BaseSmokeTest):
    """MH07 — Studio Library: Thu Vien panel mo, upload input ton tai."""

    _MH_DIR = "MH07_library"
    _TC_IDS = ["TC_DAILY_018", "TC_DAILY_019"]

    # ── TC_DAILY_018 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_018_library_panel_opens(self, page: Page, base_url: str):
        """TC_DAILY_018 — Studio: Nut 'Thu Vien' mo panel, tab AI hien thi."""
        page.goto(
            f"{base_url}/studio?category=t-shirts",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(3000)

        library_content = page.locator(
            "button:has-text('ẢNH CỦA BẠN'), button:has-text('MẪU THIẾT KẾ'), "
            "button:has-text('ANH CUA BAN'), [class*='library'], "
            "div:has-text('Ảnh của bạn'), div:has-text('Thêm ảnh')"
        ).first

        if library_content.is_visible(timeout=5000):
            self.shot(page, "TC_DAILY_018", "1", "library_content_visible")
            print("  [PASS] Noi dung Thu Vien hien thi san (panel dang mo)")
        else:
            library_btn = page.locator("button").filter(has_text="Thư Viện").first
            library_btn.click(force=True)
            page.wait_for_timeout(2000)
            self.shot(page, "TC_DAILY_018", "1", "library_after_click")

            assert library_content.is_visible(timeout=8000), \
                "TC_DAILY_018 FAIL: Khong tim thay noi dung Thu Vien sau khi click"
            self.shot(page, "TC_DAILY_018", "2", "library_content_visible")
            print("  [PASS] Thu Vien panel mo thanh cong")

    # ── TC_DAILY_019 ──────────────────────────────────────────────────────────

    @pytest.mark.daily
    @pytest.mark.smoke
    def test_TC_DAILY_019_manual_upload_available(self, page: Page, base_url: str):
        """TC_DAILY_019 — Studio: file input ton tai, co the upload anh thu cong."""
        page.goto(
            f"{base_url}/studio?category=t-shirts",
            wait_until="domcontentloaded", timeout=30000
        )
        try:
            page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass
        page.wait_for_timeout(3000)

        library_btn = page.locator("button").filter(has_text="Thư Viện").first
        if library_btn.is_visible(timeout=3000):
            library_btn.click()
            page.wait_for_timeout(2000)

        self.shot(page, "TC_DAILY_019", "1", "library_for_upload")

        file_input_count = page.locator("input[type='file']").count()
        assert file_input_count > 0, \
            "TC_DAILY_019 FAIL: Khong tim thay input[type='file'] — tinh nang upload khong kha dung"

        upload_trigger = page.locator(
            "button:has-text('Tải lên'), button:has-text('Tai len'), "
            "button:has-text('Upload'), label[for*='file'], "
            ":text('Tải ảnh lên'), :text('Tai anh len')"
        ).first
        upload_visible = upload_trigger.is_visible(timeout=5000)
        self.shot(page, "TC_DAILY_019", "2", "upload_trigger_state")

        if upload_visible:
            print(f"  [PASS] Upload trigger hien thi + file input ton tai ({file_input_count} input)")
        else:
            print(f"  [PASS] File input ton tai trong DOM ({file_input_count} input) — upload kha dung")
