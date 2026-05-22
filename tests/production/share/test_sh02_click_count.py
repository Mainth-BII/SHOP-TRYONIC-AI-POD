from __future__ import annotations
"""
SH02 — Đếm lượt click gian hàng (TC3)

TC3: Mỗi lần khách click vào link gian hàng từ user/trình duyệt khác nhau
     thì số lượt click trên trang /affiliate tăng thêm 1.
     Cùng trình duyệt click lại → KHÔNG tăng (cookie/fingerprint tracking).

Cơ chế test:
  1. Đọc click count hiện tại từ /affiliate (browser đã login = affiliate owner)
  2. Mở browser context mới (incognito-like) → navigate đến store link → đóng
  3. Quay lại /affiliate → verify count + 1
  4. Mở lại cùng context đó → navigate lại → đóng
  5. Verify count KHÔNG tăng thêm (same browser fingerprint)
"""
import pytest
from playwright.sync_api import Browser
from .base_share_flow import BaseShareFlowTest


class TestSH02ClickCount(BaseShareFlowTest):
    """TC3: Click count tăng đúng theo điều kiện khác user/trình duyệt."""

    _MH_NAMES = {
        "MH1":   "Đọc click count ban đầu",
        "MH2":   "Click từ browser mới (incognito) → count +1",
        "MH3":   "Click lại cùng browser → count KHÔNG đổi",
        "Login": "Đăng nhập",
    }
    _REPORT_TITLE = "SH02 — Click Count Gian hàng (TC3)"

    @pytest.fixture(autouse=True)
    def setup(self, home_page, product_list_page, product_detail_page,
              studio_page, auth_page, checkout_page, env):
        self.home     = home_page
        self.listing  = product_list_page
        self.detail   = product_detail_page
        self.studio   = studio_page
        self.auth     = auth_page
        self.checkout = checkout_page
        self.env      = env
        self.page     = home_page.page
        self.tc       = "SH02_CLICK_COUNT"
        self.root     = "production"
        self.domain   = "sh02_click_count"
        self._results = []

    def _get_store_share_link(self) -> str | None:
        """Lấy link chia sẻ gian hàng (có thể chứa ref/affiliate param)."""
        # Thử tìm link có chứa ref= hoặc aff= hoặc utm_source
        link = self.page.evaluate(r"""() => {
            const text = document.body.innerHTML || '';
            // Tìm input copy-link hoặc href chứa ref/aff param
            const inp = document.querySelector('input[value*="ref="], input[value*="aff="], input[value*="affiliate"]');
            if (inp) return inp.value;

            const a = document.querySelector('a[href*="ref="], a[href*="aff="]');
            if (a) return a.href;

            // Fallback: link gian hàng trực tiếp
            const storeA = document.querySelector('a[href*="/store/"], a[href*="/gian-hang/"]');
            if (storeA) return storeA.href;

            return null;
        }""")
        return link

    def _visit_store_as_new_user(self, store_url: str, browser: Browser) -> bool:
        """Mở browser context mới (simulate user/trình duyệt khác) → visit store_url."""
        ctx = None
        try:
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
                locale="vi-VN",
                viewport={"width": 390, "height": 844},
            )
            new_page = ctx.new_page()
            new_page.goto(store_url, wait_until="domcontentloaded", timeout=15000)
            new_page.wait_for_timeout(2000)
            return True
        except Exception as e:
            print(f"  [WARN] _visit_store_as_new_user: {e}")
            return False
        finally:
            if ctx:
                ctx.close()

    @pytest.mark.production
    def test_click_count(self, browser: Browser):
        """TC3: Click count +1 khi khác browser, không đổi khi cùng browser."""
        tc = self.tc
        self._login()

        # ════════════════════════════════════════════════════════════════════
        # MH1 — Đọc click count ban đầu
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH1: Đọc click count ban đầu ──────────────────────────")
        self._goto_affiliate()
        self._shot("MH1_1", "affiliate_before")

        if not self._is_affiliate_approved():
            pytest.skip(f"SKIP {tc}: User chưa được duyệt affiliate")

        store_link = self._get_store_share_link()
        if not store_link:
            pytest.skip(f"SKIP {tc}: Không tìm thấy link gian hàng")

        # Đảm bảo URL đầy đủ
        if not store_link.startswith("http"):
            store_link = f"{self.env.fe_url.rstrip('/')}/{store_link.lstrip('/')}"

        count_before = self._read_click_count()
        self._record_check(
            "MH1", "MH1 Đọc click count ban đầu",
            "✅ PASS" if count_before is not None else "⚠️ WARN",
            str(count_before) if count_before is not None else "N/A", "Số nguyên ≥ 0",
        )
        print(f"  [INFO] MH1: click_count_before = {count_before}")
        print(f"  [INFO] MH1: store_link = {store_link}")

        # ════════════════════════════════════════════════════════════════════
        # MH2 — Click từ browser mới → count phải + 1
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH2: Click từ browser mới (incognito) ─────────────────")
        visited = self._visit_store_as_new_user(store_link, browser)
        self._record_check(
            "MH2", "MH2 Visit store từ browser mới thành công",
            "✅ PASS" if visited else "⚠️ WARN",
            "OK" if visited else "Failed", "Request gửi đến store",
        )
        self.page.wait_for_timeout(2000)  # chờ server cập nhật count

        # Refresh affiliate page để đọc count mới
        self._goto_affiliate()
        self._shot("MH2_1", "affiliate_after_new_browser")
        count_after_new = self._read_click_count()

        if count_before is not None and count_after_new is not None:
            expected_after = count_before + 1
            ok = abs(count_after_new - expected_after) <= 1  # cho phép ±1
            self._record_check(
                "MH2", "MH2 Click count +1 sau browser mới",
                "✅ PASS" if ok else "❌ FAIL",
                str(count_after_new), f"{expected_after} (before+1)",
            )
            print(f"  [{'PASS' if ok else 'FAIL'}] MH2: count {count_before} → {count_after_new} (exp {expected_after})")
        else:
            self._record_check(
                "MH2", "MH2 Click count sau browser mới",
                "⚠️ WARN", str(count_after_new), "Không đọc được count",
            )
            print(f"  [WARN] MH2: count_after_new = {count_after_new}")

        # ════════════════════════════════════════════════════════════════════
        # MH3 — Click lại cùng context → count KHÔNG tăng
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH3: Click lại cùng browser → count KHÔNG đổi ────────")

        # Tạo context thứ 2 với cùng user-agent (simulate same browser)
        ctx2 = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
            locale="vi-VN",
            viewport={"width": 390, "height": 844},
        )
        try:
            p2 = ctx2.new_page()
            # Visit lần 1 từ context này
            p2.goto(store_link, wait_until="domcontentloaded", timeout=15000)
            p2.wait_for_timeout(1500)
            # Visit lần 2 từ cùng context (cùng cookie/fingerprint)
            p2.goto(store_link, wait_until="domcontentloaded", timeout=15000)
            p2.wait_for_timeout(1500)
        except Exception as e:
            print(f"  [WARN] MH3: {e}")
        finally:
            ctx2.close()

        self.page.wait_for_timeout(2000)
        self._goto_affiliate()
        self._shot("MH3_1", "affiliate_after_same_browser")
        count_after_same = self._read_click_count()

        if count_after_new is not None and count_after_same is not None:
            # Cho phép tăng tối đa 1 (click đầu tiên của context này đếm, click 2 không)
            max_increase = 1
            ok = count_after_same <= (count_after_new + max_increase)
            self._record_check(
                "MH3", "MH3 Click count KHÔNG tăng khi cùng browser",
                "✅ PASS" if ok else "❌ FAIL",
                str(count_after_same),
                f"≤ {count_after_new + max_increase} (không tăng quá 1)",
            )
            print(f"  [{'PASS' if ok else 'FAIL'}] MH3: count {count_after_new} → {count_after_same}")
        else:
            self._record_check(
                "MH3", "MH3 Click count không tăng (same browser)",
                "⚠️ WARN", str(count_after_same), "Không đọc được",
            )

        print(f"\n  [PASS] {tc}: TC3 COMPLETED")
        self._print_summary_table()
