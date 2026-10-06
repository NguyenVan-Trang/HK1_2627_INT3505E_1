# BÁO CÁO REVIEW GITHUB REST API

* **Họ và tên:** Nguyễn Văn Tráng
* **MSSV:** 23021737
* **Nhóm:** 04
* **Phần phụ trách:** Tiêu chí 07, 08, 09 (theo Checklist Review API - Buổi 3)

## TỔNG QUAN NHIỆM VỤ
Trong khuôn khổ bài thực hành đánh giá API công khai, nhóm 4 lựa chọn đối tượng khảo sát là **GitHub REST API**. Đây là một trong những hệ thống API công khai quy mô lớn, hoạt động lâu năm và có độ ổn định cao.

Phần báo cáo dưới đây tập trung phân tích và đánh giá 3 tiêu chí:
1. **Tiêu chí 07:** Filter / Sort đa dạng
2. **Tiêu chí 08:** Authentication & Security
3. **Tiêu chí 09:** Versioning + Deprecation

## TIÊU CHÍ 07: FILTER / SORT ĐA DẠNG

### Yêu cầu chuẩn thiết kế
Hệ thống cần hỗ trợ lọc theo các trường chính, sắp xếp đa trường (multi-field sort) và hỗ trợ lựa chọn trường trả về (sparse fieldsets) nhằm tối ưu băng thông.

### Phân tích thực tế tại GitHub REST API

* **Khả năng lọc (Filtering):**
  GitHub hỗ trợ lọc dữ liệu thông qua query parameters ở hầu hết các collection endpoint.
  * *Ví dụ:* Lọc theo trạng thái và quyền sở hữu với `?type=owner`, `?state=open`; hoặc lọc theo mốc thời gian cập nhật với `?since=2024-01-01T00:00:00Z`.

* **Khả năng sắp xếp (Sorting):**
  API cho phép sắp xếp thông qua tham số `sort` kết hợp với `direction` (mặc định chiều sắp xếp thường là `desc`).
  * *Ví dụ:* `?sort=updated&direction=asc`.

* **Hạn chế về sắp xếp đa trường (Multi-field sort):**
  GitHub chưa hỗ trợ sắp xếp đồng thời theo nhiều trường (như `?sort=priority,name`). Client chỉ có thể sắp xếp dựa trên một tiêu chí duy nhất do endpoint quy định sẵn.

* **Hạn chế về Sparse Fieldsets:**
  GitHub REST API hoàn toàn không cung cấp cơ chế generic sparse fieldsets (không hỗ trợ tham số chung như `?fields=id,name,html_url`). Dữ liệu trả về luôn tuân theo schema cố định của tài nguyên đó. Điều này dẫn đến tình trạng over-fetching (dư thừa dữ liệu), khiến kích thước payload lớn không cần thiết, đặc biệt là đối với các ứng dụng di động.

> **Giải pháp từ GitHub:** Để giải quyết triệt để vấn đề over-fetching và sparse fieldsets, GitHub định hướng các nhà phát triển sử dụng GitHub GraphQL API thay vì cố gắng nhồi nhét cú pháp vào REST API.

### Ví dụ minh họa Request

GET /users/octocat/repos?type=owner&sort=updated&direction=desc&per_page=10 HTTP/1.1
Host: api.github.com

Accept: application/vnd.github+json

### Đánh giá mức độ tuân thủ tiêu chí 07
* **Lọc (Filtering):** Tốt, đầy đủ query parameters theo ngữ nghĩa nghiệp vụ.
* **Sắp xếp (Sorting):** Đạt một phần, hỗ trợ sort một thuộc tính kèm direction, chưa hỗ trợ đa trường.
* **Lựa chọn trường (Sparse Fieldsets):** Không đạt, payload cố định theo schema.

 **Kết luận tiêu chí 07:** **ĐẠT MỘT PHẦN (Partial Pass)**.


## TIÊU CHÍ 08: AUTHENTICATION & SECURITY

