
from product_api.factory import create_app
from product_api.extensions import db
from product_api.models import Product, Order, OrderItem

app = create_app()

sample_products = [
    {
        "sku": "TEST001",
        "name": "Laptop Dell Inspiron",
        "description": "Laptop Dell 15 inch",
        "price_cents": 15000000,
        "qty_in_stock": 10
    },
    {
        "sku": "TEST002",
        "name": "Logitech Mouse",
        "description": "Wireless Mouse",
        "price_cents": 500000,
        "qty_in_stock": 2
    },
    {
        "sku": "TEST003",
        "name": "Mechanical Keyboard",
        "description": "RGB Gaming Keyboard",
        "price_cents": 1200000,
        "qty_in_stock": 0
    },
    {
        "sku": "TEST004",
        "name": "Samsung Monitor",
        "description": "Monitor 24 inch Full HD",
        "price_cents": 3500000,
        "qty_in_stock": 5
    },
    {
        "sku": "TEST005",
        "name": "USB-C Hub",
        "description": "Multiport USB-C Adapter",
        "price_cents": 800000,
        "qty_in_stock": 8
    }
]

sample_orders = [
    {
        "status": "pending",
        "items": [
            {"sku": "TEST001", "qty": 2},
            {"sku": "TEST002", "qty": 1}
        ]
    },
    {
        "status": "confirmed",
        "items": [
            {"sku": "TEST004", "qty": 1},
            {"sku": "TEST005", "qty": 2}
        ]
    },
    {
        "status": "completed",
        "items": [
            {"sku": "TEST001", "qty": 1},
            {"sku": "TEST003", "qty": 1},
            {"sku": "TEST004", "qty": 2}
        ]
    }
]

with app.app_context():
    # 1. Tạo dữ liệu Product
    for data in sample_products:
        existing = db.session.scalar(
            db.select(Product).where(Product.sku == data["sku"])
        )

        if existing is None:
            db.session.add(Product(**data))

    db.session.commit()

    # 2. Lấy danh sách Product
    products = {
        product.sku: product
        for product in db.session.scalars(
            db.select(Product).where(
                Product.sku.in_([p["sku"] for p in sample_products])
            )
        ).all()
    }

    # 3. Tạo dữ liệu Order và OrderItem
    if db.session.query(Order).count() == 0:
        for order_data in sample_orders:
            order = Order(status=order_data["status"])

            for item_data in order_data["items"]:
                product = products.get(item_data["sku"])

                if product is None:
                    continue

                order.items.append(
                    OrderItem(
                        product=product,
                        qty=item_data["qty"],
                        unit_price_cents=product.price_cents
                    )
                )

            db.session.add(order)

        db.session.commit()
        print("Created 3 sample orders with multiple order items.")
    else:
        print("Orders already exist. Skipping order seed.")

    # 4. Thống kê dữ liệu
    print("\nSample data inserted successfully!")
    print(f"Products: {db.session.query(Product).count()}")
    print(f"Orders: {db.session.query(Order).count()}")
    print(f"OrderItems: {db.session.query(OrderItem).count()}")
