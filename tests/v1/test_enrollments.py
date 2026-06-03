import uuid
from httpx import AsyncClient


async def create_course(client: AsyncClient, admin_headers: dict, capacity: int = 30) -> dict:
    """Helper to create a fresh course for each test."""
    response = await client.post(
        "/api/v1/courses/",
        json={
            "title": f"Course {uuid.uuid4().hex[:6]}",
            "code": f"EN-{uuid.uuid4().hex[:6].upper()}",
            "capacity": capacity,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_student(client: AsyncClient) -> dict:
    """Helper to register and login a fresh student, returns headers."""
    email = f"student-{uuid.uuid4()}@test.com"
    await client.post("/api/v1/auth/register", json={
        "name": "Student",
        "email": email,
        "password": "pass123",
        "role": "student",
    })
    login = await client.post("/api/v1/auth/token", data={
        "username": email,
        "password": "pass123",
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_student_can_enroll(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    response = await client.post(
        f"/api/v1/enrollments/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 201
    assert response.json()["course_id"] == course["id"]


async def test_admin_cannot_enroll(client: AsyncClient, admin_headers: dict):
    course = await create_course(client, admin_headers)
    response = await client.post(
        f"/api/v1/enrollments/{course['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 403


async def test_unauthenticated_cannot_enroll(client: AsyncClient, admin_headers: dict):
    course = await create_course(client, admin_headers)
    response = await client.post(f"/api/v1/enrollments/{course['id']}")
    assert response.status_code == 401


async def test_duplicate_enrollment_rejected(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    response = await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    assert response.status_code == 400


async def test_enroll_inactive_course_rejected(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    await client.patch(f"/api/v1/courses/{course['id']}/toggle", headers=admin_headers)
    response = await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    assert response.status_code == 400


async def test_enroll_full_course_rejected(client: AsyncClient, admin_headers: dict):
    course = await create_course(client, admin_headers, capacity=1)
    first_student = await create_student(client)
    await client.post(f"/api/v1/enrollments/{course['id']}", headers=first_student)
    second_student = await create_student(client)
    response = await client.post(f"/api/v1/enrollments/{course['id']}", headers=second_student)
    assert response.status_code == 400


async def test_enroll_nonexistent_course(client: AsyncClient, student_headers: dict):
    response = await client.post("/api/v1/enrollments/999999", headers=student_headers)
    assert response.status_code == 404


async def test_student_can_deregister(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    response = await client.delete(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    assert response.status_code == 204


async def test_deregister_not_enrolled(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    response = await client.delete(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    assert response.status_code == 404


async def test_admin_get_all_enrollments(client: AsyncClient, admin_headers: dict):
    response = await client.get("/api/v1/enrollments/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


async def test_student_cannot_get_all_enrollments(client: AsyncClient, student_headers: dict):
    response = await client.get("/api/v1/enrollments/", headers=student_headers)
    assert response.status_code == 403


async def test_admin_get_enrollments_by_course(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    response = await client.get(
        f"/api/v1/enrollments/course/{course['id']}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


async def test_student_cannot_get_enrollments_by_course(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    response = await client.get(
        f"/api/v1/enrollments/course/{course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 403


async def test_admin_remove_student_from_course(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    enroll = await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    enrollment_id = enroll.json()["id"]
    response = await client.delete(
        f"/api/v1/enrollments/admin/{enrollment_id}",
        headers=admin_headers,
    )
    assert response.status_code == 204


async def test_student_cannot_admin_remove(client: AsyncClient, admin_headers: dict, student_headers: dict):
    course = await create_course(client, admin_headers)
    enroll = await client.post(f"/api/v1/enrollments/{course['id']}", headers=student_headers)
    enrollment_id = enroll.json()["id"]
    response = await client.delete(
        f"/api/v1/enrollments/admin/{enrollment_id}",
        headers=student_headers,
    )
    assert response.status_code == 403
