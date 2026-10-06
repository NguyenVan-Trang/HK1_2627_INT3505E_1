# Lab 3 - Triển khai /orders có cursor pagination

## 1. Chạy server:
![server-lab3](server-lab3.png)

## 2. Filter status:
Status code trả về:
![sc1_lab3](code1-lab3.png)
Kết quả
![filter](filter.png)

## 3. Cursor pagination với limit:
Status code trả về:
![sc2_lab3](code2-lab3.png)
Kết quả
![cursor_pagination_with_limit](cursor-pagination-with-limit.png)
Khi lấy trang tiếp theo, status code trả về:
![sc3_lab3](code3-lab3.png)
Kết quả trang tiếp theo:
![cursor_pagination_with_limit_p2](cursor-pagination-with-limit-p2.png)

## 4. Sparse fieldsets:
Status code trả về:
![sc4_lab3](code4-lab3.png)
Kết quả:
![sparse_fieldsets](sparse_fieldsets.png)


## 5. Test customer_id:
Status code trả về:
![sc5_lab3](code5-lab3.png)
Kết quả:
![filter_id](filter-by-id.png)

## 6. Sort:
Status code trả về:
![sc6_lab3](code6-lab3.png)
Kết quả sort tăng dần:
![sort_ascending](sort-ascending.png)
Status code trả về:
![sc7_lab3](code7-lab3.png)
Kết quả sort giảm dần:
![sort_descending](sort-descending.png)

## 7. Lỗi cursor:
Status code trả về:
![sc8_lab3](code8-lab3.png)
Kết quả:
![error_cursor](error-cursor.png)

## 8. Field không tồn tại:
Status code trả về:
![sc9_lab3](code9-lab3.png)
Kết quả:
![field_not_existed](field-not-existed.png)
