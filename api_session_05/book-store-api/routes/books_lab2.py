from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, or_
import base64
import json

from models import db, Book

bp = Blueprint("books_lab2", __name__)

SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd
}


def parse_sort(raw):
    desc = raw.startswith("-")
    key = raw[1:] if desc else raw

    if key not in SORT_FIELDS:
        return None, None

    column = SORT_FIELDS[key]
    return column, desc


def encode_cursor(book, key):
    value = book.price_vnd if key == "price" else book.id

    data = json.dumps({
        "key": key,
        "value": value,
        "id": book.id
    })

    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def decode_cursor(cursor):
    cursor += "=" * (-len(cursor) % 4)
    data = base64.urlsafe_b64decode(cursor).decode()
    return json.loads(data)


@bp.get("")
def list_books():
    category = request.args.get("category", type=int)
    sort = request.args.get("sort", "-id")
    cursor = request.args.get("cursor")
    limit = request.args.get("limit", 20, type=int)

    if not 1 <= limit <= 100:
        return jsonify({"error": "bad_limit"}), 400

    column, desc = parse_sort(sort)

    if column is None:
        return jsonify({"error": "bad_sort"}), 400

    query = select(Book)

    if category is not None:
        query = query.where(Book.category_id == category)

    if cursor:
        try:
            data = decode_cursor(cursor)

            if data["key"] != sort.lstrip("-"):
                return jsonify({"error": "sort_changed"}), 400

            value = data["value"]
            book_id = data["id"]

            if sort.lstrip("-") == "price":
                query = query.where(
                    or_(
                        column < value if desc else column > value,
                        and_(
                            column == value,
                            Book.id < book_id if desc else Book.id > book_id
                        )
                    )
                )
            else:
                query = query.where(
                    column < value if desc else column > value
                )

        except (ValueError, KeyError, TypeError):
            return jsonify({"error": "bad_cursor"}), 400

    query = query.order_by(
        column.desc() if desc else column.asc(),
        Book.id.desc() if desc else Book.id.asc()
    )

    rows = db.session.scalars(query.limit(limit + 1)).all()
    more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if items and more:
        next_cursor = encode_cursor(items[-1], sort.lstrip("-"))

    return jsonify({
        "data": [book.to_dict() for book in items],
        "page": {
            "next": next_cursor,
            "more": more
        }
    })