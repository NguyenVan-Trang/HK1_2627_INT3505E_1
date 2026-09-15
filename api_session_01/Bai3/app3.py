from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)

PRODUCTS = []

@app.route("/products", methods=["POST"])
def create_product():
    body = request.get_json(silent=True) or {}
    name = body.get("name")
    
    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_product = {
        "id": str(uuid4()),
        "name": name,
        "price": body.get("price", 0.0)
    }
    
    PRODUCTS.append(new_product)

    return {"id": new_product["id"], "name": new_product["name"]}, 201

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)