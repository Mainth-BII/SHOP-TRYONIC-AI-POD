// LOAD TEST — tải kỳ vọng (sustained). Đo hệ thống ở mức người dùng "bình
// thường giờ cao điểm": ramp lên rồi GIỮ ổn định để xem latency/throughput.
//   k6 run tests/performance/load.js
// Tùy chỉnh: -e PEAK_VUS=100 -e HOLD=5m
import { browseFlow } from './lib/scenario.js';
import { THRESHOLDS } from './config.js';

const PEAK = Number(__ENV.PEAK_VUS || 50);
const HOLD = __ENV.HOLD || '3m';

export const options = {
  stages: [
    { duration: '1m', target: PEAK },   // ramp dần tới PEAK (tránh sốc đột ngột)
    { duration: HOLD, target: PEAK },    // GIỮ tải ổn định
    { duration: '30s', target: 0 },      // ramp xuống
  ],
  thresholds: THRESHOLDS,
};

export default function () {
  browseFlow();
}
