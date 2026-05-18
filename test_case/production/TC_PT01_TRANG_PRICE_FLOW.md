# Test Case — Verify Giá Full Luồng: PT01 Áo Phông Cá Tính (Trắng)

> **Cập nhật**: 2026-05-13
> **Sản phẩm**: Áo Phông Cá Tính (PT01) | Màu: Trắng | Size: M | Qty: 1
> **Data**: `data/product_pricing.json`
> **Tolerance**: ±1.000đ

---

## Tổng quan các luồng

| Luồng | TC ID | Test file | Status |
|:---|:---|:---|:---:|
| Plain / Mua ngay | PT01_TRANG_PLAIN_BUYNOW | `test_plain_buynow_pt01_trang.py` | ✅ |
| Plain / Giỏ hàng | PT01_DEN_PLAIN_CART | `test_plain_cart_pt01_den.py` | (old) |
| Design / Mua ngay | PT01_TRANG_DESIGN_BUYNOW | `test_design_buynow_pt01_trang.py` | ✅ |
| Design / Giỏ hàng | PT01_TRANG_DESIGN_CART | `test_design_cart_pt01_trang.py` | ✅ |

---

## Expected Data

### Luồng Plain (áo phôi — không in)

| Giá trị | Số tiền | Công thức |
|:---|---:|:---|
| Giá sale (listing + detail) | **189.000đ** | `variant.salePrice` |
| Giá gốc (gạch ngang) | ~~227.000đ~~ | `variant.originalPrice` |
| VAT 8% | **15.120đ** | `189.000 × 0.08` |
| Phí giao hàng | **20.000đ** | cố định |
| **Tổng TT (không mã)** | **224.120đ** | `189k + 15.12k + 20k` |
| Giảm GIAM20 (20%) | 37.800đ | `189.000 × 0.20` |
| Tổng sau giảm | 151.200đ | `189.000 × 0.80` |
| VAT sau giảm | 12.096đ | `151.200 × 0.08` |
| **Tổng TT (có GIAM20)** | **183.296đ** | `151.2k + 12.096k + 20k` |

### Luồng Design (có in — giá in đọc động từ Review page)

| Giá trị | Số tiền | Ghi chú |
|:---|---:|:---|
| Giá áo | **189.000đ** | Không đổi |
| Giá in (DTG 1 mặt) | ~41.000đ | Đọc từ Review page (biến động) |
| **unit_price (áo + in)** | ~230.000đ | Đọc từ UI |
| VAT 8% | ~18.400đ | `unit_price × 0.08` |
| Phí giao hàng | **20.000đ** | cố định |
| **Tổng TT (không mã)** | ~268.400đ | `230k + 18.4k + 20k` |
| Giảm GIAM20 (20%) | ~46.000đ | `unit_price × 0.20` |
| **Tổng TT (có GIAM20)** | ~218.720đ | `184k + 14.72k + 20k` |

> Giá in (DTG/PET) biến động theo số hình và kích thước — test đọc động từ UI.

---

## Luồng 1: Plain / Mua ngay

**Màn hình**: MH1 → MH2 → MH3 (kiểm tra Studio) → MH4 (Popup Mua ngay) → MH5 → MH6 → MH7 → MH8 → MH9 → MH11 (Admin)

### MH1 — Product Listing

| Step | Hành động | Expected |
|:---:|:---|:---|
| 1.1 | Navigate `/product` | Listing hiển thị |
| 1.2 | Tìm card "Áo Phông Cá Tính" | Card hiển thị |
| 1.3 | Verify giá sale (màu hồng) | **189.000đ** |
| 1.4 | Verify giá gốc (gạch ngang) | ~~227.000đ~~ |

### MH2 — Product Detail

| Step | Hành động | Expected |
|:---:|:---|:---|
| 2.1 | Click card → `/product/ao-phong-ca-tinh` | Trang detail hiển thị |
| 2.2 | Verify giá sale default (Trắng) | **189.000đ** |
| 2.3 | Verify giá gốc gạch ngang | ~~227.000đ~~ |
| 2.4 | Chọn màu Trắng | Swatch Trắng active |

### MH3 — Studio (kiểm tra tồn tại)

