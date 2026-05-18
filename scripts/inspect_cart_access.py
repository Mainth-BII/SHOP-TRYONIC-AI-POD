"""Tìm cách truy cập cart đúng: URL thực hay drawer panel."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_URL = "https://test.shop.tryonic.ai"
EMAIL    = "tester_beta_2026@yopmail.com"
PASSWORD = "Admin@12"
SLUG     = "ao-phong-nang-dong"

def login(page):
    page.goto(BASE_URL)
    page.wait_for_timeout(2000)
    for sel in ["button:has-text('Đăng nhập')", "a:has-text('Đăng nhập')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click(); break
        except: pass
    page.wait_for_timeout(1000)
    page.locator("input[type='email']").first.fill(EMAIL)
    page.locator("input[type='password']").first.fill(PASSWORD)
    page.locator("button[type='submit']").first.click()
    page.wait_for_timeout(3000)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    login(page)
    page.goto(f"{BASE_URL}/product/{SLUG}")
    page.wait_for_timeout(3000)

    # === Inspect header: tìm cart icon/link ===
    print("=== HEADER LINKS & BUTTONS ===")
    header_els = page.evaluate("""() => {
        const header = document.querySelector('header, nav, [class*="header"], [class*="Header"]') || document.body;
        return Array.from(header.querySelectorAll('a, button')).map(el => ({
            tag: el.tagName,
            text: el.innerText.trim().substring(0, 40),
            href: el.getAttribute('href') || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            className: el.className.substring(0, 60)
        })).filter(e => e.text || e.href || e.ariaLabel);
    }""")
    for el in header_els:
        print(f"  {el}")

    # === Tìm tất cả a[href] chứa từ khóa cart/gio ===
    print("\n=== ALL LINKS WITH cart/gio/hang ===")
    links = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href]')).map(el => ({
            href: el.getAttribute('href'),
            text: el.innerText.trim().substring(0, 40)
        })).filter(e => /cart|gio|hang|basket/i.test(e.href || ''));
    }""")
    for l in links:
        print(f"  {l}")

    # === Add item to cart ===
    print("\n=== Add item: click Mua ngay ===")
    for sel in ["button:has-text('Mua ngay')", "button:has-text('MUA NGAY')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click(); page.wait_for_timeout(2000); print(f"  Clicked: {sel}"); break
        except: pass

    # Select size S
    for sel in ["button:text-is('S')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000): btn.click(); page.wait_for_timeout(500); break
        except: pass

    # Click Thêm vào giỏ
    for sel in ["button:has-text('Thêm vào giỏ')", "button:has-text('Thêm')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                btn.click(); page.wait_for_timeout(2000); print(f"  Added to cart: {sel}"); break
        except: pass

    print(f"  URL after add: {page.url}")

    # === Check what changed after add to cart ===
    print("\n=== PAGE STATE AFTER ADD TO CART ===")
    state = page.evaluate("""() => {
        const url = window.location.href;
        const bodyText = document.body.innerText.substring(0, 500);
        // Tìm cart panel/drawer đang mở
        const panels = Array.from(document.querySelectorAll('[class*="cart"], [class*="drawer"], [class*="panel"], aside')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 50 && r.height > 100;
        }).map(el => ({
            tag: el.tagName,
            className: el.className.substring(0, 80),
            text: el.innerText.substring(0, 200)
        }));
        return { url, panels };
    }""")
    print(f"  URL: {state['url']}")
    print(f"  Open panels: {len(state['panels'])}")
    for panel in state['panels'][:5]:
        print(f"    Panel: {panel}")

    # === Try to click cart icon in header ===
    print("\n=== CLICK CART ICON IN HEADER ===")
    for sel in [
        "header button:has-text('shopping_cart')",
        "header a[href*='cart']",
        "header [class*='cart']",
        "button[aria-label*='cart'], button[aria-label*='giỏ']",
        "[class*='cart-icon'], [class*='CartIcon']",
        "header button:nth-child(2)",
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=1500):
                print(f"  [FOUND] {sel}: '{btn.inner_text()[:30]}'")
                btn.click()
                page.wait_for_timeout(2000)
                print(f"  URL after: {page.url}")
                break
        except: pass

    # === Inspect page after cart icon click ===
    print("\n=== PAGE AFTER CART CLICK ===")
    print(f"  URL: {page.url}")
    cart_info = page.evaluate("""() => {
        const bodyText = document.body.innerText.substring(0, 1000);
        const allButtons = Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => el.innerText.trim().replace(/\\n/g, ' ').substring(0, 60)).filter(Boolean);
        const priceLines = bodyText.split('\\n').filter(l => /Tổng|\\d[\\d,.]*\\d/.test(l) && l.trim().length < 80);
        return { text: bodyText, buttons: allButtons, priceLines };
    }""")
    print(f"  Page text (500 chars): {cart_info['text'][:500]}")
    print(f"  Buttons: {cart_info['buttons'][:15]}")
    print(f"  Price lines: {cart_info['priceLines'][:10]}")

    page.screenshot(path="scripts/cart_access_screenshot.png")
    print("\n  Screenshot: scripts/cart_access_screenshot.png")
    page.wait_for_timeout(3000)
    browser.close()
