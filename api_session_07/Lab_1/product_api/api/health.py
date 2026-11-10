
from flask import Blueprint, jsonify
from sqlalchemy import text

from product_api.extensions import db


health_bp = Blueprint("health", __name__)


# Liveness check: kiểm tra ứng dụng Flask còn hoạt động
@health_bp.get("/healthz")
def healthz():
    return jsonify({
        "status": "ok"
    }), 200


# Readiness check: kiểm tra ứng dụng có thể kết nối database
@health_bp.get("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "status": "not_ready",
            "database": "disconnected"
        }), 503
