from functools import wraps
from flask import Flask, jsonify, request

app = Flask(__name__)

LATEST = "2"

SUPPORTED = {
    "1",
    "2",
    "2024-06-20"
}

USERS = {
    1: {
        "f": "Van",
        "l": "Nguyen",
        "e": "a@vnu.vn"
    }
}


# Decorator quản lý API Version
def api_version(
    supported=SUPPORTED,
    default=LATEST
):

    def decorate(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            # Lấy version từ HTTP Header
            version = request.headers.get(
                "X-API-Version",
                default
            )

            # Kiểm tra version có được hỗ trợ không
            if version not in supported:
                return jsonify({
                    "error": "unsupported version",
                    "version": version
                }), 400

            # Gọi endpoint với version tương ứng
            result = fn(version, *args, **kwargs)

            response = jsonify(result)

            # Gắn version thực tế vào response
            response.headers[
                "X-API-Version-Served"
            ] = version

            return response

        return wrapper

    return decorate


@app.route("/users/<int:uid>", methods=["GET"])
@api_version()
def get_user(version, uid):

    user = USERS.get(uid)

    if not user:
        return {"error": "User not found"}, 404

    # Version 1
    if version == "1":
        return {
            "id": uid,
            "full_name": (
                user["f"] + " " + user["l"]
            )
        }

    # Version 2 và dated version
    return {
        "id": uid,
        "first_name": user["f"],
        "last_name": user["l"],
        "email": user["e"]
    }


if __name__ == "__main__":
    app.run(debug=True)