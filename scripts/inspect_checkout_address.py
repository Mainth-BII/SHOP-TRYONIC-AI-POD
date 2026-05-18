"""Inspect DOM trang checkout — tìm địa chỉ sau khi load xong."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://test.shop.tryonic.ai"
EMAIL    = os.getenv("DAILY_TEST_EMAIL", "")
PASSWORD = os.getenv("DAILY_TEST_PASSWORD", "")


def login(page):
    page.goto(BASE_URL)
    page.wait_for_timeout(2000)
    btn = page.locator("button:has-text('Đăng nhập'), a:has-text('Đăng nhập')").first
    if btn.is_visible(timeout=5000):
        btn.click()
        page.wait_for_timeout(1500)
    for sel, val in [('input[type="email"]', EMAIL), ('input[type="password"]', PASSWORD)]:
        page.evaluate(f"""(v) => {{
            const i = document.querySelector('{sel}');
            if (i) {{ const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                s.call(i,v); i.dispatchEvent(new Event('input',{{bubbles:true}})); }}
        }}""", val)
        page.wait_for_timeout(200)
    page.evaluate("""() => {
        for (const b of document.querySelectorAll('form button, button')) {
            if (b.textContent.includes('Đăng nhập')) { b.click(); return; }
        }
    }""")
    page.wait_for_timeout(4000)
    print(f"[LOGIN] {page.url}")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    ctx = browser.new_context(viewport={"width":1440,"height":900}, locale="vi-VN")
    page = ctx.new_page()
    login(page)

    # Điều hướng đến checkout với order code từ lần test gần nhất
    # Thực ra checkout chỉ accessible khi có cart — dùng cart sẵn có
    page.goto(f"{BASE_URL}/checkout")
    page.wait_for_timeout(3000)
    print(f"URL sau navigate checkout: {page.url}")

    # Chờ address load xong
    try:
        page.wait_for_function(
            "() => !document.body.innerText.includes('Đang tải địa chỉ')",
            timeout=10000
        )
        print("Address loaded (spinner biến mất)")
    except Exception:
        print("Timeout chờ address — vẫn tiếp tục")

    # Dump toàn bộ innerText
    text = page.evaluate("() => document.body.innerText || ''")
    print(f"\n=== body.innerText ===\n{text[:1000]}")

    # Dump tất cả inputs
    inputs = page.evaluate("""() =>
        Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
            tag: el.tagName, name: el.name||el.id||'', type: el.type||'',
            ph: el.placeholder||'', val: el.value||'', visible: el.offsetWidth > 0
        }))
    """)
    print(f"\n=== Tất cả inputs ===")
    for i in inputs:
        print(f"  <{i['tag']} name='{i['name']}' type='{i['type']}' visible={i['visible']}> ph='{i['ph'][:30]}' val='{i['val'][:60]}'")

    # Dump elements gần "Địa chỉ nhận hàng"
    addr_info = page.evaluate("""() => {
        const results = [];
        for (const el of document.querySelectorAll('*')) {
            const t = (el.innerText || '').trim();
            if (t.includes('Địa chỉ nhận hàng') && t.length < 500) {
                results.push({
                    tag: el.tagName,
                    cls: (el.className || '').slice(0, 80),
                    text: t.slice(0, 300)
                });
            }
        }
        return results.slice(0, 10);
    }""")
    print(f"\n=== Elements chứa 'Địa chỉ nhận hàng' ===")
    for e in addr_info:
        print(f"  <{e['tag']} cls='{e['cls']}'>\n  TEXT: {repr(e['text'])}\n")

    # Dump elements chứa "local_shipping" hoặc shipping methods
    shipping = page.evaluate("""() => {
        const results = [];
        for (const el of document.querySelectorAll('input[type="radio"], input[value*="shipping"], input[name*="ship"]')) {
            results.push({tag:el.tagName, name:el.name, val:el.value, checked:el.checked});
        }
        return results;
    }""")
    print(f"\n=== Shipping inputs ===")
    for s in shipping:
        print(f"  name='{s['name']}' val='{s['val']}' checked={s['checked']}")

    input("\n>>> Enter để đóng...")
    browser.close()
