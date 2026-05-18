"""Inspect DOM checkout + QR sau khi mở cart drawer đúng cách."""
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
    page.locator("button:has-text('Đăng nhập')").first.click()
    page.wait_for_timeout(1000)
    page.locator("input[type='email']").first.fill(EMAIL)
    page.locator("input[type='password']").first.fill(PASSWORD)
    page.locator("button[type='submit']").first.click()
    page.wait_for_timeout(3000)
    print(f"  Logged in, URL: {page.url}")

def print_section(title, data):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")
    if isinstance(data, list):
        for x in data: print(f"  {x}")
    else:
        print(f"  {data}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    login(page)
    page.goto(f"{BASE_URL}/product/{SLUG}")
    page.wait_for_timeout(3000)

    # === Add item to cart (not Studio) ===
    page.locator("button:has-text('Mua ngay')").first.click()
    page.wait_for_timeout(2000)
    try: page.locator("button:text-is('M')").first.click()
    except: pass
    page.wait_for_timeout(500)
    page.locator("button:has-text('Thêm vào giỏ')").first.click()
    page.wait_for_timeout(2000)
    print(f"\n[STEP 1] Added item, URL: {page.url}")

    # === Open cart drawer ===
    cart_btn = page.locator("button:has-text('shopping_cart')").first
    cart_btn.click()
    page.wait_for_timeout(2000)
    print(f"\n[STEP 2] Cart drawer opened, URL: {page.url}")

    # Inspect drawer DOM
    drawer_info = page.evaluate("""() => {
        // Tìm drawer element đang hiển thị
        const selectors = [
            '[class*="drawer"]', '[class*="Drawer"]',
            '[class*="cart-panel"]', 'aside', '[role="dialog"]',
            '[class*="max-w-md"][class*="shadow"]',
            '[class*="max-w-sm"]', '[class*="slide"]'
        ];
        const results = [];
        for (const sel of selectors) {
            const els = document.querySelectorAll(sel);
            for (const el of els) {
                const r = el.getBoundingClientRect();
                if (r.width > 100 && r.height > 200) {
                    results.push({
                        sel,
                        className: el.className.substring(0, 100),
                        text: el.innerText.substring(0, 300).replace(/\\n/g, ' | '),
                        buttons: Array.from(el.querySelectorAll('button')).map(b => b.innerText.trim().replace(/\\n/g, ' ').substring(0, 40)).filter(Boolean)
                    });
                }
            }
        }
        return results;
    }""")
    print_section("DRAWER ELEMENTS", drawer_info)

    # Get all prices in page (including cart panel)
    price_lines = page.evaluate("""() => {
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
        return lines.filter(l => /Tổng|Tiền|\\d{2,3}[\\.,]\\d{3}/.test(l) && l.length < 100);
    }""")
    print_section("ALL PRICE LINES ON PAGE", price_lines)

    # All buttons
    buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => ({
            text: el.innerText.trim().replace(/\\n/g,' ').substring(0,50),
            cls: el.className.substring(0,60)
        })).filter(b => b.text);
    }""")
    print_section("ALL VISIBLE BUTTONS", buttons)

    # === Click Thanh toán ngay ===
    print("\n[STEP 3] Click 'Thanh toán ngay' in cart")
    for sel in ["button:has-text('Thanh toán ngay')", "button:has-text('Thanh toán')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                print(f"  Found: {btn.inner_text()[:50]}")
                btn.click()
                page.wait_for_timeout(4000)
                print(f"  URL after: {page.url}")
                break
        except Exception as e:
            print(f"  Miss {sel}: {e}")

    # === Inspect Checkout page ===
    print(f"\n[STEP 4] Checkout page URL: {page.url}")
    page.screenshot(path="scripts/checkout_page_screenshot.png")

    checkout_text = page.evaluate("""() => document.body.innerText.substring(0, 2000)""")
    print(f"  Checkout page text (2000 chars):\n{checkout_text}")

    price_lines2 = page.evaluate("""() => {
        const text = document.body.innerText;
        return text.split('\\n').map(l => l.trim()).filter(l =>
            l && /Tổng|VAT|Phí|Giảm|Shipping|\\d{2,3}[.,]\\d{3}/.test(l) && l.length < 100
        );
    }""")
    print_section("CHECKOUT PRICE LINES", price_lines2)

    checkout_buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(el => el.innerText.trim().replace(/\\n/g,' ').substring(0,60)).filter(Boolean);
    }""")
    print_section("CHECKOUT BUTTONS", checkout_buttons)

    # === Click payment button ===
    print("\n[STEP 5] Click payment button from checkout")
    for sel in ["button:has-text('Thanh toán')", "button:has-text('Đặt hàng')",
                "button:has-text('Xác nhận')", "button:has-text('Hoàn tất')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                print(f"  Found payment btn: {btn.inner_text()[:50]}")
                btn.click()
                page.wait_for_timeout(5000)
                print(f"  URL after: {page.url}")
                break
        except: pass

    # === QR page ===
    print(f"\n[STEP 6] QR page URL: {page.url}")
    qr_text = page.evaluate("""() => document.body.innerText.substring(0, 1000)""")
    print(f"  QR page text:\n{qr_text}")
    page.screenshot(path="scripts/qr_page_screenshot.png")

    # QR price lines
    qr_prices = page.evaluate("""() => {
        const text = document.body.innerText;
        return text.split('\\n').map(l => l.trim()).filter(l =>
            l && /Số tiền|Tổng|thanh toán|\\d{2,3}[.,]\\d{3}/.test(l) && l.length < 100
        );
    }""")
    print_section("QR PRICE LINES", qr_prices)

    # === Cancel QR ===
    print("\n[STEP 7] Cancel QR")
    for sel in ["button:has-text('Huỷ')", "button:has-text('Hủy')", "button:has-text('Huy')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                btn.click(); page.wait_for_timeout(2000)
                print(f"  Canceled QR, URL: {page.url}")
                break
        except: pass
    # Confirm cancel
    for sel in ["button:has-text('Xác nhận')", "button:has-text('Đồng ý')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000): btn.click(); page.wait_for_timeout(2000); break
        except: pass

    # === View order ===
    print(f"\n[STEP 8] After cancel, URL: {page.url}")
    order_text = page.evaluate("""() => document.body.innerText.substring(0, 1000)""")
    print(f"  Page text:\n{order_text}")
    page.screenshot(path="scripts/order_page_screenshot.png")

    # === Navigate to orders list ===
    for sel in ["a:has-text('Đơn hàng của tôi')", "a[href*='/orders']", "button:has-text('Xem đơn')"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000): btn.click(); page.wait_for_timeout(3000); break
        except: pass

    print(f"\n[STEP 9] My orders page URL: {page.url}")
    orders_text = page.evaluate("""() => document.body.innerText.substring(0, 1000)""")
    print(f"  Orders page text:\n{orders_text}")
    orders_prices = page.evaluate("""() => {
        const text = document.body.innerText;
        return text.split('\\n').map(l => l.trim()).filter(l =>
            l && /Tổng|\\d{2,3}[.,]\\d{3}|đ|₫/.test(l) && l.length < 80
        );
    }""")
    print_section("ORDERS PAGE PRICE LINES", orders_prices)
    page.screenshot(path="scripts/orders_page_screenshot.png")
    page.wait_for_timeout(2000)
    browser.close()

print("\nDone! Screenshots saved in scripts/")
