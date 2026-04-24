# Order Data Capture & Verify Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ghi lại thông số đơn hàng trong luồng test và verify lại toàn bộ trên màn hình chi tiết đơn hàng sau khi đơn được tạo thành công.

**Architecture:** Thêm 6 phương thức đọc dữ liệu vào 2 Page Object hiện có (StudioPage, CheckoutPage), thêm `verify_order_data` vào CheckoutPage, cập nhật CRITICAL_001 và CRITICAL_002 để capture và verify. Không tạo file mới, không thay đổi CRITICAL_003.

**Tech Stack:** Python · Playwright sync API · pytest · JavaScript DOM evaluation qua `page.evaluate()`

---

### Task 1: Thêm `read_panel_image_src` và `read_library_image_src` vào StudioPage

**Files:**
- Modify: `tests/pages/studio_page.py` — thêm 2 method vào cuối class (sau `wait_for_generation`)

- [ ] **Step 1: Thêm hai method vào `tests/pages/studio_page.py`**

Mở file, tìm method `wait_for_generation` (dòng cuối cùng của class), thêm ngay sau:

```python
    def read_panel_image_src(self, index: int) -> str | None:
        """Đọc src của artwork tại `index` trong left panel, skip 'Thêm ảnh' card (+1 offset)."""
        try:
            return self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index + 1}];  // +1 to skip 'Thêm ảnh'
                return target ? target.src : null;
            }}""")
        except Exception:
            return None

    def read_library_image_src(self, index: int) -> str | None:
        """Đọc src của ảnh thư viện tại `index` trong left panel (không skip)."""
        try:
            return self.page.evaluate(f"""() => {{
                const imgs = Array.from(document.querySelectorAll('img[src]')).filter(img => {{
                    const rect = img.getBoundingClientRect();
                    return rect.left < 330 && rect.width > 30 && rect.height > 30
                           && img.complete && img.naturalWidth > 0;
                }});
                const target = imgs[{index}];
                return target ? target.src : null;
            }}""")
        except Exception:
            return None
```

- [ ] **Step 2: Verify không có lỗi cú pháp**

```
cd d:\TEST_STUDIO\shop_tryonic_ai
python -c "from tests.pages.studio_page import StudioPage; print('OK')"
```

Expected: `OK`

---

### Task 2: Thêm 4 phương thức đọc dữ liệu vào CheckoutPage

**Files:**
- Modify: `tests/pages/checkout_page.py` — thêm 4 method vào cuối section `# ── Actions ──`

- [ ] **Step 1: Thêm 4 method vào `tests/pages/checkout_page.py`**

Tìm method `enter_prompt_and_wait_for_generation` (method cuối cùng), thêm 4 method mới ngay TRƯỚC nó:

```python
    def read_price_from_page(self) -> str | None:
        """Regex \\d+[,.]\\d+\\s*₫ trên document.body.innerText. Trả về match đầu tiên."""
        try:
            return self.page.evaluate(r"""() => {
                const text = document.body.innerText || '';
                const match = text.match(/\d+[,.]\d+\s*₫/);
                return match ? match[0] : null;
            }""")
        except Exception:
            return None

    def read_address_from_checkout(self) -> str | None:
        """Đọc input[name*='address'].value hoặc text từ [class*='address'] section."""
        try:
            return self.page.evaluate("""() => {
                const inp = document.querySelector(
                    'input[name*="address"], textarea[name*="address"]'
                );
                if (inp && inp.value) return inp.value;
                const section = document.querySelector('[class*="address"]');
                return section ? section.innerText.trim() : null;
            }""")
        except Exception:
            return None

    def read_order_code(self) -> str | None:
        """URL param ?orderCode=POD-... fallback regex POD-\\d{8}-\\d+ trong page text."""
        try:
            return self.page.evaluate(r"""() => {
                const params = new URLSearchParams(window.location.search);
                const fromUrl = params.get('orderCode');
                if (fromUrl && fromUrl.startsWith('POD-')) return fromUrl;
                const text = document.body.innerText || '';
                const match = text.match(/POD-\d{8}-\d+/);
                return match ? match[0] : null;
            }""")
        except Exception:
            return None

    def read_product_type(self) -> str | None:
        """Heading h1/h2/h3 chứa keyword áo|shirt|thun (case-insensitive)."""
        try:
            return self.page.evaluate(r"""() => {
                const headings = document.querySelectorAll('h1, h2, h3');
                for (const h of headings) {
                    if (/áo|shirt|thun/i.test(h.innerText)) return h.innerText.trim();
                }
                return null;
            }""")
        except Exception:
            return None
```

