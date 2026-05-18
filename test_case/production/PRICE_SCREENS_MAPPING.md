# Price Screens Mapping — Tất cả màn hình hiển thị giá

> Config giá: `data/product_pricing.json`  
> Test file chính: `tests/production/test_price_verification.py`  
> Cập nhật giá → chỉ sửa JSON, không cần đụng code test.

---

## Công thức giá chung

```
salePrice_ao     = giá bán áo (chưa VAT, trong config variants[].salePrice)
originalPrice_ao = giá niêm yết gốc (variants[].originalPrice)
salePrice_in     = giá dịch vụ in (print_sale_prices.<method>.<size>)
VAT_rate         = 0.08

subtotal         = salePrice_ao × số lượng
total_with_print = floor( (salePrice_ao + salePrice_in) × 1.08 )
shipping_fee     = 20.000đ
```

### Mã giảm giá

| Code | Giảm | Công thức |
|:---|:---|:---|
| `GIAM20` | 20% trên subtotal | `subtotal × 0.80` |

---

## MH1 — Product Listing (`/#products`)

| TC ID | Test file | Trạng thái |
|:---|:---|:---:|
| `LISTING_001` → `LISTING_004` | `TestListingPriceVerification` | ✅ Có test |

### Verify

| Loại giá | Hiển thị | Công thức verify | FAIL khi |
|:---|:---|:---|:---|
| Giá gốc (gạch ngang) | ~~227.000đ~~ | `max(variants[].originalPrice)` | displayed ≠ max ±1.000đ |
| Giá sale (màu hồng) | **189.000đ** | `min(variants[].salePrice)` | displayed ≠ min ±1.000đ |

### Giá listing theo sản phẩm

| Sản phẩm | TC | Giá gạch (max original) | Giá sale (min sale) |
|:---|:---|---:|---:|
| Áo Phông Cá Tính (PT01) | LISTING_001 | ~~227.000đ~~ | **189.000đ** |
| Áo Phông Cơ Bản (M22) | LISTING_003 | ~~167.000đ~~ | **132.000đ** |
| Áo Phông Năng Động (M21) | LISTING_002 | ~~154.000đ~~ | **119.000đ** |
| Áo Phông Trẻ Em (ET002) | LISTING_004 | ~~110.000đ~~ | **87.000đ** |

### Behavior

- Click vào ảnh/card sản phẩm → navigate đến MH2 (Product Detail)

---

## MH2 — Product Detail (`/product/<slug>`)

| URL mẫu | TC ID | Trạng thái |
|:---|:---|:---:|
| `/product/ao-phong-ca-tinh` | `DETAIL_001` | ⬜ Chưa có test |

### Verify

| Điểm kiểm tra | Mô tả | FAIL khi |
|:---|:---|:---|
| Tên sản phẩm | Hiển thị đúng tên (ví dụ: "Áo Phông Cá Tính") | Tên sai hoặc không hiện |
| Màu default | Áo hiển thị màu **Trắng** khi vào trang | Hiển thị màu khác |
| Giá gạch default | `max(variants[].originalPrice)` | displayed ≠ max ±1.000đ |
| Giá bán default | `salePrice` của variant màu **Trắng** | displayed ≠ expected ±1.000đ |
| Đổi màu áo | Click màu → ảnh và giá thay đổi tương ứng | Giá không thay đổi sau click |
| Button "Thiết kế hình in" | Click → đến Studio (lần đầu hiển thị popup điều khoản) | Không navigate hoặc popup không hiện |
| Studio có màu đúng | Màu trong studio = màu đã chọn ở MH2 | Màu sai |
| Button "Mua ngay" | Click → mở popup MH4 | Popup không mở |

### Detail URL từng sản phẩm

| Sản phẩm | URL |
|:---|:---|
| PT01 | `/product/ao-phong-ca-tinh` |
| M21 | `/product/ao-phong-nang-dong` |
| M22 | `/product/ao-phong-co-ban` |
| ET002 | `/product/ao-phong-tre-em` |

---

## MH3 — Studio (`/studio?category=t-shirts`)

