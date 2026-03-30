"""Dữ liệu test Gợi ý Size - Tiếng Việt."""

COLUMNS_SIZE = [
    "STT",
    "Danh mục Test",
    "TC_ID",
    "Giới tính",
    "Chiều cao (cm)",
    "Cân nặng (kg)",
    "Size kỳ vọng",
    "Mô tả kịch bản",
    "Độ ưu tiên",
    "Expected_Result",
    "Actual_Result",
    "Ghi chú"
]
COL_WIDTHS_SIZE = [5, 28, 14, 12, 16, 16, 14, 45, 10, 16, 16, 35]

# ============================================================
# Bảng size chuẩn (tham khảo thị trường Việt Nam / Châu Á):
#   XS: 150-158cm, 40-50kg
#   S:  155-163cm, 48-58kg
#   M:  160-170cm, 55-68kg
#   L:  167-175cm, 65-78kg
#   XL: 172-180cm, 75-90kg
#   XXL: 178-188cm, 85-105kg
# Nữ thường nhỏ hơn Nam 1 bậc ở cùng chiều cao/cân nặng
# ============================================================

SIZE_TEST_DATA = {
    "📏 TRƯỜNG HỢP CHUẨN — NAM": [
        # (tc_id, gender, height, weight, expected_size, desc, priority, notes)
        ("TC_SZ_001", "Nam", 155, 45, "XS", "Nam nhỏ nhất: thấp và nhẹ → XS", "P0", "Boundary min cho Nam"),
        ("TC_SZ_002", "Nam", 158, 50, "S", "Nam nhỏ: chiều cao TB thấp, cân nặng nhẹ → S", "P0", ""),
        ("TC_SZ_003", "Nam", 163, 58, "S", "Nam nhỏ-vừa: chiều cao dưới TB, cân vừa → S", "P1", ""),
        ("TC_SZ_004", "Nam", 165, 60, "M", "Nam trung bình Việt Nam: 165cm/60kg → M", "P0", "Case phổ biến nhất VN"),
        ("TC_SZ_005", "Nam", 168, 63, "M", "Nam TB: chiều cao TB, cân nặng TB → M", "P0", ""),
        ("TC_SZ_006", "Nam", 170, 68, "M", "Nam TB-cao: 170/68 → M hoặc L", "P1", "Ranh giới M/L"),
        ("TC_SZ_007", "Nam", 172, 72, "L", "Nam cao-vừa: 172/72 → L", "P0", ""),
        ("TC_SZ_008", "Nam", 175, 75, "L", "Nam cao: 175/75 → L", "P0", ""),
        ("TC_SZ_009", "Nam", 178, 80, "XL", "Nam cao-to: 178/80 → XL", "P0", ""),
        ("TC_SZ_010", "Nam", 180, 85, "XL", "Nam rất cao: 180/85 → XL", "P1", ""),
        ("TC_SZ_011", "Nam", 183, 90, "XXL", "Nam to lớn: 183/90 → XXL", "P0", ""),
        ("TC_SZ_012", "Nam", 188, 100, "XXL", "Nam rất to: 188/100 → XXL", "P1", "Boundary max bình thường"),
    ],

    "📏 TRƯỜNG HỢP CHUẨN — NỮ": [
        ("TC_SZ_013", "Nữ", 150, 40, "XS", "Nữ nhỏ nhất: 150/40 → XS", "P0", "Boundary min cho Nữ"),
        ("TC_SZ_014", "Nữ", 153, 45, "XS", "Nữ nhỏ: 153/45 → XS", "P1", ""),
        ("TC_SZ_015", "Nữ", 155, 48, "S", "Nữ nhỏ-vừa: 155/48 → S", "P0", ""),
        ("TC_SZ_016", "Nữ", 158, 50, "S", "Nữ TB Việt Nam: 158/50 → S", "P0", "Case phổ biến nhất VN Nữ"),
        ("TC_SZ_017", "Nữ", 160, 53, "M", "Nữ TB: 160/53 → M", "P0", ""),
        ("TC_SZ_018", "Nữ", 163, 55, "M", "Nữ TB-cao: 163/55 → M", "P1", ""),
        ("TC_SZ_019", "Nữ", 165, 60, "L", "Nữ cao: 165/60 → L", "P0", ""),
        ("TC_SZ_020", "Nữ", 168, 65, "L", "Nữ cao-vừa: 168/65 → L", "P1", ""),
        ("TC_SZ_021", "Nữ", 170, 70, "XL", "Nữ cao-to: 170/70 → XL", "P0", ""),
        ("TC_SZ_022", "Nữ", 173, 75, "XL", "Nữ rất cao: 173/75 → XL", "P1", ""),
        ("TC_SZ_023", "Nữ", 175, 80, "XXL", "Nữ to lớn: 175/80 → XXL", "P0", ""),
        ("TC_SZ_024", "Nữ", 178, 85, "XXL", "Nữ rất to: 178/85 → XXL", "P1", ""),
    ],

    "⚖️ RANH GIỚI SIZE (Boundary)": [
        ("TC_SZ_025", "Nam", 158, 50, "XS/S", "Ranh giới XS↔S Nam: đúng ngưỡng chuyển", "P0", "Kiểm tra logic chuyển size"),
        ("TC_SZ_026", "Nam", 163, 58, "S/M", "Ranh giới S↔M Nam: chiều cao gần M, cân S", "P0", ""),
        ("TC_SZ_027", "Nam", 170, 70, "M/L", "Ranh giới M↔L Nam: đúng ngưỡng", "P0", "Case nhạy cảm nhất"),
        ("TC_SZ_028", "Nam", 176, 78, "L/XL", "Ranh giới L↔XL Nam: đúng ngưỡng", "P0", ""),
        ("TC_SZ_029", "Nam", 180, 88, "XL/XXL", "Ranh giới XL↔XXL Nam: đúng ngưỡng", "P0", ""),
        ("TC_SZ_030", "Nữ", 155, 48, "XS/S", "Ranh giới XS↔S Nữ: đúng ngưỡng", "P0", ""),
        ("TC_SZ_031", "Nữ", 160, 53, "S/M", "Ranh giới S↔M Nữ: đúng ngưỡng", "P0", ""),
        ("TC_SZ_032", "Nữ", 165, 60, "M/L", "Ranh giới M↔L Nữ: đúng ngưỡng", "P0", ""),
        ("TC_SZ_033", "Nữ", 170, 68, "L/XL", "Ranh giới L↔XL Nữ: đúng ngưỡng", "P0", ""),
        ("TC_SZ_034", "Nữ", 175, 78, "XL/XXL", "Ranh giới XL↔XXL Nữ: đúng ngưỡng", "P0", ""),
    ],

    "🏋️ CHIỀU CAO THẤP + CÂN NẶNG CAO (Overweight)": [
        ("TC_SZ_035", "Nam", 160, 80, "L/XL", "Nam thấp nhưng nặng: 160/80", "P0", "Ưu tiên cân nặng hay chiều cao?"),
        ("TC_SZ_036", "Nam", 165, 90, "XL/XXL", "Nam TB nhưng rất nặng: 165/90", "P1", "Stress test logic"),
        ("TC_SZ_037", "Nam", 155, 75, "L", "Nam rất thấp mà nặng: 155/75", "P1", ""),
        ("TC_SZ_038", "Nữ", 150, 65, "L", "Nữ rất thấp mà nặng: 150/65", "P0", ""),
        ("TC_SZ_039", "Nữ", 155, 70, "L/XL", "Nữ thấp nhưng nặng: 155/70", "P1", ""),
        ("TC_SZ_040", "Nữ", 160, 80, "XL/XXL", "Nữ TB nhưng rất nặng: 160/80", "P1", ""),
    ],

    "🦒 CHIỀU CAO LỚN + CÂN NẶNG THẤP (Underweight)": [
        ("TC_SZ_041", "Nam", 180, 55, "S/M", "Nam rất cao nhưng rất gầy: 180/55", "P0", "Ưu tiên chiều cao hay cân nặng?"),
        ("TC_SZ_042", "Nam", 185, 60, "M/L", "Nam cực cao mà nhẹ: 185/60", "P1", ""),
        ("TC_SZ_043", "Nam", 175, 55, "S/M", "Nam cao mà gầy: 175/55", "P1", ""),
        ("TC_SZ_044", "Nữ", 170, 45, "S", "Nữ cao nhưng rất gầy: 170/45", "P0", ""),
        ("TC_SZ_045", "Nữ", 175, 50, "S/M", "Nữ rất cao mà nhẹ: 175/50", "P1", ""),
        ("TC_SZ_046", "Nữ", 168, 48, "S", "Nữ cao mà gầy: 168/48", "P1", ""),
    ],

    "🚫 GIÁ TRỊ INVALID / EDGE CASE": [
        ("TC_SZ_047", "Nam", 0, 0, "Lỗi", "Chiều cao và cân nặng = 0", "P0", "Phải hiển thị lỗi validation"),
        ("TC_SZ_048", "Nam", -170, 70, "Lỗi", "Chiều cao âm", "P0", "Phải reject giá trị âm"),
        ("TC_SZ_049", "Nam", 170, -60, "Lỗi", "Cân nặng âm", "P0", "Phải reject giá trị âm"),
        ("TC_SZ_050", "Nam", 100, 50, "Lỗi", "Chiều cao quá thấp (ngoài range): 100cm", "P1", "Ngoài giới hạn hợp lệ"),
        ("TC_SZ_051", "Nam", 250, 80, "Lỗi", "Chiều cao quá cao: 250cm", "P1", "Ngoài giới hạn hợp lệ"),
        ("TC_SZ_052", "Nam", 170, 200, "Lỗi", "Cân nặng quá lớn: 200kg", "P1", "Ngoài giới hạn hợp lệ"),
        ("TC_SZ_053", "Nam", 170, 10, "Lỗi", "Cân nặng quá nhỏ: 10kg", "P1", "Ngoài giới hạn hợp lệ"),
        ("TC_SZ_054", "", 170, 70, "Lỗi", "Không chọn giới tính", "P0", "Giới tính bắt buộc"),
        ("TC_SZ_055", "Nam", "", "", "Lỗi", "Không nhập chiều cao và cân nặng", "P0", "Validate required fields"),
        ("TC_SZ_056", "Nam", "abc", 70, "Lỗi", "Nhập chữ vào ô chiều cao", "P1", "Validate kiểu dữ liệu"),
        ("TC_SZ_057", "Nam", 170, "xyz", "Lỗi", "Nhập chữ vào ô cân nặng", "P1", "Validate kiểu dữ liệu"),
        ("TC_SZ_058", "Nam", 170.5, 65.3, "M", "Nhập số thập phân: 170.5cm / 65.3kg", "P1", "Hệ thống có chấp nhận decimal?"),
    ],

    "🔄 CHUYỂN ĐỔI GIỚI TÍNH (Cùng chiều cao/cân nặng)": [
        ("TC_SZ_059", "Nam", 165, 60, "M", "Nam 165/60 → kiểm tra size", "P0", "So sánh kết quả Nam vs Nữ cùng input"),
        ("TC_SZ_060", "Nữ", 165, 60, "L", "Nữ 165/60 → size phải KHÁC Nam (lớn hơn 1 bậc)", "P0", "Nữ cần form rộng hơn ở lower body"),
        ("TC_SZ_061", "Nam", 170, 65, "M", "Nam 170/65 → kiểm tra", "P1", ""),
        ("TC_SZ_062", "Nữ", 170, 65, "L", "Nữ 170/65 → so sánh với Nam", "P1", ""),
        ("TC_SZ_063", "Nam", 175, 75, "L", "Nam 175/75 → kiểm tra", "P1", ""),
        ("TC_SZ_064", "Nữ", 175, 75, "XL", "Nữ 175/75 → so sánh với Nam", "P1", ""),
    ],

    "📐 KIỂM TRA HIỂN THỊ UI GỢI Ý SIZE": [
        ("TC_SZ_065", "Nam", 170, 70, "M", "Popup gợi ý size: hiển thị đúng M + highlight trên bảng size", "P0", "Kiểm tra UI popup/overlay"),
        ("TC_SZ_066", "Nữ", 160, 53, "M", "Popup gợi ý size Nữ: hiển thị kết quả + guide ảnh", "P0", ""),
        ("TC_SZ_067", "Nam", 170, 70, "M", "Sau khi chọn size gợi ý → auto-select trong dropdown sản phẩm", "P1", "Kiểm tra logic auto-fill"),
        ("TC_SZ_068", "Nam", 170, 70, "M", "Thay đổi giới tính sau khi đã gợi ý → recalculate", "P0", "Size phải cập nhật lại"),
        ("TC_SZ_069", "Nam", 170, 70, "M", "Thay đổi chiều cao/cân nặng → recalculate real-time", "P1", "Nếu có tính năng live update"),
        ("TC_SZ_070", "Nam", 170, 70, "M", "Responsive: popup gợi ý size trên mobile 375px", "P1", "Kiểm tra responsive"),
    ],
}
