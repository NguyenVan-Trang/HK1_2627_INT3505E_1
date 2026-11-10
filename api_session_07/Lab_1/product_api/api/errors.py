
from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, error, detail, status_code):
        super().__init__(detail)
        self.error = error
        self.detail = detail
        self.status_code = status_code


class NotFound(ApiError):
    def __init__(self, detail="Product not found"):
        super().__init__("not_found", detail, 404)


class Conflict(ApiError):
    def __init__(self, detail="Resource conflict"):
        super().__init__("conflict", detail, 409)


class OutOfStock(ApiError):
    def __init__(self, detail="Insufficient stock"):
        super().__init__("out_of_stock", detail, 409)


def register_error_handlers(app):

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({
            "error": err.error,
            "detail": err.detail
        }), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({
            "error": "validation_error",
            "detail": err.messages
        }), 422

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return jsonify({
            "error": err.name.lower().replace(" ", "_"),
            "detail": err.description
        }), err.code

    @app.errorhandler(Exception)
    def handle_internal_error(err):
        app.logger.exception("Unhandled exception")

        return jsonify({
            "error": "internal_error",
            "detail": "An unexpected error occurred"
        }), 500
