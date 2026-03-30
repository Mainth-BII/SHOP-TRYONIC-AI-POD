import csv

new_tcs = [
    ['TC_DES_UI_029', 'US-15', 'EDITOR', 'Canvas', 'Canvas: Zoom In / Zoom Out (Phóng to / Thu nhỏ)', 'UI/UX', 'P1', 'Có 1 layer trên Canvas', 'Zoom 200%, 50%', '1. Dùng chuột cuộn (Ctrl + Scroll) hoặc click nút +/- trên UI\n2. Quan sát độ thu phóng', 'Canvas và các layer phóng to/thu nhỏ mượt mà. Tâm zoom focus vào vị trí chuột / giữa màn hình'],
    ['TC_DES_UI_030', 'US-15', 'EDITOR', 'Canvas', 'Canvas: Pan (Di chuyển vùng nhìn khi Zoom)', 'UI/UX', 'P1', 'Canvas đang được Zoom In > 100%', '', '1. Giữ phím Space + Drag chuột (hoặc dùng Hand Tool)\n2. Kéo thả vùng nhìn', 'Vùng nhìn di chuyển mượt mà lên/xuống/trái/phải để xem các góc khác của thiết kế'],
    ['TC_DES_UI_031', 'US-15', 'EDITOR', 'Canvas', 'Canvas: Smart Guides (Bắt dính thông minh)', 'UI/UX', 'P1', 'Có 1 layer trên Canvas', '', '1. Kéo layer vào chính giữa Canvas (Vertical/Horizontal)\n2. Kéo ngang hàng với một layer khác', 'Hiển thị các đường viền đỏ/xanh (Guides) tự động bắt dính báo hiệu layer đã vô giữa hoặc ngay ngắn'],
    ['TC_DES_UI_032', 'US-15', 'EDITOR', 'Canvas', 'Canvas: Keyboard Shortcuts cơ bản', 'UI/UX', 'P1', 'Đang chọn 1 layer', 'Ctrl+C, Ctrl+V, Del', '1. Nhấn Delete/Backspace\n2. Nhấn Ctrl+Z / Ctrl+Y\n3. Nhấn Ctrl+C rồi Ctrl+V', '1. Layer bị xóa\n2. Undo/Redo chính xác\n3. Layer được copy/paste ngay cạnh layer gốc'],
    ['TC_DES_UI_033', 'US-15', 'EDITOR', 'Layers', 'Layers: Điều chỉnh Opacity (Độ trong suốt)', 'UI/UX', 'P2', 'Chọn 1 layer hình ảnh', 'Opacity 50%', '1. Kéo thanh trượt Opacity xuống 50%\n2. Quan sát Canvas', 'Layer mờ đi 50%, hiển thị nhạt và thấy được màu áo / layer bên dưới']
]

with open('TC_POD-TShirt-Platform_v4_2026-03-13.csv', mode='a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(new_tcs)

print('Added missing UI/UX test cases successfully.')
