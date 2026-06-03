from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.courses import Course
from app.schemas.courses import CourseCreate
from datetime import datetime, timezone
from app.core.cache import get as cache_get, cache_set, cache_delete_pattern


class CourseRepository:
    """All Course database operations. Call as CourseRepository.method(db, ...)."""

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(
            select(Course).where(
                Course.id == course_id,
                Course.deleted_at == None
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Course | None:
        result = await db.execute(
            select(Course).where(
                Course.code == code,
                Course.deleted_at == None
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_paginated(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        order_by: str = 'id',
    ) -> tuple[list[Course], int]:
        cache_key = f"courses:list:{skip}:{limit}:{search or ''}"
        cached = await cache_get(cache_key)
        if cached:
            return cached["items"], cached["total"]

        stmt = select(Course).where(Course.deleted_at == None)  # noqa: E711

        if search:
            stmt = stmt.where(Course.title.ilike(f"%{search}%"))

        count_result = await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar() or 0

        col = getattr(Course, order_by, Course.id)
        stmt = stmt.order_by(col.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        courses = result.scalars().all()

        serialised = [
            {
                "id": c.id,
                "title": c.title,
                "code": c.code,
                "capacity": c.capacity,
                "is_active": c.is_active,
            }
            for c in courses
        ]
        await cache_set(cache_key, {"items": serialised, "total": total}, ttl=60)

        return courses, total

    @staticmethod
    async def get_all_active_paginated(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        order_by: str = 'id',
    ) -> tuple[list[Course], int]:
        cache_key = f"courses:active:{skip}:{limit}:{search or ''}"
        cached = await cache_get(cache_key)
        if cached:
            return cached["items"], cached["total"]

        stmt = select(Course).where(
            Course.is_active == True,
            Course.deleted_at == None
        )

        if search:
            stmt = stmt.where(Course.title.ilike(f"%{search}%"))

        count_result = await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )
        total = count_result.scalar() or 0

        col = getattr(Course, order_by, Course.id)
        stmt = stmt.order_by(col.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        courses = result.scalars().all()

        serialised = [
            {
                "id": c.id,
                "title": c.title,
                "code": c.code,
                "capacity": c.capacity,
                "is_active": c.is_active,
            }
            for c in courses
        ]
        await cache_set(cache_key, {"items": serialised, "total": total}, ttl=60)

        return courses, total

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        course = Course(
            title=data.title,
            code=data.code,
            capacity=data.capacity,
        )
        db.add(course)
        await db.flush()
        await db.refresh(course)
        await cache_delete_pattern("courses:*")
        return course

    @staticmethod
    async def update(db: AsyncSession, course: Course, fields: dict) -> Course:
        for key, value in fields.items():
            setattr(course, key, value)
        await db.flush()
        await db.refresh(course)
        await cache_delete_pattern("courses:*")
        return course

    @staticmethod
    async def delete(db: AsyncSession, course: Course) -> None:
        course.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        await cache_delete_pattern("courses:*")
