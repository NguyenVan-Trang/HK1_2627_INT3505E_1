# BTVN TUẦN 6:  KẾT QUẢ CHẠY app_hw6.py

## 1. Chạy server:
![server-w6](images/server-w6.png)

## 2. Đăng nhập thành công:
Status code trả về:
![code-login](images/code-login.png)
Kết quả
![login](images/login.png)
![set-token](images/set-token.png)

## 3. Đăng nhập sai mật khẩu:
Status code trả về:
![code-incorrect-password](images/code-incorrect-password.png)
Kết quả:
![incorrect-password](images/incorrect-password.png)

## 4. Đọc bài viết khi có quyền:
Status code trả về:
![code-get-post](images/code-get-post.png)
Kết quả
![get-post](images/get-post.png)

## 5. Truy cập không có token:
Status code trả về:
![code-unauthor-token](images/code-unauthor-token.png)
Kết quả:
![unauthor-token](images/unauthor-token.png)

## 6. Token hợp lệ nhưng không đủ scope:
Status code trả về:
![code-lack-scope](images/code-lack-scope.png)
Kết quả:
![lack-scope](images/lack-scope.png)

## 7. Bài viết không tồn tại:
Status code trả về:
![code-post-not-found](images/code-post-not-found.png)
Kết quả:
![post-not-found](images/post-not-found.png)

## 8. Làm mới token:
Status code trả về:
![code-refresh-token](images/code-refresh-token.png)
Kết quả:
![refresh-token](images/refresh-token.png)

## 9. Thử lại với token cũ:
Status code trả về:
![code-try-old-token](images/code-try-old-token.png)
Kết quả
![try-old-token](images/try-old-token.png)

# BTVN TUẦN 6: KẾT QUẢ KIỂM THỬ VỚI SWAGGER:

## 1. POST
![swagger-post-1](images/swagger-post-1.png)
![swagger-post-2](images/swagger-post-2.png)

## 2. Refresh:
![swagger-refresh-1](images/swagger-refresh-1.png)
![swagger-refresh-2](images/swagger-refresh-2.png)

## 3. Lấy post theo ID;
![swagger-get-post-by-id-1](images/swagger-get-post-by-id-1.png)
![swagger-get-post-by-id-2](images/swagger-get-post-by-id-2.png)
