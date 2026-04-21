# MH02 — 🧭 Header · Footer · Điều hướng (Smoke)

> File test: `tests/smoke/test_smoke_mh02_navigation.py` · Class: `TestSmokeMH02Navigation`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_004** | Header Navigation | Logo + Sản phẩm + Chính sách + Hướng dẫn + Đăng nhập hiển thị |
| **TC_005** | Footer Links | 7 link chính sách & hỗ trợ hiển thị |
| **TC_008** | Trang CSKH & Về Tryonic | Cả 2 trang load, không 404 |
| **TC_009** | Care Guide | Load được, có h1/h2/main |
| **TC_022** | Policy pages (4 trang) | Mỗi trang có nội dung thực, không trắng/404 |
| **TC_023** | 404 error handling | Server không crash 500, trả về 404 UI hoặc redirect |
| **TC_024** | Hướng dẫn mua hàng | Load được, có h1/h2/main, không 404/500 |

---

### [TC_DAILY_004] Header — Kiểm tra điều hướng

> Cấu trúc: Logo | Sản phẩm | Chính sách ▾ | Hướng dẫn ▾ | Về Tryonic AI | Đăng nhập | 🛒

- **S1**: Trang chủ → chờ load. Chụp ảnh `S1_header_before_check`.
- **S2**: `<header>` tồn tại và hiển thị.
- **S3**: Logo, Sản phẩm, Chính sách dropdown, Hướng dẫn dropdown, Về Tryonic AI, Đăng nhập — mỗi phần tử hiển thị.
- **S4**: Hover Chính sách → chụp `S2_header_chinh_sach_dropdown`. Hover Hướng dẫn → chụp `S3_header_huong_dan_dropdown`.
- **S5**: Chụp `S4_header_all_verified`.
- **S6**: Kiểm tra 4 sub-link Chính sách tồn tại trong DOM (`count() > 0`).

> Lưu ý: Sub-link dùng `count()` vì dropdown chỉ hiện khi hover.

---

### [TC_DAILY_005] Footer — Kiểm tra 7 link

- **S1**: Trang chủ → scroll xuống footer. Chụp ảnh `S1_footer_visible`.
- **S2**: Kiểm tra 7 link: Chính sách thanh toán · vận chuyển · đổi trả · bảo mật · Hướng dẫn mua hàng · bảo quản · Liên hệ CSKH.
- **S3**: Bất kỳ link nào không thấy → WARN + FAIL cuối cùng. Chụp `S2_footer_links_verified`.

---

### [TC_DAILY_008] Liên hệ CSKH & Về Tryonic AI

- **S1**: Navigate `/pages/lien-he-cskh` → không có `"404"`. Chụp `S1_lien_he_page`.
- **S2**: Quay Home → click **"Về Tryonic AI"** trong header.
- **S3**: Không có `"404"`. Chụp `S2_ve_tryonic_ai_page`.

---

### [TC_DAILY_009] Hướng dẫn bảo quản

- **S1**: Navigate `/care-guide` → không `"404"`.
- **S2**: Có ít nhất `h1`/`h2`/`main`/`article`. Chụp `S1_care_guide_loaded`.

---

### [TC_DAILY_022] Policy Pages — 4 trang có nội dung thực

Lần lượt navigate đến 4 trang → mỗi trang kiểm tra:
- HTTP ≠ 404/500
- Không hiển thị text "404" / "Not Found"
- Có `h1`/`h2`/`main`/`article`/`p`

FAIL tổng hợp tất cả lỗi trong một lần assert. Chụp ảnh trang cuối.

> Tại sao: TC_004/005 chỉ check link *hiển thị*, không verify nội dung trang. CMS deploy hay làm trang trắng.

---

### [TC_DAILY_023] 404 Error Handling

- **S1**: Navigate đến `/trang-nay-khong-ton-tai-tryonic-smoke-xyz-9999`. Chụp `S1_404_page_state`.
- **S2**: HTTP ≠ 500, không có text `"Internal Server Error"`.
- **S3**: PASS nếu HTTP 404 **HOẶC** UI 404 **HOẶC** redirect Home. FAIL duy nhất: 500.

---

### [TC_DAILY_024] Hướng dẫn mua hàng

- **S1**: Navigate `/pages/huong-dan-mua-hang` → HTTP ≠ 404/500. Chụp `S1_huong_dan_mua_hang_loaded`.
- **S2**: Không có text "404". Có `h1`/`h2`/`main`/`article`.
