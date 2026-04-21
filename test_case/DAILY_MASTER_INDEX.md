# Daily Test — Master Index (Phân loại theo Màn hình)

> **Mục đích:** Tra cứu nhanh toàn bộ 64 TC, nhóm theo màn hình / tính năng.  
> **Legend:** 🔵 Smoke (availability, nhanh) · 🟢 Functional (luồng thực) · 🔴 Security

---

## Tổng quan

| # | Nhóm màn hình | TC Range | Số TC | File |
|:---:|:---|:---:|:---:|:---|
| MH01 | 🏠 Trang Chủ | TC_001, 017, 029, 040 | 4 | smoke / generate |
| MH02 | 🧭 Header · Footer · Điều hướng | TC_004–005, 008–009, 022–024 | 7 | smoke |
| MH03 | 🔐 Auth Modal (Đăng nhập / Đăng ký) | TC_003, 014–016, 020 | 5 | smoke |
| MH04 | 🔐 Auth Functional (Login thực) | TC_060–061, 064–069 | 8 | auth |
| MH05 | 👤 Tài khoản & Đơn hàng của tôi | TC_012–013, 062–063 | 4 | smoke / auth |
| MH06 | 🎨 Studio — Giao diện & Canvas | TC_002, 006, 025, 027–028, 031, 041–042, 070, 072–074 | 12 | smoke / generate / customize |
| MH07 | 🖼 Studio — Thư Viện & AI Generate | TC_018–019, 043–047, 071 | 8 | smoke / generate / customize |
| MH08 | 🛒 Studio — Đặt hàng & Checkout | TC_007, 010–011, 021, 026, 030, 050–059 | 16 | smoke / order |
| INFRA | ⚙️ Technical / Infrastructure *(tham chiếu)* | TC_023, 028–029, 031 | 4 | smoke |
| | **TỔNG** | | **64 TC** | |

---

## MH01 — 🏠 Trang Chủ (Home)

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_001** | Home page load được, không 404/500, có nội dung chính | 🔵 Smoke | smoke |
| **TC_017** | Nhập AI prompt → click "Tạo ngay" → loading/navigate khởi động | 🔵 Smoke | smoke |
| **TC_029** | SEO meta tags: `<title>`, `description`, `og:title`, `og:image` không rỗng | 🔵 Smoke | smoke |
| **TC_040** | Home → nhập prompt → click "Tạo ngay" → navigate sang `/studio/<uuid>` | 🟢 Functional | generate |

---

## MH02 — 🧭 Header · Footer · Điều hướng

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_004** | Header: Logo · Sản phẩm · Chính sách (dropdown) · Hướng dẫn · Về Tryonic AI · Đăng nhập | 🔵 Smoke | smoke |
| **TC_005** | Footer: 7 link Chính sách & Hỗ trợ hiển thị đầy đủ | 🔵 Smoke | smoke |
| **TC_008** | Trang CSKH (`/pages/lien-he-cskh`) + Về Tryonic AI load, không 404 | 🔵 Smoke | smoke |
| **TC_009** | Trang Care Guide (`/care-guide`) load, có h1/h2/main | 🔵 Smoke | smoke |
| **TC_022** | 4 trang Chính sách navigate được và có nội dung thực (không trắng) | 🔵 Smoke | smoke |
| **TC_023** | URL không tồn tại → 404 UI, server không crash 500 | 🔵 Smoke | smoke |
| **TC_024** | Trang Hướng dẫn mua hàng (`/pages/huong-dan-mua-hang`) load, có nội dung | 🔵 Smoke | smoke |

---

## MH03 — 🔐 Auth Modal (Smoke — Đăng nhập / Đăng ký / Quên mật khẩu)

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_003** | Mở Login modal từ Header → có Email · Password · Submit · Google · Facebook | 🔵 Smoke | smoke |
| **TC_014** | Login modal → click "Đăng ký" → form Tạo tài khoản hiển thị | 🔵 Smoke | smoke |
| **TC_015** | Login modal → click "Quên mật khẩu" → form reset email hiển thị | 🔵 Smoke | smoke |
| **TC_016** | Nút Google/Facebook → popup mở đúng domain (`google.com` / `facebook.com`) | 🔵 Smoke | smoke |
| **TC_020** | Trang Đổi mật khẩu (`/profile` / `/account`) accessible hoặc redirect hợp lệ | 🔵 Smoke | smoke |

---

