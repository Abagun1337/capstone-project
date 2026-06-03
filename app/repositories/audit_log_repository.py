from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog


class AuditLogRepository:
    '''All AuditLog database operations.'''

    @staticmethod
    async def log(
        db: AsyncSession,
        user_id: int,
        action: str,
        entity: str,
        entity_id: int,
        detail: str | None = None,
    ) -> None:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            detail=detail,
        )
        db.add(audit)
        await db.flush()

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> list[AuditLog]:
        result = await db.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_entity(
        db: AsyncSession, entity: str, entity_id: int
    ) -> list[AuditLog]:
        result = await db.execute(
            select(AuditLog).where(
                AuditLog.entity == entity,
                AuditLog.entity_id == entity_id
            )
        )
        return result.scalars().all()
