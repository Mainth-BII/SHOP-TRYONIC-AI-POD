"""Inspect DOM của /cart và /checkout sau khi thêm item vào giỏ.

Chạy: python scripts/inspect_cart_checkout_flow.py
"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright

BASE_URL  = "https://test.shop.tryonic.ai"
EMAIL     = "tester_beta_2026@yopmail.com"
PASSWORD  = "Admin@12"
SLUG      = "ao-phong-nang-dong"

def login(page):
    page.goto(BASE_URL)
    page.wait_for_timeout(2000)
    # Click nút Login trên header
    for sel in ["button:has-text('Đăng nhập')", "a:has-text('Đăng nhập')",
                "button:has-text('Login')", "[aria-label*='login']"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                break
        except: pass
    page.wait_for_timeout(1500)
    # Điền credentials
    for sel in ["input[type='email']", "input[name='email']", "input[placeholder*='mail']"]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.fill(EMAIL)
                break
        except: pass
    for sel in ["input[type='password']", "input[name='password']"]:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.fill(PASSWORD)
                break
        except: pass
    for sel in ["button[type='submit']", "button:has-text('Đăng nhập')", "button:has-text('Login')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                break
        except: pass
    page.wait_for_timeout(3000)
    print(f"  [INFO] URL after login: {page.url}")

def add_to_cart_simple(page):
    """Navigate sản phẩm, chọn size S, thêm vào giỏ (không qua studio)."""
    page.goto(f"{BASE_URL}/product/{SLUG}")
    page.wait_for_timeout(3000)
    print(f"  [INFO] Product page: {page.url}")
    # Click nút Mua ngay (không phải Studio)
    for sel in ["button:has-text('Mua ngay')", "button:has-text('MUA NGAY')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                btn.click()
                page.wait_for_timeout(2000)
                print("  [INFO] Đã click Mua ngay")
                break
        except: pass
    page.wait_for_timeout(1000)
    # Chọn size S
    for sel in ["button:text-is('S')", "button[data-size='S']", "label:text-is('S')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)
                print("  [INFO] Đã chọn size S")
                break
        except: pass
    # Click Thêm vào giỏ
    for sel in ["button:has-text('Thêm vào giỏ')", "button:has-text('Thêm')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                btn.click()
                page.wait_for_timeout(2000)
                print("  [INFO] Đã click Thêm vào giỏ")
                break
        except: pass

def inspect_section(page, title, js_code):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    try:
        result = page.evaluate(js_code)
        if isinstance(result, list):
            for item in result:
                print(f"  {item}")
        else:
            print(f"  {result}")
    except Exception as e:
        print(f"  ERROR: {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    # === STEP 1: Login & add item ===
    print("\n[STEP 1] Login + Add to cart")
    login(page)
    add_to_cart_simple(page)

    # === STEP 2: Navigate to /cart ===
    print("\n[STEP 2] Navigate to /cart")
    page.goto(f"{BASE_URL}/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  URL: {page.url}")

    # Inspect cart page buttons
    inspect_section(page, "CART PAGE - All visible buttons", """() => {
        return Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => ({
            text: el.innerText.trim().replace(/\\n/g, ' ').substring(0, 60),
            className: el.className.substring(0, 60),
            disabled: el.disabled,
            rect: (() => { const r = el.getBoundingClientRect(); return `${Math.round(r.width)}x${Math.round(r.height)} at y=${Math.round(r.top)}`; })()
        }));
    }""")

    # Inspect cart prices
    inspect_section(page, "CART PAGE - All price-like text on page", """() => {
        const text = document.body.innerText || '';
        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        const priceLines = lines.filter(l => /\\d[\\d,.]*\\d/.test(l) && l.length < 100);
        return priceLines.slice(0, 30);
    }""")

    # Find total price section
    inspect_section(page, "CART PAGE - Elements with 'Tổng' text", """() => {
        const results = [];
        for (const el of document.querySelectorAll('*')) {
            const text = (el.innerText || '').trim();
            if (/Tổng/i.test(text) && text.length < 100 && el.children.length === 0) {
                results.push({
                    tag: el.tagName,
                    text: text,
                    className: el.className.substring(0, 60)
                });
            }
        }
        return results.slice(0, 20);
    }""")

    # === STEP 3: Click checkout button ===
    print("\n[STEP 3] Try to click checkout button")
    clicked = False
    for sel, name in [
        ("button:has-text('Thanh toán')", "has-text Thanh toán"),
        ("button:has-text('Tiến hành thanh toán')", "has-text Tiến hành"),
        ("button:has-text('Đặt hàng')", "has-text Đặt hàng"),
        ("a:has-text('Thanh toán')", "a Thanh toán"),
        ("a[href*='checkout']", "a[href checkout]"),
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                print(f"  [FOUND] {name}: '{btn.inner_text()[:50]}'")
                btn.click()
                page.wait_for_timeout(3000)
                print(f"  [INFO] URL after click: {page.url}")
                clicked = True
                break
        except Exception as e:
            print(f"  [MISS] {name}: {e}")

    if not clicked:
        print("  [WARN] Không click được checkout button")

    # === STEP 4: Inspect Checkout page ===
    print(f"\n[STEP 4] Inspect Checkout page (URL: {page.url})")
    page.wait_for_timeout(2000)

    inspect_section(page, "CHECKOUT PAGE - All price lines", """() => {
        const text = document.body.innerText || '';
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        return lines.filter(l => /Tổng|VAT|Phí|Giảm|Shipping|Total|\\d[\\d,.]*/.test(l) && l.length < 100).slice(0, 30);
    }""")

    inspect_section(page, "CHECKOUT PAGE - All visible buttons", """() => {
        return Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => ({
            text: el.innerText.trim().replace(/\\n/g, ' ').substring(0, 60),
            disabled: el.disabled
        })).filter(b => b.text);
    }""")

    # === STEP 5: Inspect QR page (nếu đã navigate) ===
    if "checkout" in page.url or "payment" in page.url or "order" in page.url:
        # Click payment button
        for sel in ["button:has-text('Thanh toán')", "button:has-text('Đặt hàng')",
                    "button:has-text('Xác nhận')", "button:has-text('Hoàn tất')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=3000):
                    print(f"\n[STEP 5] Click payment: '{btn.inner_text()[:50]}'")
                    btn.click()
                    page.wait_for_timeout(5000)
                    print(f"  URL after payment: {page.url}")
                    break
            except: pass

        inspect_section(page, "QR/PAYMENT PAGE - Price text", """() => {
            const text = document.body.innerText || '';
            const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
            return lines.filter(l => /\\d[\\d,.]*\\d|Số tiền|QR|thanh toán/i.test(l) && l.length < 100).slice(0, 20);
        }""")

    # === STEP 6: My orders page ===
    page.goto(f"{BASE_URL}/orders")
    page.wait_for_timeout(3000)
    print(f"\n[STEP 6] Orders page: {page.url}")

    inspect_section(page, "MY ORDERS PAGE - Price-related lines", """() => {
        const text = document.body.innerText || '';
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        return lines.filter(l => /Tổng|đ|₫|\\d[\\d,.]*[\\d]/.test(l) && l.length < 80).slice(0, 20);
    }""")

    page.screenshot(path="scripts/cart_inspect_screenshot.png", full_page=True)
    print("\n  [INFO] Screenshot saved: scripts/cart_inspect_screenshot.png")
    page.wait_for_timeout(2000)
    browser.close()
