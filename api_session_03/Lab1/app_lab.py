from flask import Flask, request, jsonify

app = Flask(__name__)

posts = [
    {
        "id": 1,
        "title": "Introduction to REST API",
        "content": "REST API uses resources and HTTP methods.",
        "author_id": 1
    },
    {
        "id": 2,
        "title": "Flask API",
        "content": "Building API with Flask.",
        "author_id": 2
    }
]

next_id = 3


@app.route("/api/v1/posts", methods=["GET"])
def get_posts():
    return jsonify({
        "data": posts,
        "total": len(posts)
    }), 200


@app.route("/api/v1/posts", methods=["POST"])
def create_post():
    global next_id

    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 415

    data = request.get_json()

    if not data.get("title") or not data.get("content"):
        return jsonify({
            "error": "title and content are required"
        }), 422

    post = {
        "id": next_id,
        "title": data["title"],
        "content": data["content"],
        "author_id": data.get("author_id", 1)
    }

    posts.append(post)
    next_id += 1

    return jsonify(post), 201


if __name__ == "__main__":
    app.run(debug=True)