- [ ] **Step 2: Verify không có lỗi cú pháp**

```
python -c "from tests.pages.checkout_page import CheckoutPage; print('OK')"
```

Expected: `OK`

---

### Task 3: Thêm `verify_order_data` vào CheckoutPage

**Files:**
- Modify: `tests/pages/checkout_page.py` — thêm sau 4 method vừa thêm ở Task 2

- [ ] **Step 1: Thêm method `verify_order_data`**

Thêm ngay sau `read_product_type`, trước `enter_prompt_and_wait_for_generation`:

```python
    def verify_order_data(self, order_data: dict, tc_id: str) -> None:
        """Verify từng field trong order_data trên trang chi tiết đơn hàng."""
        import re
        page_text = self.page.evaluate("() => document.body.innerText || ''")

        # order_code: exact string — FAIL nếu sai
        order_code = order_data.get("order_code")
        if order_code:
            assert order_code in page_text, \
                f"LỖI verify {tc_id}: Mã đơn '{order_code}' không tìm thấy trong trang chi tiết"

        # size: exact string — FAIL + format warning nếu sai
        size = order_data.get("size")
        if size:
            if size not in page_text:
                size_variants = [f"Size {size}", f"size {size}", f"SIZE {size}"]
                found_variant = next((v for v in size_variants if v in page_text), None)
                if found_variant:
                    print(f"  ⚠ Format size không nhất quán: captured `{size}`, "
                          f"page hiện `{found_variant}` — cần đồng nhất")
                assert False, \
                    f"LỖI verify {tc_id}: Size '{size}' không tìm thấy trong trang chi tiết"

        # unit_price: digits-only compare — WARN nếu sai
        unit_price = order_data.get("unit_price")
        if unit_price:
            digits_captured = re.sub(r"[^\d]", "", unit_price)
            page_digits = re.sub(r"[^\d]", "", page_text)
            if digits_captured and digits_captured not in page_digits:
                print(f"  [WARN] verify {tc_id}: unit_price mismatch — captured '{unit_price}'")

        # total_price: digits-only compare — WARN nếu sai
        total_price = order_data.get("total_price")
        if total_price:
            digits_captured = re.sub(r"[^\d]", "", total_price)
            page_digits = re.sub(r"[^\d]", "", page_text)
            if digits_captured and digits_captured not in page_digits:
                print(f"  [WARN] verify {tc_id}: total_price mismatch — captured '{total_price}'")

        # address, artwork_front_src, artwork_back_src, product_type: INFO log only
        for field in ("address", "artwork_front_src", "artwork_back_src", "product_type"):
            val = order_data.get(field)
            if val:
                print(f"  [INFO] verify {tc_id}: {field} = '{str(val)[:80]}'")
```

- [ ] **Step 2: Verify không có lỗi cú pháp**

```
python -c "from tests.pages.checkout_page import CheckoutPage; print('OK')"
```

Expected: `OK`

---

### Task 4: Cập nhật CRITICAL_001 — init order_data và capture points

**Files:**
- Modify: `tests/production/test_critical_flows.py`

Context:
- Line 100: `print(f"\n  [INFO] CRITICAL_001: Prompt hôm nay = ...")`
- Line 145–153: S4 block (click artwork index=0)
- Line 164: `lib_ok = self.studio.click_library_image(index=2)` (S5b)
- Line 197: `print("  [PASS] S7a: ...")`
- Line 217: `print("  [PASS] S7c: ...")`

- [ ] **Step 1: Thêm `order_data` init sau dòng 100**

Tìm đoạn:
```python
        print(f"\n  [INFO] CRITICAL_001: Prompt hôm nay = '{prompt[:60]}...'")

        # ── S0: Đăng nhập ────────────────────────────────────────────────────
```

