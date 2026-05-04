# Production — 💰 Price Verification Tests

> File test: `tests/production/test_price_verification.py` · Class: `TestPriceVerification`  
> Data: `data/product_pricing.json`  
> Screenshot: `screenshots/production/price_verification/PRICE_00X/`  
> Chạy: `pytest tests/production/test_price_verification.py --env=test -v`

Bộ test kiểm tra giá hiển thị trên **order screen** có khớp với `salePrice` trong bảng giá hay không,
cho tất cả loại sản phẩm × màu × size.

---

## Công thức giá

| Màn hình | Giá hiển thị | Ghi chú |
|:---|:---|:---|
| **Order screen** | `salePrice` (chưa VAT) | Giá áo đơn lẻ theo màu/size group |
| **Checkout screen** | `(salePrice + print_cost) × 1.08` | Tổng có VAT, phụ thuộc kích thước in |

Tolerance assert: **±1.000đ** (chấp nhận làm tròn UI).

---

## Bảng giá kỳ vọng theo sản phẩm

| TC | Sản phẩm | Variant | Màu test | Size test | salePrice kỳ vọng |
|:---|:---|:---|:---|:---|---:|
| PRICE_001 | PT01 — Áo Phông Cá Tính | XS/S/2XL/3XL | Trắng | S, 2XL | 189.000đ |
| PRICE_001 | PT01 — Áo Phông Cá Tính | M/L/XL | Trắng | M, L, XL | 189.000đ |
| PRICE_002 | M21 — Áo Phông Nặng Đông | Màu Trắng | Trắng | M | 119.000đ |
| PRICE_002 | M21 — Áo Phông Nặng Đông | Màu (non-trắng) | Đen | M | 128.000đ |
| PRICE_003 | M22 — Áo Phông Cơ Bản | Màu Trắng | Trắng | M | 132.000đ |
| PRICE_003 | M22 — Áo Phông Cơ Bản | Màu (non-trắng) | Đen | M | 139.000đ |
| PRICE_004 | ET002 — Áo Phông Trẻ Em | Size 100–140 | Trắng | 110, 130 | 87.000đ |
| PRICE_004 | ET002 — Áo Phông Trẻ Em | Size 150–160 | Trắng | 150, 160 | 91.000đ |

---

## Luồng chung (tất cả PRICE_00X)

| Step | Màn hình | Hành động | Assert |
|:---:|:---|:---|:---|
| S0 | Home | Đăng nhập | Nút "Đăng nhập" biến mất |
| S1 | Studio | Navigate theo `studio_url` trong config | Canvas visible |
| S2 | Studio | Chờ AI gen ≥ 3 artwork (120s) | ≥ 3 ảnh → SKIP nếu thiếu |
| S3 | Studio | Click artwork → Hoàn tất thiết kế → Review | Navigate `/review` |
| S4 | Review | Click Đặt hàng | Navigate `/order` |
| S4.1 | Order | Detect product type | SKIP nếu không khớp expected product |
| S5+ | Order | Với mỗi (variant × color × size): chọn color → chọn size → đọc giá | `\|displayed - expected\| ≤ 1.000đ` |

---

## SKIP guard

Nếu `studio_url` chưa đúng (tất cả đang là `/studio?category=t-shirts`), test sẽ tự **SKIP** với message:

```
SKIP PRICE_002: Studio URL '/studio?category=t-shirts' tải 'Áo Phông Cá Tính',
expected 'Áo Phông Nặng Đông' — cập nhật studio_url trong product_pricing.json
```

→ Cập nhật `studio_url` trong `data/product_pricing.json` khi biết URL đúng.

---

## Cập nhật studio_url

Để chạy test cho sản phẩm cụ thể, tìm URL của sản phẩm đó (ví dụ từ menu sản phẩm trên site)
và cập nhật `studio_url` trong `data/product_pricing.json`:

```json
{
  "code": "M21",
  "studio_url": "/studio?product=m21",   ← cập nhật khi biết URL
  ...
}
```

---

## Thay đổi data test

Để thêm/sửa màu hoặc size cần test, chỉ sửa `test_colors` và `test_sizes` trong `data/product_pricing.json`:

```json
{
  "id": "M21_TRANG",
  "test_colors": ["Trắng"],      ← màu cần kiểm tra
  "test_sizes": ["M", "L"],      ← size cần kiểm tra
  "salePrice": 119000            ← giá kỳ vọng
}
```
