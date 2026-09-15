from flask import Flask, jsonify, request

app = Flask(__name__)

PRODUCTS = [
    {"id": "1", "name": "Ban phim co", "price": 500000},
    {"id": "2", "name": "Chuot khong day", "price": 250000},
    {"id": "3", "name": "Ban di chuot", "price": 50000},
    {"id": "4", "name": "Tai nghe Gaming", "price": 800000}
]

@app.route("/products/<product_id>", methods=["GET"])
def find_product_by_id(product_id):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

@app.route("/products", methods=["GET"])
def list_products():
    search_query = request.args.get("q", "").strip().lower()
    limit = request.args.get("limit", default=20, type=int)

    filtered_products = [
        p for p in PRODUCTS if search_query in p["name"].lower()
    ] if search_query else PRODUCTS

    result = filtered_products[:limit]
    
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)