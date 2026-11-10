from product_api.factory import create_app
from product_api.extensions import db
from product_api.models import Product

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

with app.app_context():
    for data in sample_products:
        existing = db.session.scalar(
            db.select(Product).where(Product.sku == data["sku"])
        )

        if existing is None:
            db.session.add(Product(**data))

    db.session.commit()
    print("Sample data inserted successfully!")