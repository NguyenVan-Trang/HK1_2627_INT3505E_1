from flask import Blueprint
from .users_data import get_user

bp = Blueprint("v1", __name__)


@bp.route("/users/<int:uid>", methods=["GET"])
def get(uid):
    user = get_user(uid)

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": uid,
        "full_name": (
            f"{user['first_name']} {user['last_name']}"
        ),
        "email": user["email"]
    }