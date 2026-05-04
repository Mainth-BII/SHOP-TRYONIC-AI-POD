# Production — 🎨 Artwork Placement Scenarios

> File test: `tests/production/test_artwork_scenarios.py` · Class: `TestArtworkScenarios`  
> Data: `data/critical_flows.json["artwork_scenarios"]`  
> Screenshot: `screenshots/production/artwork_scenarios/ARTWORK_00X/`  
> Chạy: `pytest tests/production/test_artwork_scenarios.py --env=test -v`

Bộ test parametrized kiểm tra 3 kịch bản áp artwork lên áo. Mỗi scenario chạy độc lập, dùng chung prompt AI xoay theo ngày.

---

## Data Test (`data/critical_flows.json`)

```json
"artwork_scenarios": [
  {
    "id": "ARTWORK_001",
    "description": "Chỉ áp artwork mặt trước (front only)",
    "apply_front": true,   "apply_back": false,
    "artwork_index_front": 0,   "artwork_index_back": null,
    "color": "Trắng",   "size": "M",   "tax_code": "012345"
  },
  {
    "id": "ARTWORK_002",
    "description": "Chỉ áp artwork mặt sau (back only)",
    "apply_front": false,  "apply_back": true,
    "artwork_index_front": null,  "artwork_index_back": 1,
    "color": "Trắng",   "size": "M",   "tax_code": "012345"
  },
  {
    "id": "ARTWORK_003",
    "description": "Áp artwork cả 2 mặt (both sides)",
    "apply_front": true,   "apply_back": true,
    "artwork_index_front": 0,   "artwork_index_back": 2,
    "color": "Trắng",   "size": "M",   "tax_code": "012345"
  }
]
```

---

## Test Cases

| TC | Scenario | `apply_front` | `apply_back` | Mô tả |
|:---|:---|:---:|:---:|:---|
| **ARTWORK_001** | front_only | ✅ | ❌ | Chỉ áp artwork lên mặt trước — mặt sau để trống |
| **ARTWORK_002** | back_only | ❌ | ✅ | Bỏ qua mặt trước — xoay áo, áp artwork lên mặt sau |
| **ARTWORK_003** | both_sides | ✅ | ✅ | Áp artwork cả 2 mặt (front rồi toggle sang back) |

---

## Luồng chung (tất cả scenario)

| Step | Màn hình | Hành động | Assert | Screenshot |
|:---:|:---|:---|:---|:---|
| S0 | **Home** | Đăng nhập (credentials từ `.env`) | Nút "Đăng nhập" biến mất | `S0` |
| S1 | **Home → Studio** | Fill prompt GenZ → Click "Tạo ngay" | URL chứa `/studio`, canvas visible | `S1` |
| S2 | **Studio** | Chọn màu áo theo `color` trong data | Màu thay đổi (warn nếu không tìm thấy) | `S2` |
| S3 | **Studio** | Chờ AI tạo artwork (tối đa 120s) | ≥ 3 ảnh + ghi thời gian → SKIP nếu thiếu | `S3` |
| S4 | **Studio** | *(xem bảng theo scenario bên dưới)* | *(xem bên dưới)* | `S4` |
| S5a/5b | **Studio** | *(xem bảng theo scenario bên dưới)* | *(xem bên dưới)* | `S5a`, `S5b` |
| S6 | **Studio** | Click "Hoàn tất thiết kế" | Navigate `/review`, nút "Đặt hàng" visible | `S6` |

---

## Bảng S4 + S5 theo scenario

### ARTWORK_001 — Front Only

| Step | Hành động | Assert |
|:---:|:---|:---|
| S4 | Click artwork index **0** trong library panel | Artwork áp lên canvas mặt trước |
| S5a | **Bỏ qua** — `apply_back=false` | Screenshot "front_artwork_skipped" |

### ARTWORK_002 — Back Only

| Step | Hành động | Assert |
|:---:|:---|:---|
| S4 | **Bỏ qua** — `apply_front=false` | Screenshot "back_artwork_skipped" |
| S5a | Click "Xoay áo" → mặt sau | View chuyển mặt sau |
| S5b | Click artwork index **1** trong library panel | Artwork áp lên canvas mặt sau |

### ARTWORK_003 — Both Sides

| Step | Hành động | Assert |
|:---:|:---|:---|
| S4 | Click artwork index **0** trong library panel | Artwork áp lên canvas mặt trước |
| S5a | Click "Xoay áo" → mặt sau | View chuyển mặt sau |
| S5b | Click artwork index **2** trong library panel | Artwork áp lên canvas mặt sau |

---

## Điều kiện SKIP

| Điều kiện | Kết quả |
|:---|:---|
| Thiếu credentials trong `.env` | **SKIP** toàn bộ scenario |
| AI gen < 3 ảnh sau 120s | **SKIP** scenario đó |
| Nút "Xoay áo" không hiển thị (S5) | **INFO** log — bỏ qua mặt sau, test tiếp tục |
| `click_artwork` thất bại (S4) | **FAIL** nếu `apply_front=true` |

---

## Cấu trúc Screenshot

```
screenshots/production/artwork_scenarios/
├── ARTWORK_001/
│   ├── S0_after_login_HHMMSS.png
│   ├── S1_studio_navigated_HHMMSS.png
│   ├── S2_color_Trắng_HHMMSS.png
│   ├── S3_artworks_Nimgs_Xs_HHMMSS.png
│   ├── S4_front_artwork_idx0_applied_HHMMSS.png
│   ├── S5a_back_artwork_skipped_HHMMSS.png        ← apply_back=false
│   └── S6_review_page_HHMMSS.png
├── ARTWORK_002/
│   ├── S0_after_login_HHMMSS.png
│   ├── S1_studio_navigated_HHMMSS.png
│   ├── S2_color_Trắng_HHMMSS.png
│   ├── S3_artworks_Nimgs_Xs_HHMMSS.png
│   ├── S4_front_artwork_skipped_HHMMSS.png        ← apply_front=false
│   ├── S5a_shirt_back_view_HHMMSS.png
│   ├── S5b_back_artwork_idx1_applied_HHMMSS.png
│   └── S6_review_page_HHMMSS.png
└── ARTWORK_003/
    ├── S0_after_login_HHMMSS.png
    ├── S1_studio_navigated_HHMMSS.png
    ├── S2_color_Trắng_HHMMSS.png
    ├── S3_artworks_Nimgs_Xs_HHMMSS.png
    ├── S4_front_artwork_idx0_applied_HHMMSS.png
    ├── S5a_shirt_back_view_HHMMSS.png
    ├── S5b_back_artwork_idx2_applied_HHMMSS.png
    └── S6_review_page_HHMMSS.png
```

---

## Thay đổi data test

Để thay đổi artwork index, màu, size — chỉ sửa `data/critical_flows.json`, không cần đụng code.

| Field | Ý nghĩa | Ví dụ |
|:---|:---|:---|
| `artwork_index_front` | Index ảnh trong library panel (0-based, bỏ qua "Thêm ảnh") | `0` = ảnh đầu tiên |
| `artwork_index_back` | Index ảnh trong library panel cho mặt sau | `1` = ảnh thứ hai |
| `apply_front` | `true` = áp artwork mặt trước | — |
| `apply_back` | `true` = xoay sang mặt sau và áp artwork | — |
| `color` | Tên màu áo cần chọn | `"Trắng"`, `"Đen"` |
| `size` | Size áo | `"M"`, `"L"`, `"XL"` |
