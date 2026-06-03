from pydantic import BaseModel, ConfigDict
from datetime import datetime


class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedEnrollment(BaseModel):
    items: list[EnrollmentRead]
    total: int
    skip: int
    limit: int
