
# Lab 4 — Phân tích kết quả Load Testing Books API

## 1. Môi trường kiểm thử

- API: Books API xây dựng bằng Flask.
- Database: SQLite.
- Công cụ: Locust.
- Server: Flask development server.
- Phương thức kiểm thử: Headless load testing.
- Các task:
  - GET /books: trọng số 3.
  - GET /books/{id}: trọng số 2.
  - POST /books: trọng số 1.
  - GET /books?year={year}: trọng số 1.

Task search_by_year có xác suất 1% đánh dấu request là failure bằng
`response.failure()` ở phía Locust. Đây là lỗi giả lập phía client,
không phải HTTP 500 do Flask server trả về.

## 2. Kết quả kiểm thử

| Kịch bản | Users | Spawn rate | Duration | Requests | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 136 | 24 | 0.00% | 4.64 |
| B | 50 | 5 | 60s | 1400 | 31 | 0.29% | 23.59 |
| C | 200 | 50 | 30s | 2824 | 200 | 0.25% | 96.20 |

## 3. Phân tích kết quả

### Câu 1. Kịch bản nào có p95 cao nhất? Vì sao?

Kịch bản C có p95 cao nhất, đạt 200 ms với 200 users đồng thời.

So sánh ba kịch bản:

- A: p95 = 24 ms.
- B: p95 = 31 ms.
- C: p95 = 200 ms.

Khi số lượng users tăng từ 50 lên 200, p95 tăng đáng kể.
Nguyên nhân có thể là Flask development server và SQLite phải
xử lý nhiều request đồng thời hơn. Việc truy cập database và
các thao tác ghi dữ liệu có thể làm tăng thời gian chờ.

Kết quả cho thấy độ trễ tăng không tuyến tính khi tải tăng cao.

### Câu 2. Endpoint nào có failure rate tăng theo số user?

Endpoint GET /books?year=[year] ghi nhận các lỗi:

- Kịch bản A: 0/12 requests, failure rate 0%.
- Kịch bản B: 4/216 requests, failure rate 1.85%.
- Kịch bản C: 7/369 requests, failure rate 1.90%.

Đây là các lỗi được tạo bởi điều kiện ngẫu nhiên 1% trong
Locust thông qua `response.failure()`.

Các lỗi này không phải HTTP 500 do server phát ra. Flask vẫn
có thể trả HTTP 200 bình thường, nhưng Locust chủ động đánh
dấu một số response là failure để minh họa việc phân tích
tỷ lệ lỗi.

Tỷ lệ quan sát có thể chênh lệch so với 1% do số lượng
request trong mỗi kịch bản còn hữu hạn.

### Câu 3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt?

Cả ba kịch bản đều đạt ngưỡng p95 < 300 ms:

- A: 24 ms.
- B: 31 ms.
- C: 200 ms.

Tuy nhiên, kịch bản C đã có độ trễ tăng mạnh so với hai
kịch bản còn lại. Vì vậy, cần tiếp tục kiểm thử với nhiều
mức tải và thời gian dài hơn trước khi đưa ra kết luận.

Đề xuất CI gate:

- Sử dụng kịch bản A làm baseline.
- Giữ cố định 10 users, spawn rate 2 users/giây và thời gian
  30 giây.
- Theo dõi p95 và RPS giữa các lần chạy.
- Đặt ngưỡng p95 < 300 ms theo SLO giả định.
- Không bật lỗi giả lập trong lần kiểm thử CI dùng để đánh
  giá failure rate thực tế.

### Câu 4. Nếu connection pool bị giới hạn ở 5, điều gì xảy ra
khi 200 users truy cập đồng thời?

Khi có 200 users nhưng chỉ 5 database connections được phép
sử dụng đồng thời, các request cần truy cập database có thể
phải chờ connection khả dụng.

Điều này có thể dẫn đến:

- Thời gian phản hồi tăng.
- p95 và p99 tăng.
- Request timeout nếu thời gian chờ quá lâu.
- Failure rate thực tế tăng nếu ứng dụng không xử lý được
  tình trạng hết connection hoặc timeout.

Có thể xác nhận bằng cách cấu hình connection pool giới hạn
5 connections trong môi trường thử nghiệm phù hợp, sau đó
chạy lại kịch bản C và so sánh p95, p99, RPS cùng số lỗi.

Cần lưu ý rằng SQLite có cơ chế kết nối và locking khác với
các hệ quản trị cơ sở dữ liệu client-server. Vì vậy, không
nên mặc định rằng giới hạn pool 5 của SQLite phản ánh chính
xác hành vi của PostgreSQL hoặc MySQL.

## 4. Giới hạn phép đo

- Flask đang chạy bằng development server, không phải
  production WSGI server.
- Database sử dụng SQLite trên máy cá nhân.
- Kết quả chịu ảnh hưởng bởi cấu hình máy, tài nguyên hệ
  thống và các tiến trình chạy đồng thời.
- Các kịch bản có thời gian tương đối ngắn.
- Task tạo sách làm dữ liệu trong database tăng dần giữa
  các lần chạy.
- Failure rate có bao gồm lỗi giả lập phía Locust, không
  đại diện cho tỷ lệ lỗi thực tế của server.

Do đó, kết quả chỉ có ý nghĩa thực hành trong phạm vi bài
Lab 4, không thể dùng để khẳng định hệ thống đáp ứng SLO
trong môi trường production.