### Yêu cầu chuẩn thiết kế
Token xác thực phải được đặt trong HTTP Header, không để lộ qua URL query string. Hệ thống phải có chính sách kiểm soát lưu lượng (Rate Limit) minh bạch.

### Phân tích thực tế tại GitHub REST API

* **Cơ chế xác thực qua Header và chống rò rỉ Token:**
  GitHub yêu cầu toàn bộ mã xác thực (Personal Access Token, OAuth Token, GitHub App Token) phải được truyền qua HTTP Authorization Header theo định dạng Bearer hoặc token:
  ```http
  Authorization: Bearer <TOKEN>
  ```
  Trong quá khứ, GitHub từng cho phép client truyền token qua query string (`?access_token=...`). Tuy nhiên, để tuân thủ bảo mật và ngăn ngừa Anti-pattern số 5 (Auth trong query string), GitHub đã loại bỏ hoàn toàn phương thức này. Việc đưa token vào URL có nguy cơ cao bị lưu vết trong Server Access Logs, Web Proxy Logs, Browser History và Referer Header.

* **Cơ chế Rate Limiting minh bạch:**
  GitHub quản lý lưu lượng request cực kỳ chặt chẽ và thông báo trạng thái trực tiếp qua các Response Headers:
  * `x-ratelimit-limit`: Số lượng request tối đa trong cửa sổ 1 giờ (ví dụ: 60 cho unauthenticated, 5000 cho token xác thực).
  * `x-ratelimit-remaining`: Số request còn lại trong chu kỳ hiện tại.
  * `x-ratelimit-reset`: Mốc thời gian Unix Epoch (tính bằng giây) mà giới hạn sẽ được hồi phục lại.
  * `x-ratelimit-used`: Số request đã sử dụng trong chu kỳ.

  Khi client vượt quá hạn mức, API trả về HTTP Status Code `429 Too Many Requests` (hoặc `403 Forbidden`) kèm theo header `Retry-After` để hướng dẫn client thời điểm có thể thử lại.

* **Secondary Rate Limits (Chống lạm dụng thời gian thực):**
  Ngoài giới hạn theo giờ, GitHub áp dụng cơ chế giới hạn phụ để chống spam và tấn công DoS, bao gồm: giới hạn số lượng request đồng thời và giới hạn số lượng thao tác ghi/xóa trong một khoảng thời gian ngắn.

### Ví dụ minh họa Request và Response Headers

**Request:**
```http
GET /user HTTP/1.1
Host: api.github.com
Authorization: Bearer ghp_99xAbcDefGhi123456789...
Accept: application/vnd.github+json
```

**Response Headers:**
```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
x-ratelimit-limit: 5000
x-ratelimit-remaining: 4982
x-ratelimit-reset: 1710000000
x-ratelimit-resource: core
```

### Đánh giá mức độ tuân thủ tiêu chí 08
* **Vị trí Token:** Đạt, bắt buộc truyền qua Header, cấm hoàn toàn query param.
* **Thông tin Rate Limit:** Đạt, cung cấp rõ ràng qua các header chuyên dụng và hỗ trợ `Retry-After`.
* **Cơ chế bảo vệ hệ thống:** Đạt, có secondary rate limit ngăn chặn hành vi bất thường.

> **Kết luận tiêu chí 08:** **ĐẠT (Pass)**.

---

## TIÊU CHÍ 09: VERSIONING + DEPRECATION

### Yêu cầu chuẩn thiết kế
Có cơ chế quản lý phiên bản rõ ràng ngay từ đầu. Có quy trình và lộ trình ngừng hỗ trợ (sunset/deprecation) minh bạch, tránh gây vỡ hệ thống của client khi nâng cấp.

### Phân tích thực tế tại GitHub REST API

