from flask import Flask, request, jsonify

from gateway import dispatch

app = Flask(__name__)


@app.route("/orders", methods=["POST"])
def create_order():

    body = request.get_json(silent=True)

    # Validate request body
    if not isinstance(body, dict):
        return jsonify({
            "error": "Invalid JSON body"
        }), 400

    if not body.get("account_id"):
        return jsonify({
            "error": "account_id is required"
        }), 400

    if not body.get("product"):
        return jsonify({
            "error": "product is required"
        }), 400

    # Gateway dispatch
    which, result = dispatch(body)

    resp = jsonify(result)

    # Trả về handler đã xử lý request
    resp.headers["X-Order-Handler"] = which

    if which == "gone":
        return resp, 410

    return resp, (201 if which == "v2" else 200)


if __name__ == "__main__":
    app.run(debug=True, port=5000)