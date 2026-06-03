import uuid
from httpx import AsyncClient


def random_email():
    return f"user-{uuid.uuid4()}@test.com"


async def register_and_login(client: AsyncClient, role: str = "student") -> tuple[dict, int]:
    """Helper — returns (auth_headers, user_id)."""
    email = random_email()
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": "testpass123",
        "role": role,
    })
    user_id = reg.json()["id"]
    login = await client.post("/api/v1/auth/token", data={
        "username": email,
        "password": "testpass123",
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


async def test_get_me(client: AsyncClient, student_headers: dict):
    response = await client.get("/api/v1/users/me", headers=student_headers)
    assert response.status_code == 200
    assert "email" in response.json()


async def test_get_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


async def test_get_user_by_id(client: AsyncClient, student_headers: dict):
    headers, user_id = await register_and_login(client)
    response = await client.get(f"/api/v1/users/{user_id}", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


async def test_get_user_not_found(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/users/999999", headers=admin_headers)
    assert response.status_code == 404


async def test_get_user_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/users/1")
    assert response.status_code == 401


async def test_admin_get_all_users(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/users/", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_student_cannot_get_all_users(client: AsyncClient, student_headers: dict):
    response = await client.get("/api/v1/users/", headers=student_headers)
    assert response.status_code == 403


async def test_get_all_users_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/users/")
    assert response.status_code == 401


async def test_update_own_profile(client: AsyncClient):
    headers, user_id = await register_and_login(client)
    response = await client.put(
        f"/api/v1/users/{user_id}",
        json={"name": "Updated Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


async def test_update_other_user_forbidden(client: AsyncClient, student_headers: dict):
    _, other_user_id = await register_and_login(client)
    response = await client.put(
        f"/api/v1/users/{other_user_id}",
        json={"name": "Hacked"},
        headers=student_headers,
    )
    assert response.status_code == 403


async def test_admin_delete_user(client: AsyncClient, admin_headers: dict):
    _, user_id = await register_and_login(client, role="student")
    response = await client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
    assert response.status_code == 204


async def test_student_cannot_delete_user(client: AsyncClient, student_headers: dict):
    _, user_id = await register_and_login(client, role="student")
    response = await client.delete(f"/api/v1/users/{user_id}", headers=student_headers)
    assert response.status_code == 403
