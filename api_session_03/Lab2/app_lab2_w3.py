from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.ERROR)


class ProblemError(Exception):
    def __init__(self, status, title, detail):
        self.status = status
        self.title = title
        self.detail = detail


@app.errorhandler(ProblemError)
def handle_problem_error(error):
    response = {
        "type": "about:blank",
        "title": error.title,
        "detail": error.detail,
        "status": error.status,
        "instance": request.path
    }

    return jsonify(response), error.status, {
        "Content-Type": "application/problem+json"
    }


@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = {
        "type": "about:blank",
        "title": error.name,
        "detail": error.description,
        "status": error.code,
        "instance": request.path
    }

    return jsonify(response), error.code, {
        "Content-Type": "application/problem+json"
    }


@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.exception(error)

    response = {
        "type": "about:blank",
        "title": "Internal Server Error",
        "detail": "An unexpected error occurred.",
        "status": 500,
        "instance": request.path
    }

    return jsonify(response), 500, {
        "Content-Type": "application/problem+json"
    }


@app.route("/resources/<int:id>", methods=["GET"])
def get_resource(id):
    raise ProblemError(
        404,
        "Resource Not Found",
        f"Resource with id {id} was not found."
    )


@app.route("/test-error")
def test_error():
    raise Exception("Database connection failed")


if __name__ == "__main__":
    app.run(debug=False)