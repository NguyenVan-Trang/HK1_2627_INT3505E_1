
from flask import Flask
from models import db
from routes.books_lab1 import bp as books_lab1_bp
from routes.books_lab2 import bp as books_lab2_bp
from routes.books_btvn2 import bp as books_btvn2_bp
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "bookstore.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

version = os.getenv("BOOKS_VERSION", "lab1").lower()

blueprints = {
    "lab1": books_lab1_bp,
    "lab2": books_lab2_bp,
    "btvn2": books_btvn2_bp,
}

if version not in blueprints:
    raise ValueError(
        "BOOKS_VERSION must be lab1, lab2, or btvn2"
    )

app.register_blueprint(
    books_btvn2_bp,
    url_prefix="/api/v1/books"
)

with app.app_context():
    db.create_all()


@app.get("/")
def home():
    return {
        "message": "Bookstore API is running",
        "version": version
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
