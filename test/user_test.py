import pytest
from fastapi.testclient import TestClient

from app.user.models import Users
from app.user.queries import get_user_by_email_or_404
from main import server
from utils.database import connect_to_database, disconnect_from_database, get_db

client = TestClient(server)


@pytest.fixture(scope="module")
def db():
    connect_to_database()
    db = get_db()
    try:
        yield db
    finally:
        db.close()
        disconnect_from_database()


@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    connect_to_database()
    yield
    # Teardown
    disconnect_from_database()


def test_signup_success():
    response = client.post(
        "/accounts/signup",
        json={
            "email": "test@example.com",
            "password": "strongpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User created successfully, please check your email for verification."
    assert "data" in data
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["full_name"] == "Test User"


def test_signup_duplicate_email():
    response = client.post(
        "/accounts/signup",
        json={
            "email": "test@example.com",
            "password": "anotherpassword123",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


def test_signup_invalid_email():
    response = client.post(
        "/accounts/signup",
        json={
            "email": "invalidemail",
            "password": "password123",
            "full_name": "Invalid Email User"
        }
    )
    assert response.status_code == 422


def test_signup_weak_password():
    response = client.post(
        "/accounts/signup",
        json={
            "email": "weakpass@example.com",
            "password": "123",
            "full_name": "Weak Password User"
        }
    )
    assert response.status_code == 422


def test_login_success(db):
    # First, ensure the user exists and is verified
    user = get_user_by_email_or_404(db, "test@example.com")
    user.is_verified = True
    db.commit()

    response = client.post(
        "/accounts/login",
        json={
            "email": "test@example.com",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


def test_login_unverified_user(db):
    # Create an unverified user
    client.post(
        "/accounts/signup",
        json={
            "email": "unverified@example.com",
            "password": "password123",
            "full_name": "Unverified User"
        }
    )

    response = client.post(
        "/accounts/login",
        json={
            "email": "unverified@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert "email not verified" in response.json()["detail"].lower()


def test_login_invalid_credentials():
    response = client.post(
        "/accounts/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


def test_login_non_existent_user():
    response = client.post(
        "/accounts/login",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
    )
    assert response.status_code == 404
    assert "user not found" in response.json()["detail"].lower()


# Clean up the database after all tests
@pytest.fixture(scope="module", autouse=True)
def cleanup(db):
    yield
    db.query(Users).filter(Users.email.in_(["test@example.com", "unverified@example.com"])).delete(
        synchronize_session=False)
    db.commit()
