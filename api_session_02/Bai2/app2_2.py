from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

BOOKS = []
next_id = 1 


@app.route('/books', methods=['GET'])
def get_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in BOOKS if b['id'] == book_id), None)

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book), 200

@app.route('/books/<int:book_id>', methods=['PUT'])
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