"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

"""Lab 1 - Test Books API."""
import copy
import pytest
from jsonschema import validate, ValidationError
from tools import get_book_schema

def test_empty_books_returns_empty_array(client):
    """A. GET /books khi database rỗng phải trả về []."""
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == []
    assert isinstance(response.get_json(), list)


def test_get_nonexistent_book_returns_404(client):
    """B. GET /books/9999 phải trả về 404 và code NOT_FOUND."""
    response = client.get("/books/9999")

    assert response.status_code == 404
    data = response.get_json()

    assert data["code"] == "NOT_FOUND"


def test_create_book_without_title_returns_400(client):
    """C. POST /books thiếu title phải trả về 400."""
    response = client.post(
        "/books",
        json={
            "author": "J.J. Geewax"
        }
    )

    assert response.status_code == 400
    data = response.get_json()

    assert "errors" in data
    assert any(error["field"] == "title" for error in data["errors"])


def test_delete_book_then_get_returns_404(client, sample_book):
    """D. Xóa sách rồi GET cùng ID phải trả về 404."""
    delete_response = client.delete(f"/books/{sample_book}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/books/{sample_book}")

    assert get_response.status_code == 404
    assert get_response.get_json()["code"] == "NOT_FOUND"

def test_book_response_json_schema(client):
    """BONUS: Validate Book response và từ chối field không khai báo."""

    # 1. Tạo sách hợp lệ
    response = client.post(
        "/books",
        json={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "year": 2008
        }
    )

    assert response.status_code == 201
    book_data = response.get_json()

    # 2. Lấy schema và tạo bản sao
    schema = copy.deepcopy(get_book_schema())

    # Chuyển nullable của OpenAPI sang kiểu JSON Schema
    schema["properties"]["year"]["type"] = ["integer", "null"]
    schema["properties"]["isbn"]["type"] = ["string", "null"]

    # 3. Kiểm tra response hợp lệ
    validate(instance=book_data, schema=schema)

    # 4. Thêm trường không được khai báo
    invalid_book = copy.deepcopy(book_data)
    invalid_book["password_hash"] = "123456"

    # 5. Xác nhận schema từ chối trường lạ
    with pytest.raises(ValidationError):
        validate(instance=invalid_book, schema=schema)