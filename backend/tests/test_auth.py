import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"

def test_register_duplicate_user(client: TestClient, test_user):
    """Test registration with existing email."""
    response = client.post(
        "/auth/register",
        json={
            "email": test_user.email,
            "full_name": "Duplicate User",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_user(client: TestClient, test_user):
    """Test user login."""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user info."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication."""
    response = client.get("/auth/me")
    assert response.status_code == 401