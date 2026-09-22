from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Clean Architecture", "author": "Robert C. Martin"},
    {"id": 3, "title": "The Clean Coder", "author": "Robert C. Martin"},
    {"id": 4, "title": "1984", "author": "Orwell"},
    {"id": 5, "title": "Animal Farm", "author": "Orwell"},
    {"id": 6, "title": "Domain-Driven Design", "author": "Eric Evans"},
    {"id": 7, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
    {"id": 8, "title": "Design Patterns", "author": "Erich Gamma"},
    {"id": 9, "title": "Refactoring", "author": "Martin Fowler"},
    {"id": 10, "title": "Effective Java", "author": "Joshua Bloch"},
    {"id": 11, "title": "Java Concurrency in Practice", "author": "Brian Goetz"},
    {"id": 12, "title": "Head First Design Patterns", "author": "Eric Freeman"},
    {"id": 13, "title": "Introduction to Algorithms", "author": "Thomas Cormen"},
    {"id": 14, "title": "The Mythical Man-Month", "author": "Frederick Brooks"},
    {"id": 15, "title": "Software Engineering", "author": "Ian Sommerville"},
    {"id": 16, "title": "Code Complete", "author": "Steve McConnell"},
    {"id": 17, "title": "Working Effectively with Legacy Code", "author": "Michael Feathers"},
    {"id": 18, "title": "You Don't Know JS", "author": "Kyle Simpson"},
    {"id": 19, "title": "Learning Python", "author": "Mark Lutz"},
    {"id": 20, "title": "Computer Networks", "author": "Andrew Tanenbaum"},
    {"id": 21, "title": "The Art of Computer Programming", "author": "Donald Knuth"},
    {"id": 22, "title": "Don't Make Me Think", "author": "Steve Krug"},
    {"id": 23, "title": "The Design of Everyday Things", "author": "Don Norman"},
]

next_id = 24


DEFAULT_SIZE = 20
MAX_SIZE = 100


@app.route('/books', methods=['GET'])
def list_books():
    # Pagination
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify({
            "error": "page and size must be int"
        }), 400

    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    # Filtering
    flt = BOOKS

    author = request.args.get("author")
    if author:
        flt = [
            b for b in flt
            if b["author"].lower() == author.lower()
        ]

    # Search theo title
    q = request.args.get("q", "").lower()
    if q:
        flt = [
            b for b in flt
            if q in b["title"].lower()
        ]

    # Pagination
    total = len(flt)
    start = (page - 1) * size
    end = start + size

    items = flt[start:end]
    last = (total + size - 1) // size

    # HATEOAS links
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

    if end < total:
        links["next"] = {
            "href": u(page + 1)
        }

    # Response
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

    # Cache-Control
    resp.headers["Cache-Control"] = "public, max-age=30"

    return resp

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in BOOKS if b['id'] == book_id), None)

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book), 200

@app.route('/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    i = next((i for i, b in enumerate(BOOKS) if b["id"] == book_id), None)

    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 415

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    t = (data.get("title") or "").strip()
    a = (data.get("author") or "").strip()

    if not t or not a:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    # Resource đã tồn tại
    if i is not None:
        BOOKS[i] = {
            "id": book_id,
            "title": t,
            "author": a
        }

        return jsonify(BOOKS[i]), 200

    # Resource chưa tồn tại → tạo mới
    book = {
        "id": book_id,
        "title": t,
        "author": a
    }

    BOOKS.append(book)

    return jsonify(book), 201

@app.route('/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):
    i = next((k for k, b in enumerate(BOOKS) if b["id"] == book_id), None)

    if i is None:
        return jsonify(error="not found"), 404

    p = request.get_json(silent=True) or {}

    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422

    for k in "title author isbn price".split():
        if k in p:
            BOOKS[i][k] = p[k]

    return jsonify(BOOKS[i]), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)

    if book is None:
        return jsonify({"error": "not found"}), 404

    BOOKS.remove(book)

    return "", 204

@app.route('/books', methods=['POST'])
def create_book():
    global next_id

    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 415

    b = request.get_json(silent=True)

    if b is None:
        return jsonify({"error": "Invalid JSON"}), 400

    t = (b.get("title") or "").strip()
    a = (b.get("author") or "").strip()

    if not t or not a:
        return jsonify({
            "error": "Both title and author are required"
        }), 422

    book = {
        "id": next_id,
        "title": t,
        "author": a
    }

    BOOKS.append(book)
    next_id += 1

    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"

    return resp


if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )