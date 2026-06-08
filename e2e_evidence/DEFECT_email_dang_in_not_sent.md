# DEFECT: Không gửi email "Đơn hàng đang được in" khi PRINTING qua "Đánh dấu đã gửi"

- **Môi trường:** TEST (test.shop.tryonic.ai) — nhánh `develop`
- **Mức độ:** Medium (khách thiếu 1 thông báo trong vòng đời đơn)
- **Trạng thái:** Xác nhận bằng code + manual + test tự động

## Mô tả
Khi admin đưa đơn sang trạng thái **Đang in (PRINTING)** qua quy trình thật
(Lệnh in → chọn xưởng → **"Đánh dấu đã gửi"**), hệ thống **KHÔNG gửi email
"Đơn hàng đang được in"** cho khách. Các trạng thái khác (Xác nhận / Đang giao /
Đã giao) đều gửi email bình thường.

## Bước tái hiện
1. Đơn COD đã PAID + CONFIRMED, lệnh in đã READY.
2. Vào Lệnh in → chọn xưởng → bấm "Đánh dấu đã gửi".
3. Order tự chuyển CONFIRMED → PRINTING ("Đang in").
4. Kiểm tra hộp thư khách → KHÔNG có email "đang được in".

## Kỳ vọng vs Thực tế
- **Kỳ vọng:** khách nhận email "Đơn hàng đang được in - #<orderCode>".
- **Thực tế:** không có email.

## Nguyên nhân (code)
`PrintJobService.maybeSyncOrderStatus` (khi tất cả print job = SENT) cập nhật
trạng thái TRỰC TIẾP:
    await this.prisma.order.update({ where: { id: orderId }, data: { status: 'PRINTING' } });
→ bỏ qua `OrderService.sendStatusChangeNotification` (hàm chịu trách nhiệm gửi
email theo trạng thái). Các transition khác đi qua `OrderService.updateStatus`
nên CÓ gọi notification.

## Đề xuất fix
Trong `maybeSyncOrderStatus`, sau khi set PRINTING, gọi gửi email "đang được in"
(hoặc đi qua `sendStatusChangeNotification` / `emailProducer.sendOrderPrinting`).

## Bằng chứng
- Code: `tryonic-shop-backend/src/modules/print-job/print-job.service.ts` (maybeSyncOrderStatus)
  vs `order.service.ts` (sendStatusChangeNotification → case PRINTING → sendOrderPrinting).
- Manual QA: không nhận mail.
- Test tự động: mark-sent đơn POD-20260608-013 → order "Đang in" nhưng inbox KHÔNG có email "đang được in".
