# Design: MH10 Admin Order Verification

**Ngày**: 04/05/2026
**Scope**: Thêm bước MH10 Admin vào cuối `test_full_price_flow_mua_ngay` (PT01 Trắng)

---

## 1. Mục tiêu

Sau khi tạo đơn hàng qua luồng MH1→MH9, navigate sang Admin panel để xác minh đơn hàng hiển thị đúng toàn bộ thông tin: trạng thái, sản phẩm, giá, người nhận, khách hàng.

---

## 2. Config & Credentials

### .env (thêm 2 biến)
```
ADMIN_EMAIL=<admin account email>
ADMIN_PASSWORD=<admin account password>
```

### environments.py
Thêm `admin_email: str` và `admin_password: str` vào `Environment` dataclass. Đọc từ `os.environ.get("ADMIN_EMAIL", "")` và `os.environ.get("ADMIN_PASSWORD", "")`.

### _MH_NAMES (trong test class)
```python
"MH10": "Admin — Chi tiết đơn",
```
MH10 Giỏ hàng tách thành test case riêng sau này.

---

## 3. Flow MH10 (inline trong test_full_price_flow_mua_ngay)

Nối thẳng sau `_print_summary_table()`, dùng `order_code` đã capture từ URL MH6.

```
Bước 1: Navigate https://admin.test.shop.tryonic.ai/
         └─ Nếu redirect /login → fill ADMIN_EMAIL + ADMIN_PASSWORD → submit

Bước 2: Navigate /orders/
         └─ Tìm search box → nhập order_code → Enter/submit

Bước 3: Click row chứa order_code
         └─ Chờ trang detail load (domcontentloaded)

Bước 4: Đọc data bằng page.evaluate(innerText)
         ├─ Block thông tin đơn: mã đơn, trạng thái, thanh toán
         ├─ Block sản phẩm: tên SP, màu, size, số lượng
         ├─ Block giá: subtotal, giảm giá, ship, VAT, tổng
         └─ Block giao hàng: tên, SĐT, địa chỉ, email KH

Bước 5: Assert từng field
         └─ _assert_price() cho giá, _record_check() cho text fields
```

---

## 4. Fields Verify

| Field | Expected | Method |
|-------|----------|--------|
| Mã đơn | `order_code` từ MH6 URL | `_record_check` |
| Trạng thái | `"Chờ xác nhận"` | `_record_check` |
| Thanh toán | `"Chưa thanh toán"` | `_record_check` |
| Tên sản phẩm | `_NAME` | `_record_check` |
| Màu | `order_info["color"]` | `_record_check` |
| Size | `order_info["size"]` | `_record_check` |
| Số lượng | `order_info["qty"]` | `_record_check` |
| Subtotal | `_SALE` | `_assert_price` |
| Giảm giá | `_DISCOUNT_AMT` (nếu discount áp dụng) | `_assert_price` |
| Phí ship | `_SHIPPING` | `_assert_price` |
| VAT | `None` → INFO only | `_assert_price` |
| Tổng cộng | `actual_total_paid` | `_assert_price` |
| Tên người nhận | `order_info["receiver_name"]` | `_record_check` |
| SĐT | `order_info["phone"]` | `_record_check` |
| Email KH | `env.login_email` | `_record_check` |
| Địa chỉ | — | INFO only |

---

## 5. Screenshots

| Step | Label | Nội dung |
|------|-------|----------|
| MH10_1 | `admin_order_list` | Danh sách đơn sau khi search |
| MH10_2 | `admin_order_detail` | Trang chi tiết đơn hàng |
| MH10_3 | `admin_order_payment` | Phần giá / thanh toán |

---

## 6. Error Handling

| Tình huống | Xử lý |
|---|---|
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` thiếu | WARN + return sớm, không fail test |
| Admin login thất bại | WARN + return sớm |
| Không tìm thấy order trên admin | WARN + skip verify fields |
| Field sai giá trị | FAIL — AssertionError |
| Unexpected exception | WARN + continue (không kéo fail MH1→MH9) |

Toàn bộ MH10 wrap trong `try/except Exception`.

---

## 7. Implementation Scope

**Files thay đổi:**
- `.env.example` — thêm `ADMIN_EMAIL`, `ADMIN_PASSWORD`
- `tests/config/environments.py` — thêm 2 field vào Environment
- `tests/production/test_pt01_trang_full_price_flow.py`:
  - `_MH_NAMES`: cập nhật MH10
  - `test_full_price_flow_mua_ngay`: thêm khối MH10 Admin sau MH9

**Files KHÔNG thay đổi:** Không tạo Page Object mới. Toàn bộ logic admin inline trong test method.

---

## 8. Out of Scope

- Admin CRUD operations (chỉ đọc, không sửa)
- Verify ảnh mockup trên admin
- Test admin UI riêng biệt
- MH10 Giỏ hàng (tách case riêng sau)
