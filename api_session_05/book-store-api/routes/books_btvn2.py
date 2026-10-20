from flask import Blueprint, request, jsonify
from sqlalchemy import select, and_, or_
import base64
import json

from models import db, Book, Category

bp = Blueprint("books_btvn2", __name__)

SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
    "title": Book.title
}


def parse_sort(raw):
    specs = []
    seen = set()

    for part in raw.split(","):
        desc = part.startswith("-")
        key = part[1:] if desc else part

        if key not in SORT_FIELDS or key in seen:
            return None

        seen.add(key)
        specs.append((key, SORT_FIELDS[key], desc))

    if "id" not in seen:
        specs.append(("id", Book.id, False))

    return specs


def encode_cursor(book, sort, genre, specs):
    values = [
        book.price_vnd if key == "price" else getattr(book, key)
        for key, _, _ in specs
    ]

    data = json.dumps({
        "sort": sort,
        "genre": genre,
        "values": values
    })

    return base64.urlsafe_b64encode(data.encode()).decode().rstrip("=")


def apply_cursor(query, cursor, sort, genre, specs):
    if not cursor:
        return query

    try:
        cursor += "=" * (-len(cursor) % 4)
        data = json.loads(base64.urlsafe_b64decode(cursor).decode())

        if data["sort"] != sort or data["genre"] != genre:
            raise ValueError()

        values = data["values"]
        conditions = []
        equal = []

        for i, (_, column, desc) in enumerate(specs):
            comparison = column < values[i] if desc else column > values[i]
            conditions.append(and_(*equal, comparison))
            equal.append(column == values[i])

        return query.where(or_(*conditions))

    except (ValueError, KeyError, TypeError, IndexError):
        raise ValueError("bad_cursor")


@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "offset")
    sort = request.args.get("sort", "-id")
    genre = request.args.get("genre")
    limit = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)
    cursor = request.args.get("cursor")

    if strategy not in ("offset", "cursor"):
        return jsonify({"error": "bad_strategy"}), 400

    if not 1 <= limit <= 100:
        return jsonify({"error": "bad_limit"}), 400

    if offset < 0:
        return jsonify({"error": "bad_offset"}), 400

    specs = parse_sort(sort)
    if specs is None:
        return jsonify({"error": "bad_sort"}), 400

    query = select(Book)

    if genre:
        query = query.join(Book.category).where(Category.slug == genre)

    query = query.order_by(*[
        column.desc() if desc else column.asc()
        for _, column, desc in specs
    ])

    if strategy == "offset":
        rows = db.session.scalars(
            query.offset(offset).limit(limit + 1)
        ).all()
    else:
        try:
            query = apply_cursor(query, cursor, sort, genre, specs)
        except ValueError:
            return jsonify({"error": "bad_cursor"}), 400

        rows = db.session.scalars(query.limit(limit + 1)).all()

    more = len(rows) > limit
    items = rows[:limit]

    next_cursor = None
    if strategy == "cursor" and items and more:
        next_cursor = encode_cursor(items[-1], sort, genre, specs)

    page = {
        "strategy": strategy,
        "limit": limit,
        "more": more
    }

    if strategy == "offset":
        page["offset"] = offset
        page["next_offset"] = offset + limit if more else None
    else:
        page["next"] = next_cursor

    return jsonify({
        "data": [book.to_dict() for book in items],
        "page": page
    })