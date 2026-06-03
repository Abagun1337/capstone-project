from app.main import app
from app.core.deps import get_async_db, rate_limit
from app.core.db_async import Base
from app.core.config import settings
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
import pytest
import app.core.cache as cache_module
import uuid
import asyncio


cache_module._redis_client = None


async def override_rate_limit():
    return None

app.dependency_overrides[rate_limit] = override_rate_limit

engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def override_get_async_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_dependencies():
    app.dependency_overrides[get_async_db] = override_get_async_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient):
    email = f"admin-{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Admin User", "email": email,
        "password": "adminpass123", "role": "admin",
    })
    assert reg.status_code in (200, 201), reg.text
    login = await client.post("/api/v1/auth/token", data={
        "username": email, "password": "adminpass123",
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


@pytest_asyncio.fixture
async def student_token(client: AsyncClient):
    email = f"student-{uuid.uuid4()}@test.com"
    reg = await client.post("/api/v1/auth/register", json={
        "name": "Student User", "email": email,
        "password": "studentpass123", "role": "student",
    })
    assert reg.status_code in (200, 201), reg.text
    login = await client.post("/api/v1/auth/token", data={
        "username": email, "password": "studentpass123",
    })
    assert login.status_code == 200, login.text
    return login.json()["access_token"]


@pytest_asyncio.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest_asyncio.fixture
async def sample_course(client: AsyncClient, admin_headers):
    code = f"PY-{uuid.uuid4().hex[:6].upper()}"
    response = await client.post("/api/v1/courses/", json={
        "title": "Python Basics", "code": code, "capacity": 30,
    }, headers=admin_headers)
    assert response.status_code in (200, 201), response.text
    return response.json()
