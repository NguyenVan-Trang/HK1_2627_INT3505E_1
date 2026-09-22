import sqlite3
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
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            price REAL
        )
    """)

    # Chỉ thêm dữ liệu mẫu nếu database đang trống
    count = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    if count == 0:
        books = [
            ("Clean Code", "Robert C. Martin"),
            ("Clean Architecture", "Robert C. Martin"),
            ("The Clean Coder", "Robert C. Martin"),
            ("1984", "Orwell"),
            ("Animal Farm", "Orwell"),
            ("Domain-Driven Design", "Eric Evans"),
            ("The Pragmatic Programmer", "Andrew Hunt"),
            ("Design Patterns", "Erich Gamma"),
            ("Refactoring", "Martin Fowler"),
            ("Effective Java", "Joshua Bloch"),
            ("Java Concurrency in Practice", "Brian Goetz"),
            ("Head First Design Patterns", "Eric Freeman"),
            ("Introduction to Algorithms", "Thomas Cormen"),
            ("The Mythical Man-Month", "Frederick Brooks"),
            ("Software Engineering", "Ian Sommerville"),
            ("Code Complete", "Steve McConnell"),
            ("Working Effectively with Legacy Code", "Michael Feathers"),
            ("You Don't Know JS", "Kyle Simpson"),
            ("Learning Python", "Mark Lutz"),
            ("Computer Networks", "Andrew Tanenbaum"),
            ("The Art of Computer Programming", "Donald Knuth"),
            ("Don't Make Me Think", "Steve Krug"),
            ("The Design of Everyday Things", "Don Norman")
        ]

        conn.executemany(
            """
            INSERT INTO books (title, author)
            VALUES (?, ?)
            """,
            books
        )

        conn.commit()

    conn.close()


@app.route('/books', methods=['GET'])
def list_books():

    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify({
            "error": "page and size must be int"
        }), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    conditions = []
    params = []

    # Filter author
    author = request.args.get("author")

    if author:
        conditions.append("LOWER(author) = LOWER(?)")
        params.append(author)

    # Search title
    q = request.args.get("q")

    if q:
        conditions.append("LOWER(title) LIKE LOWER(?)")
        params.append(f"%{q}%")

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    conn = get_db()

    # Tổng số kết quả sau filter
    total = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM books
        {where_clause}
        """,
        params
    ).fetchone()[0]

    # Pagination
    offset = (page - 1) * size

    rows = conn.execute(
        f"""
        SELECT *
        FROM books
        {where_clause}
        ORDER BY id
        LIMIT ? OFFSET ?
        """,
        params + [size, offset]
    ).fetchall()

    conn.close()

    items = [dict(row) for row in rows]

    last = (total + size - 1) // size

    def u(p):
        return f"/books?page={p}&size={size}"

    links = {
        "self": {
            "href": u(page)
        },
        "first": {
            "href": u(1)
        },
        "last": {
            "href": u(max(last, 1))
        }
    }

    if page > 1:
        links["prev"] = {
            "href": u(page - 1)
        }

    if offset + len(items) < total:
        links["next"] = {
            "href": u(page + 1)
        }

    body = {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": last
        },
        "_links": links
    }

    resp = make_response(jsonify(body), 200)

    resp.headers["Cache-Control"] = "public, max-age=30"

    return resp

@app.route('/books/<int:book_id>', methods=['GET'])
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

    resp = make_response(
        jsonify(dict(row)),
        200
    )

    resp.headers["Cache-Control"] = "max-age=60"

    return resp

@app.route('/books', methods=['POST'])
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

    if not title or not author:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO books (
            title,
            author,
            isbn,
            price
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            title,
            author,
            data.get("isbn"),
            data.get("price")
        )
    )

    conn.commit()

    book_id = cursor.lastrowid

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    book = dict(row)

    resp = make_response(
        jsonify(book),
        201
    )

    resp.headers["Location"] = f"/books/{book_id}"

    return resp

@app.route('/books/<int:book_id>', methods=['PUT'])
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

    if not title or not author:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    conn = get_db()

    row = conn.execute(
        "SELECT id FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is not None:

        conn.execute(
            """
            UPDATE books
            SET title = ?,
                author = ?,
                isbn = ?,
                price = ?
            WHERE id = ?
            """,
            (
                title,
                author,
                data.get("isbn"),
                data.get("price"),
                book_id
            )
        )

        conn.commit()

        updated = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        ).fetchone()

        conn.close()

        return jsonify(dict(updated)), 200

    conn.execute(
        """
        INSERT INTO books (
            id,
            title,
            author,
            isbn,
            price
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            book_id,
            title,
            author,
            data.get("isbn"),
            data.get("price")
        )
    )

    conn.commit()

    created = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(created)), 201

@app.route('/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "error": "not found"
        }), 404

    book = dict(row)

    data = request.get_json(silent=True) or {}

    # Kiểm tra price
    if (
        "price" in data
        and data["price"] is not None
        and data["price"] < 0
    ):
        conn.close()

        return jsonify({
            "error": "price must be positive"
        }), 422

    # Chỉ cập nhật field được gửi lên
    for field in ["title", "author", "isbn", "price"]:

        if field in data:
            book[field] = data[field]

    conn.execute(
        """
        UPDATE books
        SET title = ?,
            author = ?,
            isbn = ?,
            price = ?
        WHERE id = ?
        """,
        (
            book["title"],
            book["author"],
            book["isbn"],
            book["price"],
            book_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify(book), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    conn = get_db()

    row = conn.execute(
        "SELECT id FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "error": "not found"
        }), 404

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()

    return "", 204


if __name__ == '__main__':

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )