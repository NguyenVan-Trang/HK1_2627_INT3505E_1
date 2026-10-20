
from flask import Flask
from models import db
from routes.books import bp as books_bp
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "bookstore.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(books_bp, url_prefix="/api/v1/books")

with app.app_context():
    db.create_all()


@app.get("/")
def home():
    return {
        "message": "Bookstore API is running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