Thay bằng:
```python
        print(f"\n  [INFO] CRITICAL_001: Prompt hôm nay = '{prompt[:60]}...'")
        order_data = {"color": "Trắng", "size": "M"}

        # ── S0: Đăng nhập ────────────────────────────────────────────────────
```

- [ ] **Step 2: Capture `artwork_front_src` trước S4**

Tìm đoạn:
```python
        # ── S4: Studio — Click ảnh đầu tiên để áp lên áo ────────────────────
        applied = self.studio.click_artwork(index=0)
```

Thay bằng:
```python
        # ── S4: Studio — Click ảnh đầu tiên để áp lên áo ────────────────────
        order_data["artwork_front_src"] = self.studio.read_panel_image_src(0)
        applied = self.studio.click_artwork(index=0)
```

- [ ] **Step 3: Capture `artwork_back_src` sau S5b library click**

Tìm đoạn:
```python
            lib_ok = self.studio.click_library_image(index=2)
            # Chờ canvas render ảnh lên mặt sau áo (4s)
```

Thay bằng:
```python
            lib_ok = self.studio.click_library_image(index=2)
            order_data["artwork_back_src"] = self.studio.read_library_image_src(2)
            # Chờ canvas render ảnh lên mặt sau áo (4s)
```

- [ ] **Step 4: Capture `product_type` và `unit_price` sau S7a**

Tìm đoạn:
```python
        print(f"  [PASS] S7a: Màn hình Đặt hàng — URL: {page.url}")

        # ── S7b: Chọn size M ─────────────────────────────────────────────────
```

Thay bằng:
```python
        print(f"  [PASS] S7a: Màn hình Đặt hàng — URL: {page.url}")
        order_data["product_type"] = self.checkout.read_product_type()
        order_data["unit_price"] = self.checkout.read_price_from_page()

        # ── S7b: Chọn size M ─────────────────────────────────────────────────
```

- [ ] **Step 5: Capture `total_price` và `address` sau S7c**

Tìm đoạn:
```python
        print("  [PASS] S7c: Click 'Mua ngay' → tới trang thanh toán thành công")

        # ── S8: Checkout — Điền MST → Click Thanh toán → Assert QR ─────────────
```

Thay bằng:
```python
        print("  [PASS] S7c: Click 'Mua ngay' → tới trang thanh toán thành công")
        order_data["total_price"] = self.checkout.read_price_from_page()
        order_data["address"] = self.checkout.read_address_from_checkout()

        # ── S8: Checkout — Điền MST → Click Thanh toán → Assert QR ─────────────
```

---

### Task 5: Cập nhật CRITICAL_001 — thêm S9–S13 (cancel → verify)

**Files:**
- Modify: `tests/production/test_critical_flows.py`

Context: Dòng 237–238 hiện tại là 2 dòng print kết thúc CRITICAL_001.

- [ ] **Step 1: Thay 2 dòng print cuối CRITICAL_001 bằng S9–S13**

Tìm đoạn (cuối test_CRITICAL_001):
```python
        self.studio.shot("CRITICAL_001", "15", "qr_code_displayed", domain=_D, root=_R)
        print("  [PASS] S8c: QR code thanh toán hiển thị thành công")
        print("  [PASS] CRITICAL_001: Toàn bộ luồng checkout hoàn thành")
```