| Step | Hành động | Expected |
|:---:|:---|:---|
| 3.1 | Click "Thiết kế hình in" | Navigate `/studio` |
| 3.2 | Accept popup điều khoản (nếu hiện) | Popup đóng |
| 3.3 | Verify canvas hiển thị | Canvas visible |
| 3.4 | Go back về MH2 | Trở lại trang detail |
| 3.5 | Chọn lại màu Trắng | Đảm bảo đúng variant |

### MH4 — Popup Mua ngay

| Step | Hành động | Expected |
|:---:|:---|:---|
| 4.1 | Click "Mua ngay" trên MH2 | Modal popup xuất hiện |
| 4.2 | Verify đơn giá trong popup | **189.000đ** |
| 4.3 | Chọn size M | Size M highlight |
| 4.4 | Verify giá sau chọn size | **189.000đ** |
| 4.5 | Click "Thanh toán ngay" | Navigate `/checkout` |

### MH5 — Checkout

| Step | Hành động | Expected |
|:---:|:---|:---|
| 5.1 | Verify Tổng tiền (subtotal) | **189.000đ** |
| 5.2 | Verify Thuế VAT (8%) | **15.120đ** |
| 5.3 | Verify Phí giao hàng | **20.000đ** |
| 5.4 | Verify Tổng thanh toán | **224.120đ** |
| 5.5 | Nhập mã `GIAM20` → Apply | Mã được áp dụng |
| 5.6 | Verify Giảm giá GIAM20 | **37.800đ** |
| 5.7 | Verify Tổng TT sau GIAM20 | **183.296đ** |
| 5.8 | Điền MST/CCCD | Field được điền |
| 5.9 | Click "Thanh toán" | Navigate → MH6 QR |

### MH6 — QR Code

| Step | Hành động | Expected |
|:---:|:---|:---|
| 6.1 | Verify QR code hiển thị | QR image visible |
| 6.2 | Verify số tiền trên QR | **183.296đ** (có GIAM20) |
| 6.3 | Verify số tiền trong lưu ý | Khớp Tổng TT |
| 6.4 | Click Hủy → Xác nhận | Dialog đóng |
| 6.5 | Click "Xem đơn hàng" | Navigate → MH7 |

### MH7 — Order (sau hủy QR)

| Step | Hành động | Expected |
|:---:|:---|:---|
| 7.1 | Verify banner "Vui lòng thanh toán" | **183.296đ** |
| 7.2 | Verify Phí giao hàng | **20.000đ** |

### MH8 — Đơn hàng của tôi

| Step | Hành động | Expected |
|:---:|:---|:---|
| 8.1 | Navigate `/my-orders` | Đơn hàng hiển thị |
| 8.2 | Verify giá đơn hàng đầu tiên | **183.296đ** ±1.000đ |

### MH9 — Chi tiết đơn hàng

| Step | Hành động | Expected |
|:---:|:---|:---|
| 9.1 | Click "Chi tiết" | Trang chi tiết hiển thị |
| 9.2 | Verify tên SP, màu, size, qty | PT01 / Trắng / M / 1 |
| 9.3 | Verify Phí vận chuyển | **20.000đ** |
| 9.4 | Verify Giảm giá | **37.800đ** |
| 9.5 | Verify Tổng cộng | **183.296đ** |

### MH11 — Admin verify

| Step | Hành động | Expected |
|:---:|:---|:---|
| 11.1 | Login Admin | OK |
| 11.2 | Tìm đơn theo order_code | Tìm thấy |
| 11.3 | Verify trạng thái | Chờ xác nhận |
| 11.4 | Verify tên SP / màu / size / qty | Khớp |
| 11.5 | Verify tổng tiền | **183.296đ** ±1.000đ |

---

## Luồng 2: Plain / Giỏ hàng

**Màn hình**: MH1 → MH2 → MH3 → MH4 (Thêm vào giỏ) → MH10 (Cart panel) → MH5 → ... → MH11

> Flow tương tự Luồng 1, khác ở MH4: thay vì "Mua ngay" thì "Thêm vào giỏ" → mở cart panel → click "Thanh toán ngay".

