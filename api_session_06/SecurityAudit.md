
# Security Audit – Social Network API

## 1. Phạm vi đánh giá

Tài liệu này đánh giá các nguy cơ bảo mật và rò rỉ dữ liệu đối với ba API:

- `POST /auth/login`: Xác thực người dùng và cấp access token, refresh token.
- `POST /auth/refresh`: Cấp token mới khi nhận refresh token hợp lệ.
- `GET /posts/{id}`: Lấy thông tin bài viết theo ID.

Mục tiêu là xác định các điểm có thể gây lộ thông tin, truy cập trái phép hoặc làm suy giảm tính an toàn của hệ thống.

## 2. Các nguy cơ bảo mật

### 2.1. Rò rỉ mật khẩu qua log

**Nguy cơ:** Nếu hệ thống ghi toàn bộ request body hoặc thông tin đăng nhập vào log, mật khẩu người dùng có thể bị lộ khi log bị truy cập trái phép.

**Biện pháp kiểm soát:**
- Không ghi mật khẩu hoặc request body chứa thông tin đăng nhập vào log.
- Chỉ lưu các thông tin cần thiết cho việc giám sát và xử lý sự cố.
- Không lưu mật khẩu dưới dạng văn bản thuần; sử dụng hàm băm mật khẩu phù hợp.

**Trạng thái demo:** Mật khẩu mẫu được lưu dưới dạng hash và API không chủ động ghi mật khẩu vào log.

### 2.2. Rò rỉ access token và refresh token

**Nguy cơ:** Token có thể bị lộ qua log, URL, mã nguồn được commit lên Git hoặc môi trường kiểm thử dùng chung. Người sở hữu token bị lộ có thể sử dụng token để gọi API trong thời gian token còn hiệu lực.

**Biện pháp kiểm soát:**
- Truyền token qua header `Authorization: Bearer`.
- Không đưa token vào URL hoặc log.
- Không commit token thật lên Git.
- Giới hạn thời hạn access token và bảo vệ refresh token.
- Thu hồi hoặc thay thế refresh token sau khi sử dụng thành công.

**Trạng thái demo:** Access token có thời hạn 15 phút; refresh token được thay thế sau khi refresh thành công. Trạng thái thu hồi hiện lưu trong bộ nhớ nên bị mất khi ứng dụng khởi động lại.

### 2.3. Lộ dữ liệu trong payload JWT

**Nguy cơ:** Payload JWT được mã hóa theo Base64URL nhưng không mặc nhiên được mã hóa bí mật. Người có token có thể đọc các claim trong payload.

**Biện pháp kiểm soát:**
- Không đưa mật khẩu, thông tin xác thực hoặc dữ liệu cá nhân nhạy cảm vào payload.
- Chỉ lưu các claim cần thiết như `sub`, `scope`, `type`, `iat`, `exp`, `iss`, `aud` và `jti`.
- Không coi dữ liệu trong payload là đáng tin cậy trước khi xác minh chữ ký và các claim cần thiết.

**Trạng thái demo:** JWT chứa các claim phục vụ xác thực, phân quyền và kiểm tra thời hạn; không chứa mật khẩu.

### 2.4. Xác minh JWT không đầy đủ

**Nguy cơ:** Nếu API chấp nhận token không xác minh chữ ký, không kiểm tra thời hạn hoặc cho phép thuật toán không an toàn, kẻ tấn công có thể sử dụng token giả hoặc token không hợp lệ.

**Biện pháp kiểm soát:**
- Chỉ chấp nhận thuật toán đã được cấu hình, không tin thuật toán do token tự khai báo.
- Kiểm tra chữ ký, `exp`, `iss`, `aud` và loại token.
- Từ chối token hết hạn, sai chữ ký hoặc không đúng mục đích sử dụng.
- Không sử dụng cùng một loại token thay thế cho mọi mục đích.

**Trạng thái demo:** API xác minh JWT với thuật toán HS256, thời hạn, issuer, audience và loại token.

### 2.5. Thiếu kiểm tra phân quyền và lỗi BOLA

**Nguy cơ:** Người dùng có thể đọc bài viết của người khác nếu API chỉ kiểm tra token hợp lệ mà không kiểm tra scope hoặc quyền truy cập đối với từng đối tượng.

**Biện pháp kiểm soát:**
- Yêu cầu scope `posts:read` đối với `GET /posts/{id}`.
- Kiểm tra quyền xem bài viết theo chính sách truy cập và chủ sở hữu.
- Không chỉ dựa vào việc người dùng đã đăng nhập để cho phép truy cập tài nguyên.
- Trả về `404 Not Found` khi bài viết không tồn tại hoặc không được phép nhìn thấy, nhằm hạn chế việc dò tìm tài nguyên.

**Trạng thái demo:** Endpoint kiểm tra scope `posts:read`; bài viết private chỉ hiển thị với chủ sở hữu.

