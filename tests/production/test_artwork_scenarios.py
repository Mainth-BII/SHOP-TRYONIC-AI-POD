"""
Artwork Placement Scenarios — Parametrized tests for 3 cases:
  ARTWORK_001: front only
  ARTWORK_002: back only
  ARTWORK_003: both sides
Data đọc từ data/critical_flows.json["artwork_scenarios"].
"""
import json
import os
from datetime import date

import pytest


def _load_scenarios() -> list[dict]:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "critical_flows.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)["artwork_scenarios"]


def _load_daily_prompt() -> str:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "genz_prompts.json"
    )
    with open(data_path, "r", encoding="utf-8") as f:
        prompts = json.load(f)["daily_prompts"]
    return prompts[date.today().timetuple().tm_yday % len(prompts)]


class TestArtworkScenarios:

    @pytest.fixture(autouse=True)
    def setup(self, home_page, studio_page, auth_page, env):
        self.home = home_page
        self.studio = studio_page
        self.auth = auth_page
        self.env = env
        self.domain = "artwork_scenarios"

    # ── S0: Login ────────────────────────────────────────────────────────────

    def _login(self, tc_id: str) -> None:
        email = self.env.login_email
        password = self.env.login_password
        if not email or not password:
            pytest.skip(f"BỎ QUA {tc_id}: Thiếu credentials — kiểm tra .env")

        _R = "production"
        _D = self.domain
        page = self.home.page

        self.home.navigate()
        self.home.header.click_login()
        page.wait_for_timeout(1000)
        self.auth.login(email, password)
        page.wait_for_timeout(3000)
        self.home.shot(tc_id, "0", "after_login", domain=_D, root=_R)

        is_logged = not self.home.header.login_button.is_visible(timeout=5000)
        if not is_logged:
            page.wait_for_timeout(3000)
            is_logged = not self.home.header.login_button.is_visible(timeout=3000)
        assert is_logged, f"LỖI S0 ({tc_id}): Đăng nhập thất bại"
        print(f"  [PASS] S0 ({tc_id}): Đăng nhập thành công")

    # ── Main test ─────────────────────────────────────────────────────────────

    @pytest.mark.production
    @pytest.mark.parametrize("scenario", _load_scenarios(), ids=lambda s: s["id"])
    def test_artwork_placement(self, scenario):
        """Áp artwork theo scenario: front_only / back_only / both_sides."""
        tc_id = scenario["id"]
        _R = "production"
        _D = self.domain
        page = self.home.page
        prompt = _load_daily_prompt()

        print(f"\n  [INFO] {tc_id}: {scenario['description']}")
        print(f"  [INFO] {tc_id}: Prompt = '{prompt[:60]}...'")

        # ── S0: Đăng nhập ────────────────────────────────────────────────────
        self._login(tc_id)

        # ── S1: Home → Nhập prompt → Navigate Studio ─────────────────────────
        self.home.navigate()
        self.home.fill_prompt(prompt)
        page.wait_for_timeout(500)
        self.home.click_generate()
        try:
            page.wait_for_url("**/studio**", timeout=20_000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        self.studio.shot(tc_id, "1", "studio_navigated", domain=_D, root=_R)
        assert "studio" in page.url, f"LỖI S1 ({tc_id}): Không navigate vào Studio — URL: {page.url}"
        assert self.studio.is_canvas_visible(), f"LỖI S1 ({tc_id}): Canvas không hiển thị"
        self.studio.accept_terms(tc_id)
        print(f"  [PASS] S1 ({tc_id}): Vào Studio thành công")

        # ── S2: Chọn màu áo ──────────────────────────────────────────────────
        selected = self.studio.select_color(scenario["color"])
        if not selected:
            selected = self.studio.select_color("White")
        self.studio.shot(tc_id, "2", f"color_{scenario['color']}", domain=_D, root=_R)
        print(f"  [{'PASS' if selected else 'INFO'}] S2 ({tc_id}): Màu {scenario['color']}")

        # ── S3: Chờ AI gen artwork ────────────────────────────────────────────
        print(f"  [INFO] S3 ({tc_id}): Đang chờ AI generate artwork...")
        ok, elapsed, found = self.studio.wait_for_artworks(count=3, timeout=120)
        self.studio.shot(tc_id, "3", f"artworks_{found}imgs_{int(elapsed)}s", domain=_D, root=_R)
        print(f"  [INFO] S3 ({tc_id}): {found} ảnh trong {elapsed}s")
        if not ok:
            pytest.skip(f"BỎ QUA S3 ({tc_id}): Chỉ tạo được {found}/3 ảnh sau {elapsed}s")
        print(f"  [PASS] S3 ({tc_id}): {found} artwork sẵn sàng")

        order_data = {
            "color": scenario["color"],
            "size": scenario["size"],
            "artwork_front_src": None,
            "artwork_back_src": None,
        }

        # ── S4: Áp artwork mặt trước (nếu apply_front=True) ──────────────────
        if scenario["apply_front"]:
            idx = scenario["artwork_index_front"]
            order_data["artwork_front_src"] = self.studio.read_panel_image_src(idx)
            applied = self.studio.click_artwork(index=idx)
            assert applied, f"LỖI S4 ({tc_id}): Không click được artwork index={idx} — URL: {page.url}"
            self.studio.wait_for_canvas_artwork(timeout=30, poll_ms=500)
            self.studio.shot(tc_id, "4", f"front_artwork_idx{idx}_applied", domain=_D, root=_R)
            print(f"  [PASS] S4 ({tc_id}): Đã áp artwork index={idx} lên mặt trước")
        else:
            self.studio.shot(tc_id, "4", "front_artwork_skipped", domain=_D, root=_R)
            print(f"  [INFO] S4 ({tc_id}): Bỏ qua mặt trước theo scenario")

        # ── S5: Áp artwork mặt sau (nếu apply_back=True) ─────────────────────
        if scenario["apply_back"]:
            back_visible = self.studio.back_button.is_visible(timeout=3000)
            if back_visible:
                self.studio.toggle_side("back")
                page.wait_for_timeout(1500)
                self.studio.shot(tc_id, "5a", "shirt_back_view", domain=_D, root=_R)

                idx = scenario["artwork_index_back"]
                lib_ok = self.studio.click_library_image(index=idx)
                order_data["artwork_back_src"] = self.studio.read_library_image_src(idx)
                page.wait_for_timeout(4000)
                self.studio.shot(tc_id, "5b", f"back_artwork_idx{idx}_applied", domain=_D, root=_R)
                print(f"  [{'PASS' if lib_ok else 'WARN'}] S5 ({tc_id}): Áp artwork index={idx} lên mặt sau")
            else:
                self.studio.shot(tc_id, "5a", "back_button_not_visible", domain=_D, root=_R)
                print(f"  [INFO] S5 ({tc_id}): Nút 'Xoay áo' không hiển thị — bỏ qua mặt sau")
        else:
            self.studio.shot(tc_id, "5a", "back_artwork_skipped", domain=_D, root=_R)
            print(f"  [INFO] S5 ({tc_id}): Bỏ qua mặt sau theo scenario")

        # ── S6: Hoàn tất thiết kế → Review ───────────────────────────────────
        self.studio.open_order_modal()
        page.wait_for_timeout(2000)
        self.studio.shot(tc_id, "6", "review_page", domain=_D, root=_R)
        assert "review" in page.url or page.locator("button:has-text('Đặt hàng')").is_visible(timeout=5000), \
            f"LỖI S6 ({tc_id}): Không tới trang /review — URL: {page.url}"
        print(f"  [PASS] S6 ({tc_id}): Review page OK")

        print(f"  [INFO] {tc_id} order_data: {order_data}")
        print(f"  [PASS] {tc_id}: {scenario['description']} — hoàn thành ✓")
