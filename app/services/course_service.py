from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.course_repository import CourseRepository
from app.schemas.courses import CourseCreate, CourseUpdate
from app.models.courses import Course


class CourseService:

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        return course

    @staticmethod
    async def get_all_active(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[Course], int]:
        return await CourseRepository.get_all_active_paginated(db, skip, limit, search)

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[Course], int]:
        return await CourseRepository.get_all_paginated(db, skip, limit, search)

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        existing = await CourseRepository.get_by_code(db, data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists"
            )
        return await CourseRepository.create(db, data)

    @staticmethod
    async def update(db: AsyncSession, course_id: int, data: CourseUpdate) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        if data.code:
            existing = await CourseRepository.get_by_code(db, data.code)
            if existing and existing.id != course_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course code already exists"
                )
        fields = data.model_dump(exclude_unset=True)
        return await CourseRepository.update(db, course, fields)

    @staticmethod
    async def delete(db: AsyncSession, course_id: int) -> None:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        await CourseRepository.delete(db, course)

    @staticmethod
    async def toggle_active(db: AsyncSession, course_id: int) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        fields = {"is_active": not course.is_active}
        return await CourseRepository.update(db, course, fields)