| TC ID | Trạng thái |
|:---|:---:|
| CRITICAL_001, CRITICAL_002, ARTWORK_001–003 | ✅ Có test (flow) |

### Verify giá

Studio **không hiển thị giá tiền**. Giá chỉ xuất hiện sau khi click "Hoàn tất thiết kế".

---

## MH4 — Popup "Mua ngay" (Buy Now modal)

| TC ID | Trạng thái |
|:---|:---:|
| `BUYNOW_001` | ⬜ Chưa có test |

> Ảnh tham khảo: https://prnt.sc/cnpdWMTBWIBi

### Verify

| Điểm kiểm tra | Công thức | FAIL khi |
|:---|:---|:---|
| Tên áo | Khớp tên sản phẩm | Sai tên |
| Màu áo | Khớp màu đã chọn ở MH2 | Sai màu |
| Giá đơn vị | `salePrice` của variant (color × size) | displayed ≠ expected ±1.000đ |
| Giá trên button "Thanh toán ngay" | `salePrice × quantity` | displayed ≠ expected |
| Thay đổi size | Chọn size khác → giá đơn vị thay đổi đúng variant | Giá không đổi |
| Thêm nhiều size | Tổng = Σ(salePrice × qty) từng size | Tổng sai |
| Click "Thanh toán ngay" | Navigate → MH5 Checkout | Không navigate |

---

## MH5 — Checkout (`/checkout`)

| TC ID | Trạng thái |
|:---|:---:|
| `CHECKOUT_001` | ⬜ Chưa có test |

### Verify

| Dòng | Công thức | FAIL khi |
|:---|:---|:---|
| Tổng tiền (subtotal) | `Σ salePrice × qty` | displayed ≠ expected |
| Tổng cộng | = Tổng tiền (trước thuế riêng) | displayed ≠ Tổng tiền |
| Thuế VAT (8%) | `Tổng cộng × 0.08` | displayed ≠ expected ±1đ |
| Phí giao hàng | `20.000đ` (cố định) | displayed ≠ 20.000đ |
| Mã giảm giá GIAM20 | `Tổng tiền × 0.20` (giảm đi) | Không áp dụng hoặc tính sai |
| Tổng thanh toán | `Tổng tiền - discount + shipping` | displayed ≠ computed |
| Button "Thanh toán" | Hiển thị đúng `Tổng thanh toán` | Giá trên button sai |
| Click "Thanh toán" | Navigate → MH6 QR Code | Không navigate |

### Công thức Tổng thanh toán

```
Tổng tiền    = Σ (salePrice × qty)
Discount     = Tổng tiền × 0.20   (nếu có mã GIAM20)
Tổng cộng    = Tổng tiền - Discount
Shipping     = 20.000đ
VAT          = Tổng cộng × 0.08
Tổng TT      = Tổng cộng + VAT + Shipping

Ví dụ (không mã giảm):
  Tổng tiền = 189.000đ  →  Tổng TT = 189.000 × 1.08 + 20.000 = 224.120đ

Ví dụ (có GIAM20):
  Tổng tiền = 189.000đ  →  Sau giảm = 189.000 × 0.80 = 151.200đ
  Tổng TT   = 151.200 × 1.08 + 20.000 = 183.296đ
```

---

## MH6 — QR Code

| TC ID | Trạng thái |
|:---|:---:|
| `QR_001` | ⬜ Chưa có test (CRITICAL_001 có kiểm tra navigate) |

### Verify

| Điểm kiểm tra | Công thức | FAIL khi |
|:---|:---|:---|
| Số tiền hiển thị | = `Tổng thanh toán` từ MH5 | displayed ≠ expected |
| Nội dung lưu ý | Nhập chính xác số tiền (ví dụ: `428.240₫`) | Số tiền trong text sai |
| Click "Hủy" → xác nhận | Hiện confirm dialog | Không hiện |
| Sau xác nhận hủy | Navigate → "Xem đơn hàng" → MH7 Order (chưa thanh toán) | Không navigate đúng |

---

## MH7 — Order (sau QR / sau hủy QR)

| TC ID | Trạng thái |
|:---|:---:|
| `ORDER_001` | ⬜ Chưa có test |

> Ảnh tham khảo: https://prnt.sc/CbzxJiTEU90m

