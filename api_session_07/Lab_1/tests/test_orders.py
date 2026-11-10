
from sqlalchemy import event

from product_api.extensions import db
from product_api.models import Order


# Test 1: Tạo Order thành công
def test_create_order_success(client, sample_products):
    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {
                    "product_id": sample_products[0].id,
                    "qty": 2
                },
                {
                    "product_id": sample_products[1].id,
                    "qty": 1
                }
            ]
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["status"] == "pending"
    assert len(data["items"]) == 2
    assert data["items"][0]["qty"] == 2
    assert data["items"][0]["unit_price_cents"] == 15000000


# Test 2: Tạo Order với số lượng không hợp lệ
def test_create_order_invalid_qty(client, sample_products):
    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {
                    "product_id": sample_products[0].id,
                    "qty": 0
                }
            ]
        }
    )

    assert response.status_code == 422


# Test 3: Tạo Order với Product không tồn tại
def test_create_order_product_not_found(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {
                    "product_id": 9999,
                    "qty": 2
                }
            ]
        }
    )

    assert response.status_code == 404


# Test 4: GET danh sách Order có eager loading
# Kiểm tra số lượng SQL SELECT để phát hiện N+1
def test_list_orders_eager_loading(
    app, client, sample_orders
):
    query_count = 0

    def count_queries(
        conn, cursor, statement, parameters, context, executemany
    ):
        nonlocal query_count

        if statement.lstrip().upper().startswith("SELECT"):
            query_count += 1

    with app.app_context():
        engine = db.engine

        event.listen(
            engine,
            "before_cursor_execute",
            count_queries
        )

        try:
            response = client.get("/api/v1/orders")
        finally:
            event.remove(
                engine,
                "before_cursor_execute",
                count_queries
            )

    assert response.status_code == 200

    data = response.get_json()

    # Có 3 Order, mỗi Order có 3 OrderItem
    assert len(data) == 3

    for order in data:
        assert len(order["items"]) == 3

    # 1 SELECT lấy Order + 1 SELECT lấy OrderItem
    assert query_count == 2, (
        f"Expected 2 SELECT queries, got {query_count}"
    )
