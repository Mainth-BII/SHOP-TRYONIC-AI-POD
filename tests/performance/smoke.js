// SMOKE — kiểm tra nhanh hệ thống chịu tải cơ bản (RẤT NHẸ, an toàn).
// Mục đích: xác nhận perf test chạy được + baseline latency, KHÔNG gây tải.
//   k6 run tests/performance/smoke.js
import { browseFlow } from './lib/scenario.js';
import { THRESHOLDS } from './config.js';

export const options = {
  vus: Number(__ENV.VUS || 2),          // 2 người dùng ảo
  duration: __ENV.DURATION || '30s',    // trong 30 giây
  thresholds: THRESHOLDS,
};

export default function () {
  browseFlow();
}
