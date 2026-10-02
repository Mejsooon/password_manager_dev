from typing import cast

import mysql.connector

from app.core.config import settings


def test_register_user(client):
    response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 201

    data = response.json()

    user_id = cast(int, data["id"])

    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert data["username"] == "mikolaj"

    connection = mysql.connector.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", ("mikolaj",))
        user = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    assert user is not None
    assert user["id"] == user_id
    assert user["username"] == "mikolaj"
    assert user["password_hash"] != "Test123!"
    assert user["password_hash"].startswith("$2")


def test_register_duplicate_username(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/register", json={"username": "mikolaj", "password": "AnotherPassword!"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}


def test_login(client):
    register_response = client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    user_id = cast(int, register_response.json()["id"])

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "Test123!"})

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"] != ""
    assert "id" not in data
    assert user_id > 0


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "mikolaj", "password": "Test123!"})

    response = client.post("/auth/login", json={"username": "mikolaj", "password": "WrongPassword!"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_current_user_with_jwt(authenticated_client):
    response = authenticated_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": response.json()["id"],
        "username": "mikolaj",
    }


def test_current_user_without_jwt(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}