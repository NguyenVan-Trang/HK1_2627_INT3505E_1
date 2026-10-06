# Lab 2 - Error handler trả về problem+json

## 1. Chạy server:
![server-lab2](server-lab2.png)

## 2. 404 — /resources/{id}:
Status code trả về:
![sc1_lab2](code1_lab2.png)
Kết quả
![result1_lab2](404-resources.png)

## 3. HTTPException — route không tồn tại:
Status code trả về:
![sc2_lab2](code2_lab2.png)
Kết quả
![result2_lab2](route-not-existed.png)

## 4. 405 — HTTP method không được phép:
Status code trả về:
![sc3_lab2](code3_lab2.png)
Kết quả
![result3_lab3](method-not-allowed.png)



## 5. Không có/Có Accept:
Status code trả về:
![sc1_lab2](code1_lab2.png)
Kết quả không có Accept
![result2_lab2](route-not-existed.png)
Kết quả có Accept
![result4_lab2](accept.png)

## 7. Exception chưa được bắt — 500:
Status code trả về:
![sc5_lab2](code5_lab2.png)
Kết quả:
![result5_lab2](exception-not-catched.png)
