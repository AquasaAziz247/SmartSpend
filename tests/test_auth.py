import uuid
from datetime import datetime, timedelta, timezone

import jwt

from backend.security import JWT_SECRET_KEY


def test_valid_registration_returns_201(
    client,
    cleanup_user
):

    email = (
        f"auth_{uuid.uuid4().hex}"
        "@example.com"
    )

    cleanup_user(email)

    response = client.post(
        "/users/register",
        json={
            "name": "Auth Test User",
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Auth Test User"
    assert data["email"] == email
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_returns_400(
    client,
    cleanup_user
):

    email = (
        f"duplicate_{uuid.uuid4().hex}"
        "@example.com"
    )

    cleanup_user(email)

    first_response = client.post(
        "/users/register",
        json={
            "name": "First User",
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/users/register",
        json={
            "name": "Second User",
            "email": email,
            "password": "AnotherPassword123"
        }
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["detail"] == (
        "Email already registered"
    )


def test_invalid_registration_returns_422(
    client
):

    response = client.post(
        "/users/register",
        json={
            "name": "",
            "email": "",
            "password": ""
        }
    )

    assert response.status_code == 422


def test_correct_login_returns_token(
    client,
    cleanup_user
):

    email = (
        f"login_{uuid.uuid4().hex}"
        "@example.com"
    )

    cleanup_user(email)

    register_response = client.post(
        "/users/register",
        json={
            "name": "Login Test User",
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": email,
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_wrong_password_returns_401(
    client,
    cleanup_user
):

    email = (
        f"wrong_password_{uuid.uuid4().hex}"
        "@example.com"
    )

    cleanup_user(email)

    register_response = client.post(
        "/users/register",
        json={
            "name": "Wrong Password User",
            "email": email,
            "password": "CorrectPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": email,
            "password": "WrongPassword123"
        }
    )

    assert login_response.status_code == 401

    data = login_response.json()

    assert data["detail"] == (
        "Invalid email or password"
    )


def test_unknown_email_returns_401(
    client
):

    email = (
        f"unknown_{uuid.uuid4().hex}"
        "@example.com"
    )

    login_response = client.post(
        "/users/login",
        data={
            "username": email,
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 401

    data = login_response.json()

    assert data["detail"] == (
        "Invalid email or password"
    )


def test_valid_token_allows_access(
    client,
    cleanup_user
):

    email = (
        f"valid_token_{uuid.uuid4().hex}"
        "@example.com"
    )

    cleanup_user(email)

    register_response = client.post(
        "/users/register",
        json={
            "name": "Valid Token User",
            "email": email,
            "password": "TestPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/users/login",
        data={
            "username": email,
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_missing_token_returns_401(
    client
):

    response = client.get(
        "/expenses"
    )

    assert response.status_code == 401


def test_invalid_token_returns_401(
    client
):

    response = client.get(
        "/expenses",
        headers={
            "Authorization": "Bearer invalid.token.value"
        }
    )

    assert response.status_code == 401


def test_expired_token_returns_401(
    client
):

    expired_time = (
        datetime.now(timezone.utc)
        - timedelta(minutes=10)
    )

    token = jwt.encode(
        {
            "sub": "1",
            "exp": expired_time
        },
        JWT_SECRET_KEY,
        algorithm="HS256"
    )

    response = client.get(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401