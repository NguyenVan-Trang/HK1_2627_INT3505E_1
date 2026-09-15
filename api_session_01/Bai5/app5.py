from flask import Flask, jsonify

app = Flask(__name__)

ORDERS = {
    "ord_01": {"id": "ord_01", "item": "Laptop Dell", "status": "pending"},    
    "ord_02": {"id": "ord_02", "item": "Ban phim co", "status": "shipped"},    
    "ord_03": {"id": "ord_03", "item": "Chuot Logitech", "status": "delivered"} 
}

@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(ORDERS), 200

@app.route("/orders/<order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    if order["status"] in {"shipped", "delivered"}:
        return jsonify({"error": "Cannot delete an order that has been shipped or delivered"}), 409

    ORDERS.pop(order_id, None)

    return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)