
import pytest

from product_api.factory import create_app
from product_api.config import TestConfig
from product_api.extensions import db
from product_api.models import Product, Order, OrderItem


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_products(app):
    products = [
        Product(
            sku="TEST001",
            name="Laptop Dell",
            description="Laptop for testing",
            price_cents=15000000,
            qty_in_stock=10
        ),
        Product(
            sku="TEST002",
            name="Logitech Mouse",
            description="Mouse for testing",
            price_cents=500000,
            qty_in_stock=20
        ),
        Product(
            sku="TEST003",
            name="Mechanical Keyboard",
            description="Keyboard for testing",
            price_cents=1200000,
            qty_in_stock=15
        )
    ]

    db.session.add_all(products)
    db.session.commit()

    return products


@pytest.fixture
def sample_orders(app, sample_products):
    orders = []

    for i in range(3):
        order = Order(status="pending")

        for product in sample_products:
            order.items.append(
                OrderItem(
                    product=product,
                    qty=i + 1,
                    unit_price_cents=product.price_cents
                )
            )

        orders.append(order)

    db.session.add_all(orders)
    db.session.commit()

    # Đảm bảo các quan hệ được tải lại trong request
    db.session.expire_all()

    return orders
