"""Authentication module: registration, login, sessions and role checks."""
import sqlite3
from functools import wraps

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
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


def login_required(view):
    """Redirect to the login page if nobody is logged in."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(role):
    """Allow only users with the given role ('librarian' or 'member')."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.")
                return redirect(url_for("auth.login"))
            if session.get("role") != role:
                return "Forbidden: you do not have permission.", 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


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
            flash("Registration successful. Please log in.")
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if user is None or not verify_password(user, password):
            flash("Invalid email or password.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("auth.profile"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required
def profile():
    """Show the logged-in user (placeholder until the dashboard exists)."""
    return (f"Logged in as {session['name']} "
            f"(role: {session['role']}). <a href='/logout'>Logout</a>")


@auth_bp.route("/admin-test")
@role_required("librarian")
def admin_test():
    """Librarian-only demo page used to check role protection."""
    return "Librarian area OK."