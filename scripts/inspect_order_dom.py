"""Script chẩn đoán DOM — tìm format giá và địa chỉ."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://test.shop.tryonic.ai"
EMAIL    = os.getenv("DAILY_TEST_EMAIL", "")
PASSWORD = os.getenv("DAILY_TEST_PASSWORD", "")

# Order code từ lần chạy test gần nhất
ORDER_CODE = "POD-20260424-012"


def login(page):
    page.goto(f"{BASE_URL}/")
    page.wait_for_timeout(2000)
    btn = page.locator("button:has-text('Đăng nhập'), a:has-text('Đăng nhập')").first
    if btn.is_visible(timeout=5000):
        btn.click()
        page.wait_for_timeout(1500)
    page.evaluate("""(v) => {
        const i = document.querySelector('input[type="email"]');
        if (i) { const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            s.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); }
    }""", EMAIL)
    page.wait_for_timeout(200)
    page.evaluate("""(v) => {
        const i = document.querySelector('input[type="password"]');
        if (i) { const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            s.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); }
    }""", PASSWORD)
    page.wait_for_timeout(200)
    page.evaluate("""() => {
        const btns = document.querySelectorAll('form button, button');
        for (const b of btns) { if (b.textContent.includes('Đăng nhập')) { b.click(); return; } }
    }""")
    page.wait_for_timeout(4000)
    print(f"[LOGIN] {page.url}")


def inspect(page, label):
    print(f"\n{'='*70}")
    print(f"[{label}] URL: {page.url}")

    text = page.evaluate("() => document.body.innerText || ''")
    print(f"\n--- innerText (đầu 800 chars) ---")
    print(text[:800])
    print(f"\n--- innerText (800-1600 chars) ---")
    print(text[800:1600])

    # Mọi text node ngắn chứa ký tự tiền tệ hoặc số lớn
    money = page.evaluate(r"""() => {
        const res = [];
        document.querySelectorAll('*').forEach(el => {
            if (el.children.length > 0) return;
            const t = (el.innerText || '').trim();
            if ((t.includes('đ') || t.includes('₫') || t.includes('VNĐ') || t.includes('VND')
                 || /\d{3,}/.test(t)) && t.length < 80) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) res.push({
                    tag: el.tagName,
                    cls: (el.className || '').slice(0,50),
                    text: t
                });
            }
        });
        return res.slice(0, 60);
    }""")
    print(f"\n--- Elements chứa tiền/số ---")
    for e in money:
        print(f"  <{e['tag']} class='{e['cls']}'> {e['text']}")

    # Inputs
    inputs = page.evaluate("""() =>
        Array.from(document.querySelectorAll('input,textarea,select'))
            .map(el => ({name:el.name||el.id||'', type:el.type||'', ph:el.placeholder||'', val:el.value||''}))
            .filter(x => x.name||x.ph||x.val)
    """)
    print(f"\n--- Inputs ---")
    for i in inputs:
        print(f"  name='{i['name']}' type='{i['type']}' ph='{i['ph'][:40]}' val='{i['val'][:60]}'")

    # Address-like
    addr = page.evaluate("""() =>
        Array.from(document.querySelectorAll(
            '[class*="address"],[class*="Address"],[class*="deliver"],[class*="ship"],[class*="Ship"]'
        )).map(el => ({cls:(el.className||'').slice(0,60), text:(el.innerText||'').trim().slice(0,120)}))
    """)
    print(f"\n--- Address elements ---")
    for e in addr:
        print(f"  cls='{e['cls']}' text='{e['text']}'")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    ctx = browser.new_context(viewport={"width":1440,"height":900}, locale="vi-VN")
    page = ctx.new_page()

    login(page)

    # ── 1. Trang Orders (sau khi hủy) ────────────────────────────────────────
    page.goto(f"{BASE_URL}/orders?orderCode={ORDER_CODE}")
    page.wait_for_timeout(3000)
    inspect(page, f"ORDERS redirect — orderCode={ORDER_CODE}")

    # ── 2. Click vào đơn đầu tiên nếu có ────────────────────────────────────
    first = page.locator("main div:nth-of-type(1) button").first
    if first.is_visible(timeout=5000):
        first.click()
        page.wait_for_timeout(2000)
        inspect(page, "CHI TIẾT ĐƠN HÀNG")
    else:
        # Thử /profile
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_timeout(2000)
        tab = page.locator("button:has-text('Đơn hàng của tôi')").first
        if tab.is_visible(timeout=5000):
            tab.click()
            page.wait_for_timeout(1500)
        first2 = page.locator("main div:nth-of-type(1) button").first
        if first2.is_visible(timeout=5000):
            first2.click()
            page.wait_for_timeout(2000)
            inspect(page, "CHI TIẾT ĐƠN HÀNG (from profile)")
        else:
            print("[WARN] Không tìm thấy đơn hàng nào")

    print("\n>>> Script xong — đóng browser.")
    browser.close()
