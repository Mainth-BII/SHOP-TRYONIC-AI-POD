// Cấu hình chung cho perf test (k6) — KHÓA CỨNG môi trường TEST.
//
// BASE_URL mặc định = TEST. Có thể override qua env: -e BASE_URL=...
// nhưng GUARD dưới đây CHẶN mọi URL không phải *.test.shop.tryonic.ai
// (không bao giờ load/stress PROD — tránh làm sập hệ thống thật).

export const BASE_URL = __ENV.BASE_URL || 'https://test.shop.tryonic.ai';

// 🔒 Guard: chỉ cho phép môi trường TEST. PROD 'shop.tryonic.ai' KHÔNG chứa
// chuỗi 'test.shop.tryonic.ai' → bị chặn ngay.
if (!BASE_URL.includes('test.shop.tryonic.ai')) {
  throw new Error(
    `🚫 Perf test CHỈ được chạy trên TEST. BASE_URL không hợp lệ: "${BASE_URL}". ` +
    `Phải trỏ tới *.test.shop.tryonic.ai`,
  );
}

// Các trang công khai (GET, KHÔNG tạo dữ liệu) để đo hiệu năng đọc.
// Thêm/bớt path tại đây; mỗi VU sẽ duyệt lần lượt các path này.
export const PATHS = (__ENV.PATHS ? __ENV.PATHS.split(',') : [
  '/',                       // trang chủ
  '/products',               // danh sách sản phẩm (sửa nếu route khác)
  '/studio?category=t-shirts', // studio (tải nặng FE)
]);

// Ngưỡng SLO mặc định (smoke/load dùng; stress nới lỏng riêng).
export const THRESHOLDS = {
  http_req_failed: ['rate<0.01'],          // < 1% request lỗi
  http_req_duration: ['p(95)<2000'],       // p95 < 2s
};

// think-time giữa các request (giây) — mô phỏng người dùng thật.
export const THINK_MIN = Number(__ENV.THINK_MIN || 1);
export const THINK_MAX = Number(__ENV.THINK_MAX || 3);
