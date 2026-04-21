# Daily Smoke — Index

> File test: `tests/smoke/` (split theo màn hình)  
> 31 TC · Mục tiêu hoàn thành trong **3 phút**

## Danh sách file

| File | Nhóm | TC | Số |
|:---|:---|:---|:---:|
| [smoke/MH01_home.md](smoke/MH01_home.md) | 🏠 Trang Chủ | 001, 017, 029 | 3 |
| [smoke/MH02_navigation.md](smoke/MH02_navigation.md) | 🧭 Header · Footer · Trang Phụ | 004, 005, 008, 009, 022, 023, 024 | 7 |
| [smoke/MH03_auth_modal.md](smoke/MH03_auth_modal.md) | 🔐 Auth Modal | 003, 014, 015, 016, 020 | 5 |
| [smoke/MH05_profile.md](smoke/MH05_profile.md) | 👤 Profile / Orders | 012, 013 | 2 |
| [smoke/MH06_studio_canvas.md](smoke/MH06_studio_canvas.md) | 🎨 Studio Canvas | 002, 006, 025, 027, 028, 031 | 6 |
| [smoke/MH07_library.md](smoke/MH07_library.md) | 🖼 Thư Viện & Upload | 018, 019 | 2 |
| [smoke/MH08_checkout.md](smoke/MH08_checkout.md) | 🛒 Đặt hàng & Giỏ hàng | 007, 010, 011, 021, 026, 030 | 6 |

## Cấu hình chạy

```bash
# Toàn bộ 31 TC smoke
pytest tests/smoke/ -v

# Theo từng màn hình
pytest tests/smoke/test_smoke_mh01_home.py -v
pytest tests/smoke/test_smoke_mh02_navigation.py -v
pytest tests/smoke/test_smoke_mh03_auth_modal.py -v
pytest tests/smoke/test_smoke_mh05_profile.py -v
pytest tests/smoke/test_smoke_mh06_studio_canvas.py -v
pytest tests/smoke/test_smoke_mh07_library.py -v
pytest tests/smoke/test_smoke_mh08_checkout.py -v

# Smoke cũ (giữ lại để tương thích CI)
pytest tests/test_daily_smoke.py -v
```
