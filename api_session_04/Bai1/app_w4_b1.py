
from flask import Flask, request, jsonify
from uuid import UUID, uuid4
from datetime import date

app = Flask(__name__)

# Token dùng để demo xác thực API.
API_TOKEN = "demo-token"

VALID_STATUSES = {"open", "done"}
VALID_PRIORITIES = {"low", "normal", "high"}

# Dữ liệu mẫu lưu trong bộ nhớ.
tasks = {
    "550e8400-e29b-41d4-a716-446655440000": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Hoàn thành API Specification",
        "status": "open",
        "priority": "high",
        "dueDate": "2026-10-15",
        "assigneeId": "user-001"
    },
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8": {
        "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "title": "Kiểm tra Swagger Editor",
        "status": "done",
        "priority": "normal",
        "dueDate": "2026-10-10",
        "assigneeId": "user-002"
    }
}


def error_response(status, title, detail):
    """Trả về lỗi theo cấu trúc Error trong OpenAPI."""
    return jsonify({
        "status": status,
        "title": title,
        "detail": detail
    }), status


@app.before_request
def check_authentication():
    """Yêu cầu Bearer token cho các API."""
    if not request.path.startswith("/v1/"):
        return None

    auth_header = request.headers.get("Authorization", "")
    expected_token = f"Bearer {API_TOKEN}"

    if auth_header != expected_token:
        return error_response(
            401,
            "Unauthorized",
            "Thiếu hoặc sai Bearer token"
        )

    return None


def validate_task_fields(data, creating=False):
    """Kiểm tra dữ liệu tạo mới hoặc cập nhật task."""
    if not isinstance(data, dict):
        return "Request body phải là một JSON object"

    if creating and not data.get("title"):
        return "Trường title là bắt buộc"

    allowed_fields = {
        "title", "status", "priority", "dueDate", "assigneeId"
    }

    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        return f"Trường không hợp lệ: {', '.join(sorted(unknown_fields))}"

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return "title phải là chuỗi không rỗng"

    if "status" in data and data["status"] not in VALID_STATUSES:
        return "status phải là open hoặc done"

    if "priority" in data and data["priority"] not in VALID_PRIORITIES:
        return "priority phải là low, normal hoặc high"

    if "dueDate" in data:
        try:
            date.fromisoformat(data["dueDate"])
        except (ValueError, TypeError):
            return "dueDate phải có định dạng YYYY-MM-DD"

    if "assigneeId" in data and not isinstance(data["assigneeId"], str):
        return "assigneeId phải là chuỗi"

    return None


def is_valid_uuid(value):
    try:
        UUID(value)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


# GET /v1/tasks
@app.get("/v1/tasks")
def list_tasks():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return error_response(422, "Validation Error", "limit phải là số nguyên")

    if not 1 <= limit <= 100:
        return error_response(
            422, "Validation Error", "limit phải nằm trong khoảng 1 đến 100"
        )

    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return error_response(
            422, "Validation Error", "status phải là open hoặc done"
        )

    result = list(tasks.values())

    if status:
        result = [task for task in result if task["status"] == status]

    total = len(result)
    result = result[:limit]

    return jsonify({
        "data": result,
        "limit": limit,
        "total": total
    }), 200


# POST /v1/tasks
@app.post("/v1/tasks")
def create_task():
    data = request.get_json(silent=True)
    error = validate_task_fields(data, creating=True)

    if error:
        return error_response(422, "Validation Error", error)

    task_id = str(uuid4())

    task = {
        "id": task_id,
        "title": data["title"],
        "status": data.get("status", "open"),
        "priority": data.get("priority", "normal"),
        "dueDate": data.get("dueDate"),
        "assigneeId": data.get("assigneeId")
    }

    tasks[task_id] = task
    return jsonify(task), 201


# GET /v1/tasks/{taskId}
@app.get("/v1/tasks/<task_id>")
def get_task(task_id):
    if not is_valid_uuid(task_id):
        return error_response(422, "Validation Error", "taskId không hợp lệ")

    task = tasks.get(task_id)

    if task is None:
        return error_response(404, "Not Found", "Không tìm thấy task")

    return jsonify(task), 200


# PATCH /v1/tasks/{taskId}
@app.patch("/v1/tasks/<task_id>")
def patch_task(task_id):
    if not is_valid_uuid(task_id):
        return error_response(422, "Validation Error", "taskId không hợp lệ")

    task = tasks.get(task_id)

    if task is None:
        return error_response(404, "Not Found", "Không tìm thấy task")

    data = request.get_json(silent=True)
    error = validate_task_fields(data)

    if error:
        return error_response(422, "Validation Error", error)

    if not data:
        return error_response(
            422, "Validation Error", "Cần cung cấp ít nhất một trường để cập nhật"
        )

    task.update(data)
    return jsonify(task), 200


# DELETE /v1/tasks/{taskId}
@app.delete("/v1/tasks/<task_id>")
def delete_task(task_id):
    if not is_valid_uuid(task_id):
        return error_response(422, "Validation Error", "taskId không hợp lệ")

    if task_id not in tasks:
        return error_response(404, "Not Found", "Không tìm thấy task")

    del tasks[task_id]
    return "", 204


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
