from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_async_db, require_admin
from app.services.course_service import CourseService
from app.schemas.courses import CourseCreate, CourseUpdate, CourseResponse, PaginatedCourse
from app.models.users import User

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=PaginatedCourse)
async def get_all_active_courses(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: AsyncSession = Depends(get_async_db)
):

    courses, total = await CourseService.get_all_active(db, skip, limit, search)
    return {"items": courses, "total": total, "skip": skip, "limit": limit}


@router.get("/admin/all", response_model=PaginatedCourse)
async def get_all_courses(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):

    courses, total = await CourseService.get_all(db, skip, limit, search)
    return {"items": courses, "total": total, "skip": skip, "limit": limit}


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
):

    return await CourseService.get_by_id(db, course_id)


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin)
):
    """Create a new course. Admin only."""
    course = await CourseService.create(db, data)
    await db.commit()
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):

    course = await CourseService.update(db, course_id, data)
    await db.commit()
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):

    await CourseService.delete(db, course_id)
    await db.commit()


@router.patch("/{course_id}/toggle", response_model=CourseResponse)
async def toggle_course_active(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):

    course = await CourseService.toggle_active(db, course_id)
    await db.commit()
    return course
