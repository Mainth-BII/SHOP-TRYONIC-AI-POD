# MH10 Admin Order Verification — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nối thêm bước MH10 Admin vào cuối `test_full_price_flow_mua_ngay` — sau khi tạo đơn xong, navigate sang Admin panel, login, tìm đơn hàng và verify toàn bộ thông tin.

**Architecture:** Inline trong test method (không tạo Page Object mới). Credentials admin lưu trong `.env` / `environments.py`. `order_code` extract từ URL ở MH6. Đọc data dùng `page.evaluate(innerText)`, actions dùng Playwright locator linh hoạt.

**Tech Stack:** Python, Playwright, pytest, `page.evaluate` JS inline.

---

## File Map

| File | Thay đổi |
|------|----------|
| `.env.example` | Thêm `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| `.env` | Thêm giá trị thật (không commit) |
| `tests/config/environments.py` | Thêm `admin_email`, `admin_password` vào `Environment` dataclass và cả 2 instances TEST/PROD |
| `tests/production/test_pt01_trang_full_price_flow.py` | (1) Cập nhật `_MH_NAMES` MH10, (2) capture `order_code` từ URL MH6, (3) thêm khối MH10 Admin sau `_print_summary_table()` |

---

## Task 1: Thêm admin credentials vào config

**Files:**
- Modify: `.env.example`
- Modify: `.env`
- Modify: `tests/config/environments.py`

- [ ] **Step 1: Thêm vào `.env.example`**

Mở `.env.example`, thêm vào cuối file (sau block GOOGLE):

```
# Admin panel credentials — dùng cho MH10 Admin verify
ADMIN_EMAIL=your_admin_email@example.com
ADMIN_PASSWORD=YourAdminPassword
```

- [ ] **Step 2: Thêm giá trị thật vào `.env`**

Mở `.env` (không commit), thêm credentials thật của admin account:

```
ADMIN_EMAIL=<email admin thật>
ADMIN_PASSWORD=<password admin thật>
```

- [ ] **Step 3: Cập nhật `Environment` dataclass**

Mở `tests/config/environments.py`. Thêm 2 field vào dataclass (sau `login_password`):

```python
@dataclass(frozen=True)
class Environment:
    """Holds all URLs and default credentials for a specific environment."""
    name: str
    fe_url: str
    api_url: str
    admin_url: str
    login_email: str = ""
    login_password: str = ""
    admin_email: str = ""        # ← thêm
    admin_password: str = ""     # ← thêm
```

- [ ] **Step 4: Truyền admin credentials vào TEST và PROD instances**

Trong cùng file `tests/config/environments.py`, cập nhật 2 instances:

```python
TEST = Environment(
    name="test",
    fe_url="https://test.shop.tryonic.ai",
    api_url="https://api.test.shop.tryonic.ai",
    admin_url="https://admin.test.shop.tryonic.ai",
    login_email=os.getenv("DAILY_TEST_EMAIL", ""),
    login_password=os.getenv("DAILY_TEST_PASSWORD", ""),
    admin_email=os.getenv("ADMIN_EMAIL", ""),       # ← thêm
    admin_password=os.getenv("ADMIN_PASSWORD", ""), # ← thêm
)

