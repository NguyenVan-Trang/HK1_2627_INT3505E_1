def v1_create_order(body):
    # Handler v1: xử lý đơn hàng theo phiên bản cũ.
    return {
        "message": "Order created using v1",
        "account_id": body["account_id"],
        "product": body["product"],
        "handler": "v1"
    }


def v2_create_order(body):
    # Handler v2: xử lý đơn hàng theo phiên bản mới.
    return {
        "message": "Order created using v2",
        "account_id": body["account_id"],
        "product": body["product"],
        "handler": "v2",
        "version": 2
    }