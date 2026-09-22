import sqlite3
import hashlib
import json
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

DATABASE = "books.db"
DEFAULT_SIZE = 20
MAX_SIZE = 100


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            price REAL
        )
    """)

    books = [
        ("Clean Code", "Robert C. Martin", "9780132350884", 25.0),
        ("Clean Architecture", "Robert C. Martin", "9780134494166", 30.0),
        ("The Clean Coder", "Robert C. Martin", "9780137081073", 28.0),
        ("1984", "George Orwell", "9780451524935", 15.0),
        ("Animal Farm", "George Orwell", "9780451526342", 12.0),
        ("Domain-Driven Design", "Eric Evans", "9780321125217", 35.0),
        ("The Pragmatic Programmer", "Andrew Hunt", "9780135957059", 32.0),
        ("Design Patterns", "Erich Gamma", "9780201633610", 40.0),
        ("Refactoring", "Martin Fowler", "9780134757599", 38.0),
        ("Effective Java", "Joshua Bloch", "9780134685991", 35.0),
        ("Java Concurrency in Practice", "Brian Goetz", "9780321349606", 42.0),
        ("Head First Design Patterns", "Eric Freeman", "9780596007126", 30.0),
        ("Introduction to Algorithms", "Thomas Cormen", "9780262046305", 50.0),
        ("The Mythical Man-Month", "Frederick Brooks", "9780201835953", 25.0),
        ("Software Engineering", "Ian Sommerville", "9780133943030", 45.0),
        ("Code Complete", "Steve McConnell", "9780735619678", 40.0),
        ("Working Effectively with Legacy Code", "Michael Feathers", "9780131177055", 35.0),
        ("You Don't Know JS", "Kyle Simpson", "9781491904244", 28.0),
        ("Learning Python", "Mark Lutz", "9781449355739", 40.0),
        ("Computer Networks", "Andrew Tanenbaum", "9780132126953", 45.0),
        ("The Art of Computer Programming", "Donald Knuth", "9780201896831", 60.0),
        ("Don't Make Me Think", "Steve Krug", "9780321965516", 25.0),
        ("The Design of Everyday Things", "Don Norman", "9780465050659", 30.0)
    ]

    conn.executemany("""
        INSERT INTO books (title, author, isbn, price)
        VALUES (?, ?, ?, ?)
    """, books)

    conn.commit()
    conn.close()

    print("books.db created successfully!")


@app.route("/books", methods=["GET"])
def get_books():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", DEFAULT_SIZE, type=int)

    if page < 1:
        page = 1

    if size < 1:
        size = DEFAULT_SIZE

    size = min(size, MAX_SIZE)

    author = request.args.get("author")
    q = request.args.get("q")

    conn = get_db()

    conditions = []
    params = []

    if author:
        conditions.append("LOWER(author) = LOWER(?)")
        params.append(author)

    if q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{q}%")

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    total = conn.execute(
        f"SELECT COUNT(*) FROM books {where_clause}",
        params
    ).fetchone()[0]

    total_pages = max(1, (total + size - 1) // size)

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * size

    rows = conn.execute(
        f"""
        SELECT id, title, author, isbn, price
        FROM books
        {where_clause}
        ORDER BY id
        LIMIT ? OFFSET ?
        """,
        params + [size, offset]
    ).fetchall()

    conn.close()

    items = [dict(row) for row in rows]

    base_url = "/books"

    links = {
        "self": {
            "href": f"{base_url}?page={page}&size={size}"
        },
        "first": {
            "href": f"{base_url}?page=1&size={size}"
        },
        "last": {
            "href": f"{base_url}?page={total_pages}&size={size}"
        }
    }

    if page > 1:
        links["prev"] = {
            "href": f"{base_url}?page={page - 1}&size={size}"
        }

    if page < total_pages:
        links["next"] = {
            "href": f"{base_url}?page={page + 1}&size={size}"
        }

    response = make_response(jsonify({
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages
        },
        "_links": links
    }))

    response.headers["Cache-Control"] = "public, max-age=30"

    return response


@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "error": "Book not found"
        }), 404

    book = dict(row)

    content = json.dumps(
        book,
        sort_keys=True,
        separators=(",", ":")
    )

    etag = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    etag = f'"{etag}"'

    client_etag = request.headers.get("If-None-Match")

    if client_etag == etag:
        response = make_response("", 304)
        response.headers["ETag"] = etag
        return response

    response = make_response(
        jsonify(book),
        200
    )

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "max-age=60"

    return response


@app.route("/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Invalid JSON"
        }), 400

    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    isbn = data.get("isbn")
    price = data.get("price")

    if not title or not author:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO books (title, author, isbn, price)
        VALUES (?, ?, ?, ?)
        """,
        (title, author, isbn, price)
    )

    conn.commit()

    book_id = cursor.lastrowid

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(row)), 201


@app.route("/books/<int:book_id>", methods=["PUT"])
def put_book(book_id):
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Invalid JSON"
        }), 400

    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    isbn = data.get("isbn")
    price = data.get("price")

    if not title or not author:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row:
        conn.execute(
            """
            UPDATE books
            SET title = ?, author = ?, isbn = ?, price = ?
            WHERE id = ?
            """,
            (title, author, isbn, price, book_id)
        )

        conn.commit()

        row = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(row)), 200

    conn.execute(
        """
        INSERT INTO books (id, title, author, isbn, price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (book_id, title, author, isbn, price)
    )

    conn.commit()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(row)), 201


@app.route("/books/<int:book_id>", methods=["PATCH"])
def patch_book(book_id):
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Invalid JSON"
        }), 400

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return jsonify({
            "error": "Book not found"
        }), 404

    allowed_fields = ["title", "author", "isbn", "price"]

    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])

    if not updates:
        conn.close()
        return jsonify(dict(row)), 200

    values.append(book_id)

    conn.execute(
        f"""
        UPDATE books
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        values
    )

    conn.commit()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(row)), 200


@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is None:
        conn.close()
        return jsonify({
            "error": "Book not found"
        }), 404

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()

    return "", 204


if __name__ == "__main__":
    init_db()
    app.run(debug=True)