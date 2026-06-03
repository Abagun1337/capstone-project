from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    entity: str
    entity_id: int
    detail: str | None = None


class AuditLogRead(AuditLogCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
