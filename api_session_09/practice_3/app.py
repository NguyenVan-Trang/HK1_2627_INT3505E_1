from datetime import datetime, timezone

from flask import Flask

from sunset import deprecate_at

app = Flask(__name__)


# Ngày API V1 chính thức ngừng hoạt động
V1_SUNSET = datetime(
    2020, 12, 31,
    23, 59, 59,
    tzinfo=timezone.utc
)


# API V1
@app.route("/api/v1/users/<int:uid>")
@deprecate_at(
    V1_SUNSET,
    replacement="/api/v2/users"
)
def get_v1(uid):

    return {
        "id": uid,
        "full_name": "Nguyen Van A"
    }


# API V2
@app.route("/api/v2/users/<int:uid>")
def get_v2(uid):

    return {
        "id": uid,
        "first_name": "Van",
        "last_name": "Nguyen"
    }


if __name__ == "__main__":
    app.run(debug=True)