### Verify

| Điểm kiểm tra | Công thức | FAIL khi |
|:---|:---|:---|
| Banner "Vui lòng thanh toán Xđ" | X = `Tổng thanh toán` | Số tiền trong text sai |
| Tổng tiền | `Σ salePrice × qty` | displayed ≠ expected |
| Tổng giá | = Tổng tiền | displayed ≠ Tổng tiền |
| Thuế VAT (8%) | `Tổng cộng × 0.08` | displayed ≠ expected ±1đ |
| Phí giao hàng | `20.000đ` | displayed ≠ 20.000đ |
| Mã giảm giá GIAM20 | `Tổng tiền × 0.20` | Không hiện hoặc tính sai |
| Tổng cộng | = Tổng thanh toán | displayed ≠ computed |
| Click "Đơn hàng của tôi" | Navigate → MH8 | Không navigate |

---

## MH8 — Đơn hàng của tôi (`/my-orders`)

| TC ID | Trạng thái |
|:---|:---:|
| `MYORDER_001` | ⬜ Chưa có test |

### Verify

| Điểm kiểm tra | FAIL khi |
|:---|:---|
| Giá tiền đơn hàng | displayed ≠ Tổng thanh toán ±1.000đ |
| Click "Chi tiết" | Không navigate → MH9 |

---

## MH9 — Chi tiết đơn hàng

| TC ID | Trạng thái |
|:---|:---:|
| `ORDERDETAIL_001` | ⬜ Chưa có test |

### Verify

| Điểm kiểm tra | FAIL khi |
|:---|:---|
| Tổng tiền | displayed ≠ Tổng thanh toán ±1.000đ |
| Tất cả dòng giá tiền | Bất kỳ dòng nào sai |

---

## MH10 — Giỏ hàng (`/cart`)

| TC ID | Trạng thái |
|:---|:---:|
| `CART_001` | ⬜ Chưa có test |

### Verify

| Điểm kiểm tra | Công thức | FAIL khi |
|:---|:---|:---|
| Giá từng item | `salePrice` của variant | displayed ≠ expected ±1.000đ |
| Tổng giỏ hàng | `Σ salePrice × qty` | displayed ≠ expected |

---

## Tóm tắt trạng thái

> Test file PT01 Trắng: `tests/production/test_pt01_trang_full_price_flow.py`  
> Test case doc: `test_case/production/TC_PT01_TRANG_PRICE_FLOW.md`

| MH | Màn hình | TC IDs | Trạng thái |
|:---:|:---|:---|:---:|
| 1 | Product Listing `/#products` | LISTING_001–004 | ✅ Có test |
| 2 | Product Detail `/product/<slug>` | PT01_TRANG (MH2) | ✅ Có test |
| 3 | Studio `/studio` | PT01_TRANG (MH3) | ✅ Flow test |
| 4 | Popup Mua ngay | PT01_TRANG (MH4) | ✅ Có test |
| 5 | Checkout `/checkout` | PT01_TRANG (MH5) | ✅ Có test |
| 6 | QR Code | PT01_TRANG (MH6) | ✅ Có test |
| 7 | Order (sau QR) | PT01_TRANG (MH7) | ✅ Có test |
| 8 | Đơn hàng của tôi | PT01_TRANG (MH8) | ✅ Có test |
| 9 | Chi tiết đơn hàng | PT01_TRANG (MH9) | ✅ Có test |
| 10 | Giỏ hàng `/cart` | PT01_TRANG (MH10) | ✅ Có test |

---

## Cập nhật giá (hướng dẫn)

| Cần thay đổi | Sửa ở đâu trong `product_pricing.json` |
|:---|:---|
| Giá áo | `products[].variants[].salePrice` / `originalPrice` |
| Giá in | `print_sale_prices.<method>.<size>` |
| Giá listing | Tự tính từ max/min variants (không cần sửa thêm) |
| Phí giao hàng | `global.shipping_fee` |
| Mã giảm giá | `discount_codes.<CODE>.value` |
| Tổng combo (áo+in) | `expected_total_prices` — tính lại theo `floor((ao+in)×1.08)` |
