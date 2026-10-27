import os
import time
import uuid
from functools import wraps

import jwt
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "dev-only-change-this-secret-before-deployment"
)
app.config["ACCESS_TOKEN_SECONDS"] = 900
app.config["REFRESH_TOKEN_SECONDS"] = 30 * 24 * 60 * 60

USERS = {
    "alice@example.com": {
        "id": "user-alice",
        "password_hash": generate_password_hash("AliceDemo123!"),
        "scopes": ["posts:read", "auth:refresh"],
    },
    "bob@example.com": {
        "id": "user-bob",
        "password_hash": generate_password_hash("BobDemo123!"),
        "scopes": ["auth:refresh"],
    },
}

POSTS = {
    "post-001": {
        "id": "post-001",
        "author_id": "user-alice",
        "title": "Hello SOA",
        "content": "This is a sample post for the API demonstration.",
        "visibility": "public",
    },
    "post-002": {
        "id": "post-002",
        "author_id": "user-bob",
        "title": "Private draft",
        "content": "This sample post is private.",
        "visibility": "private",
    },
}

REVOKED_REFRESH_JTIS = set()


def error_response(status, code, message):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_token(user_id, scopes, token_type, lifetime_seconds):
    now = int(time.time())
    claims = {
        "sub": user_id,
        "scope": " ".join(scopes),
        "type": token_type,
        "iat": now,
        "exp": now + lifetime_seconds,
        "iss": "soa-auth-api-demo",
        "aud": "social-network-api",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(claims, app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token, expected_type):
    claims = jwt.decode(
        token,
        app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
        issuer="soa-auth-api-demo",
        audience="social-network-api",
        options={"require": ["sub", "exp", "iat", "iss", "aud", "jti", "type"]},
    )
    if claims.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return claims


def bearer_token():
    auth = request.headers.get("Authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def require_auth(required_scopes=None, token_type="access"):
    required_scopes = set(required_scopes or [])

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = bearer_token()
            if not token:
                return error_response(401, "UNAUTHORIZED", "A valid Bearer token is required.")
            try:
                claims = decode_token(token, token_type)
            except jwt.ExpiredSignatureError:
                return error_response(401, "TOKEN_EXPIRED", "The token has expired.")
            except jwt.InvalidTokenError:
                return error_response(401, "INVALID_TOKEN", "The token is invalid.")
            if token_type == "refresh" and claims["jti"] in REVOKED_REFRESH_JTIS:
                return error_response(401, "REFRESH_TOKEN_REVOKED", "The refresh token has been revoked.")

            actual_scopes = set(claims.get("scope", "").split())
            if not required_scopes.issubset(actual_scopes):
                return error_response(403, "INSUFFICIENT_SCOPE", "The token lacks the required scope.")
            request.jwt_claims = claims
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.get("/")
def index():
    return jsonify({"name": "Social Network Auth API Demo", "docs": "/docs", "openapi": "/openapi.yaml"})


@app.get("/openapi.yaml")
def openapi_yaml():
    return send_from_directory(app.root_path, "openapi.yaml", mimetype="application/yaml")


@app.get("/docs")
def swagger_ui():
    return """
    <!doctype html>
    <html>
      <head>
        <title>Social Network API - Swagger UI</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => SwaggerUIBundle({
            url: "/openapi.yaml",
            dom_id: "#swagger-ui",
            persistAuthorization: true
          });
        </script>
      </body>
    </html>
    """


@app.post("/auth/login")
def login():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error_response(400, "INVALID_REQUEST", "A JSON object is required.")
    email = body.get("email")
    password = body.get("password")
    if not isinstance(email, str) or not email.strip() or not isinstance(password, str) or not password:
        return error_response(400, "INVALID_REQUEST", "email and password are required.")
    user = USERS.get(email.strip().lower())
    # Generic message avoids disclosing whether an account exists.
    if not user or not check_password_hash(user["password_hash"], password):
        return error_response(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")

    access = create_token(user["id"], user["scopes"], "access", app.config["ACCESS_TOKEN_SECONDS"])
    refresh = create_token(user["id"], ["auth:refresh"], "refresh", app.config["REFRESH_TOKEN_SECONDS"])
    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": app.config["ACCESS_TOKEN_SECONDS"],
        "scope": " ".join(user["scopes"]),
    }), 200


@app.post("/auth/refresh")
@require_auth(required_scopes=["auth:refresh"], token_type="refresh")
def refresh():
    claims = request.jwt_claims
    REVOKED_REFRESH_JTIS.add(claims["jti"])
    user = next((u for u in USERS.values() if u["id"] == claims["sub"]), None)
    if not user:
        return error_response(401, "INVALID_TOKEN", "The token is invalid.")
    access = create_token(user["id"], user["scopes"], "access", app.config["ACCESS_TOKEN_SECONDS"])
    replacement = create_token(user["id"], ["auth:refresh"], "refresh", app.config["REFRESH_TOKEN_SECONDS"])
    return jsonify({
        "access_token": access,
        "refresh_token": replacement,
        "token_type": "Bearer",
        "expires_in": app.config["ACCESS_TOKEN_SECONDS"],
        "scope": " ".join(user["scopes"]),
    }), 200


@app.get("/posts/<post_id>")
@require_auth(required_scopes=["posts:read"], token_type="access")
def get_post(post_id):
    post = POSTS.get(post_id)
    if not post or (post["visibility"] == "private" and post["author_id"] != request.jwt_claims["sub"]):
        return error_response(404, "POST_NOT_FOUND", "The post was not found.")
    return jsonify({
        "id": post["id"],
        "author_id": post["author_id"],
        "title": post["title"],
        "content": post["content"],
        "visibility": post["visibility"],
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
