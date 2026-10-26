import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "library.db")

def get_connection():
    """SQLite veritabanı bağlantısı oluşturur ve satırları sözlük gibi döndürür."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Veritabanı tablolarını sıfırdan oluşturur."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Üyeler Tablosu (Kişisel veri içermez, roller: member veya librarian)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'member'
    );
    """)

    # 2. Kitaplar Tablosu
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

    # 3. Ödünç İşlemleri Tablosu
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

    # 4. Bildirim Log Tablosu (4. üyenin hocadan onay aldığı şartlar için)
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
    print("Veritabanı ve tablolar başarıyla oluşturuldu.")

if __name__ == "__main__":
    init_db()