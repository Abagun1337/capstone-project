import uuid
from httpx import AsyncClient


def unique_course(prefix="CRS"):
    return {
        "title": f"Course {uuid.uuid4().hex[:6]}",
        "code": f"{prefix}-{uuid.uuid4().hex[:6].upper()}",
        "capacity": 30,
    }


async def test_get_all_active_courses(client: AsyncClient, sample_course: dict):
    response = await client.get("/api/v1/courses/")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


async def test_get_all_active_courses_no_auth(client: AsyncClient):
    response = await client.get("/api/v1/courses/")
    assert response.status_code == 200


async def test_get_course_by_id(client: AsyncClient, sample_course: dict):
    course_id = sample_course["id"]
    response = await client.get(f"/api/v1/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["id"] == course_id


async def test_get_course_not_found(client: AsyncClient):
    response = await client.get("/api/v1/courses/99999")
    assert response.status_code == 404


async def test_get_all_courses_admin(client: AsyncClient, admin_headers: dict, sample_course: dict):
    response = await client.get("/api/v1/courses/admin/all", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


async def test_get_all_courses_student_forbidden(client: AsyncClient, student_headers: dict):
    response = await client.get("/api/v1/courses/admin/all", headers=student_headers)
    assert response.status_code == 403


async def test_get_all_courses_unauthenticated(client: AsyncClient):
    response = await client.get("/api/v1/courses/admin/all")
    assert response.status_code == 401


async def test_create_course_admin(client: AsyncClient, admin_headers: dict):
    response = await client.post(
        "/api/v1/courses/",
        json=unique_course("NEW"),
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["is_active"] is True


async def test_create_course_student_forbidden(client: AsyncClient, student_headers: dict):
    response = await client.post(
        "/api/v1/courses/",
        json=unique_course("STU"),
        headers=student_headers,
    )
    assert response.status_code == 403


async def test_create_course_duplicate_code(client: AsyncClient, admin_headers: dict):
    data = unique_course("DUP")
    await client.post("/api/v1/courses/", json=data, headers=admin_headers)
    response = await client.post("/api/v1/courses/", json=data, headers=admin_headers)
    assert response.status_code == 400


async def test_create_course_invalid_capacity(client: AsyncClient, admin_headers: dict):
    data = unique_course("BAD")
    data["capacity"] = 0
    response = await client.post("/api/v1/courses/", json=data, headers=admin_headers)
    assert response.status_code == 422


async def test_update_course(client: AsyncClient, admin_headers: dict, sample_course: dict):
    course_id = sample_course["id"]
    response = await client.put(
        f"/api/v1/courses/{course_id}",
        json={"title": "Python Advanced", "capacity": 50},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Python Advanced"


async def test_update_course_student_forbidden(client: AsyncClient, student_headers: dict, sample_course: dict):
    response = await client.put(
        f"/api/v1/courses/{sample_course['id']}",
        json={"title": "Hacked"},
        headers=student_headers,
    )
    assert response.status_code == 403


async def test_toggle_course(client: AsyncClient, admin_headers: dict):

    course = await client.post(
        "/api/v1/courses/",
        json=unique_course("TOG"),
        headers=admin_headers,
    )
    course_id = course.json()["id"]
    original_status = course.json()["is_active"]
    response = await client.patch(
        f"/api/v1/courses/{course_id}/toggle",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] != original_status


async def test_toggle_course_student_forbidden(client: AsyncClient, student_headers: dict, sample_course: dict):
    response = await client.patch(
        f"/api/v1/courses/{sample_course['id']}/toggle",
        headers=student_headers,
    )
    assert response.status_code == 403


async def test_delete_course(client: AsyncClient, admin_headers: dict):

    course = await client.post(
        "/api/v1/courses/",
        json=unique_course("DEL"),
        headers=admin_headers,
    )
    course_id = course.json()["id"]

    response = await client.delete(f"/api/v1/courses/{course_id}", headers=admin_headers)
    assert response.status_code == 204

    public = await client.get("/api/v1/courses/")
    ids = [c["id"] for c in public.json()["items"]]
    assert course_id not in ids


async def test_delete_course_student_forbidden(client: AsyncClient, student_headers: dict, sample_course: dict):
    response = await client.delete(
        f"/api/v1/courses/{sample_course['id']}",
        headers=student_headers,
    )
    assert response.status_code == 403
