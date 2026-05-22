from __future__ import annotations
"""Shared helpers cho AI size recommendation popup tests."""
import json
import os
import re
from playwright.sync_api import Page

_CHARTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "data", "size_charts.json",
)


def _in_range(value: int, range_str: str) -> bool:
    """Kiểm tra value có nằm trong range '<N' hoặc 'N-M' không."""
    if range_str.startswith("<"):
        return value < int(range_str[1:])
    parts = range_str.split("-")
    if len(parts) == 2:
        return int(parts[0]) <= value <= int(parts[1])
    return False


def get_expected_size(product_code: str, height: int, weight: int) -> str | None:
    """Tra cứu size kỳ vọng từ size_charts.json theo chiều cao và cân nặng.

    Trả về tên size (vd: 'M', 'L', '120') hoặc None nếu ngoài bảng.
    """
    with open(_CHARTS_PATH, encoding="utf-8") as f:
        charts = json.load(f)
    if product_code not in charts:
        return None
    for size, spec in charts[product_code]["chart"].items():
        if _in_range(height, spec["chieu_cao"]) and _in_range(weight, spec["can_nang"]):
            return size
    return None

# AI popup: bg-black/40 (buy-now popup dùng bg-black/30 — phân biệt qua opacity)
AI_POPUP_SEL = "div[class*='bg-black\\/40']"

# Submit button màu hồng bên trong AI popup
_SUBMIT_BTN_SEL = "button[class*='EC4899']"


