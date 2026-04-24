# Order Data Capture & Verify — CRITICAL_001 / CRITICAL_002

**Date:** 2026-04-24  
**Scope:** `tests/production/test_critical_flows.py`, `tests/pages/studio_page.py`, `tests/pages/checkout_page.py`

---

## Mục tiêu

Trong luồng test, ghi lại đầy đủ thông số đơn hàng (loại áo, màu, hình in, size, giá, địa chỉ, mã đơn) rồi verify lại toàn bộ trên màn hình chi tiết đơn hàng sau khi đơn được tạo thành công.

---

## 1. New Page Object Methods

### StudioPage (`tests/pages/studio_page.py`)

| Method | Mô tả |
|---|---|
| `read_panel_image_src(index: int) -> str \| None` | Đọc `src` của artwork tại `index` trong left panel, skip 'Thêm ảnh' card (`+1` offset). Dùng kết hợp với `click_artwork`. |
| `read_library_image_src(index: int) -> str \| None` | Đọc `src` của ảnh thư viện tại `index` (không skip). Dùng kết hợp với `click_library_image`. |

Cả hai dùng JS position-based filter: `rect.left < 330 && rect.width > 30 && rect.height > 30 && img.complete && img.naturalWidth > 0`.

### CheckoutPage (`tests/pages/checkout_page.py`)

| Method | Mô tả |
|---|---|
| `read_price_from_page() -> str \| None` | Regex `\d+[,.]\d+\s*₫` trên `document.body.innerText`. Trả về match đầu tiên. |
| `read_address_from_checkout() -> str \| None` | Đọc `input[name*="address"].value` hoặc text từ `[class*="address"]` section. |
| `read_order_code() -> str \| None` | Ưu tiên URL param `?orderCode=POD-...`, fallback regex `POD-\d{8}-\d+` trong page text. |
| `read_product_type() -> str \| None` | Heading (`h1/h2/h3`) chứa keyword `áo\|shirt\|thun` (case-insensitive). |
| `verify_order_data(order_data: dict, tc_id: str)` | Verify từng field theo bảng dưới. |

### Verify logic trong `verify_order_data`

| Field | So sánh | Kết quả nếu sai |
|---|---|---|
| `order_code` | Exact string trong page text | `AssertionError` — FAIL |
| `size` | Exact string trong page text | `AssertionError` — FAIL + in cảnh báo format: *"⚠ Format size không nhất quán: captured `M`, page hiện `Size M` — cần đồng nhất"* |
| `unit_price` | Digits-only (bỏ `₫`, `.`, `,`) | `[WARN]` + in format diff nếu mismatch |
| `total_price` | Digits-only | `[WARN]` |
| `address` | Log only | `[INFO]` |
| `artwork_front_src` | Log only | `[INFO]` |
| `artwork_back_src` | Log only | `[INFO]` |
| `product_type` | Log only | `[INFO]` |

---

## 2. CRITICAL_001 — Capture Points & New Steps

### Capture points (insert vào các step hiện tại)

```
order_data = {"color": "Trắng", "size": "M"}

Before S4  → order_data["artwork_front_src"] = studio.read_panel_image_src(0)
In S5b     → order_data["artwork_back_src"]  = studio.read_library_image_src(2)
After S7a  → order_data["product_type"]      = checkout.read_product_type()
           → order_data["unit_price"]         = checkout.read_price_from_page()
After S7c  → order_data["total_price"]        = checkout.read_price_from_page()
           → order_data["address"]            = checkout.read_address_from_checkout()
```

### New steps S9–S13 (thêm sau S8c)

| Step | Hành động | Assert |
|---|---|---|
| S9 | Click nút "Hủy" trên trang QR | `assert cancel.is_visible(timeout=10000)` |
| S10 | Xác nhận hủy — capture `order_code` từ URL redirect | `assert "pay" not in page.url` |
| S11 | Click "Xem đơn hàng" (nếu không có → navigate `/profile`) | `assert view_order.is_visible(timeout=5000)` |
| S12 | Click "Đơn hàng của tôi" tab — in toàn bộ `order_data` | `assert my_orders.is_visible(timeout=5000)` |
| S13 | Click đơn đầu tiên → `verify_order_data(order_data, "CRITICAL_001")` | Assert từ verify logic |

Screenshots mới: `S16_after_cancel`, `S17_view_orders`, `S18_my_orders`, `S19_order_detail`

---

## 3. CRITICAL_002 — Capture Points & Verify tại S15

### Capture points (insert vào các step hiện tại)

```
order_data = {"size": "4XL"}

Before S3  → order_data["artwork_front_src"] = studio.read_panel_image_src(1)
Before S4  → order_data["artwork_back_src"]  = studio.read_panel_image_src(0)
After S6   → order_data["product_type"]      = checkout.read_product_type()
           → order_data["unit_price"]         = checkout.read_price_from_page()
After S9   → order_data["total_price"]        = checkout.read_price_from_page()
           → order_data["address"]            = checkout.read_address_from_checkout()
After S13  → order_data["order_code"]         = checkout.read_order_code()
```

### Thêm verify tại S15 (sau click first order)

```python
# Sau khi click đơn hàng đầu tiên và wait:
self.checkout.verify_order_data(order_data, "CRITICAL_002")
print(f"  [INFO] order_data: {order_data}")
```

S16 (repay) giữ nguyên.

---

## 4. Out of Scope

- Không verify artwork image URL trực tiếp (order detail hiển thị composite shirt image, không phải raw artwork)
- Không thêm test case mới
- Không thay đổi CRITICAL_003
