from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update


from ..extensions import db
from ..models import Product
from ..schemas import ProductOut, ProductIn, ReserveIn, ProductPatch
from .errors import ApiError, NotFound, Conflict, OutOfStock


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/v1/products"
)


@products_bp.get("")
def list_products():

    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except (ValueError, TypeError):
        raise ApiError(
            "invalid_pagination",
            "page and size must be integers",
            422
        )

    if page < 1 or size < 1 or size > 100:
        raise ApiError(
            "invalid_pagination",
            "page must be >= 1 and size must be between 1 and 100",
            422
        )

    base_query = db.select(Product).where(
        Product.archived.is_(False)
    )

    total = db.session.scalar(
        db.select(db.func.count())
        .select_from(Product)
        .where(Product.archived.is_(False))
    )

    products = db.session.execute(
        base_query
        .order_by(Product.id)
        .offset((page - 1) * size)
        .limit(size)
    ).scalars().all()

    items = ProductOut(many=True).dump(products)

    return jsonify({
        "items": items,
        "page": page,
        "size": size,
        "total": total
    }), 200


@products_bp.get("/<int:id>")
def get_product(id):

    product = db.session.scalar(
        db.select(Product).where(
            Product.id == id,
            Product.archived.is_(False)
        )
    )

    if product is None:
        raise NotFound(
            f"Product with id {id} not found"
        )

    return jsonify(ProductOut().dump(product)), 200

@products_bp.post("")
def create_product():

    print("RAW BODY:", request.get_data(as_text=True))
    print("PARSED JSON:", request.get_json(silent=True))

    json_data = request.get_json(silent=True) or {}

    data = ProductIn().load(json_data)

    existing_product = db.session.scalar(
        db.select(Product).where(
            Product.sku == data["sku"]
        )
    )

    if existing_product is not None:
        raise Conflict(
            f"Product with SKU '{data['sku']}' already exists"
        )

    product = Product(**data)

    db.session.add(product)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        raise Conflict(
            f"Product with SKU '{data['sku']}' already exists"
        )

    return jsonify(ProductOut().dump(product)), 201

@products_bp.post("/<int:id>/reserve")
def reserve_product(id):

    json_data = request.get_json(silent=True) or {}
    data = ReserveIn().load(json_data)

    qty = data["qty"]

    stmt = (
        update(Product)
        .where(
            Product.id == id,
            Product.archived.is_(False),
            Product.qty_in_stock >= qty
        )
        .values(
            qty_in_stock=Product.qty_in_stock - qty
        )
    )

    try:
        result = db.session.execute(stmt)

        if result.rowcount == 0:

            product = db.session.scalar(
                db.select(Product).where(
                    Product.id == id,
                    Product.archived.is_(False)
                )
            )

            db.session.rollback()

            if product is None:
                raise NotFound(
                    f"Product with id {id} not found"
                )

            raise OutOfStock(
                f"Insufficient stock for product {id}"
            )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    product = db.session.get(Product, id)

    return jsonify(ProductOut().dump(product)), 200


@products_bp.patch("/<int:id>")
def update_product(id):

    product = db.session.scalar(
        db.select(Product).where(
            Product.id == id,
            Product.archived.is_(False)
        )
    )

    if product is None:
        raise NotFound(
            f"Product with id {id} not found"
        )

    json_data = request.get_json(silent=True) or {}
    data = ProductPatch().load(json_data)

    if not data:
        raise ApiError(
            "validation_error",
            "At least one valid field must be provided",
            422
        )

    for field, value in data.items():
        setattr(product, field, value)

    db.session.commit()

    return jsonify(ProductOut().dump(product)), 200


@products_bp.delete("/<int:id>")
def delete_product(id):

    product = db.session.scalar(
        db.select(Product).where(
            Product.id == id,
            Product.archived.is_(False)
        )
    )

    if product is None:
        raise NotFound(
            f"Product with id {id} not found"
        )

    product.archived = True

    db.session.commit()

    return "", 204
