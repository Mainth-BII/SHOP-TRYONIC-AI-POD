// Kịch bản người dùng dùng chung cho smoke / load / stress.
// CHỈ GET trang công khai → an toàn (không tạo đơn / không ghi dữ liệu).
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';
import { BASE_URL, PATHS, THINK_MIN, THINK_MAX } from '../config.js';

// Metric riêng: thời gian tải trang (tách theo path qua tag).
export const pageDuration = new Trend('page_duration', true);

function think() {
  sleep(Math.random() * (THINK_MAX - THINK_MIN) + THINK_MIN);
}

// 1 lượt "duyệt web": lần lượt mở các trang trong PATHS.
export function browseFlow() {
  for (const path of PATHS) {
    const url = `${BASE_URL}${path}`;
    const res = http.get(url, {
      tags: { path },                 // gắn tag để xem latency theo từng trang
      headers: { 'Accept-Language': 'vi-VN,vi;q=0.9' },
    });
    pageDuration.add(res.timings.duration, { path });
    check(res, {
      'status 2xx/3xx': (r) => r.status >= 200 && r.status < 400,
      'có nội dung HTML': (r) => (r.body ? r.body.length : 0) > 0,
    });
    think();
  }
}
