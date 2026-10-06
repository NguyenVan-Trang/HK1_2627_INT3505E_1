from flask import Flask, request, jsonify
import base64
import json

app = Flask(__name__)

orders = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 120},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 80},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 200},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 50},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 150},
    {"id": 6, "customer_id": 104, "status": "pending", "total": 90},
    {"id": 7, "customer_id": 103, "status": "paid", "total": 300},
    {"id": 8, "customer_id": 101, "status": "pending", "total": 70},
    {"id": 9, "customer_id": 104, "status": "paid", "total": 180},
    {"id": 10, "customer_id": 102, "status": "cancelled", "total": 40}
]

VALID_FIELDS = {"id", "customer_id", "status", "total"}


def encode_cursor(offset):
    data = json.dumps({"offset": offset}).encode()
    return base64.urlsafe_b64encode(data).decode()


def decode_cursor(cursor):
    try:
        data = base64.urlsafe_b64decode(cursor.encode())
        return json.loads(data)["offset"]
    except Exception:
        raise ValueError("Invalid cursor")


@app.route("/orders", methods=["GET"])
def get_orders():
    result = orders.copy()

    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    sort = request.args.get("sort", "id")
    fields = request.args.get("fields")

    # Filter
    if status:
        result = [o for o in result if o["status"] == status]

    if customer_id:
        result = [o for o in result if str(o["customer_id"]) == customer_id]

    # Sort
    reverse = sort.startswith("-")
    sort_field = sort.lstrip("-")

    if sort_field not in VALID_FIELDS:
        return jsonify({"error": "Invalid sort field"}), 400

    result.sort(key=lambda x: x[sort_field], reverse=reverse)

    # Cursor
    cursor = request.args.get("cursor")
    offset = 0

    if cursor:
        try:
            offset = decode_cursor(cursor)
        except ValueError:
            return jsonify({"error": "Invalid cursor"}), 400

    # Limit
    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        return jsonify({"error": "Invalid limit"}), 400

    if limit < 1 or limit > 100:
        return jsonify({"error": "limit must be between 1 and 100"}), 400

    page = result[offset:offset + limit]

    next_cursor = None

    if offset + limit < len(result):
        next_cursor = encode_cursor(offset + limit)

    # Sparse fieldsets
    if fields:
        selected_fields = fields.split(",")

        for field in selected_fields:
            if field not in VALID_FIELDS:
                return jsonify({"error": f"Invalid field: {field}"}), 400

        page = [
            {field: order[field] for field in selected_fields}
            for order in page
        ]

    return jsonify({
        "data": page,
        "next": f"/orders?cursor={next_cursor}" if next_cursor else None
    }), 200


if __name__ == "__main__":
    app.run(debug=True)