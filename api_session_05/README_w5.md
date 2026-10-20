# LAB 1: 

## 1. Chạy server:
![server-w5](images/server-w5.png)

## 2. Tạo sách:
Status code trả về:
![code-post](images/code-post.png)
Kết quả
![post](images/post.png)

## 3. Lấy danh sách:
Status code trả về:
![code-get-1](images/code-get-1.png)
Kết quả khi mới chạy server:
![get-1](images/get-1.png)
Status code trả về khi lấy lần 2:
![code-get-2](images/code-get-2.png)
Kết quả sau khi post tạo sách:
![get-2](images/get-2.png)

## 4. Cập nhật sách:
Status code trả về:
![code-put](images/code-put.png)
Kết quả
![put](images/update.png)

## 5. Xóa sách:
Kết quả:
![delete](images/delete-book.png)

## 6. JSON sai cú pháp:
Kết quả:
![json](images/json-error-syntax.png)

## 7. Thiếu trường bắt buộc:
Kết quả:
![missing-field](images/missing-field.png)

## 8. ID không tồn tại:
Kết quả:
![id-not-existed](images/id-not-existed.png)


# LAB 2: PARSE_SORT VÀ FILTER 

## 1. Lấy danh sách mặc định:
Status code trả về:
![code-get-lab2](images/code-get-lab2.png)
Kết quả
![get-ds](images/get-lab2.png)

## 2. Sắp xếp giá tăng dần & giảm dần:
Sắp xếp tăng dần:
Status code trả về:
![code-get-lab2](images/code-get-lab2.png)
Kết quả sắp xếp giá tăng dần:
![sort-asc-1](images/sort-asc-price-1.png)
![sort-asc-2](images/sort-asc-price-2.png)
![sort-asc-3](images/sort-asc-price-3.png)

Sắp xếp giảm dần:
Status code trả về:
![code-desc](images/code-get-desc.png)
Kết quả sắp xếp giá giảm dần:
![sort-desc-1](images/sort-desc-price-1.png)
![sort-desc-2](images/sort-desc-price-2.png)
![sort-desc-3](images/sort-desc-price-3.png)

## 3. Sắp xếp ID giảm dần:
Status code trả về:
![code-desc-id](images/code-get-desc-id.png)
Kết quả sắp xếp ID giảm dần:
![sort-desc-id-1](images/sort-desc-id-1.png)
![sort-desc-id-2](images/sort-desc-id-2.png)
![sort-desc-id-3](images/sort-desc-id-3.png)

## 4. Sort không hợp lệ:
Status code trả về:
![invalid-sort-code](images/code-invalid-sort.png)
Kết quả:
![invalid-sort](images/invalid-sort.png)

## 5. Sort nhiều trường:
Status code trả về:
![code-sort-with-many-fields](images/code-sort-with-many-fields.png)
Kết quả:
![sort-with-many-fields](images/sort-with-many-fields.png)

## 6. Lấy một sách mỗi trang:
Status code trả về:
![code-get-1-book-per-page](images/code-get-1-book-per-page.png)
Kết quả:
![get-1-book-per-page](images/get-1-book-per-page.png)

## 7. Lọc theo danh mục:
Status code trả về:
![code-filer-by-category](images/code-filer-by-category.png)
Kết quả:
![filer-by-category-1](images/filer-by-category-1.png)
![filer-by-category-2](images/filer-by-category-2.png)

## 8. Test cursor:
Status code trả về:
![code-cursor](images/code-cursor.png)
Kết quả:
![cursor](images/test-cursor.png)

# BTVN SỐ 2: HOÀN THIỆN list_books Ở LAB 1: implement cả offset và cursor (chọn qua param ?strategy=... ) + thêm filter ?genre + sort multi-key.

## 1. Phân trang Offset với 3 bản ghi mỗi trang:
Status code trả về:
![code-offset-1](images/code-offset-1.png)

Kết quả
![offset](images/offset.png)

## 2. Phân trang cursor:
Status code trả về:
![code-cursor-paging-1](images/code-cursor-paging-1.png)
![code-cursor-paging-2](images/code-cursor-paging-2.png)

Kết quả:
![cursor-paging-1](images/cursor-paging-1.png)
![cursor-paging-2](images/cursor-paging-2.png)

## 3. Sắp xếp nhiều trường:
Status code trả về:
![code-sort-with-many-fields](images/code-sort-with-many-fields-hw2.png)
Kết quả:
![sort-with-many-fields-1](images/sort-with-many-fields-1.png)
![sort-with-many-fields-2](images/sort-with-many-fields-2.png)
![sort-with-many-fields-3](images/sort-with-many-fields-3.png)

## 4. Strategy không hợp lệ:
Status code trả về:
![code-invalid-strategy](images/code-invalid-strategy.png)
Kết quả:
![invalid-strategy](images/invalid-strategy.png)

## 5. Limit vượt giới hạn:
Status code trả về:
![code-bad-limit](images/code-bad-limit.png)
Kết quả:
![bad-limit](images/bad-limit.png)

## 6. Kiểm tra cursor ràng buộc với bộ lọc và sắp xếp
Kiểm tra cursor với sort khác nhau:
Status code trả về:
![code-test-cursor-with-sort](images/code-test-cursor-with-sort.png)
Kết quả:
![test-cursor-with-sort](images/test-cursor-with-sort.png)

Kiểm tra cursor với genre khác:
Status code trả về:
![code-test-cursor-with-genre](images/code-test-cursor-with-genre.png)
Kết quả:
![test-cursor-with-genre](images/test-cursor-with-genre.png)

## 7. Kết quả với Postman:
![postman-1](images/postman-1.png)
![postman-2](images/postman-2.png)
![postman-3](images/postman-3.png)
![postman-4](images/postman-4.png)
![postman-5](images/postman-5.png)
![postman-6](images/postman-6.png)