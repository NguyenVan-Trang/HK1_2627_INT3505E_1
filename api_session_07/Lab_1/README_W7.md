# BTVN TUẦN 7: 

# TEST 6 ENDPOINT của LAB 1:

## 1. Chạy server:
![server-w7](images/server-w7.png)

## 2. Lấy toàn bộ danh sách sản phẩm:
![get-all-list](images/get-all-list.png)

## 3. Lấy sản phẩm với ID không tồn tại:
![get-invalid-id](images/get-invalid-id.png)

## 4. Tạo sản phẩm:
![create-product](images/create-product.png)

## 5. Cập nhật sản phẩm:
![patch](images/patch.png)

## 6. POST thiếu SKU/SKU đã tồn tại/Reserve vượt quá tồn kho:
POST thiếu SKU:

![post-without-SKU](images/post-without-SKU.png)

POST với SKU đã tồn tại:

![post-with-existing-SKU](images/post-with-existing-SKU.png)

POST Reserve vượt quá tồn kho:

![post-out-of-stock](images/post-out-of-stock.png)

## 7. POST/PATCH sản phẩm giá âm:
POST:

![post-with-negative-price](images/post-with-negative-price.png)


PATCH:

![patch-with-negative-price](images/patch-with-negative-price.png)

## 8. Xoá sản phẩm:
![delete](images/delete.png)


# TEST ENDPOINT với resource OderItems, Order:

## 1. Lấy danh sách đơn hàng:
![get-order](images/get-order.png)

## 2. Lấy đơn hàng theo ID:
![get-order-by-id](images/get-order-by-id.png)

## 3. Tạo đơn hàng:
![create-order](images/create-order.png)

## 4. Tạo đơn hàng với ID không tồn tại/Lấy thông tin đơn hàng với ID không tồn tại:
POST:

![create-order-with-invalid-id](images/create-order-with-invalid-id.png)

GET:

![get-order-with-invalid-id](images/get-order-with-invalid-id.png)

## 5. Thêm sản phẩm mới vào đơn hàng:
![add-product-to-order](images/add-product-to-order.png)

## 6. Tạo đơn hàng với số lượng bằng 0, sản phẩm trống, không có số lượng:
POST với qty = 0:

![post-with-zero-qty](images/post-with-zero-qty.png)

POST với sản phẩm trống:

![post-with-empty-item](images/post-with-empty-item.png)

POST không có qty:

![post-missing-qty](images/post-missing-qty.png)

## 7. POST/PATCH sản phẩm giá âm:
POST:

![post-with-negative-price](images/post-with-negative-price.png)


PATCH:

![patch-with-negative-price](images/patch-with-negative-price.png)

## 8. Xoá sản phẩm:
![delete](images/delete.png)


# TEST DOCKER:

## 1. Kiểm thử API trong Docker:
![test-api-docker-1](images/test-api-docker-1.png)
![test-api-docker-2](images/test-api-docker-2.png)

## 2. Kiểm thử khả năng lưu dữ liệu:
Dữ liệu hiện có:

![test-save-data-docker-1](images/test-save-data-docker-1.png)

Dừng + khởi động lại container, kiểm tra lại dữ liệu:

![test-save-data-docker-2](images/test-save-data-docker-2.png)


# TEST Healthz và Ready:

Healthz:

![test-healthz](images/test-healthz.png)

Ready:

![test-ready](images/test-ready.png)