## MH04 — 🔐 Auth Functional (Login thực tế · Social · Bảo mật)

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_060** | Điền email + password đúng → submit → login thành công | 🟢 Functional | auth |
| **TC_061** | Điền sai mật khẩu → submit → hiển thị error message, không crash | 🟢 Functional | auth |
| **TC_064** | Login từ Studio (click User icon) → modal mở | 🟢 Functional | auth |
| **TC_065** | Login từ Checkout (click "Mua ngay" khi chưa đăng nhập) → modal/redirect | 🟢 Functional | auth |
| **TC_066** | Google login popup → điền email → màn hình password Google | 🟢 Functional | auth |
| **TC_067** | Facebook login popup → verify URL `facebook.com` | 🟢 Functional | auth |
| **TC_068** | Nhập sai 7 lần liên tiếp → hiển thị thông báo khóa tài khoản | 🔴 Security | auth |
| **TC_069** | Đăng nhập thực → click Đăng xuất → trạng thái guest khôi phục | 🟢 Functional | auth |

---

## MH05 — 👤 Tài khoản & Đơn hàng của tôi

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_012** | `/profile` load được hoặc redirect về login — không 404/500 | 🔵 Smoke | smoke |
| **TC_013** | `/my-orders` load được hoặc redirect về login — không 404/500 | 🔵 Smoke | smoke |
| **TC_062** | Đã đăng nhập → `/profile` → hiển thị thông tin tài khoản | 🟢 Functional | auth |
| **TC_063** | Đã đăng nhập → `/my-orders` → hiển thị danh sách đơn hoặc "Chưa có đơn" | 🟢 Functional | auth |

---

## MH06 — 🎨 Studio — Giao diện & Canvas

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_002** | Studio T-shirt load, canvas/main hiển thị | 🔵 Smoke | smoke |
| **TC_006** | Studio Product page (`?view=product`) load, có nội dung sản phẩm | 🔵 Smoke | smoke |
| **TC_025** | Studio Hoodie category load, canvas hiển thị | 🔵 Smoke | smoke |
| **TC_027** | Ảnh mockup sản phẩm render thành công (`naturalWidth > 0`) | 🔵 Smoke | smoke |
| **TC_028** | Mobile viewport 390×844: Home + Studio không crash | 🔵 Smoke | smoke |
| **TC_031** | Page load timing: Home < 8s · Studio < 12s · Policy < 6s | 🔵 Smoke | smoke |
| **TC_041** | Canvas + nút "Đặt hàng" + Sidebar đều hiển thị | 🟢 Functional | generate |
| **TC_042** | Toggle Mặt trước ↔ Mặt sau hoạt động | 🟢 Functional | generate |
| **TC_070** | Đổi màu sản phẩm (color swatches) cập nhật UI | 🟢 Functional | customize |
| **TC_072** | Đổi category T-shirt → Hoodie: URL/UI thay đổi, canvas còn | 🟢 Functional | customize |
| **TC_073** | Artwork Mặt trước ≠ Mặt sau (isolation giữa 2 mặt) | 🟢 Functional | customize |
| **TC_074** | Click Artwork trên Canvas → hiển thị handle Resize · Rotate · Delete | 🟢 Functional | customize |

---

## MH07 — 🖼 Studio — Thư Viện & AI Generate

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_018** | Nút "Thư Viện" mở panel, có nội dung | 🔵 Smoke | smoke |
| **TC_019** | `input[type='file']` tồn tại trong DOM (upload khả dụng) | 🔵 Smoke | smoke |
| **TC_043** | Library mở, tab AI hiển thị | 🟢 Functional | generate |
| **TC_044** | Polling chờ AI tạo ảnh xong (≤75s) → ≥1 ảnh badge "AI" xuất hiện | 🟢 Functional | generate |
| **TC_045** | Hover ảnh AI → click "Thay thế" → ảnh áp lên Canvas | 🟢 Functional | generate |
| **TC_046** | Sửa prompt trong Studio → click "Tạo" → trạng thái "Đang tạo" xuất hiện | 🟢 Functional | generate |
| **TC_047** | Upload ảnh thủ công (PIL image) → hiển thị trong Library | 🟢 Functional | generate |
| **TC_071** | Studio → Đặt hàng → click "Bảng size" → modal hiển thị thông số | 🟢 Functional | customize |

---