PROD = Environment(
    name="prod",
    fe_url="https://shop.tryonic.ai",
    api_url="https://api.shop.tryonic.ai",
    admin_url="https://admin.shop.tryonic.ai",
    login_email=os.getenv("PROD_EMAIL", ""),
    login_password=os.getenv("PROD_PASSWORD", ""),
    admin_email=os.getenv("ADMIN_EMAIL", ""),       # ← thêm
    admin_password=os.getenv("ADMIN_PASSWORD", ""), # ← thêm
)
```

- [ ] **Step 5: Verify import không vỡ**

```bash
python -c "from tests.config.environments import TEST, PROD; print(TEST.admin_email, PROD.admin_email)"
```

Expected: in ra 2 dòng (có thể rỗng nếu chưa set .env), không exception.

- [ ] **Step 6: Commit**

```bash
git add .env.example tests/config/environments.py
git commit -m "feat(config): add ADMIN_EMAIL/ADMIN_PASSWORD to Environment"
```

---

## Task 2: Capture `order_code` từ URL MH6 và cập nhật `_MH_NAMES`

**Files:**
- Modify: `tests/production/test_pt01_trang_full_price_flow.py`

- [ ] **Step 1: Cập nhật `_MH_NAMES`**

Trong class `TestPT01TrangFullPriceFlow`, tìm `_MH_NAMES` dict (khoảng line 168), đổi:

```python
_MH_NAMES = {
    "MH1": "Product Listing",
    "MH2": "Product Detail",
    "MH3": "Studio",
    "MH4": "Popup Mua ngay",
    "MH5": "Checkout",
    "MH6": "QR Code",
    "MH7": "Order (sau hủy QR)",
    "MH8": "Đơn hàng của tôi",
    "MH9": "Chi tiết đơn hàng",
    "MH10": "Admin — Chi tiết đơn",   # ← đổi từ "Giỏ hàng"
    "Login": "Đăng nhập",
}
```

- [ ] **Step 2: Capture `order_code` từ URL sau MH6**

Trong `test_full_price_flow_mua_ngay`, tìm dòng:
```python
print(f"  [INFO] MH6: URL sau hủy = {self.page.url}")
```

Thêm ngay bên dưới dòng đó:

```python
# Capture order_code từ URL — dùng cho MH10 Admin
_oc_match = re.search(r'orderCode=([\w-]+)', self.page.url)
order_code = _oc_match.group(1) if _oc_match else ""
print(f"  [INFO] MH6: order_code = {order_code}")
```

- [ ] **Step 3: Verify order_code được capture**

Chạy test với `-s` và grep output:

```bash
python -m pytest tests/production/test_pt01_trang_full_price_flow.py -k "mua_ngay" --env=test --headed --tb=short -s 2>&1 | grep "order_code"
```

Expected output (ví dụ):
```
[INFO] MH6: order_code = POD-20260504-025
```

- [ ] **Step 4: Commit**

```bash
git add tests/production/test_pt01_trang_full_price_flow.py
git commit -m "feat(test): capture order_code từ URL MH6, update MH10 name"
```

---

## Task 3: Thêm khối MH10 Admin vào cuối `test_full_price_flow_mua_ngay`

**Files:**
- Modify: `tests/production/test_pt01_trang_full_price_flow.py` (sau dòng `self._print_summary_table()`)

- [ ] **Step 1: Thêm khối MH10 Admin**

Tìm dòng `self._print_summary_table()` trong `test_full_price_flow_mua_ngay` (khoảng line 944), thêm khối sau đây ngay bên dưới:

```python
        # ════════════════════════════════════════════════════════════════════
        # MH10 — Admin: verify đơn hàng trên Admin panel
        # ════════════════════════════════════════════════════════════════════
        print(f"\n  ── MH10: Admin — Verify đơn hàng ────────────────────────")
        try:
            admin_email    = self.env.admin_email
            admin_password = self.env.admin_password
            admin_url      = self.env.admin_url  # https://admin.test.shop.tryonic.ai

            if not admin_email or not admin_password:
                self._record_check("MH10", "MH10 Admin login", "⚠️ WARN",
                                   "Thiếu credentials", "ADMIN_EMAIL / ADMIN_PASSWORD trong .env")
                print(f"  [WARN] MH10: Thiếu ADMIN_EMAIL/ADMIN_PASSWORD — bỏ qua MH10")
            elif not order_code:
                self._record_check("MH10", "MH10 Admin — tìm đơn", "⚠️ WARN",
                                   "order_code rỗng", "orderCode từ URL MH6")
                print(f"  [WARN] MH10: Không có order_code — bỏ qua MH10")
            else:
                # ── Bước 1: Navigate admin và login ──────────────────────
                self.page.goto(admin_url, wait_until="domcontentloaded", timeout=30_000)
                self.page.wait_for_timeout(2000)

                # Nếu có form login → điền credentials
                email_input = self.page.locator(
                    "input[type='email'], input[name='email'], input[placeholder*='mail' i]"
                ).first
                if email_input.is_visible(timeout=5000):
                    email_input.fill(admin_email)
                    self.page.locator(
                        "input[type='password'], input[name='password']"
                    ).first.fill(admin_password)
                    self.page.locator(
                        "button[type='submit'], button:has-text('Đăng nhập'), button:has-text('Login')"
                    ).first.click()
                    self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                    self.page.wait_for_timeout(2000)

                # Kiểm tra login thành công (không còn form login)
                still_login = self.page.locator(
                    "input[type='email'], input[type='password']"
                ).first.is_visible(timeout=3000)
                if still_login:
                    self._record_check("MH10", "MH10 Admin login", "⚠️ WARN",
                                       "Login thất bại", "Vẫn còn form login")
                    print(f"  [WARN] MH10: Admin login thất bại — bỏ qua verify")
                else:
                    self._record_check("MH10", "MH10 Admin login", "✅ PASS",
                                       "OK", "Đăng nhập thành công")
                    print(f"  [PASS] MH10: Admin login OK")
                    self._shot("MH10_1", "admin_order_list")

                    # ── Bước 2: Navigate trang đơn hàng + search ─────────
                    orders_url = admin_url.rstrip("/") + "/orders"
                    self.page.goto(orders_url, wait_until="domcontentloaded", timeout=30_000)
                    self.page.wait_for_timeout(2000)

                    # Tìm search box và nhập order_code
                    search_box = self.page.locator(
                        "input[placeholder*='tìm' i], input[placeholder*='Mã' i], "
                        "input[placeholder*='search' i], input[placeholder*='đơn' i], "
                        "input[type='search']"
                    ).first
                    if search_box.is_visible(timeout=5000):
                        search_box.fill(order_code)
                        search_box.press("Enter")
                        self.page.wait_for_timeout(2000)

                    self._shot("MH10_1", "admin_order_list")

                    # ── Bước 3: Click vào row chứa order_code ────────────
                    order_row = self.page.locator(
                        f"tr:has-text('{order_code}'), "
                        f"[data-order-code='{order_code}'], "
                        f"a:has-text('{order_code}')"
                    ).first
                    clicked_order = False
                    if order_row.is_visible(timeout=5000):
                        order_row.click()
                        self.page.wait_for_load_state("domcontentloaded", timeout=15_000)
                        self.page.wait_for_timeout(2000)
                        clicked_order = True
                        self._shot("MH10_2", "admin_order_detail")
                    else:
                        self._record_check("MH10", "MH10 Admin — tìm đơn", "⚠️ WARN",
                                           "Không tìm thấy", order_code)
                        print(f"  [WARN] MH10: Không tìm thấy order {order_code} trên admin")

                    if clicked_order:
                        # ── Bước 4: Đọc toàn bộ data từ trang detail ─────
                        admin_text = self.page.evaluate("() => document.body.innerText || ''")

                        def _parse_admin(text: str) -> dict:
                            """Trích xuất các field từ innerText trang admin order detail."""
                            import re as _re
                            result = {}
                            lines = [l.strip() for l in text.split('\n') if l.strip()]

                            # Mã đơn
                            m = _re.search(r'(POD-[\w-]+)', text)
                            result["order_code"] = m.group(1) if m else ""

                            # Trạng thái đơn hàng
                            for kw in ["Chờ xác nhận", "Đang xử lý", "Đã xác nhận",
                                       "Đang giao", "Hoàn thành", "Đã hủy"]:
                                if kw in text:
                                    result["trang_thai"] = kw
                                    break

                            # Trạng thái thanh toán
                            for kw in ["Chưa thanh toán", "Đã thanh toán", "Hoàn tiền"]:
                                if kw in text:
                                    result["thanh_toan"] = kw
                                    break

                            # Thông tin sản phẩm
                            for i, line in enumerate(lines):
                                if _re.search(r'Áo Phông|áo phông|T-Shirt|t-shirt', line, _re.I):
                                    result["ten_sp"] = line
                                    break

                            # Màu / Size / Số lượng — thường trên cùng dòng hoặc dòng kế
                            m = _re.search(r'(Trắng|Đen|Xanh|Đỏ|Hồng|Vàng|Xám|Nâu|Cam|Tím)', text, _re.I)
                            result["mau"] = m.group(1) if m else ""

                            m = _re.search(r'\b([XSML23456789XL]+)\b.*?\bx\s*(\d+)\b', text, _re.I)
                            if m:
                                result["size"] = m.group(1)
                                result["qty"] = int(m.group(2))
                            else:
                                m = _re.search(r'\b([XSML23456789XL]+)\b', text)
                                result["size"] = m.group(1) if m else ""
                                result["qty"] = None

                            # Email khách hàng
                            m = _re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
                            result["email"] = m.group(0) if m else ""

                            # Thông tin người nhận
                            m = _re.search(r'0\d{9,10}', text)
                            result["phone"] = m.group(0) if m else ""

                            # Giá — parse các số tiền lớn
                            amounts = _re.findall(r'(\d{1,3}(?:[.,]\d{3})+)\s*(?:đ|₫|vnd)?', text, _re.I)
                            unique_amounts = []
                            seen = set()
                            for a in amounts:
                                val = int(_re.sub(r'[^\d]', '', a))
                                if val not in seen and val >= 1000:
                                    seen.add(val)
                                    unique_amounts.append(val)

                            # Tìm subtotal, ship, total từ danh sách số tìm được
                            result["raw_amounts"] = unique_amounts
                            return result

                        admin_data = _parse_admin(admin_text)
                        print(f"  [INFO] MH10: admin_data = {admin_data}")

                        # ── Bước 5: Verify từng field ─────────────────────

                        # Mã đơn
                        if admin_data.get("order_code") and order_code in admin_data["order_code"]:
                            self._record_check("MH10", "MH10 Mã đơn hàng", "✅ PASS",
                                               admin_data["order_code"], order_code)
                            print(f"  [PASS] MH10 Mã đơn: '{admin_data['order_code']}'")
                        else:
                            self._record_check("MH10", "MH10 Mã đơn hàng", "⚠️ WARN",
                                               admin_data.get("order_code", "N/A"), order_code)
                            print(f"  [WARN] MH10: Không đọc được mã đơn")

                        # Trạng thái
                        if admin_data.get("trang_thai"):
                            ok = "xác nhận" in admin_data["trang_thai"].lower()
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Trạng thái đơn", status,
                                               admin_data["trang_thai"], "Chờ xác nhận")
                            print(f"  [{status}] MH10 Trạng thái: '{admin_data['trang_thai']}'")
                            assert ok, f"LỖI MH10: Trạng thái sai — expected 'Chờ xác nhận', got '{admin_data['trang_thai']}'"
                        else:
                            self._record_check("MH10", "MH10 Trạng thái đơn", "⚠️ WARN",
                                               "N/A", "Chờ xác nhận")
                            print(f"  [WARN] MH10: Không đọc được trạng thái đơn")

                        # Trạng thái thanh toán
                        if admin_data.get("thanh_toan"):
                            ok = "chưa" in admin_data["thanh_toan"].lower()
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Trạng thái thanh toán", status,
                                               admin_data["thanh_toan"], "Chưa thanh toán")
                            print(f"  [{status}] MH10 Thanh toán: '{admin_data['thanh_toan']}'")
                            assert ok, f"LỖI MH10: Thanh toán sai — expected 'Chưa thanh toán', got '{admin_data['thanh_toan']}'"
                        else:
                            self._record_check("MH10", "MH10 Trạng thái thanh toán", "⚠️ WARN",
                                               "N/A", "Chưa thanh toán")
                            print(f"  [WARN] MH10: Không đọc được trạng thái thanh toán")

                        # Tên sản phẩm
                        if admin_data.get("ten_sp") and _NAME.lower() in admin_data["ten_sp"].lower():
                            self._record_check("MH10", "MH10 Tên sản phẩm", "✅ PASS",
                                               admin_data["ten_sp"], _NAME)
                            print(f"  [PASS] MH10 Tên SP: '{admin_data['ten_sp']}'")
                        else:
                            self._record_check("MH10", "MH10 Tên sản phẩm", "⚠️ WARN",
                                               admin_data.get("ten_sp", "N/A"), _NAME)
                            print(f"  [WARN] MH10: Không đọc được tên SP — found: '{admin_data.get('ten_sp', '')}'")

                        # Màu
                        if admin_data.get("mau"):
                            ok = order_info["color"].lower() in admin_data["mau"].lower()
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Màu áo", status,
                                               admin_data["mau"], order_info["color"])
                            print(f"  [{status}] MH10 Màu: '{admin_data['mau']}'")
                        else:
                            self._record_check("MH10", "MH10 Màu áo", "⚠️ WARN",
                                               "N/A", order_info["color"])

                        # Size
                        if admin_data.get("size"):
                            ok = order_info["size"].upper() == admin_data["size"].upper()
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Size", status,
                                               admin_data["size"], order_info["size"])
                            print(f"  [{status}] MH10 Size: '{admin_data['size']}'")
                        else:
                            self._record_check("MH10", "MH10 Size", "⚠️ WARN",
                                               "N/A", order_info["size"])

                        # Số lượng
                        if admin_data.get("qty") is not None:
                            ok = admin_data["qty"] == order_info["qty"]
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Số lượng", status,
                                               str(admin_data["qty"]), str(order_info["qty"]))
                            print(f"  [{status}] MH10 Qty: {admin_data['qty']}")
                        else:
                            self._record_check("MH10", "MH10 Số lượng", "⚠️ WARN",
                                               "N/A", str(order_info["qty"]))

                        # Email khách hàng
                        if admin_data.get("email"):
                            ok = self.env.login_email.lower() in admin_data["email"].lower()
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 Email khách hàng", status,
                                               admin_data["email"], self.env.login_email)
                            print(f"  [{status}] MH10 Email KH: '{admin_data['email']}'")
                        else:
                            self._record_check("MH10", "MH10 Email khách hàng", "⚠️ WARN",
                                               "N/A", self.env.login_email)

                        # SĐT người nhận
                        if admin_data.get("phone") and order_info.get("phone"):
                            ok = order_info["phone"] in admin_data["phone"]
                            status = "✅ PASS" if ok else "❌ FAIL"
                            self._record_check("MH10", "MH10 SĐT người nhận", status,
                                               admin_data["phone"], order_info["phone"])
                            print(f"  [{status}] MH10 SĐT: '{admin_data['phone']}'")
                        else:
                            self._record_check("MH10", "MH10 SĐT người nhận", "⚠️ WARN",
                                               admin_data.get("phone", "N/A"),
                                               order_info.get("phone", ""))

                        # Địa chỉ — INFO only
                        self._record_check("MH10", "MH10 Địa chỉ giao hàng", "ℹ️ INFO",
                                           "xem screenshot", "")
                        print(f"  [INFO] MH10 Địa chỉ: xem screenshot MH10_2")

                        # Giá — dùng _assert_price với raw_amounts
                        self._shot("MH10_3", "admin_order_payment")
                        raw = admin_data.get("raw_amounts", [])

                        # Tìm subtotal (_SALE = 189_000) trong danh sách raw amounts
                        subtotal_found = next((v for v in raw if abs(v - _SALE) <= _TOLERANCE), None)
                        self._assert_price(subtotal_found, _SALE, "MH10 Subtotal")

                        # Tìm tổng cộng (actual_total_paid)
                        total_found = next((v for v in raw if abs(v - actual_total_paid) <= _TOLERANCE), None)
                        self._assert_price(total_found, actual_total_paid, "MH10 Tổng cộng")

                        # Ship
                        ship_found = next((v for v in raw if abs(v - _SHIPPING) <= _TOLERANCE), None)
                        self._assert_price(ship_found, _SHIPPING, "MH10 Phí vận chuyển")

                        print(f"  [PASS] MH10: Admin verify OK")

        except AssertionError:
            raise
        except Exception as e:
            self._record_check("MH10", "MH10 Admin — unexpected error", "⚠️ WARN",
                               str(e)[:80], "")
            print(f"  [WARN] MH10: Lỗi không mong đợi — {e}")

        # In lại bảng tổng hợp với MH10
        self._print_summary_table()
