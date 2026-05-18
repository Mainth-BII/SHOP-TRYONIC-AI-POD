"""Script inspect color swatches DOM trên product detail page."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

ENV_URL = 'https://test.shop.tryonic.ai'
SLUG = 'ao-phong-nang-dong'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f'{ENV_URL}/product/{SLUG}')
    page.wait_for_timeout(3000)

    print("=== ALL BUTTONS with aria-label or title ===")
    buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button[aria-label], button[title]')).map(el => ({
            ariaLabel: el.getAttribute('aria-label'),
            title: el.getAttribute('title'),
            text: el.innerText.trim().substring(0, 30),
            className: el.className.substring(0, 100),
            rect: (() => { const r = el.getBoundingClientRect(); return {w: Math.round(r.width), h: Math.round(r.height)}; })(),
            offsetParent: el.offsetParent !== null
        }));
    }""")
    for b in buttons:
        print(b)

    print("\n=== COLOR-RELATED parent elements ===")
    parents = page.evaluate("""() => {
        const kws = ['color', 'swatch', 'Color', 'Swatch', 'picker', 'mau', 'variant'];
        const results = [];
        for (const kw of kws) {
            const els = document.querySelectorAll(`[class*='${kw}']`);
            for (const el of els) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0) {
                    results.push({
                        tag: el.tagName,
                        className: el.className.substring(0, 100),
                        children: el.children.length
                    });
                }
            }
        }
        return results;
    }""")
    for p_el in parents[:20]:
        print(p_el)

    print("\n=== SMALL BUTTONS (likely swatches, w<60 h<60) ===")
    small_btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.width < 60 && r.height > 0 && r.height < 60;
        }).map(el => ({
            ariaLabel: el.getAttribute('aria-label'),
            title: el.getAttribute('title'),
            text: el.innerText.trim().substring(0, 20),
            className: el.className.substring(0, 100),
            rect: (() => { const r = el.getBoundingClientRect(); return {w: Math.round(r.width), h: Math.round(r.height)}; })()
        }));
    }""")
    for b in small_btns:
        print(b)

    browser.close()
