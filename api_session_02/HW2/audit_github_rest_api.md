# Bài tập 2 – Audit một Public API thực

## 1. API được lựa chọn

Em lựa chọn tìm hiểu về **GitHub REST API**. Đây là API chính thức của GitHub, cho phép ứng dụng tương tác với repositories, users, issues, pull requests và nhiều tài nguyên khác.

**Base URL:**
`https://api.github.com`

GitHub REST API sử dụng HTTP methods, resource-oriented URLs, HTTP status codes và headers để cung cấp giao diện thống nhất. API hiện được version bằng header `X-GitHub-Api-Version`; nếu không chỉ định version thì GitHub sử dụng version mặc định.


## 2. Audit 5 endpoints

### Bảng tổng quan

| # | Endpoint | Method | Status thành công | Headers tiêu biểu | RESTful? |
|---|---|---|---|---|---|
| 1 | `/users/{username}` | `GET` | `200 OK` | `Accept`, `X-GitHub-Api-Version`, `ETag`, `Content-Type`, `X-RateLimit-*` | Có |
| 2 | `/repos/{owner}/{repo}/issues` | `GET` | `200 OK` | `Accept`, `X-GitHub-Api-Version`, `Link`, `ETag`, `X-RateLimit-*` | Có |
| 3 | `/repos/{owner}/{repo}/issues` | `POST` | `201 Created` | `Accept`, `Authorization`, `X-GitHub-Api-Version`, `Content-Type` | Có |
| 4 | `/repos/{owner}/{repo}/issues/{issue_number}` | `GET` | `200 OK` | `Accept`, `X-GitHub-Api-Version`, `ETag`, `Content-Type` | Có |
| 5 | `/repos/{owner}/{repo}/issues/{issue_number}` | `PATCH` | `200 OK` | `Accept`, `Authorization`, `X-GitHub-Api-Version`, `Content-Type` | Có |

### Chi tiết các Endpoint

#### Endpoint 1 – Get a user
`GET /users/{username}`

* **Mô tả:** Endpoint này lấy thông tin public của một GitHub user. 
* **Status thành công:** `200 OK` (nếu username không tồn tại có thể nhận `404 Not Found`).
* **Header khuyến nghị:** `Accept: application/vnd.github+json`
* **RESTful:** Có.
* **Lý do:** URL biểu diễn resource users, còn `GET` thể hiện thao tác đọc resource. Không sử dụng động từ như `/getUser/{username}`.

#### Endpoint 2 – List repository issues
`GET /repos/{owner}/{repo}/issues`

* **Mô tả:** Endpoint này lấy danh sách issues của repository. Đây là collection resource và hỗ trợ pagination. Khi kết quả được phân trang, GitHub sử dụng `Link` header để cung cấp các liên kết tới trang tiếp theo/trước đó.
* **Status chính:** `200 OK`
* **Headers đáng chú ý:**
  * `Accept: application/vnd.github+json`
  * `X-GitHub-Api-Version: 2026-03-10`
  * `Link: <...>; rel="next", <...>; rel="last"`
  * `ETag: W/"..."`
  * `X-RateLimit-Remaining: ...`
* **Cơ chế khác:** GitHub hỗ trợ conditional request bằng `ETag`; nếu dữ liệu không thay đổi, client có thể nhận `304 Not Modified`.
* **RESTful:** Có.
* **Lý do:** `/issues` biểu diễn collection resource và `GET` được sử dụng để lấy dữ liệu.

#### Endpoint 3 – Create an issue
`POST /repos/{owner}/{repo}/issues`

* **Mô tả:** Endpoint này tạo một issue mới trong repository.
* **Request Headers:**
  * `Accept: application/vnd.github+json`
  * `Authorization: Bearer <TOKEN>`
  * `X-GitHub-Api-Version: 2026-03-10`
  * `Content-Type: application/json`
* **Status thành công:** `201 Created`
* **Status lỗi có thể gặp:** `400`, `403`, `404`, `410`, `422`, `503`.
* **RESTful:** Có.
* **Lý do:** Client thao tác với collection `/issues` bằng HTTP method `POST` để tạo resource mới. URL không chứa động từ như `/createIssue`.

#### Endpoint 4 – Get an issue
`GET /repos/{owner}/{repo}/issues/{issue_number}`

* **Mô tả:** Endpoint này lấy một issue cụ thể dựa trên `issue_number`.
* **Status thành công:** `200 OK`
* **Status khác:** `304 Not Modified`, `404 Not Found`, `410 Gone`.
* **Header tiêu biểu:**
  * `Accept: application/vnd.github+json`
  * `X-GitHub-Api-Version: 2026-03-10`
  * `ETag: W/"..."`
  * `Content-Type: application/json`
* **RESTful:** Có.
* **Lý do:** `/issues/{issue_number}` xác định một resource cụ thể, còn `GET` dùng để đọc resource đó.

#### Endpoint 5 – Update an issue
`PATCH /repos/{owner}/{repo}/issues/{issue_number}`

* **Mô tả:** Endpoint này cập nhật một phần thông tin của issue. GitHub liệt kê endpoint `PATCH /repos/{owner}/{repo}/issues/{issue_number}` trong REST API.
* **Ví dụ Request:**
  ```http
  PATCH /repos/octocat/Hello-World/issues/1 HTTP/1.1
  Host: api.github.com
  Content-Type: application/json
  Accept: application/vnd.github+json
  Authorization: Bearer <TOKEN>
  X-GitHub-Api-Version: 2026-03-10

  {
    "title": "Updated issue title"
  }
  ```
* **Status thành công:** `200 OK`
* **RESTful:** Có.
* **Lý do:** `PATCH` phù hợp với việc cập nhật một phần representation của resource. URL tiếp tục xác định resource bằng `/issues/{issue_number}` thay vì tạo một URL dạng `/updateIssue`.


## 3. Kết luận

Qua audit 5 endpoint của GitHub REST API, có thể thấy API tuân thủ rõ các nguyên tắc REST:

1. **Resource-oriented URL:** URL đại diện cho users, repositories và issues.
2. **HTTP methods có ý nghĩa:** `GET` đọc, `POST` tạo, `PATCH` cập nhật một phần.
3. **HTTP status codes:** Sử dụng `200`, `201`, `304`, `404`, `410` và các mã lỗi phù hợp.
4. **HTTP headers:** Sử dụng `Accept`, `Content-Type`, `Authorization`, `ETag`, `Link` và các header quản lý API version/rate limit.
5. **Cache và conditional request:** GitHub hỗ trợ `ETag` và `304 Not Modified`.

Do đó, 5 endpoint được khảo sát đều có thiết kế RESTful, thể hiện rõ việc sử dụng resource, HTTP methods và các cơ chế chuẩn của HTTP.