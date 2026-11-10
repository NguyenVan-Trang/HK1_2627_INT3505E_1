from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Order, OrderItem, Product
from ..schemas import OrderCreate, OrderOut
from .errors import ApiError, NotFound


orders_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/api/v1/orders"
)


@orders_bp.post("")
def create_order():
    json_data = request.get_json(silent=True) or {}
    data = OrderCreate().load(json_data)

    order = Order(status="pending")

    for item_data in data["items"]:
        product = db.session.get(Product, item_data["product_id"])

        if product is None or product.archived:
            raise NotFound(
                f"Product with id {item_data['product_id']} not found"
            )

        item = OrderItem(
            product=product,
            qty=item_data["qty"],
            unit_price_cents=product.price_cents
        )

        order.items.append(item)

    db.session.add(order)
    db.session.commit()

    return jsonify(OrderOut().dump(order)), 201


@orders_bp.get("")
def list_orders():
    orders = db.session.execute(
        db.select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.id)
    ).scalars().all()

    return jsonify(OrderOut(many=True).dump(orders)), 200


@orders_bp.get("/<int:id>")
def get_order(id):
    order = db.session.execute(
        db.select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == id)
    ).scalar_one_or_none()

    if order is None:
        raise NotFound(f"Order with id {id} not found")

    return jsonify(OrderOut().dump(order)), 200

@orders_bp.post("/<int:id>/items")
def add_order_item(id):
    json_data = request.get_json(silent=True) or {}

    product_id = json_data.get("product_id")
    qty = json_data.get("qty")

    if product_id is None or qty is None:
        raise ApiError(
            "validation_error",
            "product_id and qty are required",
            422
        )

    if type(product_id) is not int or type(qty) is not int:
        raise ApiError(
            "validation_error",
            "product_id and qty must be integers",
            422
        )

    if product_id < 1 or qty < 1:
        raise ApiError(
            "validation_error",
            "product_id and qty must be greater than 0",
            422
        )

    order = db.session.get(Order, id)

    if order is None:
        raise NotFound(f"Order with id {id} not found")

    product = db.session.get(Product, product_id)

    if product is None or product.archived:
        raise NotFound(f"Product with id {product_id} not found")

    existing_item = next(
        (item for item in order.items if item.product_id == product_id),
        None
    )

    if existing_item:
        existing_item.qty += qty
    else:
        order.items.append(
            OrderItem(
                product=product,
                qty=qty,
                unit_price_cents=product.price_cents
            )
        )

    db.session.commit()

    return jsonify(OrderOut().dump(order)), 201