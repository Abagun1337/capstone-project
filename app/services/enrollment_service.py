from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.enrollments import Enrollment
from app.models.users import User


class EnrollmentService:

    @staticmethod
    async def enroll(db: AsyncSession, course_id: int, current_user: User) -> Enrollment:

        if current_user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can enroll in courses"
            )

        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is not active"
            )

        existing = await EnrollmentRepository.get_by_user_and_course(
            db, current_user.id, course_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )

        count = await EnrollmentRepository.get_enrollment_count_for_course(db, course_id)
        if count >= course.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is full"
            )

        enrollment = await EnrollmentRepository.create(db, current_user.id, course_id)
        await AuditLogRepository.log(
            db,
            user_id=current_user.id,
            action="enrolled",
            entity="enrollment",
            entity_id=enrollment.id,
            detail=f"User {current_user.id} enrolled in course {course_id}",
        )
        return enrollment

    @staticmethod
    async def deregister(
        db: AsyncSession, course_id: int, current_user: User
    ) -> None:
        enrollment = await EnrollmentRepository.get_by_user_and_course(
            db, current_user.id, course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        await EnrollmentRepository.delete(db, enrollment)
        await AuditLogRepository.log(
            db,
            user_id=current_user.id,
            action="deregistered",
            entity="enrollment",
            entity_id=enrollment.id,
            detail=f"User {current_user.id} deregistered from course {course_id}",
        )

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Enrollment], int]:
        return await EnrollmentRepository.get_all_paginated(db, skip, limit)

    @staticmethod
    async def get_by_course(
        db: AsyncSession,
        course_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Enrollment], int]:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        return await EnrollmentRepository.get_by_course_paginated(db, course_id, skip, limit)

    @staticmethod
    async def remove_student(
        db: AsyncSession, enrollment_id: int
    ) -> None:
        enrollment = await EnrollmentRepository.get_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        await EnrollmentRepository.delete(db, enrollment)
        await AuditLogRepository.log(
            db,
            user_id=enrollment.user_id,
            action="removed_by_admin",
            entity="enrollment",
            entity_id=enrollment.id,
            detail=f"User {enrollment.user_id} removed from course {enrollment.course_id} by admin",
        )
