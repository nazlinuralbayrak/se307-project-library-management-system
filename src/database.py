import sqlite3
import os
import csv
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "library.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_books.csv")

def get_connection():
    """Connect to the SQLite database and return rows as dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and create tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Table of members
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'member'
    );
    """)

    # 2. Table of books
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE NOT NULL,
        total_copies INTEGER NOT NULL DEFAULT 1,
        available_copies INTEGER NOT NULL DEFAULT 1
    );
    """)

    # 3. Table of loans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        loan_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        status TEXT NOT NULL DEFAULT 'active',
        FOREIGN KEY (member_id) REFERENCES members (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    );
    """)

    # 4. Table of notifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        due_date DATE NOT NULL,
        message_text TEXT NOT NULL,
        date_created DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'simulated_sent',
        FOREIGN KEY (loan_id) REFERENCES loans (id),
        FOREIGN KEY (member_id) REFERENCES members (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    );
    """)

    conn.commit()
    conn.close()
    print("Database and tables initialized successfully.")

def seed_data():
    """Seed initial sample books and test accounts into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Default initial accounts (passwords securely hashed)
    default_users = [
        ("Library Admin", "admin@library.com", generate_password_hash("admin123"), "librarian"),
        ("Sample Student", "student@library.com", generate_password_hash("student123"), "member")
    ]

    for name, email, pwd_hash, role in default_users:
        cursor.execute("""
        INSERT OR IGNORE INTO members (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """, (name, email, pwd_hash, role))

    # Populate catalog from CSV dataset
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute("""
                INSERT OR IGNORE INTO books (title, author, isbn, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    row["title"],
                    row["author"],
                    row["isbn"],
                    int(row["total_copies"]),
                    int(row["available_copies"])
                ))

    conn.commit()
    conn.close()
    print("Database seed completed successfully.")

if __name__ == "__main__":
    init_db()
    seed_data()