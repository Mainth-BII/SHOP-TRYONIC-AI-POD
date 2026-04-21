# MH05 — 👤 Profile / Orders (Smoke)

> File test: `tests/smoke/test_smoke_mh05_profile.py` · Class: `TestSmokeMH05Profile`

| TC | Mô tả | Kết quả mong đợi |
|:---|:---|:---|
| **TC_012** | Profile | `/profile` load hoặc redirect login — không 404/500 |
| **TC_013** | Đơn hàng | `/my-orders` load hoặc redirect login — không 404/500 |

> **Lưu ý:** Đây là Smoke check — chỉ verify không bị 404/500. Functional tests (TC_062, TC_063) với đăng nhập thực nằm trong `tests/test_daily_auth.py`.

---

### [TC_DAILY_012] Profile — Load hoặc redirect hợp lệ

- **S1**: Navigate `/profile` → chờ load + 2 giây. Chụp `S1_profile_page`.
- **S2**: Không có `404` / `Not Found` / `500` / `Internal Server Error`.
- **S3**: PASS nếu: hiển thị nội dung profile **HOẶC** redirect về login/home.

---

### [TC_DAILY_013] Đơn hàng của tôi — Load hoặc redirect hợp lệ

- **S1**: Navigate `/my-orders` → chờ load + 2 giây. Chụp `S1_my_orders_page`.
- **S2**: Không có `404` / `Not Found` / `500` / `Internal Server Error`.
- **S3**: PASS nếu: hiển thị danh sách đơn **HOẶC** redirect về login/home.
