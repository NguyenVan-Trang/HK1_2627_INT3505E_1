
from flask import Blueprint, request, jsonify
from sqlalchemy import select, tuple_
from jsonschema import validate, ValidationError
import json
import os
import base64

from models import db, Book, Author, Category

bp = Blueprint("books", __name__)

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "schemas",
    "book.json"
)

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    BOOK_SCHEMA = json.load(f)


def validate_book(payload):
    try:
        validate(instance=payload, schema=BOOK_SCHEMA)
        return None
    except ValidationError as e:
        return {
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }


def find_book(book_id):
    return db.session.get(Book, book_id)

# Bat dau Lab 2: parse_sort va filter
SORT_FIELDS = {
    "id": Book.id,
    "price": Book.price_vnd,
}


def parse_sort(raw):
    desc = raw.startswith("-")
    key = raw[1:] if desc else raw
    key = key.strip()

    if key not in SORT_FIELDS:
        return None, None, None

    p = SORT_FIELDS[key]
    cols = [
        p.desc() if desc else p.asc(),
        Book.id.desc() if desc else Book.id.asc(),
    ]

    return p, cols, desc


def _encode_cursor(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def apply_cursor(q, raw, sort, p, desc):
    if not raw:
        return q, None, 200

    try:
        padding = "=" * (-len(raw) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode(raw + padding).decode("utf-8")
        )

        if not isinstance(payload, dict):
            raise ValueError("Cursor must be a JSON object")

        if payload.get("s") != sort:
            return None, "sort_chg", 400

        value = payload["v"]
        book_id = payload["i"]

        if type(book_id) is not int or book_id <= 0:
            raise ValueError("Invalid cursor id")

        if type(value) is not int:
            raise ValueError("Invalid cursor value")

        # ID sort dùng chính ID làm giá trị sort.
        # Với price sort, value là price_vnd.
        if sort == "id" and value != book_id:
            raise ValueError("Invalid cursor value")

        op = "<" if desc else ">"
        condition = tuple_(p, Book.id).op(op)((value, book_id))

        return q.where(condition), None, 200

    except (ValueError, TypeError, KeyError, UnicodeDecodeError):
        return None, "bad_cursor", 400


def build_response(items, limit, sort, p, more):
    nxt = None

    if items and more:
        last = items[-1]
        nxt = _encode_cursor({
            "s": sort,
            "v": getattr(last, p.key),
            "i": last.id,
        })

    return jsonify({
        "data": [book.to_dict() for book in items],
        "page": {
            "next": nxt,
            "more": more,
        },
    })
# End Lab 2

# GET /api/v1/books
@bp.get("")
def list_books():
    raw = request.args.get("cursor")
    sort = request.args.get("sort", "-id")
    limit = min(request.args.get("limit", 20, type=int), 100)
    category_id = request.args.get("category", type=int)

    # Kiểm tra limit
    if limit < 1:
        return jsonify({
            "error": "invalid_limit",
            "message": "limit must be between 1 and 100"
        }), 400

    # Parse sort theo whitelist
    p, cols, desc = parse_sort(sort)

    if p is None:
        return jsonify({
            "error": "bad_sort",
            "message": "Supported sort values: id, -id, price, -price"
        }), 400

    # Tạo query và áp dụng filter
    q = select(Book)

    if category_id is not None:
        q = q.where(Book.category_id == category_id)

    q = q.order_by(*cols)

    # Áp dụng cursor
    q, err, code = apply_cursor(q, raw, sort, p, desc)

    if err:
        return jsonify({"error": err}), code

    # Lấy thêm một bản ghi để xác định còn trang sau không
    rows = db.session.scalars(q.limit(limit + 1)).all()
    more = len(rows) > limit
    items = rows[:limit]

    return build_response(items, limit, sort, p, more)



# POST /api/v1/books
@bp.post("")
def create_book():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "invalid_json",
            "message": "Request body must be a JSON object"
        }), 400

    error = validate_book(payload)
    if error:
        return jsonify(error), 400

    isbn = payload.get("isbn")
    if isbn and Book.query.filter_by(isbn=isbn).first():
        return jsonify({
            "error": "isbn_exists",
            "message": "ISBN already exists"
        }), 409

    category_id = payload.get("category_id")
    category = None

    if category_id is not None:
        category = db.session.get(Category, category_id)
        if category is None:
            return jsonify({
                "error": "category_not_found",
                "message": "Category does not exist"
            }), 400

    author_ids = payload.get("author_ids", [])
    authors = []

    for author_id in author_ids:
        author = db.session.get(Author, author_id)
        if author is None:
            return jsonify({
                "error": "author_not_found",
                "message": f"Author {author_id} does not exist"
            }), 400
        authors.append(author)

    book = Book(
        title=payload["title"],
        isbn=isbn,
        price_vnd=payload["price_vnd"],
        stock=payload.get("stock", 0),
        category=category,
        authors=authors
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


# GET /api/v1/books/<id>
@bp.get("/<int:book_id>")
def get_book(book_id):
    book = find_book(book_id)

    if book is None:
        return jsonify({
            "error": "book_not_found",
            "message": "Book does not exist"
        }), 404

    return jsonify(book.to_dict())


# PUT /api/v1/books/<id>
@bp.put("/<int:book_id>")
def update_book(book_id):
    book = find_book(book_id)

    if book is None:
        return jsonify({
            "error": "book_not_found",
            "message": "Book does not exist"
        }), 404

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "invalid_json",
            "message": "Request body must be a JSON object"
        }), 400

    # PUT ở bài lab này cho phép cập nhật một phần field.
    # Các field không gửi lên sẽ giữ nguyên giá trị.
    allowed = {
        "title", "isbn", "price_vnd", "stock",
        "category_id", "author_ids"
    }

    if not payload or not set(payload).issubset(allowed):
        return jsonify({
            "error": "invalid_fields",
            "message": "Empty body or unsupported fields"
        }), 400

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            return jsonify({
                "error": "validation_failed",
                "field": ["title"],
                "message": "Title must not be empty"
            }), 400
        book.title = payload["title"].strip()

    if "isbn" in payload:
        isbn = payload["isbn"]
        if isbn is not None:
            if not isinstance(isbn, str) or len(isbn) != 13 or not isbn.isdigit():
                return jsonify({
                    "error": "validation_failed",
                    "field": ["isbn"],
                    "message": "ISBN must contain exactly 13 digits"
                }), 400

            existing = Book.query.filter_by(isbn=isbn).first()
            if existing and existing.id != book.id:
                return jsonify({
                    "error": "isbn_exists",
                    "message": "ISBN already exists"
                }), 409

        book.isbn = isbn

    if "price_vnd" in payload:
        price = payload["price_vnd"]
        if type(price) is not int or price < 0:
            return jsonify({
                "error": "validation_failed",
                "field": ["price_vnd"],
                "message": "Price must be a non-negative integer"
            }), 400
        book.price_vnd = price

    if "stock" in payload:
        stock = payload["stock"]
        if type(stock) is not int or stock < 0:
            return jsonify({
                "error": "validation_failed",
                "field": ["stock"],
                "message": "Stock must be a non-negative integer"
            }), 400
        book.stock = stock

    if "category_id" in payload:
        category_id = payload["category_id"]
        category = None

        if category_id is not None:
            category = db.session.get(Category, category_id)
            if category is None:
                return jsonify({
                    "error": "category_not_found",
                    "message": "Category does not exist"
                }), 400

        book.category = category

    if "author_ids" in payload:
        author_ids = payload["author_ids"]

        if (
            not isinstance(author_ids, list)
            or any(type(aid) is not int or aid <= 0 for aid in author_ids)
            or len(author_ids) != len(set(author_ids))
        ):
            return jsonify({
                "error": "validation_failed",
                "field": ["author_ids"],
                "message": "author_ids must be a list of unique positive integers"
            }), 400

        authors = []
        for author_id in author_ids:
            author = db.session.get(Author, author_id)
            if author is None:
                return jsonify({
                    "error": "author_not_found",
                    "message": f"Author {author_id} does not exist"
                }), 400
            authors.append(author)

        book.authors = authors

    db.session.commit()
    return jsonify(book.to_dict())


# DELETE /api/v1/books/<id>
@bp.delete("/<int:book_id>")
def delete_book(book_id):
    book = find_book(book_id)

    if book is None:
        return jsonify({
            "error": "book_not_found",
            "message": "Book does not exist"
        }), 404

    db.session.delete(book)
    db.session.commit()

    return "", 204
