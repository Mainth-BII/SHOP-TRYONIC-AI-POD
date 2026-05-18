"""Script inspect DOM của popup Gợi Ý Size Bằng AI.

Chạy: python scripts/inspect_size_guide_popup.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_URL = 'https://test.shop.tryonic.ai'
SLUG     = 'ao-phong-ca-tinh'

# Selector popup AI (overlay z-[9999])
AI_POPUP_SEL = "div.fixed.bg-black\\/40"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page()

    page.goto(f'{BASE_URL}/product/{SLUG}')
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(2000)

    # Mở buy-now popup
    page.locator("button:has-text('Mua ngay'), button:has-text('Mua Ngay')").first.click()
    page.wait_for_timeout(1500)

    # Click "Gợi ý size" link (màu #4F46F1) trong buy-now popup
    link_btn = page.locator("button.text-\\[\\#4F46F1\\]").first
    if not link_btn.is_visible(timeout=2000):
        # fallback: button nhỏ chứa text gợi ý
        link_btn = page.locator("button:has-text('Gợi ý size')").first
    link_btn.click()
    page.wait_for_timeout(1500)

    print("\n=== Popup AI container ===")
    popup_info = page.evaluate("""() => {
        // Tìm container có z-[9999] hoặc fixed overlay chứa popup AI
        const overlays = [...document.querySelectorAll('div[class*="fixed"]')].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 300 && r.height > 300;
        });
        return overlays.map(el => ({
            class: el.className.substring(0, 120),
            children: el.children.length,
            text: el.innerText.substring(0, 200)
        }));
    }""")
    for el in popup_info:
        print(el)

    print("\n=== Tất cả button visible trong popup ===")
    btns = page.evaluate("""() => {
        return [...document.querySelectorAll('button')].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => ({
            text: el.innerText.trim().substring(0, 40),
            className: el.className.substring(0, 80),
            rect: (() => { const r = el.getBoundingClientRect(); return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width)}; })()
        }));
    }""")
    print("Buttons visible:")
    for b in btns:
        print(f"  {b}")

    print("\n=== Tìm 'bảng size' element ===")
    bang_els = page.evaluate("""() => {
        const result = [];
        for (const el of document.querySelectorAll('*')) {
            const t = (el.innerText || el.textContent || '').trim();
            if (t.includes('bảng size') || t.includes('bang size') || t.includes('Bảng size')) {
                const r = el.getBoundingClientRect();
                if (r.width > 0) {
                    result.push({
                        tag: el.tagName,
                        text: t.substring(0, 60),
                        className: el.className.substring(0, 60),
                        href: el.getAttribute('href') || ''
                    });
                }
            }
        }
        return result.slice(0, 10);
    }""")
    print("'Bảng size' elements:")
    for el in bang_els:
        print(f"  {el}")

    print("\n=== Submit Gợi ý size (click trong popup) ===")
    # Click submit button — tìm button PINK (không phải link xanh)
    submit_clicked = page.evaluate("""() => {
        const btns = [...document.querySelectorAll('button')].filter(el => {
            const t = el.innerText.trim();
            const cls = el.className;
            const r = el.getBoundingClientRect();
            // Submit button: chứa 'Gợi ý', visible, KHÔNG phải link nhỏ màu xanh
            return t.includes('Gợi ý') && r.width > 100 && r.height > 30;
        });
        if (btns.length) { btns[btns.length - 1].click(); return true; }
        return false;
    }""")

    # Nhập dữ liệu trước → submit sau
    h_input = page.locator("input[placeholder*='chiều cao']").first
    w_input = page.locator("input[placeholder*='cân nặng']").first
    if h_input.is_visible(timeout=2000):
        h_input.fill("170")
    if w_input.is_visible(timeout=2000):
        w_input.fill("65")

    # Click Gợi ý size (submit) — dùng JS để bypass overlay intercept
    page.evaluate("""() => {
        const btns = [...document.querySelectorAll('button')].filter(el => {
            const t = el.innerText.trim();
            const r = el.getBoundingClientRect();
            return t.includes('Gợi ý') && r.width > 100;
        });
        if (btns.length) btns[btns.length - 1].click();
    }""")
    page.wait_for_timeout(2000)

    print("\n=== Kết quả sau khi submit ===")
    result = page.evaluate("""() => {
        // Tìm popup container (fixed, z cao) và đọc text
        const overlays = [...document.querySelectorAll('div[class*="fixed"]')].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 200 && r.height > 200;
        });
        if (overlays.length) return overlays[0].innerText.substring(0, 600);
        return document.body.innerText.substring(0, 600);
    }""")
    print(f"Popup text sau submit:\n{result}")

    print("\n=== Click 'bảng size tại đây' ===")
    page.evaluate("""() => {
        for (const el of document.querySelectorAll('*')) {
            const t = (el.innerText || el.textContent || '').trim();
            if ((t.includes('bảng size') || t.includes('Bảng size')) && el.children.length === 0) {
                el.click();
                return true;
            }
        }
        return false;
    }""")
    page.wait_for_timeout(2000)

    print("\n=== DOM sau khi click bảng size ===")
    chart_text = page.evaluate("""() => {
        const overlays = [...document.querySelectorAll('div[class*="fixed"], div[class*="modal"], div[class*="dialog"]')]
            .filter(el => el.getBoundingClientRect().width > 200)
            .map(el => el.innerText.substring(0, 800));
        return overlays[0] || document.body.innerText.substring(0, 800);
    }""")
    print(f"Bảng size text:\n{chart_text}")

    input("\n=== PAUSE — Xem browser, nhấn ENTER để đóng ===")
    browser.close()
