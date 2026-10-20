from flask import Blueprint, request, jsonify
from sqlalchemy import select
from models import db, Book

bp = Blueprint("books_lab1s", __name__)


@bp.get("")
def list_books():
    category = request.args.get("category", type=int)

    query = select(Book)

    if category is not None:
        query = query.where(Book.category_id == category)

    books = db.session.scalars(query.order_by(Book.id)).all()

    return jsonify({
        "data": [book.to_dict() for book in books]
    })


@bp.get("/<int:book_id>")
def get_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({"error": "book_not_found"}), 404

    return jsonify(book.to_dict())


@bp.post("")
def create_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "invalid_json"}), 400

    if not data.get("title") or type(data.get("price_vnd")) is not int:
        return jsonify({"error": "invalid_fields"}), 400

    book = Book(
        title=data["title"],
        isbn=data.get("isbn"),
        price_vnd=data["price_vnd"],
        stock=data.get("stock", 0),
        category_id=data.get("category_id")
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


@bp.put("/<int:book_id>")
def update_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({"error": "book_not_found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "invalid_json"}), 400

    if "title" in data:
        book.title = data["title"]

    if "price_vnd" in data:
        if type(data["price_vnd"]) is not int or data["price_vnd"] < 0:
            return jsonify({"error": "invalid_price"}), 400
        book.price_vnd = data["price_vnd"]

    if "stock" in data:
        if type(data["stock"]) is not int or data["stock"] < 0:
            return jsonify({"error": "invalid_stock"}), 400
        book.stock = data["stock"]

    db.session.commit()
    return jsonify(book.to_dict())


@bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        return jsonify({"error": "book_not_found"}), 404

    db.session.delete(book)
    db.session.commit()

    return "", 204