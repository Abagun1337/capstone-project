from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.enrollments import Enrollment


class EnrollmentRepository:
    """All Enrollment database operations. Call as EnrollmentRepository.method(db, ...)."""

    @staticmethod
    async def get_by_id(db: AsyncSession, enrollment_id: int) -> Enrollment | None:
        return await db.get(Enrollment, enrollment_id)

    @staticmethod
    async def get_by_user_and_course(
        db: AsyncSession, user_id: int, course_id: int
    ) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment).order_by(Enrollment.id.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_paginated(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Enrollment], int]:
        stmt = select(Enrollment)

        total = await db.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        stmt = stmt.order_by(Enrollment.id.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)

        return result.scalars().all(), total

    @staticmethod
    async def get_by_course(
        db: AsyncSession, course_id: int
    ) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment).where(Enrollment.course_id == course_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_course_paginated(
        db: AsyncSession,
        course_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Enrollment], int]:
        stmt = select(Enrollment).where(Enrollment.course_id == course_id)

        total = await db.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        stmt = stmt.order_by(Enrollment.id.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)

        return result.scalars().all(), total

    @staticmethod
    async def get_enrollment_count_for_course(
        db: AsyncSession, course_id: int
    ) -> int:
        result = await db.execute(
            select(func.count()).where(Enrollment.course_id == course_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_by_user(
        db: AsyncSession, user_id: int
    ) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment).where(Enrollment.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id,
        )
        db.add(enrollment)
        await db.flush()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def delete(db: AsyncSession, enrollment: Enrollment) -> None:
        await db.delete(enrollment)
        await db.flush()
