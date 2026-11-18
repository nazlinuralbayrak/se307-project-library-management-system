import sqlite3

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

DATABASE_PATH = "data/library.db"

def get_db_connection():
    """Connects to the SQLite database and sets row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def search_books(query="", category=""):
    """
    Searches books by title, author, or category.
    Returns a list of matching book records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql_query = "SELECT * FROM books WHERE 1=1"
    params = []
    
    if query:
        sql_query += " AND (title LIKE ? OR author LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
        
    if category:
        sql_query += " AND category = ?"
        params.append(category)
        
    cursor.execute(sql_query, params)
    books = cursor.fetchall()
    conn.close()
    return books

from datetime import datetime, timedelta

MAX_BORROW_LIMIT = 3
LOAN_DURATION_DAYS = 14

def get_member_active_loans(member_id):
    """Returns a list of currently borrowed (unreturned) books for a specific member."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT loans.id AS loan_id, books.id AS book_id, books.title, books.author, 
               loans.borrow_date, loans.due_date
        FROM loans
        JOIN books ON loans.book_id = books.id
        WHERE loans.member_id = ? AND loans.return_date IS NULL
    """
    cursor.execute(query, (member_id,))
    active_loans = cursor.fetchall()
    conn.close()
    return active_loans

def borrow_book(member_id, book_id):
    """
    Processes a book loan request.
    Checks book availability and member's maximum active loan limit.
    Returns a tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check if the book exists and is available
    cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return False, "Book not found."
        
    if not book["available"]:
        conn.close()
        return False, "This book is currently unavailable."
        
    # 2. Check if the member reached the maximum borrow limit
    cursor.execute(
        "SELECT COUNT(*) AS count FROM loans WHERE member_id = ? AND return_date IS NULL",
        (member_id,)
    )
    active_count = cursor.fetchone()["count"]
    
    if active_count >= MAX_BORROW_LIMIT:
        conn.close()
        return False, f"Borrow limit reached. You can borrow up to {MAX_BORROW_LIMIT} books at once."
        
    # 3. Create loan record and mark book as unavailable
    borrow_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=LOAN_DURATION_DAYS)).strftime("%Y-%m-%d")
    
    cursor.execute(
        "INSERT INTO loans (member_id, book_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
        (member_id, book_id, borrow_date, due_date)
    )
    cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
    
    conn.commit()
    conn.close()
    return True, f"Book borrowed successfully. Due date: {due_date}"

def return_book(loan_id):
    """
    Processes a book return.
    Updates the loan's return_date and marks the book as available again.
    Returns a tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT book_id, return_date FROM loans WHERE id = ?", (loan_id,))
    loan = cursor.fetchone()
    
    if not loan:
        conn.close()
        return False, "Loan record not found."
        
    if loan["return_date"] is not None:
        conn.close()
        return False, "This book has already been returned."
        
    return_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("UPDATE loans SET return_date = ? WHERE id = ?", (return_date, loan_id))
    cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (loan["book_id"],))
    
    conn.commit()
    conn.close()
    return True, "Book returned successfully."   

def get_dashboard_stats():
    """
    Generates library statistics and base64-encoded charts using pandas and matplotlib.
    Returns a dictionary with summary metrics and chart image strings.
    """
    conn = get_db_connection()
    
    # Load books and loans into pandas DataFrames
    books_df = pd.read_sql_query("SELECT * FROM books", conn)
    loans_df = pd.read_sql_query("SELECT * FROM loans", conn)
    conn.close()
    
    total_books = len(books_df)
    available_books = int(books_df["available"].sum()) if not books_df.empty else 0
    borrowed_books = total_books - available_books
    total_loans = len(loans_df)
    
    # Chart 1: Books by Category (Bar Chart)
    category_chart = None
    if not books_df.empty and "category" in books_df.columns:
        plt.figure(figsize=(6, 4))
        category_counts = books_df["category"].value_counts()
        category_counts.plot(kind="bar", color="#0d6efd", edgecolor="black")
        plt.title("Books by Category")
        plt.xlabel("Category")
        plt.ylabel("Number of Books")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        category_chart = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        
    # Chart 2: Book Availability Status (Pie Chart)
    status_chart = None
    if total_books > 0:
        plt.figure(figsize=(5, 4))
        plt.pie(
            [available_books, borrowed_books],
            labels=["Available", "Borrowed"],
            autopct="%1.1f%%",
            colors=["#198754", "#6c757d"],
            startangle=90
        )
        plt.title("Book Availability Ratio")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        status_chart = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        
    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books,
        "total_loans": total_loans,
        "category_chart": category_chart,
        "status_chart": status_chart
    }