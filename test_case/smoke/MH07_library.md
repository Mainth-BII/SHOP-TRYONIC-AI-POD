# MH07 — 🖼 Thư Viện & Upload (Smoke)

> File test: `tests/smoke/test_smoke_mh07_library.py` · Class: `TestSmokeMH07Library`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_018** | Library panel | Nút "Thư Viện" mở được panel, có nội dung bên trong |
| **TC_019** | Upload input | `input[type='file']` tồn tại trong DOM sau khi mở Library |

---

### [TC_DAILY_018] Thư Viện — Panel mở thành công

- **S1**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây.
- **S2**: Tìm `button:has-text('Thư Viện')` → xác nhận hiển thị (10s).
- **S3**: Click nút → chờ 2 giây. Chụp `S1_library_opened`.
- **S4**: Panel có nội dung: `[class*='library']` / `[class*='gallery']` / text "Ảnh của bạn" / "Thêm ảnh" hiển thị (8s). Chụp `S2_library_content_visible`.

---

### [TC_DAILY_019] Upload — Input tồn tại trong DOM

- **S1**: Navigate `/studio?category=t-shirts` → chờ load + 3 giây.
- **S2**: Click nút "Thư Viện" nếu thấy → chờ 2 giây. Chụp `S1_library_for_upload`.
- **S3**: Đếm `input[type='file']` → FAIL nếu `count == 0`.
- **S4**: Tìm upload trigger (button "Tải lên" / label / text "Tải ảnh lên") → log `[PASS]` nếu thấy, không FAIL nếu không thấy. Chụp `S2_upload_trigger_state`.

> **Lưu ý:** TC_019 chỉ kiểm tra sự tồn tại của `input[type='file']` trong DOM. Không thực sự upload file.
