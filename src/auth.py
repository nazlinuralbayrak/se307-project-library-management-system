"""Authentication module: user lookup, password hashing and registration."""
import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from src.database import get_connection

auth_bp = Blueprint("auth", __name__)


def get_user_by_email(email):
    """Return the member row with this email, or None."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM members WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user


def create_user(name, email, password, role="member"):
    """Insert a new member with a hashed password. Returns False if email exists."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO members (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), role),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_password(user, password):
    """Check a plain password against the stored hash."""
    return check_password_hash(user["password_hash"], password)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.")
        elif password != confirm:
            flash("Passwords do not match.")
        elif not create_user(name, email, password):
            flash("This email is already registered.")
        else:
            flash("Registration successful.")
            return redirect(url_for("auth.register"))  # will point to login on day 2

    return render_template("register.html")