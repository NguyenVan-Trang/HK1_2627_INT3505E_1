from flask import Flask, jsonify, request
app = Flask(__name__)

next_id = 1

BOOKS = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
]

def find_book(book_id):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None

@app.route("/books", methods=["GET"])
def get_books():
    limit = int(request.args.get("limit", len(BOOKS)))
    return jsonify(BOOKS[:limit]), 200

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

@app.route("/books", methods=["POST"])
def create_book():
    global next_id
    body = request.get_json(silent=True) or {}

    title = body.get("title")
    author = body.get("author")

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400
    
    next_id += 1
    new_book = {"id": next_id, "title": title, "author": author}
    

    BOOKS.append(new_book)
    return jsonify(new_book), 201, {"Location": f"/books/{new_book['id']}"}

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    body = request.get_json(silent=True) or {}

    book.update({k: v for k, v in body.items() if k in ("title", "author")})

    return jsonify(book), 200

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    BOOKS.remove(book)
    return jsonify({"message": "Book deleted"}), 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
