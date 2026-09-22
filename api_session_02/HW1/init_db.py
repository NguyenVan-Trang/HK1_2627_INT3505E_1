import sqlite3

DATABASE = "books.db"

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            price REAL
        )
    """)

    books = [
        ("Clean Code", "Robert C. Martin", "9780132350884", 25.0),
        ("Clean Architecture", "Robert C. Martin", "9780134494166", 30.0),
        ("The Clean Coder", "Robert C. Martin", "9780137081073", 28.0),
        ("1984", "George Orwell", "9780451524935", 15.0),
        ("Animal Farm", "George Orwell", "9780451526342", 12.0),
        ("Domain-Driven Design", "Eric Evans", "9780321125217", 35.0),
        ("The Pragmatic Programmer", "Andrew Hunt", "9780135957059", 32.0),
        ("Design Patterns", "Erich Gamma", "9780201633610", 40.0),
        ("Refactoring", "Martin Fowler", "9780134757599", 38.0),
        ("Effective Java", "Joshua Bloch", "9780134685991", 35.0),
        ("Java Concurrency in Practice", "Brian Goetz", "9780321349606", 42.0),
        ("Head First Design Patterns", "Eric Freeman", "9780596007126", 30.0),
        ("Introduction to Algorithms", "Thomas Cormen", "9780262046305", 50.0),
        ("The Mythical Man-Month", "Frederick Brooks", "9780201835953", 25.0),
        ("Software Engineering", "Ian Sommerville", "9780133943030", 45.0),
        ("Code Complete", "Steve McConnell", "9780735619678", 40.0),
        ("Working Effectively with Legacy Code", "Michael Feathers", "9780131177055", 35.0),
        ("You Don't Know JS", "Kyle Simpson", "9781491904244", 28.0),
        ("Learning Python", "Mark Lutz", "9781449355739", 40.0),
        ("Computer Networks", "Andrew Tanenbaum", "9780132126953", 45.0),
        ("The Art of Computer Programming", "Donald Knuth", "9780201896831", 60.0),
        ("Don't Make Me Think", "Steve Krug", "9780321965516", 25.0),
        ("The Design of Everyday Things", "Don Norman", "9780465050659", 30.0)
    ]

    conn.executemany("""
        INSERT INTO books (title, author, isbn, price)
        VALUES (?, ?, ?, ?)
    """, books)

    conn.commit()
    conn.close()

    print("books.db created successfully!")


if __name__ == "__main__":
    init_db()