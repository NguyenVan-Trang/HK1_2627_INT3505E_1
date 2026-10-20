from app import app
from models import db, Book, Category

with app.app_context():
    # Tạo 3 danh mục nếu chưa tồn tại
    categories_data = [
        {"name": "Programming", "slug": "programming"},
        {"name": "Database", "slug": "database"},
        {"name": "Software Engineering", "slug": "software-engineering"},
    ]

    categories = {}

    for item in categories_data:
        category = Category.query.filter_by(slug=item["slug"]).first()

        if category is None:
            category = Category(
                name=item["name"],
                slug=item["slug"]
            )
            db.session.add(category)

        categories[item["slug"]] = category

    db.session.flush()

    # Dữ liệu mẫu: cố ý có giá trùng nhau
    books_data = [
        {
            "title": "Python Basics",
            "isbn": "9780000000001",
            "price_vnd": 100000,
            "stock": 10,
            "category": "programming",
        },
        {
            "title": "Java Fundamentals",
            "isbn": "9780000000002",
            "price_vnd": 150000,
            "stock": 8,
            "category": "programming",
        },
        {
            "title": "Clean Architecture",
            "isbn": "9780000000003",
            "price_vnd": 200000,
            "stock": 5,
            "category": "software-engineering",
        },
        {
            "title": "SQL Essentials",
            "isbn": "9780000000004",
            "price_vnd": 100000,
            "stock": 12,
            "category": "database",
        },
        {
            "title": "Database Design",
            "isbn": "9780000000005",
            "price_vnd": 150000,
            "stock": 6,
            "category": "database",
        },
        {
            "title": "Design Patterns",
            "isbn": "9780000000006",
            "price_vnd": 200000,
            "stock": 4,
            "category": "software-engineering",
        },
        {
            "title": "Advanced Python",
            "isbn": "9780000000007",
            "price_vnd": 150000,
            "stock": 9,
            "category": "programming",
        },
        {
            "title": "Web Development",
            "isbn": "9780000000008",
            "price_vnd": 100000,
            "stock": 7,
            "category": "programming",
        },
    ]

    added = 0

    for item in books_data:
        exists = Book.query.filter_by(isbn=item["isbn"]).first()

        if exists:
            continue

        book = Book(
            title=item["title"],
            isbn=item["isbn"],
            price_vnd=item["price_vnd"],
            stock=item["stock"],
            category=categories[item["category"]],
        )
        db.session.add(book)
        added += 1

    db.session.commit()

    print(f"Đã thêm {added} sách mới.")
    print(f"Tổng số sách hiện tại: {Book.query.count()}")
    print(f"Tổng số danh mục: {Category.query.count()}")