## MH08 — 🛒 Studio — Đặt hàng & Checkout

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_007** | Nút "Đặt hàng" mở Order modal/form | 🔵 Smoke | smoke |
| **TC_010** | Studio → Đặt hàng → Mua ngay → Checkout form hiển thị | 🔵 Smoke | smoke |
| **TC_011** | Nút "Thêm vào giỏ" → không crash, có phản hồi | 🔵 Smoke | smoke |
| **TC_021** | Trang `/cart` (giỏ hàng) accessible, không 404/500 | 🔵 Smoke | smoke |
| **TC_026** | Giá trong Order modal ≠ `undefined` / `NaN` / `null` | 🔵 Smoke | smoke |
| **TC_030** | Cart badge số lượng tăng sau khi "Thêm vào giỏ" | 🔵 Smoke | smoke |
| **TC_050** | Order modal mở ra từ Studio (functional confirm) | 🟢 Functional | order |
| **TC_051** | Chọn size S → giá hiển thị > 0 | 🟢 Functional | order |
| **TC_052** | Click "Mua ngay" → Checkout form xuất hiện | 🟢 Functional | order |
| **TC_053** | Checkout form điền được: Tên · SĐT · Email | 🟢 Functional | order |
| **TC_054** | Đã đăng nhập → Checkout → "Thêm địa chỉ mới" → Lưu thành công | 🟢 Functional | order |
| **TC_055** | Guest → Checkout → điền thông tin → Thanh toán → QR hiển thị | 🟢 Functional | order |
| **TC_056** | Đã đăng nhập → Checkout (địa chỉ tự điền) → Thanh toán → QR | 🟢 Functional | order |
| **TC_057** | Guest → QR → Hủy thanh toán → Xem đơn hàng → trạng thái đúng | 🟢 Functional | order |
| **TC_058** | Đã đăng nhập → QR → Hủy → "Quay lại thiết kế" → Studio | 🟢 Functional | order |
| **TC_059** | Chọn size/qty → Mua ngay → Back trình duyệt → state giữ nguyên | 🟢 Functional | order |

---

## INFRA — ⚙️ Technical / Infrastructure

| TC | Mô tả | Loại | File |
|:---|:---|:---:|:---|
| **TC_023** | URL không tồn tại → 404 UI, không crash 500 *(cũng ở MH02)* | 🔵 Smoke | smoke |
| **TC_028** | Mobile viewport 390×844: Home + Studio không crash *(cũng ở MH06)* | 🔵 Smoke | smoke |
| **TC_029** | SEO meta tags *(cũng ở MH01)* | 🔵 Smoke | smoke |
| **TC_031** | Page load performance baseline *(cũng ở MH06)* | 🔵 Smoke | smoke |

---

## Ma trận Màn hình × Loại test

```
Nhóm                          Smoke  Functional  Security  Tổng
────────────────────────────────────────────────────────────────
MH01  Trang Chủ                  3       1           -        4
MH02  Header · Footer · Điều hướng 7      -           -        7
MH03  Auth Modal                 5       -           -        5
MH04  Auth Functional            -       7           1        8
MH05  Profile / Orders           2       2           -        4
MH06  Studio Canvas              6       6           -       12
MH07  Studio Library & AI        2       6           -        8
MH08  Studio Checkout            6      10           -       16
────────────────────────────────────────────────────────────────
TỔNG                            31      32           1  =  64 TC
```

> **INFRA** (TC_023, TC_028, TC_029, TC_031) là tham chiếu chéo — đã được tính trong
> MH02 / MH06 / MH01 ở trên, không cộng thêm vào tổng.

---

## Thứ tự chạy đề xuất (Daily pipeline)

```bash
# 1. Gate check — nếu fail dừng toàn bộ pipeline
pytest tests/test_daily_smoke.py -v -x --timeout=300

# 2. Core flows — chạy song song nếu đủ worker
pytest tests/test_daily_generate.py -v --timeout=180
pytest tests/test_daily_order.py    -v --timeout=300
pytest tests/test_daily_auth.py     -v --timeout=180
pytest tests/test_daily_customize.py -v --timeout=120

# 3. Chạy toàn bộ 64 TC một lần
pytest tests/test_daily_*.py -v --timeout=600

# 4. Chạy theo màn hình cụ thể (dùng -k filter theo ID)
pytest tests/ -k "040 or 041 or 042 or 043 or 044 or 045 or 046 or 047" -v  # AI Generate
pytest tests/ -k "050 or 051 or 052 or 053 or 054 or 055 or 056 or 057 or 058 or 059" -v  # Order
pytest tests/ -k "060 or 061 or 062 or 063 or 064 or 065 or 066 or 067 or 068 or 069" -v  # Auth
```

---

## File map

| File | Class | TC Range | Màn hình chính |
|:---|:---|:---|:---|
| `test_daily_smoke.py` | `TestDailySmoke` | TC_001–TC_031 | Tất cả màn hình (availability) |
| `test_daily_generate.py` | `TestDailyGenerate` | TC_040–TC_047 | Home AI + Studio Library |
| `test_daily_order.py` | `TestDailyOrder` | TC_050–TC_059 | Studio Đặt hàng + Checkout |
| `test_daily_auth.py` | `TestDailyAuth` | TC_060–TC_069 | Auth Modal + Profile |
| `test_daily_customize.py` | `TestDailyCustomize` | TC_070–TC_074 | Studio Canvas + Thư Viện |
