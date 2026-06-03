from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_async_db, get_current_active_user, require_admin
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollments import EnrollmentRead, PaginatedEnrollment
from app.models.users import User

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/{course_id}", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    enrollment = await EnrollmentService.enroll(db, course_id, current_user)
    await db.commit()
    return enrollment


@router.get("/", response_model=PaginatedEnrollment)
async def get_all_enrollments(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    enrollments, total = await EnrollmentService.get_all(db, skip, limit)
    return {"items": enrollments, "total": total, "skip": skip, "limit": limit}


@router.get("/course/{course_id}", response_model=PaginatedEnrollment)
async def get_enrollments_by_course(
    course_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """Retrieve all enrollments for a specific course. Admin only."""
    enrollments, total = await EnrollmentService.get_by_course(db, course_id, skip, limit)
    return {"items": enrollments, "total": total, "skip": skip, "limit": limit}


@router.delete("/admin/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_student_from_course(
    enrollment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """Remove a student from a course. Admin only."""
    await EnrollmentService.remove_student(db, enrollment_id)
    await db.commit()


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_from_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    await EnrollmentService.deregister(db, course_id, current_user)
    await db.commit()