### 2.6. Tấn công dò mật khẩu và đăng nhập tự động

**Nguy cơ:** Kẻ tấn công có thể gửi nhiều yêu cầu đăng nhập để đoán mật khẩu hoặc thử danh sách thông tin đăng nhập bị rò rỉ.

**Biện pháp kiểm soát:**
- Giới hạn số lần đăng nhập trong một khoảng thời gian.
- Theo dõi các lần đăng nhập thất bại bất thường.
- Sử dụng thông báo lỗi chung để không tiết lộ email có tồn tại hay không.
- Có thể bổ sung cơ chế trì hoãn hoặc khóa tạm thời khi phát hiện hành vi đáng ngờ.

**Trạng thái demo:** API trả thông báo lỗi chung khi thông tin đăng nhập sai. Rate limiting chưa được triển khai thực tế.

### 2.7. Sử dụng lại refresh token

**Nguy cơ:** Nếu refresh token bị đánh cắp và không bị thu hồi sau khi sử dụng, kẻ tấn công có thể tiếp tục sử dụng token đó để lấy access token mới.

**Biện pháp kiểm soát:**
- Thay thế refresh token sau mỗi lần refresh thành công.
- Thu hồi refresh token đã sử dụng.
- Lưu trạng thái thu hồi trong kho dữ liệu bền vững khi triển khai thực tế.
- Xử lý các yêu cầu refresh đồng thời để hạn chế việc sử dụng lại token.

**Trạng thái demo:** API thu hồi `jti` của refresh token đã dùng và từ chối lần sử dụng tiếp theo. Cơ chế hiện tại dùng bộ nhớ nên chưa phù hợp cho hệ thống nhiều instance hoặc cần duy trì trạng thái sau khi khởi động lại.

### 2.8. Lộ khóa bí mật ký JWT

**Nguy cơ:** Nếu khóa ký JWT bị đưa trực tiếp vào mã nguồn hoặc commit lên Git, kẻ tấn công có thể sử dụng khóa đó để tạo token giả.

**Biện pháp kiểm soát:**
- Đọc khóa bí mật từ biến môi trường hoặc hệ thống quản lý secret.
- Không commit khóa bí mật thật lên Git.
- Sử dụng khóa đủ mạnh và có quy trình thay đổi khóa khi cần.
- Không sử dụng khóa mặc định trong môi trường production.

**Trạng thái demo:** Ứng dụng hỗ trợ cấu hình `JWT_SECRET_KEY` qua biến môi trường. Giá trị mặc định chỉ phục vụ demo local và phải được thay thế khi triển khai.

### 2.9. Trả về quá nhiều dữ liệu từ API

**Nguy cơ:** Nếu API trả trực tiếp toàn bộ bản ghi cơ sở dữ liệu, response có thể chứa trường nội bộ hoặc thông tin người dùng không cần thiết.

**Biện pháp kiểm soát:**
- Xác định rõ các trường được phép trả về trong response.
- Không trả mật khẩu, thông tin xác thực, dữ liệu nội bộ hoặc trường nhạy cảm.
- Kiểm tra quyền truy cập trước khi trả dữ liệu của từng bài viết.

**Trạng thái demo:** Endpoint bài viết tạo response từ danh sách trường được xác định trước, thay vì trả trực tiếp toàn bộ bản ghi dữ liệu.

### 2.10. Rò rỉ token trong môi trường kiểm thử Swagger UI

**Nguy cơ:** Token có thể còn trong trạng thái Authorize của trình duyệt sau khi kiểm thử, đặc biệt khi sử dụng máy tính dùng chung hoặc trình duyệt có nhiều người truy cập.

**Biện pháp kiểm soát:**
- Chỉ sử dụng tài khoản và token mẫu khi trình diễn.
- Xóa trạng thái Authorize sau khi hoàn tất kiểm thử.
- Không sử dụng token hoặc tài khoản production trong môi trường demo.
- Giới hạn quyền truy cập vào môi trường kiểm thử.

**Trạng thái demo:** Swagger UI hỗ trợ nhập token để kiểm thử. Người thực hiện cần chủ động xóa token sau khi hoàn tất.

## 3. Tổng kết

Các nguy cơ chính của API nằm ở việc bảo vệ thông tin đăng nhập, quản lý vòng đời JWT, kiểm tra scope, phân quyền trên từng bài viết và bảo vệ khóa bí mật.

Bản demo đã minh họa các cơ chế cơ bản gồm xác minh JWT, kiểm tra thời hạn và loại token, kiểm tra scope, kiểm soát quyền xem bài viết, thông báo đăng nhập lỗi chung và thu hồi refresh token sau khi sử dụng.

Tuy nhiên, đây vẫn là ứng dụng minh họa chạy local. Trước khi triển khai thực tế cần  kiểm thử bảo mật toàn diện hơn.
