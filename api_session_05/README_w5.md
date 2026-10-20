# LAB 1: 

## 1. Chạy server:
![server-w5](server-w5.png)

## 2. Tạo sách:
Status code trả về:
![code-post](code-post.png)
Kết quả
![post](post.png)

## 3. Lấy danh sách:
Status code trả về:
![code-get-1](code-get-1.png)
Kết quả khi mới chạy server:
![get-1](get-1.png)
Status code trả về khi lấy lần 2:
![code-get-2](code-get-2.png)
Kết quả sau khi post tạo sách:
![get-2](get-2.png)

## 4. Cập nhật sách:
Status code trả về:
![code-put](code-put.png)
Kết quả
![put](update.png)

## 5. Xóa sách:
Kết quả:
![delete](delete-book.png)

## 6. JSON sai cú pháp:
Kết quả:
![json](json-error-syntax.png)

## 7. Thiếu trường bắt buộc:
Kết quả:
![missing-field](missing-field.png)

## 8. ID không tồn tại:
Kết quả:
![id-not-existed](id-not-existed.png)


# LAB 2: PARSE_SORT VÀ FILTER 

## 1. Lấy danh sách mặc định:
Status code trả về:
![code-get-lab2](code-get-lab2.png)
Kết quả
![get-ds](get-lab2.png)

## 2. Sắp xếp giá tăng dần & giảm dần:
Sắp xếp tăng dần:
Status code trả về:
![code-get-lab2](code-get-lab2.png)
Kết quả sắp xếp giá tăng dần:
![sort-asc-1](sort-asc-price-1.png)
![sort-asc-2](sort-asc-price-2.png)
![sort-asc-3](sort-asc-price-3.png)

Sắp xếp giảm dần:
Status code trả về:
![code-desc](code-get-desc.png)
Kết quả sắp xếp giá giảm dần:
![sort-desc-1](sort-desc-price-1.png)
![sort-desc-2](sort-desc-price-2.png)
![sort-desc-3](sort-desc-price-3.png)

## 3. Sắp xếp ID giảm dần:
Status code trả về:
![code-desc-id](code-get-desc-id.png)
Kết quả sắp xếp ID giảm dần:
![sort-desc-id-1](sort-desc-id-1.png)
![sort-desc-id-2](sort-desc-id-2.png)
![sort-desc-id-3](sort-desc-id-3.png)

## 4. Sort không hợp lệ:
Status code trả về:
![invalid-sort-code](code-invalid-sort.png)
Kết quả:
![invalid-sort](invalid-sort.png)

## 5. Sort nhiều trường:
Status code trả về:
![code-sort-with-many-fields](code-sort-with-many-fields.png)
Kết quả:
![sort-with-many-fields](sort-with-many-fields.png)

## 6. Lấy một sách mỗi trang:
Status code trả về:
![code-get-1-book-per-page](code-get-1-book-per-page.png)
Kết quả:
![get-1-book-per-page](get-1-book-per-page.png)

## 7. Lọc theo danh mục:
Status code trả về:
![code-filer-by-category](code-filer-by-category.png)
Kết quả:
![filer-by-category-1](filer-by-category-1.png)
![filer-by-category-2](filer-by-category-2.png)

## 8. Test cursor:
Status code trả về:
![code-cursor](code-cursor.png)
Kết quả:
![cursor](test-cursor.png)

# BTVN SỐ 2: HOÀN THIỆN list_books Ở LAB 1: implement cả offset và cursor (chọn qua param ?strategy=... ) + thêm filter ?genre + sort multi-key.

## 1. Phân trang Offset với 3 bản ghi mỗi trang:
Status code trả về:
![code-offset-1](code-offset-1.png)

Kết quả
![offset](offset.png)

## 2. Phân trang cursor:
Status code trả về:
![code-cursor-paging-1](code-cursor-paging-1.png)
![code-cursor-paging-2](code-cursor-paging-2.png)

Kết quả:
![cursor-paging-1](cursor-paging-1.png)
![cursor-paging-2](cursor-paging-2.png)

## 3. Sắp xếp nhiều trường:
Status code trả về:
![code-sort-with-many-fields](code-sort-with-many-fields-hw2.png)
Kết quả:
![sort-with-many-fields-1](sort-with-many-fields-1.png)
![sort-with-many-fields-2](sort-with-many-fields-2.png)
![sort-with-many-fields-3](sort-with-many-fields-3.png)

## 4. Strategy không hợp lệ:
Status code trả về:
![code-invalid-strategy](code-invalid-strategy.png)
Kết quả:
![invalid-strategy](invalid-strategy.png)

## 5. Limit vượt giới hạn:
Status code trả về:
![code-bad-limit](code-bad-limit.png)
Kết quả:
![bad-limit](bad-limit.png)

## 6. Kiểm tra cursor ràng buộc với bộ lọc và sắp xếp
Kiểm tra cursor với sort khác nhau:
Status code trả về:
![code-test-cursor-with-sort](code-test-cursor-with-sort.png)
Kết quả:
![test-cursor-with-sort](test-cursor-with-sort.png)

Kiểm tra cursor với genre khác:
Status code trả về:
![code-test-cursor-with-genre](code-test-cursor-with-genre.png)
Kết quả:
![test-cursor-with-genre](test-cursor-with-genre.png)

## 7. Kết quả với Postman:
![postman-1](postman-1.png)
![postman-2](postman-2.png)
![postman-3](postman-3.png)
![postman-4](postman-4.png)
![postman-5](postman-5.png)
![postman-6](postman-6.png)