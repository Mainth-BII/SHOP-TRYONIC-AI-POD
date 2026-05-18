"""Debug: kiểm tra tại sao submit form AI size không trả kết quả."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests'))

from playwright.sync_api import sync_playwright

BASE_URL = "https://test.shop.tryonic.ai"
SLUG     = "ao-phong-ca-tinh"

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=500)
        ctx = browser.new_context(locale="vi-VN", viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        print("1. Mở product page...")
        page.goto(f"{BASE_URL}/product/{SLUG}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        print("2. Click Mua ngay...")
        page.locator("button:has-text('Mua ngay'), button:has-text('Mua Ngay')").first.click()
        page.wait_for_timeout(1500)

        print("3. Click Gợi ý size...")
        clicked = page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button')];
            const link = btns.find(b =>
                b.innerText.trim() === 'Gợi ý size' && b.className.includes('12px')
            );
            if (link) { link.click(); return true; }
            return false;
        }""")
        print(f"   clicked = {clicked}")
        page.wait_for_timeout(1500)

        # Dump popup text BEFORE fill
        before = page.evaluate("""() => {
            for (const d of document.querySelectorAll('div[class*="fixed"]')) {
                if (d.innerText.includes('Gợi Ý Size')) return d.innerText;
            }
            return 'POPUP NOT FOUND';
        }""")
        print(f"\n=== POPUP TEXT BEFORE FILL ===\n{before[:500]}\n")

        # Thử method 1: native setter
        print("4a. Fill inputs bằng native setter...")
        result1 = page.evaluate("""() => {
            const h = document.querySelector("input[placeholder*='chiều cao']");
            const w = document.querySelector("input[placeholder*='cân nặng']");
            if (!h || !w) return 'INPUTS NOT FOUND';
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            setter.call(h, '170');
            h.dispatchEvent(new Event('input', { bubbles: true }));
            h.dispatchEvent(new Event('change', { bubbles: true }));
            setter.call(w, '65');
            w.dispatchEvent(new Event('input', { bubbles: true }));
            w.dispatchEvent(new Event('change', { bubbles: true }));
            return `h.value=${h.value}, w.value=${w.value}`;
        }""")
        print(f"   Input values: {result1}")

        # Click Nam gender
        page.locator("button:text-is('Nam')").first.click()
        page.wait_for_timeout(300)

        # Đọc React state qua input values
        state = page.evaluate("""() => {
            const h = document.querySelector("input[placeholder*='chiều cao']");
            const w = document.querySelector("input[placeholder*='cân nặng']");
            return {
                h_value: h ? h.value : 'NOT FOUND',
                w_value: w ? w.value : 'NOT FOUND',
            };
        }""")
        print(f"   Sau fill - h={state['h_value']}, w={state['w_value']}")

        print("5. Click submit (JS)...")
        page.evaluate("""() => {
            const btn = document.querySelector("button[class*='EC4899']");
            if (btn) btn.click();
            return btn ? 'clicked' : 'NOT FOUND';
        }""")

        print("6. Chờ 3s để AI process...")
        page.wait_for_timeout(3000)

        # Dump full popup text AFTER submit
        after = page.evaluate("""() => {
            for (const d of document.querySelectorAll('div[class*="fixed"]')) {
                if (d.innerText.includes('Gợi Ý Size')) return d.innerText;
            }
            return 'POPUP NOT FOUND';
        }""")
        print(f"\n=== POPUP TEXT AFTER SUBMIT ===\n{after[:1000]}\n")

        # Tìm kết quả
        import re
        m = re.search(r'Size hoàn hảo dành cho bạn là:\s*\n\s*([^\n]+)', after)
        print(f"Regex match: {m.group(1) if m else 'NO MATCH'}")

        # Thử method 2: Playwright locator fill
        print("\n--- Method 2: Playwright .fill() ---")
        page.goto(f"{BASE_URL}/product/{SLUG}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        page.locator("button:has-text('Mua ngay')").first.click()
        page.wait_for_timeout(1500)
        page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button')];
            const link = btns.find(b => b.innerText.trim() === 'Gợi ý size' && b.className.includes('12px'));
            if (link) link.click();
        }""")
        page.wait_for_timeout(1500)

        page.locator("button:text-is('Nam')").first.click()
        page.wait_for_timeout(300)

        h2 = page.locator("input[placeholder*='chiều cao']").first
        w2 = page.locator("input[placeholder*='cân nặng']").first
        h2.click()
        h2.fill("170")
        page.wait_for_timeout(100)
        w2.click()
        w2.fill("65")
        page.wait_for_timeout(300)

        vals2 = page.evaluate("""() => {
            const h = document.querySelector("input[placeholder*='chiều cao']");
            const w = document.querySelector("input[placeholder*='cân nặng']");
            return `h=${h?.value}, w=${w?.value}`;
        }""")
        print(f"   After .fill(): {vals2}")

        page.evaluate("() => { const b = document.querySelector(\"button[class*='EC4899']\"); if(b) b.click(); }")
        page.wait_for_timeout(3000)

        after2 = page.evaluate("""() => {
            for (const d of document.querySelectorAll('div[class*="fixed"]')) {
                if (d.innerText.includes('Gợi Ý Size')) return d.innerText;
            }
            return 'POPUP NOT FOUND';
        }""")
        print(f"\n=== AFTER .fill() SUBMIT ===\n{after2[:1000]}\n")

        page.wait_for_timeout(2000)
        ctx.close()
        browser.close()

if __name__ == "__main__":
    main()