**Verify bổ sung tại MH10 (Cart panel)**:

| Step | Hành động | Expected |
|:---:|:---|:---|
| 10.1 | Mở cart panel (click icon Giỏ hàng) | Panel slide-in xuất hiện |
| 10.2 | Verify tên SP trong giỏ | "Áo Phông Cá Tính" |
| 10.3 | Verify màu trong giỏ | Trắng |
| 10.4 | Verify size trong giỏ | M |
| 10.5 | Verify tổng giỏ hàng | **189.000đ** |
| 10.6 | Click "Thanh toán ngay" | Navigate `/checkout` |

---

## Luồng 3: Design / Mua ngay

**Màn hình**: MH1 → MH2 → MH3 (thiết kế) → MH12 (Review) → MH4 (Step 3 Đặt hàng) → MH5 → MH6 → MH7 → MH8 → MH9 → MH11

### MH3 — Studio (thiết kế thực sự)

| Step | Hành động | Expected |
|:---:|:---|:---|
| 3.1 | Click "Thiết kế hình in" → `/studio` | Studio hiển thị |
| 3.2 | Accept điều khoản | Đồng ý |
| 3.3 | Verify canvas visible | Canvas hiển thị |
| 3.4 | Mở library → click hình | Hình được thêm lên canvas |
| 3.5 | Click "Đặt hàng" (hoàn tất thiết kế) | Navigate → MH12 Review |

### MH12 — Xác nhận thiết kế (Review)

| Step | Hành động | Expected |
|:---:|:---|:---|
| 12.1 | Verify Giá áo | **189.000đ** |
| 12.2 | Verify Giá in (DTG) | ~41.000đ (đọc động) |
| 12.3 | Verify Tổng (Áo + In) | ~230.000đ |
| 12.4 | Click "Đặt hàng" | Navigate → MH4 |

### MH4 — Trang Đặt hàng (Studio step 3)

> Đây là trang đầy đủ (không phải popup), hiển thị ảnh áo + size buttons + chi tiết giá.

| Step | Hành động | Expected |
|:---:|:---|:---|
| 4.1 | Verify trang hiển thị (URL chứa `/studio/`) | Step 3 "Đặt hàng" |
| 4.2 | Chọn size M | Size M highlight |
| 4.3 | Verify Tổng (1 sản phẩm) | ~230.000đ |
| 4.4 | Click "Mua ngay" | Navigate `/checkout` |

### MH5 → MH11

> Tương tự Luồng 1 nhưng subtotal = unit_price (áo + in) ~230.000đ thay vì 189.000đ.

---

## Luồng 4: Design / Giỏ hàng

**Màn hình**: MH1 → MH2 → MH3 → MH12 → MH4 (step 3) → MH10 (Cart panel) → MH5 → ... → MH11

### MH4 — Trang Đặt hàng (Studio step 3) — chọn Thêm vào giỏ

| Step | Hành động | Expected |
|:---:|:---|:---|
| 4.1 | Chọn size M | Size M highlight |
| 4.2 | Verify Tổng (1 sản phẩm) | ~230.000đ |
| 4.3 | Click "Thêm vào giỏ" | Toast "Đã thêm vào giỏ hàng!" |

### MH10 — Giỏ hàng (từ Studio header)

| Step | Hành động | Expected |
|:---:|:---|:---|
| 10.1 | Click icon Giỏ hàng trên Studio header | Cart panel slide-in |
| 10.2 | Verify tên SP / màu / size | Áo Phông Cá Tính / Trắng / M |
| 10.3 | Verify tổng giỏ | ~230.000đ |
| 10.4 | Click "Thanh toán ngay" | Navigate `/checkout` |

### MH5 → MH11

> Tương tự Luồng 3.

---

## Chạy test

```bash
# Tất cả PT01
pytest tests/production/price/ -k "pt01" -v -m production --env=test

# Từng luồng
pytest tests/production/price/test_plain_buynow_pt01_trang.py  -v -m production --env=test
pytest tests/production/price/test_design_buynow_pt01_trang.py -v -m production --env=test
pytest tests/production/price/test_design_cart_pt01_trang.py   -v -m production --env=test
```