Thay bằng:
```python
        self.studio.shot("CRITICAL_001", "15", "qr_code_displayed", domain=_D, root=_R)
        print("  [PASS] S8c: QR code thanh toán hiển thị thành công")

        # ── S9: Click nút Hủy trên trang QR ─────────────────────────────────
        cancel_qr = page.locator("button:has-text('Huỷ'), button:has-text('Hủy')").first
        assert cancel_qr.is_visible(timeout=10000), \
            f"LỖI S9: Không tìm thấy nút 'Hủy' trên trang QR — URL: {page.url}"
        cancel_qr.click()
        page.wait_for_timeout(1500)

        # ── S10: Xác nhận hủy — capture order_code từ URL redirect ──────────
        confirm_cancel = page.locator("#cancel-payment, button:has-text('Xác nhận hủy')").first
        if confirm_cancel.is_visible(timeout=5000):
            confirm_cancel.click()
            page.wait_for_timeout(5000)
        self.studio.shot("CRITICAL_001", "16", "after_cancel", domain=_D, root=_R)
        assert "pay" not in page.url, \
            f"LỖI S10: Hủy thanh toán thất bại — vẫn ở trang payOS — URL: {page.url}"
        order_data["order_code"] = self.checkout.read_order_code()
        print(f"  [PASS] S10: Hủy thanh toán thành công — URL: {page.url}")
        print(f"  [INFO] CRITICAL_001 order_data tại S10: {order_data}")

        # ── S11: Click "Xem đơn hàng" (fallback navigate /profile) ──────────
        view_order = page.locator(
            "button:has-text('Xem đơn hàng'), a:has-text('Xem đơn hàng')"
        ).first
        if view_order.is_visible(timeout=5000):
            view_order.click()
            page.wait_for_timeout(3000)
        else:
            self.home.goto("/profile")
            page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "17", "view_orders", domain=_D, root=_R)
        print(f"  [PASS] S11: Xem đơn hàng — URL: {page.url}")

        # ── S12: Click "Đơn hàng của tôi" tab ───────────────────────────────
        my_orders = page.locator("button:has-text('Đơn hàng của tôi')").first
        assert my_orders.is_visible(timeout=5000), \
            f"LỖI S12: Không tìm thấy tab 'Đơn hàng của tôi' — URL: {page.url}"
        my_orders.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "18", "my_orders", domain=_D, root=_R)
        print("  [PASS] S12: Tab 'Đơn hàng của tôi'")

        # ── S13: Click đơn đầu tiên → verify_order_data ──────────────────────
        first_order = page.locator("main div:nth-of-type(1) button").first
        assert first_order.is_visible(timeout=5000), \
            f"LỖI S13: Không tìm thấy đơn hàng nào — URL: {page.url}"
        first_order.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_001", "19", "order_detail", domain=_D, root=_R)
        self.checkout.verify_order_data(order_data, "CRITICAL_001")
        print("  [PASS] S13: Chi tiết đơn hàng — verify hoàn thành")
        print("  [PASS] CRITICAL_001: Toàn bộ luồng checkout hoàn thành")
```

---

### Task 6: Cập nhật CRITICAL_002 — init order_data, capture points, verify tại S15

**Files:**
- Modify: `tests/production/test_critical_flows.py`

Context:
- Line 249: `prompt = _load_daily_prompt()`
- Line 281: `applied_s3 = self.studio.click_artwork(index=1)` (S3)
- Line 289: `if self.studio.back_button.is_visible(timeout=3000):` (S4 start)
- Line 323: `print("  [PASS] S6: ...")`
- Line 361: `print(f"  [PASS] S9: ...")`
- Line 483: `print(f"  [PASS] S13: Xem đơn hàng — URL: {page.url}")`
- Line 500: `self.studio.shot("CRITICAL_002", "15", "order_detail", ...)`

- [ ] **Step 1: Init `order_data` sau `prompt = _load_daily_prompt()`**

Tìm đoạn:
```python
        prompt = _load_daily_prompt()

        # Pre-check: credentials needed for login at checkout
```

Thay bằng:
```python
        prompt = _load_daily_prompt()
        order_data = {"size": "4XL"}

        # Pre-check: credentials needed for login at checkout
```

- [ ] **Step 2: Capture `artwork_front_src` trước S3**

Tìm đoạn:
```python
        # ── S3: Click Variant 2 → Apply lên mặt trước ───────────────────────
        applied_s3 = self.studio.click_artwork(index=1)
```

Thay bằng:
```python
        # ── S3: Click Variant 2 → Apply lên mặt trước ───────────────────────
        order_data["artwork_front_src"] = self.studio.read_panel_image_src(1)
        applied_s3 = self.studio.click_artwork(index=1)
```

- [ ] **Step 3: Capture `artwork_back_src` trước S4 click**

