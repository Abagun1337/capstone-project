import uuid
import pytest
from httpx import AsyncClient


def random_email():
    return f"user-{uuid.uuid4()}@test.com"


# ── Register ──────────────────────────────────────────────────────

async def test_register_student(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Test Student",
        "email": random_email(),
        "password": "testpass123",
        "role": "student",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "student"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_admin(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "name": "Test Admin",
        "email": random_email(),
        "password": "adminpass123",
        "role": "admin",
    })
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


async def test_register_duplicate_email(client: AsyncClient):
    email = random_email()
    await client.post("/api/v1/auth/register", json={
        "name": "User One",
        "email": email,
        "password": "testpass123",
        "role": "student",
    })
    response = await client.post("/api/v1/auth/register", json={
        "name": "User Two",
        "email": email,
        "password": "testpass123",
        "role": "student",
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


async def test_login_success(client: AsyncClient):
    email = random_email()
    await client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": email,
        "password": "testpass123",
        "role": "student",
    })
    response = await client.post("/api/v1/auth/token", data={
        "username": email,
        "password": "testpass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    email = random_email()
    await client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": email,
        "password": "testpass123",
        "role": "student",
    })
    response = await client.post("/api/v1/auth/token", data={
        "username": email,
        "password": "wrongpass",
    })
    assert response.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post("/api/v1/auth/token", data={
        "username": "nobody@test.com",
        "password": "testpass123",
    })
    assert response.status_code == 401


async def test_login_inactive_user(client: AsyncClient, admin_headers: dict):
    email = f"inactive-{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Inactive User",
        "email": email,
        "password": "testpass123",
        "role": "student",
    })
    user_id = reg.json()["id"]
    await client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
    response = await client.post("/api/v1/auth/token", data={
        "username": email,
        "password": "testpass123",
    })
    assert response.status_code in (400, 403)


async def test_get_me(client: AsyncClient, student_headers: dict):
    response = await client.get("/api/v1/auth/me", headers=student_headers)
    assert response.status_code == 200
    assert "email" in response.json()


async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