```

> ⚠️ **Lưu ý:** Xóa `self._print_summary_table()` ở dòng ngay trước khối MH10 (dòng 944) vì bây giờ gọi ở cuối sau MH10 thay thế.

- [ ] **Step 2: Xóa `_print_summary_table()` cũ ở dòng 943-944**

Tìm đoạn:
```python
        print(f"\n  [PASS] {tc}: MH1→MH9 (luồng Mua ngay) PASSED")
        self._print_summary_table()
```

Đổi thành:
```python
        print(f"\n  [PASS] {tc}: MH1→MH9 (luồng Mua ngay) PASSED")
```

(Xóa dòng `self._print_summary_table()` — sẽ gọi lại ở cuối MH10)

- [ ] **Step 3: Cập nhật docstring test method**

Tìm dòng cuối `test_full_price_flow_mua_ngay` docstring:
```python
    def test_full_price_flow_mua_ngay(self):
        """PT01 Trắng — full flow qua MH1→MH9 qua luồng Mua ngay."""
```

Đổi thành:
```python
    def test_full_price_flow_mua_ngay(self):
        """PT01 Trắng — full flow qua MH1→MH10 (MH10 = Admin verify đơn hàng)."""
```

- [ ] **Step 4: Chạy test để verify**

```bash
python -m pytest tests/production/test_pt01_trang_full_price_flow.py -k "mua_ngay" --env=test --headed --tb=short -s 2>&1
```

Expected: Test PASS, thấy block `── MH10: Admin — Verify đơn hàng ──` trong output. Nếu admin credentials chưa set → thấy `[WARN] MH10: Thiếu ADMIN_EMAIL/ADMIN_PASSWORD`.

- [ ] **Step 5: Commit**

```bash
git add tests/production/test_pt01_trang_full_price_flow.py
git commit -m "feat(test): thêm MH10 Admin order verify vào test_full_price_flow_mua_ngay"
```

---

## Task 4: Smoke check với credentials thật

Chạy sau khi đã set `ADMIN_EMAIL` / `ADMIN_PASSWORD` trong `.env`.

- [ ] **Step 1: Chạy full test với headed mode để quan sát**

```bash
python -m pytest tests/production/test_pt01_trang_full_price_flow.py -k "mua_ngay" --env=test --headed --tb=short -s 2>&1
```

Expected output MH10:
```
── MH10: Admin — Verify đơn hàng ────────────────────────
[PASS] MH10: Admin login OK
[PASS] MH10 Mã đơn: 'POD-2026xxxx-xxx'
[PASS] MH10 Trạng thái: 'Chờ xác nhận'
[PASS] MH10 Thanh toán: 'Chưa thanh toán'
[PASS] MH10 Tên SP: 'Áo Phông Cá Tính'
[PASS] MH10 Màu: 'Trắng'
[PASS] MH10 Size: 'L'
[PASS] MH10 Qty: 1
[PASS] MH10 Email KH: 'tester_beta_2026@yopmail.com'
[PASS] MH10 SĐT: '0901234567'
[✅ PASS] MH10 Subtotal | expected=189,000đ | displayed=189,000đ
[✅ PASS] MH10 Tổng cộng | expected=183,296đ | displayed=183,296đ
[✅ PASS] MH10 Phí vận chuyển | expected=20,000đ | displayed=20,000đ
[PASS] MH10: Admin verify OK
```

- [ ] **Step 2: Nếu có field WARN — điều chỉnh selector**

Nếu một field báo WARN (ví dụ không đọc được tên SP), chụp screenshot MH10_2, xem DOM, điều chỉnh regex tương ứng trong hàm `_parse_admin()` bên trong khối MH10.

Ví dụ: nếu tên SP được hiển thị là "Áo phông cá tính" (viết thường) thì sửa regex:
```python
if _re.search(r'Áo [Pp]hông|áo phông|T-Shirt|t-shirt', line, _re.I):
```

- [ ] **Step 3: Final commit nếu có điều chỉnh**

```bash
git add tests/production/test_pt01_trang_full_price_flow.py
git commit -m "fix(test): điều chỉnh regex _parse_admin sau smoke check MH10"
```
