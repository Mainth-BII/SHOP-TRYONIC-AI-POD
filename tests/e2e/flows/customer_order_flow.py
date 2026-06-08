"""Flow: khách đặt 1 đơn COD trên TEST → trả (order_code, total).

Orchestrate các page object khách (detail/studio/checkout). KHÓA env=test.
"""
from __future__ import annotations
from urllib.parse import urlparse, parse_qs

from e2e._shots import shot

_SLUG = "ao-phong-ca-tinh"
_COLOR = "Trắng"
_SIZE = "M"


def place_cod_order(t, tc: str = "e2e") -> dict:
    """`t` = test instance (đã có self.detail/studio/checkout/page/env + _login()).

    Trả dict: {code, total, payment_method, url}.
    """
    assert t.env.name == "test", f"🚫 E2E chỉ chạy TEST, đang {t.env.name}"
    p = t.page

    t._login()
    shot(p, "cust_01_logged_in")
    t.detail.navigate(_SLUG)
    p.wait_for_timeout(1_000)
    t.detail.select_color(_COLOR)
    p.wait_for_timeout(800)
    shot(p, "cust_02_product_detail")

    if not t.detail.click_thiet_ke_hinh_in():
        return {"code": None, "total": None, "payment_method": None, "url": p.url}
    p.wait_for_timeout(2_000)
    t.studio.accept_terms(tc)
    p.wait_for_timeout(1_000)
    t.studio.open_library()
    p.wait_for_timeout(1_000)
    t.studio.click_library_image(1)
    p.wait_for_timeout(1_500)
    shot(p, "cust_03_studio_design")

    t.studio.open_order_modal()
    try:
        p.wait_for_url("**/review", timeout=10_000)
    except Exception:
        p.wait_for_timeout(3_000)
    shot(p, "cust_04_review")

    try:
        b = p.locator("button:has-text('Đặt hàng')").first
        if b.is_visible(timeout=5_000):
            b.click()
            p.wait_for_timeout(2_000)
    except Exception:
        pass
    shot(p, "cust_05_order_popup")

    t.checkout.clear_cart()
    t.checkout.select_size_by_name(_SIZE)
    p.wait_for_timeout(800)
    if not t.checkout.click_them_vao_gio():
        return {"code": None, "total": None, "payment_method": None, "url": p.url}
    p.wait_for_timeout(2_000)

    t.checkout.open_cart_panel()
    shot(p, "cust_06_cart")
    if not t.checkout.click_checkout_from_cart():
        p.goto(f"{t.env.fe_url}/checkout")
    try:
        p.wait_for_url("**/checkout**", timeout=10_000)
    except Exception:
        p.wait_for_timeout(3_000)
    shot(p, "cust_07_checkout")

    try:
        t.checkout.fill_guest_shipping_info("QA Lifecycle", "0900000000",
                                            "123 Test, P1, Q1, HCM", tc)
    except Exception:
        pass

    for sel in ("label:has-text('Thanh toán khi nhận hàng')",
                "label:has-text('khi nhận hàng')", "label:has-text('COD')", ":text('COD')"):
        try:
            el = p.locator(sel).first
            if el.is_visible(timeout=1_500):
                el.click()
                break
        except Exception:
            continue
    p.wait_for_timeout(600)
    shot(p, "cust_08_cod_selected")

    if not t.checkout.click_checkout_payment():
        t.checkout.click_thanh_toan_ngay()
    try:
        p.wait_for_url("**/checkout/success**", timeout=15_000)
    except Exception:
        p.wait_for_timeout(4_000)
    shot(p, "cust_09_order_success")

    url = p.url
    qs = parse_qs(urlparse(url).query)
    code = (qs.get("orderCode") or [None])[0]
    total = (qs.get("total") or [None])[0]
    pay = (qs.get("paymentMethod") or [None])[0]
    if not code:
        try:
            code = t.checkout.read_order_code()
        except Exception:
            code = None
    return {
        "code": code,
        "total": int(total) if total else None,
        "payment_method": pay,
        "url": url,
    }