def open_ai_size_popup(page: Page, base_url: str, slug: str) -> bool:
    """Điều hướng đến product page → Mua ngay → click Gợi ý size."""
    try:
        page.goto(f"{base_url}/product/{slug}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        page.locator("button:has-text('Mua ngay'), button:has-text('Mua Ngay')").first.click()
        page.wait_for_timeout(1500)

        # Click "Gợi ý size" link (link text nhỏ dạng text, không phải submit button EC4899)
        clicked = page.evaluate("""() => {
            const btns = [...document.querySelectorAll('button')];
            // Ưu tiên tìm theo text chính xác, bỏ qua submit button (bg-[#EC4899])
            const link = btns.find(b =>
                b.innerText.trim() === 'Gợi ý size'
                && !b.className.includes('EC4899')
            );
            if (link) { link.click(); return true; }
            // Debug: log tên các button nếu không tìm được
            console.log('[DEBUG] buttons:', btns.map(b => JSON.stringify({t: b.innerText.trim().slice(0,30), c: b.className.slice(0,60)})));
            return false;
        }""")
        if not clicked:
            # Thử lại với Playwright locator trực tiếp
            try:
                page.locator("button", has_text="Gợi ý size").first.click(timeout=3000)
                clicked = True
            except Exception:
                pass
        if not clicked:
            return False
        page.wait_for_timeout(1500)

        return page.locator(AI_POPUP_SEL).first.is_visible(timeout=3000)
    except Exception:
        return False


def _fill_react(locator, value: str) -> None:
    """Điền giá trị vào React controlled input bằng keyboard typing.

    .fill() không trigger React onChange; press_sequentially gửi keystroke
    thật nên React nhận đúng giá trị qua onKeyDown/onKeyUp/onChange.
    """
    locator.click()
    locator.press("Control+a")
    locator.press_sequentially(value, delay=50)


def submit_recommendation(page: Page, gender: str, height: int | None, weight: int | None) -> None:
    """Điền form AI size recommendation và click submit."""
    if gender:
        page.locator(f"button:text-is('{gender}')").first.click()
        page.wait_for_timeout(300)

    h_input = page.locator("input[placeholder*='chiều cao']").first
    w_input = page.locator("input[placeholder*='cân nặng']").first

    if h_input.is_visible(timeout=2000):
        if height is not None:
            _fill_react(h_input, str(height))
        else:
            h_input.clear()

    if w_input.is_visible(timeout=2000):
        if weight is not None:
            _fill_react(w_input, str(weight))
        else:
            w_input.clear()

    page.wait_for_timeout(300)

    # Tìm submit button bằng nội dung text "Gợi ý size" bên trong AI popup
    # (tránh nhầm với gender button có bg-[#EC4899] khi selected)
    page.evaluate("""() => {
        const popup = [...document.querySelectorAll('div[class*="fixed"]')]
            .find(d => d.innerText.includes('G\\u1ee3i \\u00dd Size B\\u1eb1ng AI'));
        if (!popup) return;
        const btn = [...popup.querySelectorAll('button')]
            .find(b => b.innerText.trim() === 'G\\u1ee3i \\u00fd size');
        if (btn) btn.click();
    }""")

    # Chờ result xuất hiện (tối đa 10s)
    try:
        page.wait_for_function(
            """() => {
                for (const d of document.querySelectorAll('div[class*="fixed"]')) {
                    if (d.innerText.includes('ho\\u00e0n h\\u1ea3o')) return true;
                }
                return false;
            }""",
            timeout=10000,
        )
    except Exception:
        pass  # timeout — result không xuất hiện


def read_recommended_size(page: Page) -> str | None:
    """Đọc size được gợi ý từ kết quả. Trả về chuỗi size hoặc None."""
    try:
        text = page.evaluate("""() => {
            // Tìm AI popup bằng nội dung (tránh nhầm với backdrop buy-now)
            for (const div of document.querySelectorAll('div[class*="fixed"]')) {
                const t = div.innerText || '';
                if (t.includes('Gợi Ý Size Bằng AI') || t.includes('hoàn hảo')) {
                    return t;
                }
            }
            return '';
        }""")
        m = re.search(r'Size hoàn hảo dành cho bạn là:\s*\n\s*([^\n]+)', text)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return None


def is_result_displayed(page: Page) -> bool:
    return read_recommended_size(page) is not None


def read_popup_message(page: Page) -> str | None:
    """Đọc thông báo validation/lỗi từ popup sau khi submit thiếu dữ liệu.

    Ưu tiên tìm element có class *red*, [role=alert], *error* bên trong popup.
    Trả về None nếu popup đang hiển thị kết quả thành công.
    """
    try:
        msg = page.evaluate("""() => {
            const STATIC = new Set([
                'G\\u1ee3i \\u00dd Size B\\u1eb1ng AI', 'Nam', 'N\\u1EEF',
                'G\\u1ee3i \\u00fd size', 'b\\u1ea3ng size t\\u1ea1i \\u0111\\u00e2y'
            ]);
            for (const pop of document.querySelectorAll('div[class*="fixed"]')) {
                const t = (pop.innerText || '').trim();
                if (!t.includes('G\\u1ee3i \\u00dd Size B\\u1eb1ng AI')) continue;
                if (t.includes('ho\\u00e0n h\\u1ea3o')) return '';   // success — không phải error
                // Ưu tiên tìm element có class red/error/alert
                for (const el of pop.querySelectorAll(
                    '[class*="red-"], [class*="text-red"], [role="alert"], [class*="error"]'
                )) {
                    const txt = el.innerText.trim();
                    if (txt && txt.length > 2) return txt;
                }
                // Fallback: tìm <p> không phải static, không phải disclaimer "tham khảo"
                for (const el of pop.querySelectorAll('p')) {
                    const txt = el.innerText.trim();
                    if (txt && txt.length > 5 && !STATIC.has(txt)
                        && !txt.includes('tham khảo')) return txt;
                }
                return '';
            }
            return '';
        }""")
        return msg.strip() or None
    except Exception:
        pass
    return None


def click_bang_size(page: Page) -> None:
    """Click 'bảng size tại đây' button (indigo text, mở size chart)."""
    page.evaluate("""() => {
        const btn = document.querySelector("button[class*='indigo']");
        if (btn && btn.innerText.includes('bảng')) btn.click();
    }""")
    page.wait_for_timeout(1000)


def click_chon_size(page: Page) -> bool:
    """Click button 'Chọn Size X' để áp dụng size được gợi ý."""
    try:
        btn = page.locator("button:has-text('Chọn Size')").first
        if btn.is_visible(timeout=2000):
            btn.click()
            page.wait_for_timeout(800)
            return True
    except Exception:
        pass
    return False
