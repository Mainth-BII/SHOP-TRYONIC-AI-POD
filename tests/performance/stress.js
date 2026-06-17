// STRESS TEST — đẩy tải TĂNG DẦN vượt mức bình thường để tìm "điểm gãy"
// (breaking point): khi nào latency tăng vọt / lỗi tăng / hệ thống quá tải.
//   k6 run tests/performance/stress.js
// ⚠️ Tải NẶNG — chỉ chạy TEST, canh giờ thấp điểm, báo team trước.
// Tùy chỉnh bậc thang qua -e MAX_VUS=400
import { browseFlow } from './lib/scenario.js';

const MAX = Number(__ENV.MAX_VUS || 300);

export const options = {
  // Bậc thang tăng dần — quan sát latency/error ở từng mức để xác định ngưỡng.
  stages: [
    { duration: '1m', target: Math.round(MAX * 0.17) },  // ~50
    { duration: '2m', target: Math.round(MAX * 0.33) },  // ~100
    { duration: '2m', target: Math.round(MAX * 0.67) },  // ~200
    { duration: '2m', target: MAX },                      // đỉnh
    { duration: '2m', target: 0 },                        // hồi phục (recovery)
  ],
  // Stress: KHÔNG abort khi vượt ngưỡng — để quan sát hành vi quá tải.
  // Thresholds chỉ để đánh dấu (informational), không làm fail sớm.
  thresholds: {
    http_req_failed: ['rate<0.10'],       // cảnh báo nếu >10% lỗi
    http_req_duration: ['p(95)<5000'],    // cảnh báo nếu p95 > 5s
  },
};

export default function () {
  browseFlow();
}
