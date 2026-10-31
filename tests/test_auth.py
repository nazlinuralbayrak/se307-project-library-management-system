"""Tests for the authentication module (register, login, roles)."""
import os

import pytest
from flask import Flask

from src import database
from src.auth import auth_bp

TEMPLATES = os.path.join(os.path.dirname(__file__), "..", "templates")


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client that uses a temporary database."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    database.seed_data()

    app = Flask(__name__, template_folder=TEMPLATES)
    app.secret_key = "test-secret"
    app.register_blueprint(auth_bp)
    return app.test_client()


def register(client, email="new@test.com", password="123456", confirm="123456"):
    return client.post("/register", data={
        "name": "Test User", "email": email,
        "password": password, "confirm_password": confirm,
    }, follow_redirects=True)


def login(client, email, password):
    return client.post("/login", data={"email": email, "password": password},
                       follow_redirects=True)


def test_register_success(client):
    response = register(client)
    assert b"Registration successful" in response.data


def test_register_duplicate_email(client):
    register(client)
    response = register(client)
    assert b"already registered" in response.data


def test_register_password_mismatch(client):
    response = register(client, confirm="654321")
    assert b"do not match" in response.data


def test_register_short_password(client):
    response = register(client, password="123", confirm="123")
    assert b"at least 6 characters" in response.data


def test_login_success(client):
    response = login(client, "student@library.com", "student123")
    assert b"Logged in as Sample Student" in response.data


def test_login_wrong_password(client):
    response = login(client, "student@library.com", "wrongpass")
    assert b"Invalid email or password" in response.data


def test_login_unknown_email(client):
    response = login(client, "nobody@test.com", "123456")
    assert b"Invalid email or password" in response.data


def test_profile_requires_login(client):
    response = client.get("/profile", follow_redirects=True)
    assert b"Please log in first" in response.data


def test_member_cannot_access_librarian_page(client):
    login(client, "student@library.com", "student123")
    response = client.get("/admin-test")
    assert response.status_code == 403


def test_librarian_can_access_librarian_page(client):
    login(client, "admin@library.com", "admin123")
    response = client.get("/admin-test")
    assert response.status_code == 200


def test_logout_clears_session(client):
    login(client, "student@library.com", "student123")
    client.get("/logout")
    response = client.get("/profile", follow_redirects=True)
    assert b"Please log in first" in response.data