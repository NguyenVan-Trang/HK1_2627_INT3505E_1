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