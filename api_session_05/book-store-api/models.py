
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text, ForeignKey, Table, Column
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Bảng trung gian cho quan hệ N:M giữa Book và Author
book_authors = Table(
    "book_authors",
    db.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    isbn = db.Column(String(13), unique=True)
    price_vnd = db.Column(Integer, nullable=False)
    stock = db.Column(Integer, default=0)
    category_id = db.Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="books")
    authors = relationship(
        "Author",
        secondary=book_authors,
        back_populates="books"
    )
    reviews = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category_id": self.category_id,
            "authors": [
                {"id": author.id, "name": author.name}
                for author in self.authors
            ]
        }


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    bio = db.Column(Text)

    books = relationship(
        "Book",
        secondary=book_authors,
        back_populates="authors"
    )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    slug = db.Column(String(100), unique=True, nullable=False)

    books = relationship("Book", back_populates="category")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(255), unique=True, nullable=False)
    display_name = db.Column(String(100), nullable=False)

    reviews = relationship("Review", back_populates="user")


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(Integer, primary_key=True)
    rating = db.Column(Integer, nullable=False)
    book_id = db.Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = db.Column(Integer, ForeignKey("users.id"), nullable=False)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