Tìm đoạn:
```python
        # ── S4: Xoay áo → Click Variant 1 cho mặt sau ───────────────────────
        if self.studio.back_button.is_visible(timeout=3000):
            self.studio.toggle_side("back")
            page.wait_for_timeout(1500)
            self.studio.click_artwork(index=0)
```

Thay bằng:
```python
        # ── S4: Xoay áo → Click Variant 1 cho mặt sau ───────────────────────
        order_data["artwork_back_src"] = self.studio.read_panel_image_src(0)
        if self.studio.back_button.is_visible(timeout=3000):
            self.studio.toggle_side("back")
            page.wait_for_timeout(1500)
            self.studio.click_artwork(index=0)
```

- [ ] **Step 4: Capture `product_type` và `unit_price` sau S6**

Tìm đoạn:
```python
        print(f"  [PASS] S6: Màn hình đặt hàng — URL: {page.url}")

        # ── S7: Chọn size 4XL ────────────────────────────────────────────────
```

Thay bằng:
```python
        print(f"  [PASS] S6: Màn hình đặt hàng — URL: {page.url}")
        order_data["product_type"] = self.checkout.read_product_type()
        order_data["unit_price"] = self.checkout.read_price_from_page()

        # ── S7: Chọn size 4XL ────────────────────────────────────────────────
```

- [ ] **Step 5: Capture `total_price` và `address` sau S9**

Tìm đoạn:
```python
        print(f"  [PASS] S9: Checkout — URL: {page.url}")

        # ── S10: Login tại Checkout ──────────────────────────────────────────
```

Thay bằng:
```python
        print(f"  [PASS] S9: Checkout — URL: {page.url}")
        order_data["total_price"] = self.checkout.read_price_from_page()
        order_data["address"] = self.checkout.read_address_from_checkout()

        # ── S10: Login tại Checkout ──────────────────────────────────────────
```

- [ ] **Step 6: Capture `order_code` sau S13**

Tìm đoạn:
```python
        print(f"  [PASS] S13: Xem đơn hàng — URL: {page.url}")

        # ── S14: Click "Đơn hàng của tôi" ───────────────────────────────────
```

Thay bằng:
```python
        print(f"  [PASS] S13: Xem đơn hàng — URL: {page.url}")
        order_data["order_code"] = self.checkout.read_order_code()

        # ── S14: Click "Đơn hàng của tôi" ───────────────────────────────────
```

- [ ] **Step 7: Thêm `verify_order_data` tại S15**

Tìm đoạn:
```python
        first_order.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "15", "order_detail", domain=_D, root=_R)
        print("  [PASS] S15: Chi tiết đơn hàng")
```

Thay bằng:
```python
        first_order.click()
        page.wait_for_timeout(2000)
        self.studio.shot("CRITICAL_002", "15", "order_detail", domain=_D, root=_R)
        self.checkout.verify_order_data(order_data, "CRITICAL_002")
        print(f"  [INFO] order_data: {order_data}")
        print("  [PASS] S15: Chi tiết đơn hàng — verify hoàn thành")
```

---

### Task 7: Chạy test để verify

- [ ] **Step 1: Chạy CRITICAL_001**

```powershell
$env:PYTHONIOENCODING = "utf-8"
cd d:\TEST_STUDIO\shop_tryonic_ai
python -m pytest tests/production/test_critical_flows.py::TestCriticalFlows::test_CRITICAL_001_full_journey_to_checkout -v --env=test --headed -s 2>&1 | tail -30
```

Expected: `PASSED` — in ra `[PASS] S13: Chi tiết đơn hàng — verify hoàn thành`

- [ ] **Step 2: Chạy CRITICAL_002**

```powershell
python -m pytest tests/production/test_critical_flows.py::TestCriticalFlows::test_CRITICAL_002_add_to_cart_and_repay -v --env=test --headed -s 2>&1 | tail -30
```

Expected: `PASSED` — in ra `[INFO] order_data: {...}` với đủ fields

- [ ] **Step 3: Commit**

```bash
git add tests/pages/studio_page.py tests/pages/checkout_page.py tests/production/test_critical_flows.py
git commit -m "feat: capture & verify order data in CRITICAL_001 and CRITICAL_002"
```