* **Cơ chế quản lý phiên bản (Date-based Versioning):**
  Thay vì đưa version vào đường dẫn URL (như `/v1`, `/v2`) làm thay đổi bản chất định danh tài nguyên, GitHub triển khai cơ chế Versioning theo ngày phát hành (Calendar-based) thông qua HTTP Header:
  ```http
  X-GitHub-Api-Version: YYYY-MM-DD
  ```
  Phiên bản ổn định hiện tại của hệ thống là `2022-11-28`. Nếu client không truyền header này, hệ thống sẽ tự động sử dụng phiên bản mặc định nhằm bảo đảm tính tương thích ngược cho các hệ thống cũ.

* **Quản lý Breaking Changes:**
  GitHub có chính sách rõ ràng: các thay đổi có nguy cơ phá vỡ ứng dụng client (xóa endpoint, đổi tên tham số, xóa trường dữ liệu, thay đổi kiểu dữ liệu) sẽ không bao giờ được cập nhật trực tiếp vào phiên bản đang chạy. Tất cả breaking changes đều được gom lại và phát hành trong một phiên bản mới theo ngày.

* **Quy trình Deprecation và Sunset (Chuẩn RFC 8594):**
  * **Cam kết vòng đời:** Một phiên bản cũ được cam kết hỗ trợ tối thiểu 24 tháng kể từ ngày phiên bản kế tiếp được ra mắt.
  * **Cảnh báo ngưng hỗ trợ:** Khi một tính năng hoặc phiên bản bước vào giai đoạn sắp dừng hoạt động, GitHub sử dụng các HTTP Header chuẩn gồm:
    * `Deprecation: @<timestamp>` (Báo hiệu tính năng đã cũ)
    * `Sunset: <date>` (Thời điểm chính xác API sẽ bị đóng hoàn toàn)
    * `Link: <url>; rel="sunset"` (Liên kết đến tài liệu migration)
  * **Trạng thái kết thúc:** Sau khi hết thời gian hỗ trợ, mọi request gửi tới phiên bản đó sẽ nhận về mã lỗi HTTP `410 Gone` (thay vì `404 Not Found`), thể hiện đúng ngữ nghĩa kỹ thuật là tài nguyên này đã từng tồn tại nhưng hiện tại đã bị dỡ bỏ vĩnh viễn.

### Ví dụ minh họa Request chỉ định Version
```http
GET /octocat HTTP/1.1
Host: api.github.com
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

### Đánh giá mức độ tuân thủ tiêu chí 09
* **Cơ chế Versioning:** Đạt, sử dụng header theo ngày linh hoạt, không làm bẩn URL.
* **Chính sách Breaking Changes:** Đạt, văn bản hóa công khai và quản lý chặt chẽ.
* **Quy trình Deprecation:** Đạt, cam kết tối thiểu 24 tháng, ứng dụng chuẩn Deprecation/Sunset và mã `410 Gone`.

> **Kết luận tiêu chí 09:** **ĐẠT (Pass)**.

---

## TỔNG KẾT BẢNG ĐÁNH GIÁ (TIÊU CHÍ 07 ĐẾN 09)

| Tiêu chí | Trạng thái | Nhận xét chi tiết |
| :--- | :---: | :--- |
| **Tiêu chí 07 - Filter / Sort đa dạng** | **Đạt một phần** | Cơ chế lọc và phân trang tốt, nhưng chưa có sắp xếp đa trường và thiếu sparse fieldsets chung cho REST. Khuyến nghị dùng GraphQL khi cần tối ưu payload. |
| **Tiêu chí 08 - Authentication & Security** | **Đạt** | Token được bảo mật tuyệt đối trong Header, chính sách Rate Limit và Secondary Rate Limit minh bạch, xử lý tốt theo chuẩn HTTP. |
| **Tiêu chí 09 - Versioning + Deprecation** | **Đạt** | Sử dụng versioning theo ngày qua Header tân tiến, vòng đời hỗ trợ phiên bản cũ dài (tối thiểu 24 tháng), tuân thủ chặt chẽ tiêu chuẩn Deprecation và Sunset. |