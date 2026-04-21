# MH09 — 🤖 AI Features: Tạo Artwork, Công Nghệ In, Tryon, Gợi Ý Size

> File test: `tests/smoke/test_smoke_mh09_ai_features.py` · Class: `TestAIFeatures`

| TC | Tính năng | Mô tả | Kết quả mong đợi |
|:---|:---|:---|:---|
| **TC_039** | Tạo artwork | Prompt → AI gen → artwork hiển thị trên áo | Nút "Hoàn tất thiết kế" ENABLED sau gen |
| **TC_041** | Công nghệ in | Thông tin kỹ thuật in accessible trên site | Tìm thấy content in ấn hoặc [WARN] nếu chưa có |
| **TC_042** | Tryon | Virtual try-on mockup hiển thị trong Studio/product | Tryon element visible hoặc [WARN] |
| **TC_043** | Gợi ý size | Size guide / size suggestion accessible từ /product | Size chart hiển thị, không crash |

> **Lưu ý markers**: TC_039 dùng `@pytest.mark.artwork @pytest.mark.slow` (AI gen ~90s).
> TC_041–043 thuộc `@pytest.mark.smoke @pytest.mark.daily`.

---

### [TC_DAILY_039] Tạo Artwork — Full AI Generation Flow

- **S1**: Navigate `/studio?category=t-shirts` → accept terms → chụp `S1_studio_before_gen`.
- **S2**: Fill textarea prompt → click "Tạo" / Enter.
- **S3**: Poll 18×5s (90s max) cho `button:has-text('Hoàn tất thiết kế')` chuyển ENABLED. Chụp `gen2_generation_complete`.
- **S4**: ASSERT nút ENABLED (= gen xong). Chụp `S2_generation_done_btn_enabled`.
- **S5**: Kiểm tra `img[src*='tryon'], img[src*='artwork'], canvas` visible → chụp `S3_artwork_on_shirt`.
- **PASS**: Nút ENABLED. **[WARN]** nếu không tìm thấy img nhưng nút đã enabled.

---

### [TC_DAILY_041] Công Nghệ In — Thông Tin In Accessible

- **S1**: Lần lượt thử các URL: `/`, `/cong-nghe-in`, `/in-the-nao`, `/huong-dan-mua-hang`, `/product`.
- **S2**: Tại mỗi URL (status ≠ 404/500): tìm `:text('Công nghệ in')`, `:text('DTF')`, `:text('In kỹ thuật số')`, `:text('Thêu vi tính')`.
- **S3**: Chụp `S1_cong_nghe_in_result`.
- **PASS**: Tìm thấy content tại bất kỳ URL nào. **[WARN]** nếu không tìm thấy — trang không crash là đủ.

---

### [TC_DAILY_042] Tryon — Virtual Try-On Feature

- **S1**: Navigate Studio → accept terms → chụp `S1_studio_for_tryon`.
- **S2**: Tìm `img[src*='tryon'], button:has-text('Thử áo'), button:has-text('Xem trên người'), [class*='tryon']`.
- **S3**: Nếu tìm thấy → chụp `S2_tryon_found_in_studio` → **PASS**.
- **S4**: Fallback: navigate `/product` → tìm tryon element → chụp `S2_product_for_tryon`.
- **PASS**: Tryon element tìm thấy. **[WARN]** nếu chỉ xuất hiện sau khi gen artwork — trang không crash là đủ.

---

### [TC_DAILY_043] Gợi Ý Size — Size Guide Accessible

- **S1**: Navigate `/product` → chụp `S1_product_page_loaded`.
- **S2**: Tìm `button:has-text('Gợi ý size')`, `button:has-text('Hướng dẫn chọn size')`, `a:has-text('Size guide')`, `[class*='size-guide']`.
- **S3a**: Nếu tìm thấy → click → chờ 2s → chụp `S3_size_guide_opened` → kiểm tra `[role='dialog']` / `table` / `:text('cm')`.
- **S3b**: Nếu không → kiểm tra size chart inline (`table`, `:text('38/40/42')`). Chụp `S2_size_chart_inline`.
- **S4**: ASSERT `h1:has-text('500')` không visible (tránh false positive bảng size).
- **PASS**: Size guide/chart tồn tại, không crash. **[WARN]** nếu cả hai đều không tìm thấy.
