import sqlite3
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