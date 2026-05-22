"""Utility: Tạo 5 design mới trong test account để mở rộng phạm vi test tryon.

Usage:
    python scripts/create_test_designs.py

Requires .env with DAILY_TEST_EMAIL and DAILY_TEST_PASSWORD.
Kết quả: 5 design mới xuất hiện trong /my-designs của tester_beta_2026@yopmail.com
"""
from __future__ import annotations
import sys
import os
import time
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
except ImportError:
    pass

from playwright.sync_api import sync_playwright, Page

FE_URL   = "https://test.shop.tryonic.ai"
EMAIL    = os.getenv("DAILY_TEST_EMAIL", "")
PASSWORD = os.getenv("DAILY_TEST_PASSWORD", "")

PROMPTS = [
    "áo gia đình đi biển mùa hè sóng nước vui tươi",
    "áo thể thao năng động màu sắc rực rỡ cá tính",
    "áo phông hoạt hình anime dễ thương kawaii",
    "áo couple tình yêu đôi lứa ngọt ngào lãng mạn",
    "áo in hoa văn truyền thống Việt Nam đẹp tinh tế",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _banner(msg: str) -> None:
    print(f"\n{'='*60}\n  {msg}\n{'='*60}")


def _log(msg: str) -> None:
    print(f"  [INFO] {msg}")


def _warn(msg: str) -> None:
    print(f"  [WARN] {msg}")


def login(page: Page) -> bool:
    """Login via auth modal. Trả về True nếu thành công."""
    if not EMAIL or not PASSWORD:
        print("  [ERROR] Chưa set DAILY_TEST_EMAIL / DAILY_TEST_PASSWORD trong .env")
        return False

    page.goto(FE_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2_000)

    # Click Login button in header
    login_btn = page.locator(
        "button:has-text('Đăng nhập'), button:has-text('Login'), "
        "a:has-text('Đăng nhập'), a:has-text('Login')"
    ).first
    try:
        login_btn.click(timeout=5_000)
    except Exception:
        _warn("Không tìm thấy nút Login — thử click Header login")
        return False

    page.wait_for_timeout(1_500)

    # Fill email
    email_input = page.locator(
        "input[type='email'], input[placeholder*='email' i], input[name='email']"
    ).first
    try:
        email_input.fill(EMAIL, timeout=5_000)
    except Exception as e:
        _warn(f"Không tìm thấy email input: {e}")
        return False

    # Fill password
    pwd_input = page.locator(
        "input[type='password'], input[placeholder*='password' i], input[name='password']"
    ).first
    try:
        pwd_input.fill(PASSWORD, timeout=5_000)
    except Exception as e:
        _warn(f"Không tìm thấy password input: {e}")
        return False

    # Submit
    submit_btn = page.locator(
        "button[type='submit'], button:has-text('Đăng nhập'), button:has-text('Đăng Nhập')"
    ).first
    try:
        submit_btn.click(timeout=5_000)
    except Exception:
        pwd_input.press("Enter")

    page.wait_for_timeout(4_000)

    # Verify logged in: không còn nút Đăng nhập nổi bật
    is_logged_in = page.evaluate("""() => {
        // Nếu có avatar / điểm / tên user → đã login
        const body = document.body.innerText || '';
        if (/\\d+\\s*[Đđ]iểm/.test(body)) return true;
        // Không còn modal đăng nhập
        const modal = document.querySelector('[role="dialog"]');
        if (!modal || !modal.checkVisibility()) return true;
        return false;
    }""")

    if is_logged_in:
        _log("Đăng nhập thành công")
        return True
    else:
        _warn("Không xác nhận được trạng thái đăng nhập")
        return True  # tiếp tục thử


def dismiss_product_dialog(page: Page) -> None:
    """Đóng dialog 'Chọn sản phẩm' nếu xuất hiện."""
    try:
        dialog_title = page.locator("text='Chọn sản phẩm'")
        if not dialog_title.is_visible(timeout=5_000):
            return

        _log("Dialog 'Chọn sản phẩm' đang mở — đang chọn sản phẩm đầu tiên...")
        result = page.evaluate("""() => {
            const heading = Array.from(document.querySelectorAll('*')).find(
                el => el.childElementCount === 0
                   && el.textContent.trim() === 'Chọn sản phẩm'
            );
            if (!heading) return 'no-heading';
            let modal = heading.parentElement;
            for (let i = 0; i < 10 && modal && modal !== document.body; i++) {
                if (modal.querySelectorAll('img[src]').length >= 2) break;
                modal = modal.parentElement;
            }
            if (!modal || modal === document.body) return 'no-modal';
            const cards = Array.from(modal.querySelectorAll('div, button, li'))
                .filter(el => {
                    if (!el.querySelector('img[src]')) return false;
                    const r = el.getBoundingClientRect();
                    return r.width >= 80 && r.width <= 420 && r.height >= 100;
                })
                .sort((a, b) => {
                    const ra = a.getBoundingClientRect();
                    const rb = b.getBoundingClientRect();
                    return (ra.width * ra.height) - (rb.width * rb.height);
                });
            if (cards.length === 0) return 'no-cards';
            const card = cards[0];
            card.dispatchEvent(new MouseEvent('click',   {bubbles: true}));
            card.dispatchEvent(new MouseEvent('dblclick',{bubbles: true}));
            return 'ok:' + card.tagName;
        }""")
        _log(f"Double-click card: {result}")

        try:
            page.wait_for_selector("text='Chọn sản phẩm'", state="hidden", timeout=8_000)
            _log("Dialog đã đóng")
        except Exception:
            page.keyboard.press("Escape")
            page.wait_for_timeout(1_000)

        page.wait_for_timeout(1_500)
    except Exception as e:
        _warn(f"dismiss_product_dialog: {e}")


def accept_terms(page: Page) -> None:
    """Đồng ý Điều khoản nếu có."""
    try:
        agree_btn = page.locator(
            "button:has-text('Tôi đồng ý với Điều khoản'), "
            "button:has-text('Tôi đồng ý'), "
            "button:has-text('Đồng ý với Điều khoản'), "
            "button:has-text('Đồng ý')"
        ).first
        if agree_btn.is_visible(timeout=3_000):
            agree_btn.click()
            page.wait_for_timeout(1_500)
            _log("Đã đồng ý Điều khoản")
    except Exception:
        pass


def generate_artwork(page: Page, prompt: str) -> bool:
    """Nhập prompt trong Studio chat và submit. Trả về True nếu OK."""
    try:
        # Tìm textarea / input prompt trong studio
        prompt_input = page.locator(
            "textarea[placeholder*='Mô tả ý tưởng'], textarea[placeholder*='Mo ta y tuong'], "
            "textarea[placeholder*='Mô tả'], textarea[placeholder*='Bạn'], "
            "input[placeholder*='ý tưởng'], input[placeholder*='Bạn muốn']"
        ).first

        prompt_input.click(timeout=5_000)
        prompt_input.fill(prompt)
        page.wait_for_timeout(300)

        # Thử click nút Tạo
        try:
            gen_btn = page.locator(
                "button:has-text('Tạo ngay'), button:has-text('Tạo'), button:has-text('Generate')"
            ).first
            if gen_btn.is_visible(timeout=2_000):
                gen_btn.click()
                _log(f"Đã click 'Tạo ngay' với prompt: {prompt[:40]}...")
                return True
        except Exception:
            pass

        # Fallback: Enter
        prompt_input.press("Enter")
        _log(f"Đã nhập prompt và nhấn Enter: {prompt[:40]}...")
        return True
    except Exception as e:
        _warn(f"generate_artwork error: {e}")
        return False


def count_chat_artworks(page: Page) -> int:
    """Đếm artwork trong AI chat panel bên phải (x > 65% viewport)."""
    try:
        return page.evaluate("""() => {
            const vw = window.innerWidth;
            const threshold = vw * 0.65;
            return Array.from(document.querySelectorAll('img[src]')).filter(img => {
                const r = img.getBoundingClientRect();
                return r.x > threshold && r.width >= 80 && r.height >= 80
                    && img.complete && img.naturalWidth > 0;
            }).length;
        }""")
    except Exception:
        return 0


def wait_for_new_artworks(page: Page, baseline: int = 0, timeout: int = 120) -> tuple:
    """Chờ ít nhất 1 artwork mới xuất hiện. Trả về (success, elapsed, new_count)."""
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        current = count_chat_artworks(page)
        if current > baseline and (current - baseline) >= 1:
            elapsed = round(time.time() - start, 1)
            return True, elapsed, current - baseline
        page.wait_for_timeout(2_000)

    elapsed = round(time.time() - start, 1)
    final = count_chat_artworks(page)
    return False, elapsed, max(0, final - baseline)


def click_hoan_tat(page: Page, timeout: int = 30) -> bool:
    """Chờ nút 'Hoàn tất thiết kế' enabled và click. Trả về True nếu thành công."""
    hoan_tat = page.locator("button:has-text('Hoàn tất thiết kế')").first
    start = time.time()
    deadline = start + timeout
    while time.time() < deadline:
        try:
            if hoan_tat.is_visible(timeout=500) and not hoan_tat.is_disabled():
                hoan_tat.click(force=True)
                _log("Đã click 'Hoàn tất thiết kế'")
                return True
        except Exception:
            pass
        page.wait_for_timeout(2_000)

    _warn(f"Nút 'Hoàn tất thiết kế' không enabled sau {timeout}s")
    return False


def create_design(page: Page, prompt: str, design_num: int) -> Optional[str]:
    """Tạo 1 design. Trả về studio URL nếu thành công, None nếu thất bại."""
    _banner(f"Design #{design_num}: {prompt}")

    # ── 1. Mở Studio ─────────────────────────────────────────────────────────
    _log("Mở Studio...")
    page.goto(f"{FE_URL}/studio?category=t-shirts", wait_until="domcontentloaded")
    page.wait_for_timeout(3_000)

    # ── 2. Accept terms + dismiss dialog ────────────────────────────────────
    accept_terms(page)
    dismiss_product_dialog(page)
    page.wait_for_timeout(1_000)

    # ── 3. Generate artwork ───────────────────────────────────────────────────
    baseline = count_chat_artworks(page)
    _log(f"Baseline artworks: {baseline}")

    ok = generate_artwork(page, prompt)
    if not ok:
        _warn("Không nhập được prompt → skip design này")
        return None

    page.wait_for_timeout(1_000)

    # ── 4. Chờ artwork xuất hiện ──────────────────────────────────────────────
    _log("Đang chờ AI tạo artwork (tối đa 120s)...")
    success, elapsed, new_count = wait_for_new_artworks(page, baseline=baseline, timeout=120)
    if success:
        _log(f"AI tạo xong {new_count} artwork mới sau {elapsed}s")
    else:
        _warn(f"Không thấy artwork mới sau {elapsed}s — thử tiếp")

    # ── 5. Dọn dẹp dialogs sau khi gen ──────────────────────────────────────
    accept_terms(page)
    dismiss_product_dialog(page)
    page.wait_for_timeout(1_000)

    # ── 6. Click Hoàn tất thiết kế ───────────────────────────────────────────
    clicked = click_hoan_tat(page, timeout=30)
    if not clicked:
        _warn("Không click được 'Hoàn tất thiết kế' — design có thể chưa được lưu")

    # ── 7. Chờ navigate đến /review ───────────────────────────────────────────
    try:
        page.wait_for_url("**/studio/**/review", timeout=10_000)
    except Exception:
        page.wait_for_timeout(2_000)

    current_url = page.url
    if "/studio/" in current_url:
        # Strip /review để lấy studio base URL
        studio_url = current_url.rstrip("/").replace("/review", "")
        _log(f"Design đã lưu: {studio_url}")
        return studio_url
    else:
        _warn(f"URL không như mong đợi: {current_url}")
        return current_url


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    _banner("CREATE TEST DESIGNS — test.shop.tryonic.ai")
    print(f"  Account: {EMAIL}")
    print(f"  Số design cần tạo: {len(PROMPTS)}")

    created = []
    failed  = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False để debug dễ
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()

        # ── Login ─────────────────────────────────────────────────────────────
        _banner("ĐĂNG NHẬP")
        if not login(page):
            print("  [ERROR] Đăng nhập thất bại — dừng lại")
            browser.close()
            return

        page.wait_for_timeout(2_000)

        # ── Tạo từng design ───────────────────────────────────────────────────
        for i, prompt in enumerate(PROMPTS, 1):
            try:
                url = create_design(page, prompt, i)
                if url:
                    created.append({"num": i, "prompt": prompt, "url": url})
                    print(f"  ✅ Design #{i} OK: {url}")
                else:
                    failed.append({"num": i, "prompt": prompt})
                    print(f"  ❌ Design #{i} FAIL")
            except Exception as e:
                failed.append({"num": i, "prompt": prompt})
                print(f"  ❌ Design #{i} EXCEPTION: {e}")

            # Nghỉ 2s giữa các lần để tránh rate limit
            if i < len(PROMPTS):
                page.wait_for_timeout(2_000)

        # ── Xác nhận trong /my-designs ────────────────────────────────────────
        _banner("XÁC NHẬN /my-designs")
        page.goto(f"{FE_URL}/my-designs", wait_until="domcontentloaded")
        page.wait_for_timeout(3_000)

        design_count = page.evaluate("""() => {
            return document.querySelectorAll('a[href*="/studio/"]').length;
        }""")
        _log(f"Số design có trong /my-designs: {design_count}")

        browser.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    _banner("KẾT QUẢ")
    print(f"  ✅ Tạo thành công: {len(created)}/{len(PROMPTS)}")
    for d in created:
        print(f"     #{d['num']}: {d['prompt'][:50]}")
        print(f"        → {d['url']}")
    if failed:
        print(f"  ❌ Thất bại: {len(failed)}/{len(PROMPTS)}")
        for d in failed:
            print(f"     #{d['num']}: {d['prompt'][:50]}")

    print(f"\n  Tổng designs trong /my-designs: {design_count}")
    print(f"  Mở /my-designs để xác nhận: {FE_URL}/my-designs\n")


if __name__ == "__main__":
    main()
