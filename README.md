# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing a course enrollment platform. Implements JWT authentication, role-based access control (RBAC), PostgreSQL with async SQLAlchemy, Redis rate limiting, and comprehensive automated tests.

---

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** — relational database
- **SQLAlchemy (async)** — ORM
- **Alembic** — database migrations
- **Redis** — rate limiting
- **JWT** — authentication
- **Docker** — containerisation
- **pytest** — automated testing

---

## Project Structure

```
app/
├── api/v1/          # Routers (auth, users, courses, enrollments)
├── core/            # Config, security, deps, middleware, cache
├── models/          # SQLAlchemy models
├── repositories/    # Database access layer
├── services/        # Business logic
├── schemas/         # Pydantic request/response models
alembic/             # Migration files
tests/v1/            # Automated test suite
```

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Clone the Repository

```bash
git clone <your-repo-url>
cd CAPSTONE_PROJECT
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Start the Application

```bash
docker compose up -d
```

API will be available at: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

---

## Running Migrations

```bash
docker compose exec api alembic upgrade head
```

To create a new migration after model changes:

```bash
docker compose exec api alembic revision --autogenerate -m "your message"
docker compose exec api alembic upgrade head
```

---

## Running Tests

Tests run against a separate `capstone_project_test` database. Create it first:

```bash
docker compose exec db psql -U postgres -c "CREATE DATABASE capstone_project_test;"
```

Then run the test suite:

```bash
docker compose exec api pytest tests/ -v
```

> **Note:** Tests use a dedicated test database and do not affect your main database.

---

## API Endpoints

### Authentication

| Method | Endpoint                | Access        | Description              |
| ------ | ----------------------- | ------------- | ------------------------ |
| POST   | `/api/v1/auth/register` | Public        | Register a new user      |
| POST   | `/api/v1/auth/token`    | Public        | Login and get JWT token  |
| GET    | `/api/v1/auth/me`       | Authenticated | Get current user profile |

### Users

| Method | Endpoint             | Access        | Description      |
| ------ | -------------------- | ------------- | ---------------- |
| GET    | `/api/v1/users/me`   | Authenticated | Get own profile  |
| GET    | `/api/v1/users/`     | Admin         | Get all users    |
| GET    | `/api/v1/users/{id}` | Authenticated | Get user by ID   |
| PUT    | `/api/v1/users/{id}` | Authenticated | Update user      |
| DELETE | `/api/v1/users/{id}` | Admin         | Soft delete user |

### Courses

| Method | Endpoint                      | Access | Description                 |
| ------ | ----------------------------- | ------ | --------------------------- |
| GET    | `/api/v1/courses/`            | Public | Get all active courses      |
| GET    | `/api/v1/courses/{id}`        | Public | Get course by ID            |
| GET    | `/api/v1/courses/admin/all`   | Admin  | Get all courses             |
| POST   | `/api/v1/courses/`            | Admin  | Create a course             |
| PUT    | `/api/v1/courses/{id}`        | Admin  | Update a course             |
| PATCH  | `/api/v1/courses/{id}/toggle` | Admin  | Toggle course active status |
| DELETE | `/api/v1/courses/{id}`        | Admin  | Soft delete a course        |

### Enrollments

| Method | Endpoint                                    | Access  | Description                |
| ------ | ------------------------------------------- | ------- | -------------------------- |
| POST   | `/api/v1/enrollments/{course_id}`           | Student | Enroll in a course         |
| DELETE | `/api/v1/enrollments/{course_id}`           | Student | Deregister from a course   |
| GET    | `/api/v1/enrollments/`                      | Admin   | Get all enrollments        |
| GET    | `/api/v1/enrollments/course/{course_id}`    | Admin   | Get enrollments by course  |
| DELETE | `/api/v1/enrollments/admin/{enrollment_id}` | Admin   | Remove student from course |

---

## Role-Based Access Control

| Action                 | Student | Admin |
| ---------------------- | ------- | ----- |
| View courses           | ✅      | ✅    |
| Enroll in course       | ✅      | ❌    |
| Deregister from course | ✅      | ❌    |
| Create course          | ❌      | ✅    |
| Update course          | ❌      | ✅    |
| Delete course          | ❌      | ✅    |
| View all enrollments   | ❌      | ✅    |

---

## Bonus Features

- **Pagination & filtering** — all list endpoints support `skip`, `limit`, and `search`
- **Soft deletes** — users and courses are soft-deleted (`deleted_at` timestamp)
- **Audit logs** — enrollment actions are logged
- **Rate limiting** — login endpoint limited to 5 attempts per 60 seconds per IP

## Live API

https://capstone-project-3kpl.onrender.com/docs
