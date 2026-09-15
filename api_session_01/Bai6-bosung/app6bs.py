from flask import Flask, jsonify, request

app = Flask(__name__)

next_id = 1

BOOKS = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925},
]

def find_book(book_id):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None

@app.route("/books", methods=["GET"])
def get_books():
    q = request.args.get("q", "").strip().lower()
    sort_by = request.args.get("sort")
    limit = int(request.args.get("limit", len(BOOKS)))

    result = []
    for book in BOOKS:
        if q in book["title"].lower() or q in book["author"].lower():
            result.append(book)

    if sort_by in ["title", "author", "year"]:
        result = sorted(result, key=lambda b: str(b[sort_by]).lower() if isinstance(b[sort_by], str) else b[sort_by])

    return jsonify(result[:limit]), 200

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
    year = body.get("year")

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    if year is None:
        return jsonify({"error": "Year is required"}), 400
    if not isinstance(year, int) or year < 1900:
        return jsonify({"error": "Year must be an integer >= 1900"}), 400
    
    next_id += 1
    new_book = {"id": next_id, "title": title, "author": author, "year": year}

    BOOKS.append(new_book)
    return jsonify(new_book), 201, {"Location": f"/books/{new_book['id']}"}

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    body = request.get_json(silent=True) or {}

    if "year" in body:
        new_year = body["year"]
        if not isinstance(new_year, int) or new_year < 1900:
            return jsonify({"error": "Year must be an integer >= 1900"}), 400

    book.update({k: v for k, v in body.items() if k in ("title", "author", "year")})

    return jsonify(book), 200

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404

    BOOKS.remove(book)
    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)