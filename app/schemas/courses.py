from pydantic import BaseModel, ConfigDict, field_validator


class CourseBase(BaseModel):
    title: str
    code: str
    capacity: int

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = None
    code: str | None = None
    is_active: bool | None = None
    capacity: int | None = None

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseResponse(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedCourse(BaseModel):
    items: list[CourseResponse]
    total: int
    skip: int
    limit: int
